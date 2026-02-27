#!/bin/bash
# Cron Status Reporter — reads job states from jobs.json, logs new completions to task-ledger
# Run hourly (alongside watchdog)

JOBS_FILE="/Users/deaconsopenclaw/.openclaw/cron/jobs.json"
LEDGER="/Users/deaconsopenclaw/.openclaw/workspace/ops/task-ledger.md"
STATE_FILE="/tmp/cron-reporter-last-run.json"
NOW=$(date '+%Y-%m-%d %H:%M')

python3 << 'PYEOF'
import json, os, sys
from datetime import datetime

jobs_file = '/Users/deaconsopenclaw/.openclaw/cron/jobs.json'
ledger = '/Users/deaconsopenclaw/.openclaw/workspace/ops/task-ledger.md'
state_file = '/tmp/cron-reporter-last-run.json'

# Load previous state (last known run timestamps per job)
prev_state = {}
if os.path.exists(state_file):
    try:
        with open(state_file) as f:
            prev_state = json.load(f)
    except:
        pass

# Load current jobs
with open(jobs_file) as f:
    data = json.load(f)

new_state = {}
entries = []

for job in data.get('jobs', []):
    jid = job.get('id', '')
    name = job.get('name', 'unnamed')
    agent = job.get('agentId', '?')
    state = job.get('state', {})
    
    last_run_ms = state.get('lastRunAtMs', 0)
    last_status = state.get('lastStatus', state.get('lastRunStatus', 'unknown'))
    last_error = state.get('lastError', '')
    duration_ms = state.get('lastDurationMs', 0)
    consec_errors = state.get('consecutiveErrors', 0)
    
    new_state[jid] = last_run_ms
    
    # Only log if this run is newer than what we last recorded
    prev_run_ms = prev_state.get(jid, 0)
    if last_run_ms > prev_run_ms and last_run_ms > 0:
        # Format timestamp
        ts = datetime.fromtimestamp(last_run_ms / 1000).strftime('%Y-%m-%d %H:%M')
        duration_s = round(duration_ms / 1000, 1)
        
        # Map status to emoji
        if last_status == 'ok':
            status_str = '✅ done'
        elif last_status == 'error':
            status_str = '❌ failed'
        else:
            status_str = f'⚠️ {last_status}'
        
        summary = f'{name} ({duration_s}s)'
        if last_error:
            summary += f' — {last_error[:80]}'
        if consec_errors > 1:
            summary += f' [{consec_errors} consecutive errors]'
        
        entries.append(f'[{ts}] [cron] [{agent}] [{status_str}] — {summary}')

# Append to ledger
if entries:
    with open(ledger, 'a') as f:
        for e in entries:
            f.write(e + '\n')
    print(f'Logged {len(entries)} cron completions to ledger')
else:
    print('No new cron completions since last check')

# Save state
with open(state_file, 'w') as f:
    json.dump(new_state, f)
PYEOF
