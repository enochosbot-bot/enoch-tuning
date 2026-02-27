#!/bin/bash
# Wrapper for openai-image-gen that outputs to workspace
SKILL_DIR="/opt/homebrew/lib/node_modules/openclaw/skills/openai-image-gen"
OUT_DIR="/Users/deaconsopenclaw/.openclaw/workspace/creative-output"
mkdir -p "$OUT_DIR"

python3 "$SKILL_DIR/scripts/gen.py" \
  --out-dir "$OUT_DIR" \
  --model gpt-image-1 \
  --quality high \
  --count 1 \
  "$@"
