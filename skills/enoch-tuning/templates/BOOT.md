# BOOT.md — Crash Recovery Protocol

_Run this procedure whenever you start fresh: session restart, gateway restart, or post-compaction. This is your recovery anchor._

---

## When to Run This

- Session restart (gateway restarted, system rebooted)
- Post-compaction (context was compacted, working memory lost)
- You wake up with no memory of what was in progress

If none of these apply — normal session start, just woke up naturally — skip to your normal `AGENTS.md` startup sequence.

---

## Step 1 — Read `active-tasks.md`

This file is the crash recovery anchor. It contains everything that was in-progress when the last session ended.

```
read active-tasks.md
```

Look for tasks marked `IN_PROGRESS`. These are recovery candidates.

If `active-tasks.md` doesn't exist or is empty: no active tasks. Proceed to Step 4.

---

## Step 2 — Verify each IN_PROGRESS task

For each task marked `IN_PROGRESS`:

1. **Check the deliverable, not your memory.** Does the file/output exist on disk? Does it have real content?
2. **If complete:** mark it `DONE` in `active-tasks.md`. Write a one-line entry to `ops/changelog.md`.
3. **If incomplete:** pick up where it stopped. Use the task description + any partial output to reconstruct state.

**Completion contract:** A task is not done until:
- The deliverable exists on disk with real content
- You've verified it (read it, ran it, checked the output)
- It's committed to git (if the task requires it)

"I think I did it" is not done. "The sub-agent said done" is not done. Verified is done.

---

## Step 3 — Resume or close

**If tasks remain incomplete:** resume them now, before reading new messages or taking new requests. Incomplete work from the previous session takes priority over new incoming work. Finish the contract first.

**If all tasks are done or no tasks existed:** close out the recovery pass. Write one line to `ops/changelog.md`:

```
[DATE] Boot recovery: X tasks verified complete, 0 tasks remaining
```

---

## Step 4 — Resume normal operation

1. Read `ops/changelog.md` — catch up on what changed while you were down
2. Read `SOUL.md`, `AGENTS.md`, `USER.md` (if not already in context)
3. Resume the normal startup sequence from `AGENTS.md`

---

## `active-tasks.md` Format

Keep this simple. One task per line. Update it in real time — when a task starts, add it. When it finishes, mark it done. The file is a live state record, not a retrospective.

```markdown
## Active Tasks

### IN_PROGRESS
- [2026-02-26] Build X feature — coding agent dispatched, waiting for output
- [2026-02-26] Research Y topic — 3/5 sources processed

### DONE
- [2026-02-25] Update README — committed, pushed
- [2026-02-25] Memory consolidation — promoted 12 entries

### BLOCKED
- [2026-02-26] Deploy Z — waiting for [YOUR_NAME] approval
```

---

## Notes for Customization

- Adapt quiet hours, cron schedules, and delivery targets in `AGENTS.md` — not here.
- If you run multiple agents, each workspace should have its own `BOOT.md` and `active-tasks.md`. Agents don't share state files.
- The `ops/changelog.md` is shared across agents — it's the coordination layer. Always write to it on recovery.
