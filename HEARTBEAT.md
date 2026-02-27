# HEARTBEAT.md

## Active Tasks

### 1. Stale Dispatch Check
Read `ops/in-flight.md`. Check the Active table.
- If any row has been open for **>60 minutes**: alert Deacon with the task name, agent, and how long it's been running. Check `sessions_history` for that agent if possible.
- If Active table is empty or all rows are recent (<60min): no action needed.
- Quiet hours apply (23:00–08:00 CST) — skip alert unless a task has been stale >3 hours.
