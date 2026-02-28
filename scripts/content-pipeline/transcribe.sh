#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage:
  bash transcribe.sh /path/to/video.mp4 --srt /path/to/transcript.srt --json /path/to/transcript.json

Notes:
- Uses OpenAI Whisper API when OPENAI_API_KEY is present.
- Falls back to local whisper CLI if available.
- For files >25MB, extracts/splits audio and transcribes in chunks.
EOF
}

VIDEO=""
OUT_SRT=""
OUT_JSON=""

if [ $# -lt 1 ]; then
  usage
  exit 1
fi

VIDEO="$1"
shift

while [[ $# -gt 0 ]]; do
  case "$1" in
    --srt)
      OUT_SRT="${2:-}"
      shift 2
      ;;
    --json)
      OUT_JSON="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [ ! -f "$VIDEO" ]; then
  echo "❌ Video not found: $VIDEO" >&2
  exit 1
fi

if [ -z "$OUT_SRT" ] || [ -z "$OUT_JSON" ]; then
  echo "❌ --srt and --json are required" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT_SRT")" "$(dirname "$OUT_JSON")"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

AUDIO="$TMP_DIR/audio.wav"
ffmpeg -hide_banner -loglevel error -y -i "$VIDEO" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$AUDIO"

FILE_SIZE_BYTES="$(stat -f%z "$AUDIO")"
LIMIT_BYTES=$((25 * 1024 * 1024))

USE_OPENAI=0
if [ -n "${OPENAI_API_KEY:-}" ]; then
  USE_OPENAI=1
fi

if [ $USE_OPENAI -eq 0 ] && ! command -v whisper >/dev/null 2>&1; then
  echo "❌ Neither OPENAI_API_KEY is set nor local 'whisper' CLI is installed." >&2
  exit 1
fi

transcribe_chunk_openai() {
  local in_audio="$1"
  local out_json="$2"
  curl -sS https://api.openai.com/v1/audio/transcriptions \
    -H "Authorization: Bearer ${OPENAI_API_KEY}" \
    -F "file=@${in_audio}" \
    -F "model=whisper-1" \
    -F "response_format=verbose_json" \
    > "$out_json"

  if ! jq -e . >/dev/null 2>&1 < "$out_json"; then
    echo "❌ OpenAI transcription returned invalid JSON" >&2
    exit 1
  fi

  if jq -e '.error' >/dev/null 2>&1 < "$out_json"; then
    local err_msg
    err_msg="$(jq -r '.error.message // .error' "$out_json")"
    echo "⚠️  OpenAI transcription error: $err_msg" >&2
    # Check for quota/billing errors — fall back to local whisper
    if echo "$err_msg" | grep -qi "quota\|billing\|rate.limit\|insufficient"; then
      echo "↩️  Falling back to local whisper..." >&2
      USE_OPENAI=0
      transcribe_chunk_local "$in_audio" "$out_json"
      return
    fi
    echo "❌ OpenAI transcription error (non-recoverable)" >&2
    exit 1
  fi
}

transcribe_chunk_local() {
  local in_audio="$1"
  local out_json="$2"
  local base="$(basename "$in_audio")"
  local stem="${base%.*}"
  local out_dir="$TMP_DIR/local-whisper"
  mkdir -p "$out_dir"

  whisper "$in_audio" \
    --model base \
    --output_format json \
    --output_dir "$out_dir" \
    --fp16 False \
    >/dev/null 2>&1

  local produced="$out_dir/${stem}.json"
  if [ ! -f "$produced" ]; then
    echo "❌ Local whisper did not produce expected JSON: $produced" >&2
    exit 1
  fi
  cp "$produced" "$out_json"
}

transcribe_chunk() {
  local in_audio="$1"
  local out_json="$2"
  if [ $USE_OPENAI -eq 1 ]; then
    transcribe_chunk_openai "$in_audio" "$out_json"
  else
    transcribe_chunk_local "$in_audio" "$out_json"
  fi
}

# If >25MB, split into ~8 minute chunks first.
CHUNK_DURATION=480
DURATION="$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$AUDIO")"

CHUNKS_DIR="$TMP_DIR/chunks"
mkdir -p "$CHUNKS_DIR"

if [ "$FILE_SIZE_BYTES" -gt "$LIMIT_BYTES" ]; then
  ffmpeg -hide_banner -loglevel error -y -i "$AUDIO" -f segment -segment_time "$CHUNK_DURATION" -c copy "$CHUNKS_DIR/chunk_%03d.wav"
else
  cp "$AUDIO" "$CHUNKS_DIR/chunk_000.wav"
fi

shopt -s nullglob
CHUNKS=("$CHUNKS_DIR"/chunk_*.wav)
if [ ${#CHUNKS[@]} -eq 0 ]; then
  echo "❌ No audio chunks created" >&2
  exit 1
fi

SEGMENTS_FILE="$TMP_DIR/segments.ndjson"
: > "$SEGMENTS_FILE"
FULL_TEXT_FILE="$TMP_DIR/full_text.txt"
: > "$FULL_TEXT_FILE"

for idx in "${!CHUNKS[@]}"; do
  chunk="${CHUNKS[$idx]}"
  chunk_json="$TMP_DIR/chunk_${idx}.json"
  transcribe_chunk "$chunk" "$chunk_json"

  offset_sec=$(python3 - <<PY
idx = int(${idx})
print(idx * ${CHUNK_DURATION})
PY
)

  jq -c --argjson off "$offset_sec" '
    (.segments // [])[]
    | {
        start: ((.start // 0) + $off),
        end: ((.end // 0) + $off),
        text: (.text // "")
      }
  ' "$chunk_json" >> "$SEGMENTS_FILE"

  jq -r '.text // ""' "$chunk_json" >> "$FULL_TEXT_FILE"
  echo >> "$FULL_TEXT_FILE"
done

python3 - "$SEGMENTS_FILE" "$OUT_JSON" <<'PY'
import json, sys
segments_path, out_json = sys.argv[1], sys.argv[2]
segments = []
with open(segments_path, 'r', encoding='utf-8') as f:
    for line in f:
        line=line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if obj.get('end',0) > obj.get('start',0):
                segments.append(obj)
        except Exception:
            pass
text = " ".join(s.get('text','').strip() for s in segments).strip()
out = {"text": text, "segments": segments}
with open(out_json, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
PY

python3 - "$OUT_JSON" "$OUT_SRT" <<'PY'
import json, sys

def srt_time(sec: float) -> str:
    if sec < 0:
        sec = 0
    ms = int(round(sec * 1000))
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

in_json, out_srt = sys.argv[1], sys.argv[2]
with open(in_json, 'r', encoding='utf-8') as f:
    data = json.load(f)
segments = data.get('segments', [])
with open(out_srt, 'w', encoding='utf-8') as f:
    i=1
    for seg in segments:
        st = float(seg.get('start', 0))
        en = float(seg.get('end', st + 1))
        text = (seg.get('text') or '').strip()
        if not text or en <= st:
            continue
        f.write(f"{i}\n{srt_time(st)} --> {srt_time(en)}\n{text}\n\n")
        i += 1
PY

echo "✅ Transcript written:"
echo "  - $OUT_SRT"
echo "  - $OUT_JSON"
