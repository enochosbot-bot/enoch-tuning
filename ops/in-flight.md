# ops/in-flight.md — Active Dispatch Tracker
_Enoch maintains this file. Updated at dispatch and on close._

## Active

| Task | Agent | Dispatched | Expected Close | Notes |
|------|-------|------------|----------------|-------|
| RR-Site — Fix broken nav (orphaned links) + strip bloated homepage sections | Bezzy (coder) | 2026-02-27T15:20Z | 2026-02-27T16:00Z | Fix ghost HTML in all 34 updated nav files; remove 3 sections from homepage (smallbiz-case, modules-preview, pricing-preview). Deploy + verify live. |


## Completed (last 7 days)

| Task | Agent | Dispatched | Closed | Result |
|------|-------|------------|--------|--------|
| RR-Site — Small Business page + homepage products + nav cleanup | Bezzy (coder) | 2026-02-27T15:02Z | 2026-02-27T15:30Z | Shipped: /small-business/ page (hero + 6 use cases + industry links + CTA), "What We Build" product cards on homepage, nav consolidated (Small Business → added, Products & Pricing merged). 34/37 HTML files updated. Both URLs return 200. |
| BL-018 — Data Flow Audit (all external API touchpoints) | Berean (researcher) | 2026-02-27T13:01Z | 2026-02-27T13:03Z | Delivered `shared-context/agent-outputs/data-flow-audit.md`. 8 services audited. Top finding: OpenAI embeddings = highest risk (continuous background sync of sessions). Twilio not configured. Ollama demo-ready. Clean-room pattern documented. Mirrored to Obsidian. |
| BL-013 — Build vidgen.py multi-platform AI video generator CLI | Bezzy (coder) | 2026-02-27T13:01Z | 2026-02-27T13:04Z | Delivered `scripts/vidgen.py` (executable) with optional Claude optimization, parallel provider fan-out (Kling/MiniMax/Luma/Runway when keys available), async polling with 5-minute timeout/platform, Desktop output directory creation under `~/Desktop/vidgen-output/{timestamp}/`, and run logging to `scripts/vidgen-log.jsonl`. Smoke tested with `python3 scripts/vidgen.py "dramatic sunset over mountains"` (no crash). |
| BL-003 — Draft 5 LinkedIn posts for Ridley Research launch week | Ezra (scribe) | 2026-02-26T03:00Z | 2026-02-27T03:02Z | 5 posts delivered to shared-context/drafts/linkedin-launch-week.md. All 100–200 words. Covers: Intro, Policy (SEC AI governance), Data (zero AI at boutique RIA tier), Story (founder), CTA. Awaiting Solomon review + Deacon approval. |
| Turn off Telegram streaming + fix watchdog timeouts + gateway restart | Bezzy | 2026-02-26T22:01Z | 2026-02-26T22:30Z | streaming=off, timeouts 2m→10m/1m→5m, gateway running pid 83269 |
| Wire Selah for YouTube Shorts upload pipeline | Bezzy | 2026-02-26T22:15Z | 2026-02-26T22:30Z | inbox/scripts/workflow built, OAuth client secrets still needed to go live |
| Cron cleanup: kill email jobs, merge dispatch loops, gateway restart | Bezzy | 2026-02-26T22:45Z | 2026-02-27T01:54Z | Gateway confirmed healthy (pid 7041). 6 jobs killed, Mission Pulse expanded. Row closed by Enoch — Bezzy never sent close ping. |

---

## Rules
- Every dispatch → add a row to Active immediately
- Every close → move row to Completed, add result summary
- If Active row is >60min old → heartbeat flags it to Deacon
- Never leave a row in Active after work is confirmed done
