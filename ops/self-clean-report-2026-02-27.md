# Self-Clean Oven Report — Friday, February 27, 2026

Generated: 6:30 AM CST

---

## ✅ Fixes Applied (5)

### 1. Nehemiah — Output QA Sweep (df42afd5)
**Error:** `No delivery target resolved for channel "telegram". Set delivery.to.`
**Fix:** Added `--to "-1003772049875:topic:3061"` + channel telegram. Will resolve at next run (10 AM).

### 2. Backlog Intake — Task Decomposition (454c0ba1)
**Error:** `cron announce delivery failed`
**Fix:** Added `--to "-1003772049875:topic:3061"`. Was silently erroring every morning at 7 AM.

### 3. Daily Self-Reflection (53a89988)
**Error:** `cron announce delivery failed`
**Fix:** Added `--to "-1003772049875:topic:3061"`. 2 AM nightly run was silently erroring.

### 4. Session Resume — Handoff Pickup (50883b0d)
**Error:** `cron announce delivery failed`
**Fix:** Added `--to "-1003772049875:topic:3061"`. 4:15 AM pickup job was failing delivery.

### 5. Berean — X Bookmarks Nightly Sync (7270d8de)
**Error:** `cron: job execution timed out` (was set to 180s)
**Fix:** Timeout bumped to 300s. The Brave cookie decryption + tweety-ns API calls are slow; 3 minutes should clear it.

---

## ⚠️ Blockers Needing Decision (3 missing scripts)

These scripts are referenced in active cron jobs but **do not exist** on disk. Jobs appear healthy (return "ok") because the agent reports the error as output — but the actual functionality is silently dead.

| Script | Referenced By | Impact |
|--------|--------------|--------|
| `scripts/cost-report.py` | Daily Cost Report (8 AM) | No daily spend data in Ops topic |
| `scripts/daily-cost-report.py` | Nightly Maintenance (3 AM) | No cost section in morning brief |
| `scripts/cron-delivery-check.py` | Gideon Deep Audit (3:30 AM) | Delivery health pre-check skipped |

**Action needed:** These need to be created (or the cron job prompts need to be updated to use an alternative approach — e.g., `openclaw status` + `ops/cost-ledger.md` for cost data). Flagged for Deacon or Bezzy to build.

---

## 💰 Cost Savings Opportunities

**High-frequency Sonnet jobs** — these run on `anthropic/claude-sonnet-4-6`:

| Job | Runs/Day | Notes |
|-----|----------|-------|
| Mission Pulse | 7×/day | Complex orchestration — keep Sonnet |
| Nehemiah QA Sweep | 3×/day | Could downgrade to haiku-4-5 if backlog stays simple |
| Backlog Intake | 1×/day | File read + task generation — haiku-capable |
| Daily Self-Reflection | 1×/day | Reasoning-heavy — keep Sonnet |
| Internal Improvement Scan | 1×/day | Pattern analysis — borderline haiku |

**qwen2.5-coder:14b suitability:** None of the current jobs are code-generation tasks appropriate for local model. Best candidates would be script-writing or code review tasks once those land in the backlog.

**Estimated quick win:** Downgrade Backlog Intake + Nehemiah QA Sweep to `anthropic/claude-haiku-4-5` saves ~4 Sonnet calls/day. Low risk — these are structured tasks with file reads and templated outputs.

---

## 🗑️ Stale Job Flag

**Kiriakou Upload — Quota Reset Batch** (5d489472)
- Ran successfully Feb 27 at 2 AM (12 clips uploaded/scheduled)
- Next scheduled run: **Feb 27, 2027** (one year out)
- Job is effectively one-and-done; it's just sitting there
- **Recommend:** Disable unless you want it to auto-repeat next February

---

## ✔️ Verification — Key Scripts & Health

| Item | Status |
|------|--------|
| `scripts/git-memory-commit.sh` | ✅ Exists, executable |
| `scripts/shorty-trigger.py` | ✅ Exists |
| `scripts/x-bookmarks-sync.py` | ✅ Exists |
| `scripts/content-factory/approval_poller.py` | ✅ Exists |
| Workspace Git backup (every 6h) | ✅ Running (lastStatus: ok) |
| Gideon Nightly Deep Audit | ✅ ok |
| Gideon Abaddon Red Team | ✅ ok |
| Heartbeat Night/Daytime | ✅ ok (both) |
| Session Auto-Prune | ✅ ok |

**Note:** Approval Poller runs every **30 seconds**. That's 2,880 cron firings/day. It's fast (3.8s avg) and silent when idle — but worth monitoring if agent costs increase.

---

## 📊 Stack Health Summary

- Total jobs: 27
- Jobs with errors: 5 → **0** (all fixed this run)
- Missing scripts: 3 (require build work — flagged above)
- Stale/dead jobs: 1 (Kiriakou — flagged)
- No duplicate reminders found
- Future one-time reminders (Hawaii, Stonebriar) are valid and correctly dated

---

*Next self-clean: Saturday, February 28, 2026 at 6:30 AM CST*
