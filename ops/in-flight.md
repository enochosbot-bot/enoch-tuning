# ops/in-flight.md — Active Dispatch Tracker
_Enoch maintains this file. Updated at dispatch and on close._

## Active

| Task | Agent | Dispatched | Expected Close | Notes |
|------|-------|------------|----------------|-------|




## Completed (last 7 days)

| Task | Agent | Dispatched | Closed | Result |
|------|-------|------------|--------|--------|
| openclaw-starter build + GitHub push + tmp cleanup | Enoch (main) | 2026-02-28T07:04Z | 2026-02-28T07:05Z | ✅ Repo pushed to enochosbot-bot/openclaw-starter. /private/tmp/openclaw-starter wiped. |

---

## Rules
- Every dispatch → add a row to Active immediately
- Every close → move row to Completed, add result summary
- If Active row is >60min old → heartbeat flags it to Deacon
- Never leave a row in Active after work is confirmed done
