#!/usr/bin/env bash
set -euo pipefail

FFMPEG=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg

usage() {
  cat <<EOF
Usage:
  bash cut-clips.sh --video /path/to/video.mp4 --clips /path/to/clips.json --output-dir /path/to/output
EOF
}

VIDEO=""
CLIPS_JSON=""
OUT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --video) VIDEO="${2:-}"; shift 2 ;;
    --clips) CLIPS_JSON="${2:-}"; shift 2 ;;
    --output-dir) OUT_DIR="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1 ;;
  esac
done

[ -f "$VIDEO" ] || { echo "❌ Video not found: $VIDEO" >&2; exit 1; }
[ -f "$CLIPS_JSON" ] || { echo "❌ Clips JSON not found: $CLIPS_JSON" >&2; exit 1; }
[ -n "$OUT_DIR" ] || { echo "❌ --output-dir required" >&2; exit 1; }
mkdir -p "$OUT_DIR"

COUNT="$(jq '.clips | length' "$CLIPS_JSON")"
if [ "$COUNT" -eq 0 ]; then
  echo "❌ No clips in $CLIPS_JSON" >&2
  exit 1
fi

for i in $(seq 0 $((COUNT - 1))); do
  idx=$((i + 1))
  start="$(jq -r ".clips[$i].start_time" "$CLIPS_JSON")"
  end="$(jq -r ".clips[$i].end_time" "$CLIPS_JSON")"
  duration="$(python3 - <<PY
s=float(${start})
e=float(${end})
print(max(0.1, e-s))
PY
)"
  fade_out_start="$(python3 - <<PY
d=float(${duration})
print(max(0, d-0.3))
PY
)"

  out="$OUT_DIR/clip-${idx}-raw.mp4"

  ffmpeg -hide_banner -loglevel error -y \
    -ss "$start" -to "$end" -i "$VIDEO" \
    -vf "fade=t=in:st=0:d=0.3,fade=t=out:st=${fade_out_start}:d=0.3" \
    -af "afade=t=in:st=0:d=0.3,afade=t=out:st=${fade_out_start}:d=0.3" \
    -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 160k \
    "$out"

  echo "✅ Created $out"
done
