# BL-007 — Cron Audit Report
**Auditor:** Gideon (observer subagent)
**Date:** 2026-02-27 (00:28 UTC / 18:28 CST)
**Period Covered:** Last 7 days (activeMinutes=10080)
**Source:** `/Users/deaconsopenclaw/.openclaw/cron/jobs.json` (30 jobs total)

---

## ⚠️ CRITICAL FLAGS (Read First)

### 1. Main Session JSONL at 3.9MB — Needs Manual Intervention
**File:** `/Users/deaconsopenclaw/.openclaw/agents/main/sessions/boot-2026-02-26_08-42-43-675-d497f5de.jsonl`
**Size:** 3.9MB — **97% above the 2MB auto-rotate threshold**

The Session Auto-Prune cron runs every 6h and executes `openclaw sessions cleanup --all-agents --enforce`. It last ran at 00:04 UTC and the file is **still 3.9MB**, meaning the cleanup did NOT rotate it. This is a boot session (named `boot-...`), not a UUID cron session — `openclaw sessions cleanup` may not handle boot sessions, or the rotation logic only fires at the next session reset (4 AM daily). **Do not wait.** Manual action required:

```
openclaw sessions cleanup --all-agents --enforce
# or force a gateway restart to trigger rotation
openclaw gateway restart
```

The session has been accumulating since 08:42 UTC today (Feb 26) — nearly 16 hours of continuous Telegram interaction including multiple subagent dispatches. This is the primary driver of context bloat.

### 2. Gmail Digest — Evening: Missing `agentId` + 5+ Days Silent
The job `6d3cf0d3` has **no `agentId` field** in jobs.json (all other jobs have one). Last status: OK from 127h ago (Feb 21). Has not fired in 5+ days. This is a silent failure — no error logged, no consecutive error counter incremented. The missing agentId means it may be silently dropping. **Action required.**

### 3. Gideon — Daily Quick Scan: consecutiveErrors=1
Error: `"No delivery target resolved for channel 'telegram'. Set delivery.to."` The job uses `delivery.mode: none` but the message prompt instructs the agent to call the message tool directly to `threadId="3061"`. The agent fires, but the delivery-check script (run at start of Nightly Deep Audit) flagged something. Not critical but leaving an error counter uncleaned.

---

## Summary Table

| Name | Schedule | Agent | Model | Last Fired | Status | Verdict |
|------|----------|-------|-------|-----------|--------|---------|
| Gideon — Weekly Full Audit | Sun 8 AM | observer | Sonnet | 82h ago (Feb 23) | ✅ OK | **KEEP** |
| Gideon — Daily Quick Scan | Daily 6 AM | observer | Sonnet | 12.5h ago | ❌ Error | **MODIFY** — fix delivery |
| Workspace Git + Drive Backup | Every 6h | main | Haiku | 0.4h ago | ✅ OK | **KEEP** |
| Email Auto-Sorter | Every 2h | main | Haiku | 0.9h ago | ✅ OK | **KEEP** |
| Stonebriar Brass Band Reminder | Mar 15 | main | Haiku | NEVER | (future) | **KEEP** |
| Hawaii Flights Reminder | Apr 1 | main | Haiku | NEVER | (future) | **KEEP** |
| Morning Briefing | Daily 7 AM | main | Sonnet | 131h ago | ⛔ Disabled | **KILL** — superseded |
| Weekly Memory Hygiene | Sun 3 AM | main | Sonnet | NEVER | ⚠️ Never fired | **MODIFY** — verify timing |
| Proactive Dispatch — Hourly | Every 60min | main | Sonnet | 0.0h ago | ✅ OK | **MODIFY** — merge w/ Mission Pulse |
| memory-consolidation | Daily 3 AM | main | Sonnet | 135h ago | ⛔ Disabled | **KILL** — superseded |
| Solomon Daily Strategy | Daily 10:13 AM | solomon | (none) | 127h ago | ⛔ Disabled | **KILL** — no model, stale |
| Gideon — Nightly Deep Audit | Daily 3:30 AM | observer | Sonnet | 15h ago | ✅ OK | **KEEP** |
| Gideon — Abaddon Nightly Red Team | Daily 3:45 AM | observer | Sonnet | 14.7h ago | ✅ OK | **KEEP** |
| Gmail Digest — Evening | Daily 7:07 PM | (missing!) | Haiku | 127h ago | 🚨 Broken | **MODIFY** — add agentId |
| Internal Improvement Scan — Daily | Daily 7 AM | main | Sonnet | 11.5h ago | ✅ OK | **MODIFY** — merge w/ Self-Clean |
| Self-Clean Oven — Daily | Daily 6:30 AM | main | Sonnet | 12h ago | ✅ OK | **MODIFY** — merge w/ Improvement Scan |
| Heartbeat — Daytime | Every 30min 8-22 | main | Haiku | 0.5h ago | ✅ OK | **KEEP** |
| Heartbeat — Night | 23,1,3,5,7 AM | main | Haiku | 11.4h ago | ✅ OK | **KEEP** |
| Morning Brief (8 AM) | Daily 8 AM | main | Sonnet | 10.5h ago | ✅ OK | **KEEP** |
| Nightly Maintenance + Brief Compilation | Daily 3 AM | main | Haiku | 15.5h ago | ✅ OK | **KEEP** |
| Daily Cost Report | Daily 8 AM | observer | Haiku | 10.4h ago | ✅ OK | **KEEP** |
| Nehemiah — Daily Smoke Test | Daily 6:30 AM | basher | Haiku | 11.9h ago | ✅ OK | **KEEP** |
| Berean — X Bookmarks Nightly Sync | Daily 4 AM | researcher | (none) | 14.5h ago | ✅ OK | **KEEP** — verify model |
| Session Auto-Prune | Every 6h | observer | Haiku | 0.4h ago | ✅ OK | **KEEP** — not rotating boot sessions |
| Session Resume — Handoff Pickup | Daily 4:15 AM | main | Haiku | 14.2h ago | ✅ OK | **KEEP** |
| Mission Pulse — Idle Self-Direction | 9,12,15,18,21 | main | Sonnet | 0.5h ago | ✅ OK | **MODIFY** — merge w/ Proactive Dispatch |
| Daily Self-Reflection | Daily 2 AM | main | Sonnet | NEVER | ⚠️ New | **KEEP** — monitor |
| Nehemiah — Output QA Sweep | 10,16,22 | basher | Sonnet | 2.5h ago | ✅ OK | **KEEP** |
| Backlog Intake — Task Decomposition | Daily 7 AM | main | Sonnet | NEVER | ⚠️ New | **KEEP** — monitor |
| X Engagement Monitor — Daily Batch | Daily 8 AM | researcher | (none) | 10.4h ago | ✅ OK | **KEEP** — verify model |

---

## Per-Cron Analysis

### ✅ KEEP — No Action Required

**Workspace Git + Drive Backup** (`cbe2fb6c`)
- Schedule: Every 6h | Model: Haiku | Duration: 122s
- Fires reliably, uploads to Google Drive, stays silent on success. Core infrastructure. Zero issues.

**Email Auto-Sorter** (`24a3e572`)
- Schedule: Every 2h | Model: Haiku | Duration: 7s
- Running fine, 7s average — extremely cheap. Silent on clean runs.

**Stonebriar Brass Band Reminder** (`cc7456e9`) + **Hawaii Flights Reminder** (`f8484f6f`)
- One-time future events. Not firing yet. Keep until they fire.

**Gideon — Nightly Deep Audit** (`920f1fe4`)
- Schedule: Daily 3:30 AM | Duration: 355s | Delivering to Security topic
- Core security infrastructure. Takes 6 minutes but covers Offensive/Defensive/Data Privacy/Operational. High value. KEEP.

**Gideon — Abaddon Nightly Red Team** (`79e87055`)
- Schedule: Daily 3:45 AM | Duration: 246s | Delivering to Security topic
- Running clean, posts grade. Complementary to Deep Audit — different adversarial angle. KEEP.

**Gideon — Weekly Full Audit** (`46607546`)
- Schedule: Sunday 8 AM | Duration: 24s (surprisingly fast) | Last run Sunday Feb 23
- On track. Next run Sunday 8 AM CST. KEEP.

**Heartbeat — Daytime** (`f0818bbf`)
- Schedule: Every 30min 8 AM–10 PM (28 fires/day) | Duration: 9s | Haiku
- Cheapest reliable health signal. Silent when clean. Essential.

**Heartbeat — Night** (`1a8e125b`)
- Schedule: 11 PM, 1, 3, 5, 7 AM (5 fires) | Duration: 27s | Haiku
- Covers quiet hours. Total 33 heartbeat checks/day with daytime. KEEP.

**Morning Brief (8 AM)** (`5235d2f8`)
- Schedule: Daily 8 AM | Duration: 78s | Delivering to Security topic (and DM)
- Delivering successfully. Well-structured. Keep.
- _Note: delivery target is Security topic not Deacon DM — this may be intentional or a config error worth confirming._

**Nightly Maintenance + Brief Compilation** (`2ec8c5a8`)
- Schedule: Daily 3 AM | Duration: 321s | Haiku | Silent
- The workhorse: memory consolidation, vault hygiene, workspace cleanup, cost report, brief data. Running on Haiku — correct choice for a long task. KEEP.

**Daily Cost Report** (`a74fc77c`)
- Schedule: Daily 8 AM | Duration: 8s | Haiku
- Fast, cheap, delivers to Security topic. KEEP.

**Nehemiah — Daily Smoke Test** (`37569b31`)
- Schedule: Daily 6:30 AM | Duration: 15s | Haiku
- Fast endpoint health check. Delivering. KEEP.

**Berean — X Bookmarks Nightly Sync** (`7270d8de`)
- Schedule: Daily 4 AM | Duration: 178s | Model: (none set in payload)
- Running OK. NOTE: `model` field missing from payload — inherits agent default (Sonnet). Fine but worth making explicit.

**Session Auto-Prune** (`f66b156c`)
- Schedule: Every 6h | Duration: 9s | Haiku | Silent
- Running, but NOT rotating the 3.9MB main boot session (see Critical Flag #1). The cleanup command handles standard sessions but boot sessions may require gateway restart. Fix needed at gateway level, not cron level.

**Session Resume — Handoff Pickup** (`50883b0d`)
- Schedule: Daily 4:15 AM | Duration: 11s | Haiku
- Fires after 4 AM session reset, picks up handoff files. Fast and cheap. KEEP.

**Nehemiah — Output QA Sweep** (`df42afd5`)
- Schedule: 10 AM, 4 PM, 10 PM (3x daily) | Duration: 10s | Sonnet
- Only 10s per run — very fast (backlog probably mostly empty). Silent when nothing to validate. Sonnet overhead for 10s runs is wasteful — consider downgrading to Haiku, but functionally fine.

**Daily Self-Reflection** (`53a89988`) — NEVER FIRED (NEW JOB)
- Schedule: Daily 2 AM | New job (no runs yet) | Sonnet
- First run tonight at 2 AM. Give it one cycle before evaluating.

**Backlog Intake — Task Decomposition** (`454c0ba1`) — NEVER FIRED (NEW JOB)
- Schedule: Daily 7 AM | New job | Sonnet
- First run tomorrow 7 AM. Monitor output before evaluating.

**X Engagement Monitor — Daily Batch** (`df07756c`)
- Schedule: Daily 8 AM | Duration: 264s (4.4 min) | Model: (none set — uses agent default)
- Delivering to Research topic. 4.4 minutes is long for a monitoring job. Producing intelligence output. KEEP but confirm value with Deacon — if he's not acting on the posts, this is expensive noise.

---

### 🔧 MODIFY — Fix Required

**Gideon — Daily Quick Scan** (`dfb88b12`)
- **Problem:** `consecutiveErrors: 1` — Error: `"No delivery target resolved for channel 'telegram'. Set delivery.to."`
- The delivery.mode is "none" but the cron runner's delivery health check still validates it. The job itself fired (75s duration) — the error is in the post-run delivery check, not the audit itself.
- **Fix:** Add `"delivery": { "mode": "announce", "channel": "telegram", "to": "-1003772049875:topic:3061", "bestEffort": true }` to match Nightly Deep Audit. OR keep mode=none but accept the false error. The cleaner fix is to set a delivery target.

**Gmail Digest — Evening** (`6d3cf0d3`) 🚨
- **Problem:** Missing `agentId` field. Last fired 127h ago (5+ days silence). Should fire every day at 7:07 PM CST.
- **Fix:** Add `"agentId": "main"` to the job definition. Then force a manual test run to confirm it fires.
- This is the most broken enabled job in the stack.

**Weekly Memory Hygiene** (`bdef198a`)
- **Problem:** NEVER fired despite being enabled. Schedule: Sunday 3 AM — but this conflicts with nothing (Nightly Maintenance is also 3 AM but that's daily; the deep audit is 3:30 AM).
- **Real issue:** Nightly Maintenance already does memory consolidation. This job would duplicate that work on Sundays.
- **Fix Option A:** Kill it — Nightly Maintenance handles everything this does.
- **Fix Option B:** Repurpose to a weekly _deep_ memory hygiene that does things Nightly Maintenance skips (SOUL.md review, USER.md accuracy check, MEMORY.md trimming). Change schedule to Sunday 2 AM to avoid conflict.
- Recommending Option B — gives a weekly audit layer that nightly can't provide.

**Proactive Dispatch — Hourly** (`0af153e1`) + **Mission Pulse — Idle Self-Direction** (`237f664f`)
- **Problem:** TWO competing Sonnet dispatch loops running simultaneously.
  - Proactive Dispatch: every 60 min, reads production-queue/improvement-queue, dispatches 1 task, Sonnet 101s
  - Mission Pulse: 5x/day (9,12,15,18,21 CST), reads backlog.md, dispatches 1 task, Sonnet 111s
  - Combined: ~29 Sonnet dispatch runs/day. This is the **#1 cost driver** in the cron stack.
- **Fix:** Consolidate into a single dispatcher. Recommendation: Keep Mission Pulse at its 5x/day schedule but expand its prompt to also cover the improvement-queue and production-queue. Kill Proactive Dispatch hourly. Result: 5 → 29 dispatch runs/day saved in Sonnet calls.

**Internal Improvement Scan — Daily** (`950a7298`) + **Self-Clean Oven — Daily** (`cc679201`)
- **Problem:** Two daily Sonnet jobs both scanning cron for failures and improvements.
  - Internal Improvement Scan: reads cron-run-log, improvement-queue, finds failures, posts to Security topic
  - Self-Clean Oven: checks cron lastStatus errors, detects stale jobs, applies low-risk fixes, posts to Security topic
  - Both run within 30 minutes of each other (7 AM vs 6:30 AM), both post to the same channel.
- **Fix:** Merge into a single job. The combined prompt already exists across both — just combine them. Saves 1 daily Sonnet run and eliminates duplicate Security topic noise.

**Berean — X Bookmarks Nightly Sync** (`7270d8de`) + **X Engagement Monitor — Daily Batch** (`df07756c`)
- Both have no `model` field in their payloads — inherit agent default (Sonnet). Fine now but should be explicit.
- **Fix (minor):** Add `"model": "anthropic/claude-haiku-4-5"` to X Bookmarks Nightly Sync (it's mostly a script-run + file-write task, doesn't need Sonnet). X Engagement Monitor may need Sonnet for analysis.

---

### 🔴 KILL — Remove These Jobs

**Morning Briefing** (`bcb3448f`) — Already disabled
- Superseded by "Morning Brief (8 AM)" which is better structured and actively firing.
- This job has been disabled since ~Feb 21. Delete it to reduce jobs.json clutter.

**memory-consolidation** (`5774c791`) — Already disabled
- Superseded by "Nightly Maintenance + Brief Compilation" which runs at the same time (3 AM) and does everything this did plus more.
- Disabled since ~Feb 21. Delete it.

**Solomon Daily Strategy** (`7db8b668`) — Already disabled, no model set
- No `model` in payload, disabled for 5+ days. The functionality (strategic insight) is better handled on-demand via sessions or Mission Pulse dispatch.
- Zero runs in 7-day window. Delete it.

---

## Top 3 Highest-ROI Changes

### 🥇 #1 — Merge Proactive Dispatch + Mission Pulse (Saves ~24 Sonnet runs/day)
**Current state:** 2 dispatch loops, combined ~29 Sonnet runs/day, ~3,000 tokens each = significant daily cost
**Action:**
1. Expand Mission Pulse prompt to also read `ops/production-queue.md` and `ops/improvement-queue.md`
2. Disable/delete Proactive Dispatch (id: `0af153e1`)
3. Optionally change Mission Pulse to 6 fires/day (add 7 AM to the schedule) to compensate for lost hourly coverage

**Impact:** Eliminates 24 daily Sonnet dispatch calls. Single highest-ROI change in the stack.

### 🥈 #2 — Fix Gmail Digest Evening (Restore lost daily email monitoring)
**Current state:** Broken for 5+ days. No agentId → not firing.
**Action:**
1. Add `"agentId": "main"` to job `6d3cf0d3` in cron/jobs.json
2. Verify with `openclaw cron run 6d3cf0d3` (or equivalent)
3. Confirm delivery to Security topic

**Impact:** Restores daily email intelligence that's been dark since ~Feb 21. Low effort, immediate value.

### 🥉 #3 — Rotate the 3.9MB Main Session JSONL (Immediate stability fix)
**Current state:** Main agent boot session at 3.9MB, past the 2MB auto-rotate threshold. Not self-healing.
**Action:**
```bash
openclaw gateway restart
# OR
openclaw sessions cleanup --all-agents --enforce --force-boot
```
If neither works, manually delete/move the file during a low-traffic window.

**Impact:** Prevents context degradation in main agent sessions. The bloat from this single file is adding latency and cost to every main-agent cron that runs in the same session context.

---

## Stats Summary

| Category | Count |
|----------|-------|
| Total jobs | 30 |
| Enabled | 27 |
| Disabled (can be deleted) | 3 |
| Firing correctly | 21 |
| Never fired (new) | 3 |
| Erroring | 1 |
| Broken/silent | 1 (Gmail Digest) |
| Models not set (inherit default) | 3 |

**Estimated Sonnet runs/day (current):** ~39
**Estimated Sonnet runs/day (post-merge):** ~15
**Potential reduction:** ~60% fewer Sonnet cron calls

---

_Report generated: 2026-02-27 00:28 UTC by Gideon (BL-007)_
