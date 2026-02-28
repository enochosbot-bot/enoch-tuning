#!/usr/bin/env bash
set -euo pipefail

FFMPEG=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg

usage() {
  cat <<EOF
Usage:
  bash format-vertical.sh --clips clips.json --input-dir output_dir --output-dir output_dir
EOF
}

CLIPS_JSON=""
INPUT_DIR=""
OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --clips) CLIPS_JSON="${2:-}"; shift 2 ;;
    --input-dir) INPUT_DIR="${2:-}"; shift 2 ;;
    --output-dir) OUTPUT_DIR="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1 ;;
  esac
done

[ -f "$CLIPS_JSON" ] || { echo "❌ Missing clips json" >&2; exit 1; }
[ -d "$INPUT_DIR" ] || { echo "❌ Missing input dir" >&2; exit 1; }
[ -d "$OUTPUT_DIR" ] || { echo "❌ Missing output dir" >&2; exit 1; }

COUNT="$(jq '.clips | length' "$CLIPS_JSON")"

for i in $(seq 0 $((COUNT - 1))); do
  idx=$((i + 1))
  in_clip="$INPUT_DIR/clip-${idx}-captioned.mp4"
  out_clip="$OUTPUT_DIR/clip-${idx}-final-vertical.mp4"

  [ -f "$in_clip" ] || { echo "⚠️ Skipping missing $in_clip"; continue; }

  dims="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x "$in_clip")"
  width="${dims%x*}"
  height="${dims#*x}"

  aspect="$(python3 - <<PY
w=float(${width})
h=float(${height})
print(w/h if h else 1.777)
PY
)"

  is_vertical="$(python3 - <<PY
a=float(${aspect})
print('1' if a <= 0.8 else '0')
PY
)"

  if [ "$is_vertical" = "1" ]; then
    vf="scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"
  else
    vf="[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:10[bg];[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
  fi

  if [ "$is_vertical" = "1" ]; then
    $FFMPEG -hide_banner -loglevel error -y -i "$in_clip" \
      -vf "$vf" \
      -r 30 -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 160k \
      "$out_clip"
  else
    $FFMPEG -hide_banner -loglevel error -y -i "$in_clip" \
      -filter_complex "$vf" \
      -map "[v]" -map 0:a? \
      -r 30 -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 160k \
      "$out_clip"
  fi

  echo "✅ Vertical clip $out_clip"
done
