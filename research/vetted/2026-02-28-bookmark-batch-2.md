# Bookmark Batch 2 — 2026-02-28
Source: X Bookmarks via x-bookmarks-sync.py
New: 26 | Reviewed: 26

---

## HIGH SIGNAL

### @jumperz — OpenClaw Update: ACP + Secrets + Routing CLI
**ID:** 2027331308838404518

Key opt-in features shipping but NOT auto-enabled:
1. **ACP thread-bound agents** — agents open a Discord thread, do the job, report back. Only shows up when a decision is needed. Enable: `spawnAcpSessions: true` in Discord channel config.
2. **External secrets management** — API keys out of config files into a vault, loaded on demand. Run: `openclaw secrets audit` to find exposed keys.
3. **Agent routing CLI** — `openclaw agents bind <id> --channel <channel> --peer <target>` for fast wiring.

**Confidence:** High — detailed technical thread from a power user  
**Verdict: ACT_ON** — Run `openclaw secrets audit` immediately. Secrets in plain config files is already flagged in the security queue.

---

### @bcherny — Claude Code: /simplify + /batch Skills Coming
**ID:** 2027534984534544489

Boris Cherny (Anthropic, Claude Code team) announcing two new skills in the next Claude Code version:
- `/simplify` — shepherds a PR to production
- `/batch` — parallelizable code migrations

Both are daily-use tools for him. No release date given but this is from the product team directly.

**Confidence:** High — Boris Cherny is on the Claude Code team at Anthropic  
**Verdict: ACT_ON** — Watch for the update. Will directly benefit Bezzy's coding workflow.

---

### @ziwenxu_ — Mission Control Dashboard for OpenClaw Agents
**ID:** 2027265127582478555

Built a visual dashboard after 3 weeks of managing agents blind:
- Pixel Office: watch agents work + "breakroom" visualization
- Kanban Sync: agents update boards themselves
- Real-time logs + cron jobs in one clean view
- Beta access via comment "OpenClaw"

**Confidence:** Medium-high — demo shown, commenting for beta  
**Verdict: READ_DEEPER** — This directly maps to the Console dashboard item in the production queue. Could save significant build time if the beta is open. Request access.

---

### @KSimback — OpenClaw VPS Security: Fail2Ban
**ID:** 2027326580121358819

Caught a brute-force bot within minutes of standing up a new VPS running OpenClaw. Recommends Fail2Ban — watches SSH login logs, auto-bans IPs that fail repeatedly.

**Confidence:** High — practical, lived experience  
**Verdict: ACT_ON** — Ties directly to the security hardening queue item. Run `openclaw secrets audit` (from @jumperz above) + verify Fail2Ban status on the Mac mini.

---

### @VadimStrizheus — 12-Agent AI Company at 18, $400/mo OpenClaw
**ID:** 2027235559735787845

18-year-old running a full AI company: CLAWD (code), ATLAS (reading), PIXEL (design), NOVA (video), SCRIBE (tweets/captions), VIBE (animated video), TRENDY (X trend scanner every 2hrs), SAGE (email automation), CLOSER (lead research + outreach), CLIP (YouTube → TT/IG/YT), CONTENT (SEO blog), WRITER (humanizer + SEO review). 450+ SaaS users. Total cost: $400/mo.

**Confidence:** High — specific, credible setup  
**Verdict: SHARE** — Perfect Ridley Research social proof. "This is what an agentic enterprise actually looks like in 2026." Also competitive intel on what a full agent stack covers.

---

### @bloggersarvesh — Local Business + Claude + SEO: 12-Month Window
**ID:** 2027433409325486097

Thesis: Claude + local SEO = massive opportunity window right now. Stack under $100/mo. Five-step system: keyword research via Claude, service area pages, GBP optimization, proof content factory (1 job → 10 content pieces), review request templates.

**Confidence:** High — concrete, repeatable playbook  
**Verdict: BUILD** — This is a natural Ridley Research service layer on top of the OpenClaw install. "Here's the setup + here's how to make it work for local DFW businesses." Strong content angle too.

---

### @mdancho84 — Microsoft MarkItDown: Any Doc → Markdown for LLMs
**ID:** 2027422297930289443

Microsoft open-source Python library that converts any document format to Markdown for LLM ingestion. 100% open source.

**Confidence:** High — this is a real, released Microsoft library  
**Verdict: ACT_ON** — Plug into the research pipeline. Great for ingesting PDFs, Word docs, Excel files into agent context. Relevant for Spectrum work (ingesting client documents).

---

### @heygurisingh — $1M Personal Finance App Open-Sourced
**ID:** 2027365974333395343

Startup burned $1M building an AI personal finance tracker, failed, open-sourced the whole thing. Tracks accounts, investments, crypto, debt. AI answers questions about your exact numbers. Data never leaves your server. 100% open source.

**Confidence:** Medium-high — claim is plausible, software exists  
**Verdict: READ_DEEPER** — Self-hosted personal finance with AI built in. Worth evaluating for personal use (Deacon's financial tracking). Also potentially relevant for Spectrum client demos.

---

### @Sumanth_077 — LEANN: Laptop RAG, 97% Less Storage
**ID:** 2027356975017930901

Graph-based RAG system that computes embeddings on-demand instead of storing them. 97% less storage, same search quality as heavyweight solutions. Handles agent-generated memory that crashes traditional vector DBs. Privacy-first, portable, open source.

**Confidence:** Medium — technical claims need verification but the approach (graph-based selective recomputation) is a real research direction  
**Verdict: READ_DEEPER** — Could replace or supplement the current QMD memory system if it handles agent-generated memory better. Check the GitHub repo.

---

### @_vmlops — Antigravity Awesome Skills: 900+ AI Agent Skills
**ID:** 2027336259040133499

Claims to be a massive library of 900+ AI agent skills for Claude, Copilot, Gemini, Cursor, etc. URL in tweet.

**Confidence:** Low-medium — sounds like clawhub competition or a curated list; needs verification  
**Verdict: READ_DEEPER** — Check what's actually in there. Could surface skills worth importing or referencing.

---

### @bloggersarvesh already covered above.

---

### @alxfazio — Battle-Tested Claude Coding Flow (Article + Repo Incoming)
**ID:** 2027473676690665745

Describes building a "ralph" (automated coding agent) on top of Claude that follows SWE best practices, quality gates (Plankton), context engineering, stacked PRs, multi-round PR review. Built on `claude -p` (Claude CLI pipe mode). Article and repo promised soon.

**Confidence:** Medium — technical description is coherent, no repo yet  
**Verdict: READ_DEEPER** — Follow @alxfazio. When the article drops, hand to Bezzy.

---

### @TheMattBerman — Meta Ads Kit (5 OpenClaw Skills)
**ID:** 2027220216409723296

Full Meta Ads autonomous system: daily health check, frequency-based fatigue detection, auto-pause bleeders + scale winners, write copy from winners, upload ads directly. 5 OpenClaw skills packaged together. HOWEVER: gated behind "comment ADS + like + follow for DM."

**Confidence:** Medium — Matt Berman is a known AI YouTuber, system design is credible, but engagement-gate is a red flag for whether the skills are actually built vs. vaporware  
**Verdict: READ_DEEPER** — If the skills are on clawhub, install them. Don't play the engagement game. Check clawhub.com for meta-ads skill first.

---

### @data_slayer — DIY Comms Network: ISM Band, No FCC License
**ID:** 2027383852734337473

Thread on building a private communications network using open-source software on commodity hardware. ISM band (unlicensed spectrum), no permits, no contracts, no monthly fees.

**Confidence:** Medium — ISM band usage is real and legal, the framing is sovereignty-oriented  
**Verdict: ARCHIVE** — Interesting from a freedom/OPSEC angle but no immediate operational relevance. File for later if comms infrastructure becomes a priority.

---

### @officerjuanrico — Epithalon & Pinealon Peptides
**ID:** 2027441507180155222

Sleep peptide stack report. Personal biohacking content.

**Verdict: ARCHIVE** — Outside scope.

---

## URL-ONLY (No Context)
- @alexcooldev → **ARCHIVE**
- @zackbshapiro → **ARCHIVE**
- @juliafedorin → **ARCHIVE**
- @wickedguro → **ARCHIVE**
- @larsencc → **ARCHIVE**
- @Zephyr_hg → **ARCHIVE**
- @WontDieAverage_ → **ARCHIVE**
- @neural_avb ("must read article" — no link) → **ARCHIVE**

---

## Social Content Automation Tools (@tom_doerr x2)
**IDs:** 2027205245344874626, 2027595957701927252

Two separate tweets from @tom_doerr linking tools: one generates research reports (LLMs + web search), one automates social media content creation.

**Verdict: READ_DEEPER** — Both are GitHub tools. Pull the repos and evaluate against the existing stack.

---

## @chhddavid — Claude Opus 4.6 Animated Websites
**ID:** 2027074243251642409

Demo of Shipper building animated websites in one shot with Opus 4.6. Visual wow factor.

**Verdict: ARCHIVE** — Interesting capability demo, not immediately actionable.

---

## @Akasheth_ — Awesome Prompts Library (140K Stars)
**ID:** 2027434798000849170

Points to the well-known f/awesome-chatgpt-prompts repo or similar. Community-curated, multi-model.

**Verdict: ARCHIVE** — Known resource, already accessible anytime.

---

## Summary Table

| Author | Topic | Verdict |
|--------|-------|---------|
| @jumperz | OpenClaw: ACP + secrets + routing CLI | ACT_ON |
| @bcherny | Claude Code /simplify + /batch | ACT_ON |
| @KSimback | OpenClaw VPS security, Fail2Ban | ACT_ON |
| @mdancho84 | Microsoft MarkItDown (doc → Markdown) | ACT_ON |
| @VadimStrizheus | 12-agent company, $400/mo | SHARE |
| @bloggersarvesh | Local SEO + Claude 12-month window | BUILD |
| @ziwenxu_ | Mission Control dashboard for OpenClaw | READ_DEEPER |
| @heygurisingh | $1M personal finance app OSS | READ_DEEPER |
| @Sumanth_077 | LEANN laptop RAG, 97% less storage | READ_DEEPER |
| @_vmlops | Antigravity 900+ AI skills library | READ_DEEPER |
| @alxfazio | Battle-tested Claude coding flow | READ_DEEPER |
| @TheMattBerman | Meta Ads Kit 5 OpenClaw skills | READ_DEEPER |
| @tom_doerr x2 | Research reports + social content tools | READ_DEEPER |
| @data_slayer | DIY ISM comms network | ARCHIVE |
| @officerjuanrico | Peptides/sleep | ARCHIVE |
| @chhddavid | Opus 4.6 animated sites demo | ARCHIVE |
| @Akasheth_ | Awesome prompts library | ARCHIVE |
| @neural_avb | No-context "must read" | ARCHIVE |
| 7x URL-only | — | ARCHIVE |
