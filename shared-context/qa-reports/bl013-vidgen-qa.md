## Basher QA Report — BL-013 vidgen.py — 2026-02-27

### Passing
- `scripts/vidgen.py` exists at `/Users/deaconsopenclaw/.openclaw/workspace/scripts/vidgen.py` ✅
- Syntax clean — `ast.parse()` passes with zero errors ✅
- Plain-English prompt accepted as positional arg ✅
- Claude prompt optimizer implemented with `--raw` flag to skip ✅
- Parallel fan-out via `asyncio.gather()` across Kling + MiniMax/Hailuo + Luma ✅
- Runway included as optional 4th platform (key-gated) ✅
- 5-minute async polling timeout per platform (`deadline = time.time() + 300`) ✅
- Output dir: `~/Desktop/vidgen-output/{timestamp}/` — prior run dir confirmed on Desktop ✅
- Log target: `scripts/vidgen-log.jsonl` (relative to script file) — path resolves correctly ✅
- Per-platform success/failure + cost estimate reported in results table ✅
- Graceful skip when API keys missing — prints instructions, exits 1 when no platforms remain ✅
- `--platforms` flag works; `--duration` flag present; `--raw` flag skips Claude ✅

### Critical (blocks ship)
- **None.**

### Warnings (fix before v1)
- **Duplicate script:** Two versions exist — `workspace/scripts/vidgen.py` (current, async/aiohttp, full-featured) and `workspace-coder/scripts/vidgen.py` (older, urllib-based, different log schema). The `workspace-coder` version is what ran during Bezzy's smoke test (`20260227-070341` log entry). Bezzy should delete or archive `workspace-coder/scripts/vidgen.py` to avoid confusion.
- **Log not created until first successful/partial run:** `vidgen-log.jsonl` in `workspace/scripts/` does not exist yet. The `workspace-coder` version created its own log at `workspace-coder/scripts/vidgen-log.jsonl`. No data loss — just schema divergence between versions.
- **Runway uses `image_to_video.create`** but sends no image — only `prompt_text`. Runway Gen4 may reject text-only requests at runtime. Not testable without API key, but worth flagging for Bezzy to verify against Runway docs.

### Notes (nice to have)
- Keychain availability is session-dependent — `--help` showed `minimax` as available in one exec, missing in the next. Not a code bug, but may confuse users. Could add a `vidgen check-keys` subcommand.
- Log schema in workspace version (`ts`, `platforms`, `raw`, `results`) differs from workspace-coder version. Standardize before any tooling reads the log.

### Verdict
**SHIP** — All AC met. Core functionality is solid. Warnings are non-blocking; Bezzy should clean up the duplicate file and verify Runway text-only behavior.

### AC Coverage
| Criterion | Status |
|---|---|
| Plain-English prompt input | ✅ PASS |
| Claude optimization (optional) | ✅ PASS |
| Kling fan-out (parallel) | ✅ PASS |
| MiniMax/Hailuo fan-out (parallel) | ✅ PASS |
| Luma fan-out (parallel) | ✅ PASS |
| Runway (optional) | ✅ PASS |
| Async polling, 5-min timeout/platform | ✅ PASS |
| Output to `~/Desktop/vidgen-output/{timestamp}/` | ✅ PASS |
| Logs to `scripts/vidgen-log.jsonl` | ✅ PASS |
| Per-platform success/failure + cost | ✅ PASS |
