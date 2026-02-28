# Production Queue

## Personal Setup
1. **Claude Code on phone** — Install Tailscale + Termius on phone, SSH to Mac mini (`100.124.44.74`, user: `deaconsopenclaw`), run `claude`. Ask Enoch to set up SSH key auth so no password needed. _Effort: 10 min_ _Priority: whenever_

## Active

### Console / Dashboard
1. **Knowledge graph visualization** — visual graph of entities, relationships, and connections across memory/research/notes. Nodes = people, projects, concepts, tools. Edges = relationships. Interactive, explorable from the console. _Effort: high_ _Priority: normal_

> **API costs** → not a standalone dashboard. Integrate spend summary (Anthropic, OpenAI, ElevenLabs, X API, Brave) into the **daily report** via what daily-report.mjs already knows. One line per service, totals. That's it.

### 📚 Bookshelf Dashboard
- Visual bookshelf display for the castle/console dashboard
- Book covers, read/unread/partial status, reading progress
- Sourced from the Bookshelf topic catalog (Ezra-maintained)
- Cross-references to Anna's Archive / Open Library for free copies
- Author bios, summaries, Deacon's personal notes on each book
- _Effort: medium_ _Priority: normal_

### Content Creator Cataloging
- Start with **Reformation Church** — scrape all articles, statements of faith, theological positions
- Build structured reference: beliefs, reasoning, scriptural basis
- Foundation for Deacon's personal theological knowledge base
- Future: expand to other creators, generate shorts from long-form content
- _Effort: high_ _Priority: normal_

### Google Photos Organization
- Go through Deacon's photos and name/organize them
- Need to confirm: are they in Drive or Google Photos proper?
- If Drive → use `gog` CLI. If Photos → need Photos API OAuth setup.
- Low urgency — do during slow periods
- _Effort: high (volume)_ _Priority: low_

### X Bookmarks OAuth
- OAuth 2.0 Client ID and Secret saved
- Auth flow script ready at `scripts/x-bookmarks-auth.sh`
- Need to re-run auth flow when browser cooperates
- Once done: nightly bookmark scan cron job



### Increased Hardening & Security
- **Full review doc:** `research/security-hardening-review_2026-02-16.md` (also on Google Drive)
- **Status:** 🟡 Future work — not implementing now. Will revisit at a later date.
- **Summary of items (8 total):**
  1. API keys → Apple Keychain (out of ~/.zshrc)
  2. Lock personality files (chmod 444, root-owned)
  3. Change default gateway port
  4. Fix data processing transparency claims
  5. Granular Google OAuth scopes (read-only vs send)
  6. Update Tirith docs (doesn't cover OpenClaw exec)
  7. Docker sandboxing for agents
  8. Clean-room sub-agent pattern for cloud requests
- **Source:** Deacon's IT security specialist (Mark Blake) review

### 🔒 Data Flow Audit (PRIORITY — Tomorrow)
- Map every point where data leaves the machine
- Anthropic/OpenAI: what context gets sent per request, can we strip PII
- Google: OAuth scope audit, what data flows where
- Twilio: voice audio, transcriptions
- Brave: search queries
- Local LLM viability: what can Ollama handle to keep sensitive stuff on-machine
- Clean-room sub-agent implementation plan
- **Goal:** For Spectrum pitch — "here's exactly how client PII never touches a cloud API"
- _Effort: high_ _Priority: critical_

### 📌 From Bookmarks — 2026-02-28 (Batch 2)

1. ~~**`openclaw secrets audit`**~~ ✅ **DONE** — Critical fixed (`openclaw.json` chmod 600). 5 remaining warnings reviewed, all acceptable-risk.

2. **OpenClaw: enable ACP thread-bound agents** — Use thread-bound persistent ACP sessions for channel workflows (`thread: true`, `mode: session`) and run `openclaw agents bind` for faster routing. _Effort: 15 min_ _Priority: normal_

3. **Claude Code /simplify + /batch** — Watch for next release. Boris Cherny (Anthropic). _Priority: whenever_

4. **Ziwenxu Mission Control beta** — Comment "OpenClaw" on @ziwenxu_ tweet to request beta. Pixel office, kanban sync, cron/log view. Overlaps Console dashboard queue item. _Effort: 2 min_ _Priority: normal_

5. ~~**Microsoft MarkItDown**~~ ✅ **DONE** — v0.1.5 installed via pipx. `markitdown <file>` ready to use.

6. **Local SEO + Claude service for Ridley Research** — Systematize as Ridley Research add-on. GBP optimization, service area pages, content factory. Pull `local-legal-seo-audit` + `programmatic-seo` from Antigravity Skills first. _Effort: medium_ _Priority: normal_

7. ~~**Check clawhub for Meta Ads Kit**~~ ✅ **DONE** — `meta-ads` skill exists (zachgodsell93, updated today, v1.0.0). Ready to install when needed: `clawhub install meta-ads`.

8. ~~**LEANN RAG evaluation**~~ ✅ **DONE** — Too early stage (1 star, Rust rewrite only). Skip for now.

9. **`/remote-control` in Claude Code** — Updated to 2.1.63 ✓. Command not yet flagged for this account (10% rollout). Action: `claude logout && claude login` to get fresh flags. _Effort: 5 min_ _Priority: soon_

10. **Antigravity Awesome Skills — pull relevant skills** — 946 skills, 16K+ stars, updated today. Relevant: `sales-automator`, `seo-content-writer`, `programmatic-seo`, `paid-ads`, `agent-memory-systems`. Review before building any of these from scratch. _Effort: medium_ _Priority: normal_

### 📌 From Bookmarks — 2026-02-28

1. **Claude Code `/remote-control`** — Update CLI to v2.1.58+, test the `/remote-control` command (Pro feature, rolling out). Log out/in first for fresh flags. _Effort: 15 min_ _Priority: soon_

2. **@ashen_one Mac Mini + OpenClaw video** — Watch the full video. Mine "3 Actual Things My Openclaws Do" for competitive intel + content ideas for Ridley Research. _Effort: 30 min_ _Priority: normal_

3. **Obsidian Sync headless integration** — Explore headless Obsidian Sync as agentic vault access layer (from @kepano). E2E encrypted, privacy-respecting. Obsidian skill already installed. _Effort: medium_ _Priority: normal_

4. **Speed-to-lead agent — Ridley Research service** — Blueprint from @coreyganim: webhook → AI text qualify → hot/cold route → auto-quote. Make/n8n + Twilio + LLM, ~2-4 hr build. Systematize into a Ridley Research install package. _Effort: medium_ _Priority: normal_

5. **Content: GhostTrack OPSEC thread** — Write-up for Ridley Research. Angle: "here's your threat surface from just a phone number, here's how to shrink it." Source: @sukh_saroy thread. _Effort: low_ _Priority: normal_

6. **Content: Xcode 26.3 + Claude + Codex** — Blog post angle: Apple shipped AI agent coding tools natively. What it means for developers. Source: @gregjoz announcement. _Effort: low_ _Priority: normal_

## Parked (Risk Review)
- **iMessage channel** — Full Disk Access granted, `imsg` CLI installed, Messages.app needs sign-in
- **Apple Notes integration** — AppleScript working, "Enoch" folder created, needs risk assessment before full wiring

## Completed
_(none yet)_
