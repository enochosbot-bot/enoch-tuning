#\!/bin/bash
# Session Watchdog — archives any session file over 400KB and cleans refs
# Run via cron every 2 hours

AGENTS_DIR="/Users/deaconsopenclaw/.openclaw/agents"
MAX_BYTES=409600  # 400KB
LOG="/tmp/session-watchdog.log"
CLEANED=0

echo "[$(date)] Session watchdog starting" > "$LOG"

for agent_dir in "$AGENTS_DIR"/*/sessions; do
  agent=$(echo "$agent_dir" | sed "s|.*/agents/||;s|/sessions||")
  
  for f in "$agent_dir"/*.jsonl; do
    [ -f "$f" ] || continue
    size=$(stat -f%z "$f" 2>/dev/null || echo 0)
    if [ "$size" -gt "$MAX_BYTES" ]; then
      mkdir -p "$agent_dir/archive"
      mv "$f" "$agent_dir/archive/"
      CLEANED=$((CLEANED + 1))
      echo "  Archived: $agent/$(basename $f) ($(echo "$size / 1024" | bc)KB)" >> "$LOG"
    fi
  done
  
  # Clean stale refs from sessions.json
  sjson="$agent_dir/sessions.json"
  [ -f "$sjson" ] || continue
  python3 -c "
import json, os
with open() as f:
    data = json.load(f)
removed = 0
for key in list(data.keys()):
    entry = data[key]
    if isinstance(entry, dict):
        sf = entry.get(sessionFile, )
        if sf and not os.path.exists(sf):
            del data[key]
            removed += 1
if removed:
    with open(, w) as f:
        json.dump(data, f, indent=2)
" 2>/dev/null
done

echo "[$(date)] Done. Archived $CLEANED sessions." >> "$LOG"

if [ "$CLEANED" -gt 0 ]; then
  echo "$CLEANED bloated sessions archived" >> "$LOG"
fi
