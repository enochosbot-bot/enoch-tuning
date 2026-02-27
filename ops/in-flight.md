# ops/in-flight.md — Active Dispatch Tracker
_Enoch maintains this file. Updated at dispatch and on close._

## Active

| Task | Agent | Dispatched | Expected Close | Notes |
|------|-------|------------|----------------|-------|



## Completed (last 7 days)

| Task | Agent | Dispatched | Closed | Result |
|------|-------|------------|--------|--------|
| BL-010 — System health dashboard (kpis/system-health.md + generator script) | Gideon (observer) | 2026-02-27T21:00Z | 2026-02-27T21:02Z | ✅ Delivered `shared-context/kpis/system-health.md` and executable `scripts/generate-health-dashboard.py`. Includes gateway PID/uptime, session count, workspace disk usage, 24h cron pass/fail rate from task-ledger, and per-agent 24h activity from session `updatedAt`. |
| BL-005 — Build daily social posting pipeline script | Bezzy (coder) | 2026-02-27T12:55Z | 2026-02-27T13:18Z | ✅ Delivered scripts/social-post-pipeline.py + .sh. Reads shared-context/drafts/, extracts posts by section, deduplicates via SHA1 IDs, sends Telegram approval message, logs JSONL. --dry-run supported. Note: existing 11-post queue is linkedin-launch-week.md drafts — approved queue in research/social-drafts/queue/ needs to be copied into shared-context/drafts/ to flow through pipeline. |
| BL-004 — Draft 5 X/Twitter posts for Ridley Research launch week | Ezra (scribe) | 2026-02-27T12:53Z | 2026-02-27T13:10Z | ✅ 5 posts delivered to shared-context/drafts/x-launch-week.md. All <280 chars. Mon–Fri sequence: Intro/Mission, Policy thread, Data/Math, Story thread, CTA. No hashtags, no fluff. Awaiting Deacon approval. |
| BL-012 — FEC/Texas ethics cross-referencing tooling spec | Berean (researcher) | 2026-02-27T12:56Z | 2026-02-27T13:18Z | ✅ Spec delivered to shared-context/agent-outputs/fec-ethics-tooling-spec.md. SQLite schema (7 tables), TEC bulk download URLs, 4 SQL investigation patterns, MVP vs Phase 2 effort estimates. |
| RR-Site — Deploy nav fix + verify live | Enoch (main) | 2026-02-27T18:38Z | 2026-02-27T18:40Z | ✅ DEPLOYED — Bezzy had updated all 37 HTML files locally but never deployed. Enoch ran wrangler deploy. Live site now shows "Products & Pricing" nav everywhere. "See All Products" gone. Verified 200 + correct nav text on live ridleyresearch.com. |
| RR-Site — Fix broken nav + strip 3 bloated homepage sections (re-dispatch) | Bezzy (coder) | 2026-02-27T18:00Z | 2026-02-27T18:02Z | Files updated locally but NOT deployed — Bezzy closed row without running wrangler. Nav fix not live until Enoch deployed above. |
| RR-Site — Fix broken nav + strip bloated sections (attempt 1) | Bezzy (coder) | 2026-02-27T15:20Z | 2026-02-27T18:00Z | STALE/FAILED — dispatched 15:20Z, expected close 16:00Z. Site returns 200 but 3 sections (smallbiz-case, modules-preview, pricing-preview) still present on live homepage. No close ping. Re-dispatched 18:00Z. |
| BL-015 — Polish Spectrum demo outline (prose + presentation layer) | Ezra (scribe) | 2026-02-27T18:02Z | 2026-02-27T18:10Z | Polished spectrum-demo-outline.md — all talking points tightened, jargon stripped, section transitions added, demo sequences rewritten as setup+punchline, objection table made decisive. Ezra's Notes section added at top. File overwritten at shared-context/agent-outputs/spectrum-demo-outline.md. Demo-ready for early March. |
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
