#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<EOF
Usage:
  bash pipeline.sh /path/to/video.mp4 [--output-dir /path/to/output]

Description:
  Runs full video-to-shorts pipeline:
  1) transcribe
  2) find clips
  3) cut clips
  4) add captions
  5) format vertical 9:16
EOF
}

check_deps() {
  local missing=()
  local deps=(ffmpeg python3 curl jq)
  for d in "${deps[@]}"; do
    if ! command -v "$d" >/dev/null 2>&1; then
      missing+=("$d")
    fi
  done

  if [ ${#missing[@]} -gt 0 ]; then
    echo "❌ Missing required dependencies: ${missing[*]}" >&2
    echo "Install them and retry." >&2
    exit 1
  fi
}

slugify() {
  local s="$1"
  s="$(echo "$s" | tr '[:upper:]' '[:lower:]')"
  s="$(echo "$s" | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"
  echo "$s"
}

VIDEO=""
BASE_OUTPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir)
      BASE_OUTPUT="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [ -z "$VIDEO" ]; then
        VIDEO="$1"
      else
        echo "Unknown argument: $1" >&2
        usage
        exit 1
      fi
      shift
      ;;
  esac
done

if [ -z "$VIDEO" ]; then
  usage
  exit 1
fi

check_deps

if [ ! -f "$VIDEO" ]; then
  echo "❌ Video file not found: $VIDEO" >&2
  exit 1
fi

if [ -z "$BASE_OUTPUT" ]; then
  BASE_OUTPUT="$SCRIPT_DIR/output"
fi

mkdir -p "$BASE_OUTPUT"

VIDEO_NAME="$(basename "$VIDEO")"
VIDEO_STEM="${VIDEO_NAME%.*}"
DATE_TAG="$(date +%F)"
OUT_DIR="$BASE_OUTPUT/${DATE_TAG}-$(slugify "$VIDEO_STEM")"
mkdir -p "$OUT_DIR"

TRANSCRIPT_SRT="$OUT_DIR/transcript.srt"
TRANSCRIPT_JSON="$OUT_DIR/transcript.json"
CLIPS_JSON="$OUT_DIR/clips.json"

echo "▶️ Output directory: $OUT_DIR"

echo "\n[1/5] Transcribing..."
bash "$SCRIPT_DIR/transcribe.sh" "$VIDEO" --srt "$TRANSCRIPT_SRT" --json "$TRANSCRIPT_JSON"

echo "\n[2/5] Finding best clips..."
python3 "$SCRIPT_DIR/find-clips.py" \
  --transcript "$TRANSCRIPT_JSON" \
  --output "$CLIPS_JSON" \
  --count 3

echo "\n[3/5] Cutting clips..."
bash "$SCRIPT_DIR/cut-clips.sh" \
  --video "$VIDEO" \
  --clips "$CLIPS_JSON" \
  --output-dir "$OUT_DIR"

echo "\n[4/5] Burning captions..."
bash "$SCRIPT_DIR/add-captions.sh" \
  --clips "$CLIPS_JSON" \
  --transcript-srt "$TRANSCRIPT_SRT" \
  --input-dir "$OUT_DIR" \
  --output-dir "$OUT_DIR"

echo "\n[5/5] Formatting vertical..."
bash "$SCRIPT_DIR/format-vertical.sh" \
  --clips "$CLIPS_JSON" \
  --input-dir "$OUT_DIR" \
  --output-dir "$OUT_DIR"

echo "\n✅ Pipeline complete"
echo "Artifacts:"
echo "  - $TRANSCRIPT_SRT"
echo "  - $TRANSCRIPT_JSON"
echo "  - $CLIPS_JSON"
echo "  - clip-*-raw.mp4"
echo "  - clip-*-captioned.mp4"
echo "  - clip-*-final-vertical.mp4"
