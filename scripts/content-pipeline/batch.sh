#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage:
  bash batch.sh /path/to/folder/of/videos/ [--output-dir /path/to/output]
EOF
}

IN_DIR="${1:-}"
shift || true
BASE_OUTPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir) BASE_OUTPUT="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1 ;;
  esac
done

[ -d "$IN_DIR" ] || { echo "❌ Input directory not found: $IN_DIR" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

shopt -s nullglob
files=(
  "$IN_DIR"/*.mp4 "$IN_DIR"/*.mov "$IN_DIR"/*.mkv "$IN_DIR"/*.m4v "$IN_DIR"/*.avi "$IN_DIR"/*.webm
)

if [ ${#files[@]} -eq 0 ]; then
  echo "No video files found in $IN_DIR"
  exit 0
fi

for f in "${files[@]}"; do
  echo "\n=============================="
  echo "Processing: $f"
  echo "=============================="
  if [ -n "$BASE_OUTPUT" ]; then
    bash "$SCRIPT_DIR/pipeline.sh" "$f" --output-dir "$BASE_OUTPUT"
  else
    bash "$SCRIPT_DIR/pipeline.sh" "$f"
  fi
done

echo "\n✅ Batch complete"
