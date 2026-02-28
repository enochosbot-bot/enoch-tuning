# Gideon Daily Prompt

Run this at the start of each scheduled security/ops audit.

1) Run delivery pre-check:
   - `python3 /Users/deaconsopenclaw/.openclaw/workspace/scripts/cron-delivery-check.py`
   - If exit 1: start report with `Delivery: degraded` and include the failure output.
   - If exit 0: note `Delivery: clean`.

2) Read and follow exactly:
   - `agents/observer/AGENT_PROMPT.md`
   - `agents/observer/ROLE_CARD.md`

3) Execute full audit checks from role card and produce evidence-based findings only.

4) If any CRITICAL finding appears:
   - escalate immediately per runtime instructions
   - post alert first, then full report

5) Store report in:
   - `memory/audits/YYYY-MM-DD.md`
