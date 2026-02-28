# Priorities

> Updated: 2026-02-26 — Ridley Research site live, 8 agents operational, full mesh comms active.
> Source of truth for what matters RIGHT NOW. Read backlog.md for the actionable task queue.
> Agent roster: Enoch (chief of staff), Solomon (strategy), Ezra (research/writing), Selah (creative), Berean (researcher), Bezzy (engineering), Gideon (QA/self-reflection), Eliza (undefined).

---

## P0 — This Week

1. **Multi-platform AI video generation spec + build** — Highest priority now. Define and deliver `scripts/vidgen.py` workflow (Claude prompt optimization + parallel platform fan-out + output/cost logging) before non-critical backlog items.

2. **Spectrum Advisors demo prep** — Demo is early March. Need demo script (BL-008) and polished talking points. Competitive landscape research (BL-002) is complete.

3. ~~**CFP exam prep**~~ — **PAUSED** — Do not auto-dispatch CFP tasks. Deacon will re-prioritize this explicitly when ready. Agents should NOT generate practice questions or study materials until Deacon says so.

4. **Ridley Research social launch** — X account active. 5 posts drafted and queued for approval. LinkedIn posts in progress (BL-003). LinkedIn OAuth still pending (human action required). Social pipeline script in progress (BL-005).

---

## P1 — Next 2 Weeks

4. **LinkedIn OAuth app** — Deacon must register the app on LinkedIn's developer portal. Agents are blocked on this until he does. Once complete, Bezzy integrates into the posting pipeline.

5. **OpenPlanter investigations** — First real run on Texas political donor networks (BL-006). Tool is installed and configured.

6. **Cron health audit** — 28 crons running. First audit to verify actual output and kill anything producing no value (BL-007).

---

## P2 — When Available

8. **System health KPIs** — Daily dashboard in shared-context/kpis/. Gideon owns this (BL-010).

9. **FEC/ethics cross-referencing** — Political operations tooling. Intake queue until OpenPlanter run is producing results.

10. **RPG dashboard** — Deferred. Needs real agent activity data before this is worth building.

---

## Parked / Prune Candidates (Do Not Start)

- Additional agents beyond current 8
- Email/calendar integration (including daily email digest work; prune candidate)
- Telegram topic-gap investigation (BL-009; prune candidate)
- X/Twitter API direct posting — manual approval flow is the standard until further notice
- Any Spectrum-specific agent configuration (sandbox only, never production)
- CFP exam prep (paused 2026-02-27 — do not dispatch until Deacon explicitly re-prioritizes)

---

## Deprecated — Do Not Reference

The following are no longer active and should not appear in any agent output or planning:
- Arnold (deprecated — renamed Gideon)
- Xalt (deprecated agent)
- "Core 3" framing (superseded by current 8-agent roster)
- Any pre-February 2026 agent architecture references
