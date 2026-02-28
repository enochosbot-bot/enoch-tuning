#!/bin/bash
set -euo pipefail

WORKSPACE="/Users/deaconsopenclaw/.openclaw/workspace"
AGENTS_DIR="/Users/deaconsopenclaw/.openclaw/agents"
STATE_DIR="$WORKSPACE/shared-context/state"
STATE_FILE="$STATE_DIR/session-archive-seen.txt"
OUT_DIR="$HOME/Documents/Brain/Research/OpenClaw Ops/Session Incidents"
INDEX_FILE="$HOME/Documents/Brain/Research/OpenClaw Ops/OpenClaw Incident Log.md"
MAX_BYTES=204800
MAX_AGE_HOURS=8
NOW_EPOCH=$(date +%s)
TODAY=$(date +%F)
NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

mkdir -p "$STATE_DIR" "$OUT_DIR" "$(dirname "$INDEX_FILE")"
touch "$STATE_FILE"

DAILY_FILE="$OUT_DIR/$TODAY-session-incidents.md"
if [ ! -f "$DAILY_FILE" ]; then
  cat > "$DAILY_FILE" <<EOF
---
tags: [openclaw, ops, incidents, session-archive]
date: $TODAY
source: openclaw-session-watchdog
---

# Session Incidents — $TODAY

EOF
fi

if [ ! -f "$INDEX_FILE" ]; then
  cat > "$INDEX_FILE" <<EOF
---
tags: [openclaw, ops, incidents, index]
date: $TODAY
source: generated-index
---

# OpenClaw Incident Log

| Date | Severity | Agent | Component | Incident | Note |
|---|---|---|---|---|---|
EOF
fi

added=0

while IFS= read -r f; do
  [ -f "$f" ] || continue
  rel="${f#$AGENTS_DIR/}"
  if grep -Fxq "$rel" "$STATE_FILE"; then
    continue
  fi

  # Parse metadata
  agent=$(echo "$rel" | cut -d'/' -f1)
  base=$(basename "$f")
  size=$(stat -f%z "$f" 2>/dev/null || echo 0)
  size_kb=$((size/1024))
  mtime=$(stat -f%m "$f" 2>/dev/null || echo "$NOW_EPOCH")
  age_h=$(((NOW_EPOCH - mtime)/3600))

  severity="low"
  trigger="stale-session"
  if [ "$size" -gt "$MAX_BYTES" ]; then
    severity="medium"
    trigger="context-bloat"
  fi
  if [ "$size" -gt "$MAX_BYTES" ] && [ "$age_h" -gt "$MAX_AGE_HOURS" ]; then
    trigger="context-bloat+stale-session"
  fi

  topic="none"
  if [[ "$base" =~ topic-([0-9]+) ]]; then
    topic="${BASH_REMATCH[1]}"
  fi

  # Pull first matching error keyword if present (compact + safe for markdown)
  signal=$(python3 - <<PY
import re
p = r'''$f'''
pat = re.compile(r'(error|failed|enoent|timeout|exception)', re.I)
match = ''
try:
    with open(p, 'r', encoding='utf-8', errors='ignore') as fh:
        for line in fh:
            m = pat.search(line)
            if m:
                match = m.group(1).lower()
                break
except Exception:
    pass
print(match or 'none-detected')
PY
)

  cat >> "$DAILY_FILE" <<EOF
## Incident: $base
- time_utc: $NOW_ISO
- severity: $severity
- agent: $agent
- component: session-archive/watchdog
- trigger: $trigger
- reason: size=${size_kb}KB age=${age_h}h topic=${topic}
- signal: $signal
- fix: read transcripts from ~/.openclaw/agents/<agent>/sessions/... (not workspace transcriptPath); summarize + promote only important lessons to MEMORY.md
- source_file: $f

EOF

  sev_upper=$(echo "$severity" | tr '[:lower:]' '[:upper:]')
  row="| $TODAY | $sev_upper | $agent | session-archive/watchdog | $base | [[$TODAY-session-incidents]] |"
  grep -Fqx "$row" "$INDEX_FILE" || echo "$row" >> "$INDEX_FILE"
  echo "$rel" >> "$STATE_FILE"
  added=$((added+1))
done < <(find "$AGENTS_DIR" -path '*/sessions/archive/*.jsonl' -mmin -180 -type f | sort)

echo "SESSION_ARCHIVE_OBSIDIAN_SYNC added=$added file=$DAILY_FILE"
