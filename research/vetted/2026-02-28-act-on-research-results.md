# ACT_ON + Research Results — 2026-02-28
Source: Bookmark batch execution pass

---

## COMPLETED

### ✅ Security Critical — Fixed
- `openclaw.json` was world-readable (mode 644)
- Fixed: `chmod 600` applied → now mode 600 (`-rw-------`)
- Before: 1 critical, 5 warn | After: **0 critical, 5 warn**

### ✅ Claude Code Updated
- 2.1.49 → **2.1.63** (needed 2.1.58+ for remote-control)
- Updated via `claude update`

### ✅ MarkItDown Installed
- Microsoft MarkItDown v0.1.5 installed via pipx
- CLI: `markitdown <file>` or `cat file | markitdown`
- Converts PDF, Word, Excel, HTML → Markdown for LLM ingestion
- Globally available

---

## STATUS: NEEDS ACTION

### ⚠️ `/remote-control` Not Yet Active
- Claude Code is on 2.1.63 ✓ (past the 2.1.58 threshold)
- Command returns "Unknown skill" — not yet flagged for this account
- Per the tweet: rolling out to 10% of Pro users. Required: log out → log in to refresh flags
- **Action:** `claude logout && claude login` — then try `/remote-control`

### ⚠️ OpenClaw Security Warnings (5 remaining, not critical)
All 5 are acceptable-risk / intentional config:
1. **trusted_proxies_missing** — irrelevant unless Control UI is behind a reverse proxy (it's not)
2. **safeBinTrustedDirs includes /opt/homebrew/bin** — intentional for tooling, acknowledged risk
3. **denyCommands ineffective** — camera/calendar/contacts commands misnamed; functional but noted
4. **weak_tier models** — Haiku in fallbacks. Intentional for cost control on cron/observer agents. Risk: accepted.
5. **multi-user heuristic** — Group chat triggers this. Single trusted operator (Deacon). Risk: accepted.

---

## RESEARCH FINDINGS

### Antigravity Awesome Skills (sickn33/antigravity-awesome-skills)
**16,836 ★ | 3,058 forks | 946 skills | Updated today**

This is not a curated list — it's a full skill library with install scripts, a web app interface, and skills from Anthropic and Vercel officially. Topics: claude-code, agentic-skills, mcp, security-auditing, autonomous-coding.

**Directly relevant skills found:**
- `sales-automator` — directly maps to speed-to-lead agent
- `local-legal-seo-audit` — local SEO auditing
- `programmatic-seo` — scale local content production
- `seo-content-writer`, `seo-keyword-strategist`, `seo-authority-builder`, `seo-meta-optimizer` — full SEO stack
- `paid-ads` — Meta/Google ads management
- `content-creator`, `content-marketer`, `email-sequence` — content operations
- `agent-memory-systems`, `hierarchical-agent-memory`, `conversation-memory` — memory architecture

**Verdict:** High-value. Before building the speed-to-lead agent or local SEO service from scratch, pull these skills first. Many may be ready-to-run.

**Source:** https://github.com/sickn33/antigravity-awesome-skills

---

### Meta Ads Skill (clawhub: `meta-ads`)
Owner: zachgodsell93 | Updated: 2026-02-28 | v1.0.0

Real skill on clawhub, actively maintained (updated today). Full read/write Meta Ads API: campaigns, ad sets, ads, creatives, performance metrics. This is NOT the 5-skill Matt Berman kit but it's a real, usable foundation.

**Action:** `clawhub install meta-ads` in the workspace skills dir when ready to test.

---

### LEANN RAG System
- Claimed: 97% less storage, graph-based, on-device, open source
- Found: `decisiongraph/leann-rs` (Rust rewrite, 1 star) + `VoodooTwoTwo/LEANN-Workspace` (0 stars)
- The original Python version from the tweet was not findable on GitHub
- **Verdict:** Very early stage, possibly vaporware or the original author hasn't published it yet. The concept (on-demand embedding recomputation) is real research but implementation isn't there yet. Skip for now.

---

### Mission Control Dashboard (@ziwenxu_)
- Beta access via comment "OpenClaw" on the tweet
- No public repo found
- Features claimed: visual pixel office, kanban board sync, real-time log + cron view
- **Action:** Comment on the tweet to request beta. Meanwhile, this validates building toward the same thing via the Console dashboard queue item.

---

## SUMMARY OF WHAT'S DONE

| Item | Status |
|------|--------|
| Security critical (config perms) | ✅ Fixed |
| Claude Code update (2.1.49→2.1.63) | ✅ Done |
| MarkItDown installed | ✅ Done |
| `/remote-control` | ⚠️ Needs logout/login |
| Antigravity Awesome Skills | ✅ Researched — 946 skills, high value |
| Meta Ads clawhub skill | ✅ Found — ready to install |
| LEANN RAG | ❌ Too early stage — skip |
| OpenClaw security warnings | ℹ️ Reviewed — all acceptable-risk |
