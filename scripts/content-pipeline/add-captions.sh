#!/usr/bin/env bash
set -euo pipefail

# Use ffmpeg-full (has libass for subtitle burning), same as Kiriakou pipeline
FFMPEG=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg

usage() {
  cat <<EOF
Usage:
  bash add-captions.sh --clips clips.json --transcript-srt transcript.srt --input-dir output_dir --output-dir output_dir
EOF
}

CLIPS_JSON=""
TRANSCRIPT_SRT=""
INPUT_DIR=""
OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --clips) CLIPS_JSON="${2:-}"; shift 2 ;;
    --transcript-srt) TRANSCRIPT_SRT="${2:-}"; shift 2 ;;
    --input-dir) INPUT_DIR="${2:-}"; shift 2 ;;
    --output-dir) OUTPUT_DIR="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1 ;;
  esac
done

[ -f "$CLIPS_JSON" ] || { echo "❌ Missing clips json" >&2; exit 1; }
[ -f "$TRANSCRIPT_SRT" ] || { echo "❌ Missing transcript srt" >&2; exit 1; }
[ -d "$INPUT_DIR" ] || { echo "❌ Missing input dir" >&2; exit 1; }
[ -d "$OUTPUT_DIR" ] || { echo "❌ Missing output dir" >&2; exit 1; }

COUNT="$(jq '.clips | length' "$CLIPS_JSON")"

for i in $(seq 0 $((COUNT - 1))); do
  idx=$((i + 1))
  start="$(jq -r ".clips[$i].start_time" "$CLIPS_JSON")"
  end="$(jq -r ".clips[$i].end_time" "$CLIPS_JSON")"

  in_clip="$INPUT_DIR/clip-${idx}-raw.mp4"
  seg_srt="$OUTPUT_DIR/clip-${idx}.srt"
  out_clip="$OUTPUT_DIR/clip-${idx}-captioned.mp4"

  [ -f "$in_clip" ] || { echo "⚠️ Skipping missing $in_clip"; continue; }

  python3 - "$TRANSCRIPT_SRT" "$seg_srt" "$start" "$end" <<'PY'
import re, sys
from pathlib import Path

src, out, start_s, end_s = sys.argv[1:]
start, end = float(start_s), float(end_s)


def to_sec(t):
    h,m,sms = t.split(':')
    s,ms = sms.split(',')
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000

def to_srt(sec):
    if sec < 0: sec = 0
    ms = int(round(sec*1000))
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

raw = Path(src).read_text(encoding='utf-8', errors='ignore').strip()
blocks = re.split(r'\n\s*\n', raw)
out_blocks = []
for b in blocks:
    lines = [ln.rstrip() for ln in b.splitlines() if ln.strip()!='']
    if len(lines) < 2 or '-->' not in lines[1]:
        continue
    time_line = lines[1]
    left, right = [x.strip() for x in time_line.split('-->')]
    st, en = to_sec(left), to_sec(right)
    if en < start or st > end:
        continue
    nst = max(0.0, st - start)
    nen = max(nst + 0.05, min(end, en) - start)
    text = ' '.join(lines[2:]).strip()
    if not text:
        continue

    # phrase-style shortening for bold viral captions
    if len(text.split()) > 10:
        words = text.split()
        text = ' '.join(words[:10]) + '…'

    out_blocks.append((nst, nen, text))

with open(out, 'w', encoding='utf-8') as f:
    for i, (st, en, tx) in enumerate(out_blocks, start=1):
        f.write(f"{i}\n{to_srt(st)} --> {to_srt(en)}\n{tx}\n\n")
PY

  # Escape colons and backslashes in path for ffmpeg filtergraph
  escaped_srt="${seg_srt//\\/\\\\}"
  escaped_srt="${escaped_srt//:/\\:}"

  $FFMPEG -hide_banner -loglevel error -y -i "$in_clip" \
    -vf "subtitles=filename='${escaped_srt}':force_style='FontName=Arial,FontSize=18,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=3,Shadow=1,Alignment=2,MarginV=220'" \
    -c:v libx264 -preset medium -crf 18 -c:a copy \
    "$out_clip"

  echo "✅ Captioned $out_clip"
done
