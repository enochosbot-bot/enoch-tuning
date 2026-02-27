#!/bin/bash
# Session Watchdog — archives bloated or stale sessions, cleans refs, logs to ledger
# Run via cron every hour

AGENTS_DIR="/Users/deaconsopenclaw/.openclaw/agents"
WORKSPACE="/Users/deaconsopenclaw/.openclaw/workspace"
MAX_BYTES=204800  # 200KB
MAX_AGE_HOURS=8
LOG="/tmp/session-watchdog.log"
LEDGER="$WORKSPACE/ops/task-ledger.md"
CLEANED=0
NOW=$(date +%s)
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')

echo "[$(date)] Session watchdog starting" > "$LOG"

for agent_dir in "$AGENTS_DIR"/*/sessions; do
  [ -d "$agent_dir" ] || continue
  agent=$(basename $(dirname "$agent_dir"))

  for f in "$agent_dir"/*.jsonl; do
    [ -f "$f" ] || continue
    size=$(stat -f%z "$f" 2>/dev/null || echo 0)
    mtime=$(stat -f%m "$f" 2>/dev/null || echo 0)
    age_hours=$(( (NOW - mtime) / 3600 ))
    size_kb=$((size / 1024))

    if [ "$size" -gt "$MAX_BYTES" ] || [ "$age_hours" -gt "$MAX_AGE_HOURS" ]; then
      # Extract last assistant message as summary before archiving
      summary=$(python3 -c "
import json, sys
last_msg = ''
try:
    with open('$f', 'r') as fh:
        for line in fh:
            try:
                d = json.loads(line.strip())
                if d.get('role') == 'assistant':
                    content = d.get('content', '')
                    if isinstance(content, list):
                        content = ' '.join(str(c.get('text','')) for c in content if isinstance(c,dict))
                    if content:
                        last_msg = content[:120].replace('\n', ' ').strip()
            except: pass
except: pass
print(last_msg or 'no summary')
" 2>/dev/null)

      reason=""
      [ "$size" -gt "$MAX_BYTES" ] && reason="${size_kb}KB"
      [ "$age_hours" -gt "$MAX_AGE_HOURS" ] && reason="${reason:+$reason, }${age_hours}h old"

      # Log to ledger
      echo "[$TIMESTAMP] [watchdog] [$agent] [🧹 pruned] — $reason. Last: $summary" >> "$LEDGER"

      # Archive
      mkdir -p "$agent_dir/archive"
      mv "$f" "$agent_dir/archive/"
      CLEANED=$((CLEANED + 1))
      echo "  Archived: $agent/$(basename $f) (${size_kb}KB, ${age_hours}h old)" >> "$LOG"
    fi
  done

  # Clean stale refs from sessions.json
  sjson="$(dirname "$agent_dir")/sessions.json"
  [ -f "$sjson" ] || continue
  python3 -c "
import json, os
sj_path = '$sjson'
sessions_dir = '$agent_dir'
try:
    with open(sj_path, 'r') as f:
        data = json.load(f)
except:
    exit(0)
removed = 0
for key in list(data.keys()):
    entry = data[key]
    if isinstance(entry, dict) and 'file' in entry:
        sf = entry['file']
        full = os.path.join(sessions_dir, sf) if not sf.startswith('/') else sf
        if not os.path.exists(full):
            del data[key]
            removed += 1
if removed:
    with open(sj_path, 'w') as f:
        json.dump(data, f, indent=2)
" 2>/dev/null
done

# Clean archive dirs older than 24h to free disk
find "$AGENTS_DIR" -path '*/sessions/archive/*.jsonl' -mmin +1440 -delete 2>/dev/null

# Rotate ledger weekly (if >500KB)
ledger_size=$(stat -f%z "$LEDGER" 2>/dev/null || echo 0)
if [ "$ledger_size" -gt 512000 ]; then
  mkdir -p "$WORKSPACE/ops/ledger-archive"
  mv "$LEDGER" "$WORKSPACE/ops/ledger-archive/ledger-$(date +%Y%m%d).md"
  echo "# Task Ledger" > "$LEDGER"
  echo "_Rotated $(date). See ops/ledger-archive/ for history._" >> "$LEDGER"
  echo "---" >> "$LEDGER"
fi

echo "[$(date)] Done. Archived $CLEANED sessions." >> "$LOG"
