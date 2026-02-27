# HEARTBEAT.md

## Active Tasks

### 1. Stale Dispatch Check
Read `ops/in-flight.md`. Check the Active table.
- If any row has been open for **>60 minutes**: alert Deacon with the task name, agent, and how long it's been running. Check `sessions_history` for that agent if possible.
- If Active table is empty or all rows are recent (<60min): no action needed.
- Quiet hours apply (23:00–08:00 CST) — skip alert unless a task has been stale >3 hours.

### 2. Checkpoint Continuity
Read `/Users/deaconsopenclaw/.openclaw/workspace/shared-context/checkpoints/session-checkpoint.md`.
- If `status: active` and `updated_at` is older than 15 minutes: ping Deacon that active work may be stalled and include `next_step`.
- If `status: completed`: no action needed.
- If file is missing fields: rewrite with current task state before continuing work.
