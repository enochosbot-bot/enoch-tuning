# Pruning Protocols

## Why Prune
- Context windows fill up → quality degrades
- Stale data misleads future sessions
- Token costs compound on bloated files
- Agents waste time reading irrelevant history

---

## What Gets Pruned

### 1. Session Checkpoints
- **Location:** `shared-context/checkpoints/`
- **Frequency:** Every 2 hours (cron)
- **Rule:** Keep only `status: active` or last 24 hours of `status: completed`
- **Method:** Delete files older than 24 hours with completed status

### 2. Daily Logs
- **Location:** `~/Documents/Brain/Personal Memories/[Agent]/Daily Logs/`
- **Frequency:** Weekly (Sunday 3 AM)
- **Rule:** Logs older than 30 days → archive to `Daily Logs/archive/YYYY-MM/`
- **Keep:** Current month + last month always accessible

### 3. Draft Files
- **Location:** `shared-context/drafts/`
- **Frequency:** Weekly
- **Rule:** Approved/published drafts → delete after 7 days
- **KILL'd drafts:** Move to `drafts/archived/` immediately

### 4. Feedback Files
- **Location:** `shared-context/feedback/`
- **Frequency:** Weekly
- **Rule:** Delete feedback for completed content older than 14 days

### 5. In-Flight Tracker
- **Location:** `ops/in-flight.md`
- **Frequency:** Daily
- **Rule:** Completed rows older than 7 days → delete
- **Never delete:** Active rows (even if stale — those need escalation, not pruning)

### 6. Production Queue
- **Location:** `ops/production-queue.md`
- **Frequency:** Weekly
- **Rule:** Completed items older than 30 days → delete
- **Parked items:** Review quarterly, delete if no longer relevant

### 7. Exec Audit Logs
- **Location:** `ops/exec-audit.log`
- **Frequency:** Monthly
- **Rule:** Archive to `ops/exec-audit-archive/YYYY-MM.log` when >100KB

### 8. MEMORY.md
- **Location:** Workspace root
- **Frequency:** Weekly manual review
- **Rule:** Remove facts that are:
  - Outdated (superseded by newer info)
  - Duplicated in Obsidian typed memory
  - One-time context (not recurring reference)
- **Keep:** Infrastructure facts, key people, operational patterns

---

## Cron Schedule

| Job | Frequency | What |
|---|---|---|
| Session Auto-Prune | Every 2 hours | Checkpoints older than 24h |
| Weekly Memory Hygiene | Sunday 3 AM | Logs, drafts, feedback, MEMORY.md |
| Monthly Archive | 1st of month | Exec audit logs |

---

## Manual Triggers

Run these when context feels bloated:

```bash
# Check file sizes
du -sh ~/.openclaw/workspace/ops/*
du -sh ~/.openclaw/workspace/shared-context/*

# Find large/old files
find ~/.openclaw/workspace -type f -size +100k -mtime +7

# Prune completed checkpoints manually
rm shared-context/checkpoints/*-completed-*.md
```

---

## Anti-Patterns

- ❌ Pruning active work (even if old)
- ❌ Deleting without archiving (lose audit trail)
- ❌ Pruning typed memory (Obsidian Decisions/, Lessons/, etc.)
- ❌ Manual prune during active session (wait for idle)
- ❌ Pruning logs before reviewing for lessons

---

## The Nuclear Option

If context is severely degraded:
1. Trigger `/compact` in chat
2. Write critical state to `shared-context/recovery-state.md` first
3. Start fresh session
4. Re-read AGENTS.md, SOUL.md, today's daily log
5. Recovery file provides continuity

This is better than pushing through with garbage context.
