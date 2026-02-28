# Daily Log Template

## File Location
`~/Documents/Brain/Personal Memories/[Agent Name]/Daily Logs/YYYY-MM-DD.md`

Create a new file each day. Never overwrite — append within the day.

---

## Format

```markdown
# Daily Log — YYYY-MM-DD

## Session: [Context] (HH:MM AM/PM TZ)

### [Task/Topic Name] [✅|🚧|❌]
- [What was done]
- [Key decisions made]
- [Blockers encountered]
- [Links to artifacts created]

### [Another Task]
- [Details]

### Status
[1-2 sentence summary of session state: what's done, what's next]
```

---

## Status Emojis
- ✅ Complete
- 🚧 In progress / partial
- ❌ Failed / blocked
- ⏸️ Paused intentionally

---

## Rules

1. **New section per session** — mark with timestamp
2. **Task-level granularity** — not every command, but every meaningful unit of work
3. **Always include status line** — future sessions scan this first
4. **Link artifacts** — if you created a file/doc/script, note its path
5. **Capture decisions** — not just what, but why

---

## What NOT to Log
- Routine tool calls
- Failed attempts that led nowhere (unless the failure is instructive)
- Conversations that didn't result in action
- Anything already captured in typed memory (Decisions/, Lessons/, etc.)

---

## Example

```markdown
# Daily Log — 2026-02-28

## Session: Main (02:04 AM CST)

### Full Memory System Migration ✅
- Audited workspace/memory/ vs Obsidian — discovered stale architecture
- Migrated all workspace memory/ daily logs to Obsidian Daily Logs/
- Merged files with unique content (2026-02-16, 2026-02-27)
- Deleted workspace memory/ directory entirely
- Updated AGENTS.md: all memory ops now point to Obsidian

### Status
Obsidian is now the single source of truth for all memory.

## Session: Main (11:00 AM CST)

### Enoch-tuning package updates 🚧
- Added ops templates: notification-routing, production-queue, daily-log
- Still need: pruning protocols, data management

### Status
Package ~70% complete. Finishing remaining templates.
```
