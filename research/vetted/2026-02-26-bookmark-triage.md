# Bookmark Triage — 2026-02-26
160 new bookmarks. Grouped by priority. URL-only tweets flagged separately.

---

## 🔴 ACT ON — Deploy or use immediately

**@thisguyknowsai** — Scrapling: undetectable web scraper for OpenClaw
784x faster than BeautifulSoup, bypasses Cloudflare, adaptive (re-finds elements after redesigns), MCP server so agents can scrape directly, built-in proxy rotation. This is a direct capability upgrade for the research pipeline.
`pip install scrapling`
**Verdict: BUILD** — install scrapling, wire into research workflow

**@claudeai** — Claude Code Security (limited research preview)
Anthropic's own security scanner for codebases — finds vulns traditional tools miss, suggests patches for human review. Directly relevant to any serious codebase.
**Verdict: ACT_ON** — sign up for preview at anthropic.com

**@claudeai** — Claude Code → Figma push
Build prototype in code, push directly to Figma canvas via updated MCP server. Relevant if doing any design work.
**Verdict: ACT_ON** — update Figma MCP server

**@heynavtoor** — CodexBar: menu bar AI usage tracker
Tracks Claude Code, Codex, Cursor, Gemini limits in real time. Shows resets. Reads local data, no cloud. `brew install --cask steipete/tap/codexbar`
**Verdict: ACT_ON** — install this

**@blader** — Taskmaster
"Install taskmaster and you'll be in the 0.01% of users who have Claude Code running for days straight." Task management layer for extended Claude Code sessions.
**Verdict: ACT_ON** — evaluate for long coding runs

**@chiefofautism** — claude-hooks: prompt injection firewall for Claude Code
Scans every file read, URL fetch, command output for 50+ attack patterns BEFORE Claude processes. One install protects all sessions. Catches hidden instructions in READMEs, HTML comments, base64 encoding. Open source by Lasso Security.
**Verdict: BUILD** — install if running Claude Code with --dangerously-skip-permissions

**@PineAiCallAgent** — PineClaw: OpenClaw agent makes real phone calls
Actual telephony infrastructure, not browser audio. Low-latency, can navigate phone trees, join Zoom/Google Meet.
**Verdict: ACT_ON** — check if this integrates with the current agent setup

---

## 🟡 READ DEEPER — Substantive, needs more attention

**@forloopcodes** — Skills benchmark paper: smaller models with skills beat larger without
Paper claims a smaller model (Claude 4.5 Haiku) with high-quality skills beats raw Opus 4.5 by ~6%. Also: self-generated skills show NEGATIVE delta on 16/84 tasks, and giving agents >3 skills at once causes context bloat and failure. Codex GPT 5.2 gets beaten by Gemini 3 Flash on performance-per-dollar.
KEY FINDING: Skill engineering is mathematically proven to substitute for raw compute. But: quality over quantity, and manual skill design beats auto-generated.
**Verdict: READ_DEEPER** — find the actual paper, this has direct implications for how skills are built

**@StefanoErmon** — Mercury 2: world's first reasoning diffusion LLM
Claims 5x faster than speed-optimized LLMs. Comes from Inception Labs. Diffusion for language (not autoregressive) is a genuinely different architecture.
**Verdict: READ_DEEPER** — benchmark against current models for speed-sensitive tasks

**@SimonHoiberg** — RAG-based memory for OpenClaw
PostgreSQL + pgvector + CRON flush. Short-term memory in file, long-term in vector DB. "MUCH less token-greedy." The three-tool combo: OpenClaw + PostgreSQL/pgvector + n8n.
**Verdict: READ_DEEPER** — could improve current memory setup significantly

**@chiefofautism** — AI supply chain behind a single ChatGPT query
76 nodes, 13 countries, 10 layers. Key finding: one quartz mine in Spruce Pine NC supplies the ENTIRE semiconductor industry with crucibles — no backup. One landslide stops global chip production. Built an interactive map.
**Verdict: READ_DEEPER + SHARE** — this is exactly the kind of infrastructure fragility intel that matters

**@MatthewBerman** (5B tokens) — comprehensive OpenClaw OS video
Covers email pipelines, CRM, meeting intelligence, OAuth loophole fix, cron jobs, memory, cost tracking, backup/recovery, financial tracking. 38 min.
**Verdict: READ_DEEPER** — the OAuth loophole segment at 31:52 is directly relevant to what we just fixed

**@heygurisingh** — Claude-Flow: #1 agent framework on GitHub
60+ parallel agents, shared memory, 75% API cost reduction via smart routing (simple tasks → WebAssembly, complex → right model). 14,100+ stars.
**Verdict: READ_DEEPER** — worth evaluating against current multi-agent setup

**@Akashi203** — OpenFang: Rust OS for AI agents (137k lines, MIT)
WASM sandboxes for agents like Linux processes. 16 security layers: WASM sandboxing, merkle hash-chain audit trails, taint tracking on secrets, signed agent manifests, prompt injection detection, SSRF protection. "Hands" = scheduled agents that run 24/7 without prompting.
**Verdict: READ_DEEPER** — the security model is serious and the Hands concept is exactly what this setup aims for

**@heygurisingh** — WiFi-DensePose: body pose detection through walls using WiFi
Just the router, no camera/sensor. Maps full body in real time. Open-sourced. Government/corporate tech now public.
**Verdict: READ_DEEPER** — privacy/surveillance implications are significant

**@andrewfarah** — Field Theory: hot mic mode, fully offline, 89ms latency
Talk to/control your computer with no wake word. Free until 3/1. Experimental.
**Verdict: READ_DEEPER** — try it before the free window closes

**@mattzcarey** — Code Mode for MCP
"Code Mode is all you need" — excited about this direction for MCP. Appears to be a significant shift in how MCP servers interact with coding agents.
**Verdict: READ_DEEPER** — find the linked demo

**@0xKingsKuan** — Mission Control: 6-component OpenClaw dashboard
Tasks Board, Content Pipeline, Calendar, Memory, Team, Office — all built as Next.js + Convex apps by the agent itself. Chinese post but the build commands are in English.
**Verdict: READ_DEEPER** — the Tasks + Calendar + Memory combo is directly relevant to ops infrastructure

**@witcheer** — Agent with its own email and GitHub
Google Alerts on 10 topics → agent reads → updates memory → shows up in research. Nightly code pushes to private repo. Self-health check every night. "From a bot I talk to, to a system that operates on its own."
**Verdict: READ_DEEPER** — the Google Alerts → memory → research pipeline is worth replicating here

**@shinboson** — OpenPlanter: government surveillance monitor
Correlates structured/unstructured data, finds entity anomalies automatically. "Keep tabs on your government since they're almost certainly keeping tabs on you."
**Verdict: READ_DEEPER** — check what data sources it pulls from

---

## 🟢 SHARE — Worth amplifying

**@tolibear_** — Context handoff protocol
At 80% context: save handoff to memory/YYYY-MM-DD-HHMM-context-handoff.md with objective/done/pending/resume command/blockers. Never continue in same session. Clean and replicable.
**Verdict: SHARE + BUILD** — this is already partly in play here; formalizing it would be valuable

**@sharbel** — AI self-audit prompt
"Audit everything about how we work together. Review every recurring task... kill what's dead weight, automate what I'm still doing by hand, propose 3 things we're not doing that we should be. Be brutally honest."
**Verdict: SHARE** — run this against the current agent setup quarterly

**@kaostyl** — AI self-review loop every 4 hours
Caught 12 mistakes, fixed 3 recurring failure patterns, flagged a security leak without being asked. Stack: OpenClaw + Mac Mini + 4 rooted Pixels + Telegram. Cost: less than Netflix.
**Verdict: SHARE** — the self-correction loop concept is proven here

**@kloss_xyz** — Radical simplicity audit prompt (very long)
Full structured audit framework: overengineering detection, cognitive load audit, psychological/incentive audit, architectural earned complexity, subtraction exercise. Batched YES/NO/DEFER decisions only.
**Verdict: SHARE** — this is genuinely useful for any product/system review

**@jumperz** — Self-healing sentinel for agent swarms
Runs every 10 min: detect/fix/verify/log/alert. Fixes cron drift, stale context, dropped tasks, crashed agents. Saves before/after state with incident IDs. Cross-platform alerts.
**Verdict: BUILD** — relevant for the multi-agent setup; worth implementing

---

## 🗄️ ARCHIVE — Noted but no action needed

**@GeminiApp** — Nano Banana 2: faster image model at Pro quality
Already in the toolkit. Noted.

**@chhddavid** — Waze clone with Shipper (ad/promo content)

**@askOkara** — Reddit monitoring tool for first 100 users (startup marketing)

**@joanrod_ai** — QuiverAI / Arrow-1.0: SVG from images/text, $8.3M seed, a16z
Noted. Vector design niche, not immediately relevant.

**@noahiglerSEO** — Internal link SEO strategy for blue-collar websites
Good playbook but not in current scope.

**@noahiglerSEO** — 60-second AI lead response (plumbing case study)
60% conversion rate jump. Solid case study for any client-facing AI work.

**@whosjunaidd** — Esprit AI pentesting agent (lead gen tweet, comment "security")

**@dr_cintas** — ClawHub App Store / 250K skills (this is OpenClaw's own skill store)

**@0xPaulius** — Komand app with Claude + Codex skills

**@blackboxai** — Claudex Mode: Claude Code + Codex on same task
Interesting parallel verification concept. Noted.

**@svpino** — Nimble skill for Claude Code (structured web scraping via skill)
Redundant given Scrapling above, but worth knowing exists.

**@coreyganim** — practical AI tool list (Perplexity, Exa, ElevenLabs, Clay, etc.)

**@heygurisingh** — Claude Code creator's workflow (Boris Cherny: 10-15 parallel sessions, CLAUDE.md self-updating rules)
The CLAUDE.md self-improvement loop is already in use. Good validation.

**@ihtesham2005** — ClaudeCodeUI: GUI for Claude Code (visual project manager, file tree, chat history)
**@ihtesham2005** — GitNexus: GitHub repo → knowledge graph in browser (zero server, AST parsing, graph RAG)
Both noted. GitNexus is genuinely useful for codebase research.

**@sukh_saroy** — llmfit: LLM hardware compatibility checker (94 models, 30 providers)
Relevant for local model evaluation.

**@hasantoxr** — claude-code-best-practice GitHub repo

**@hasantoxr** — GitNexus (same as above, different account tweeting it)

**@WorkflowWhisper** (x2) — Synta + n8n workflow sales pitches (lead gen)

**@lukepierceops** — AI/automation pricing tiers ($500–$200K)
Good market reference for pricing AI work.

**@draprints** — SEC 8-K filings as free buyer intent data
Genuinely underused. 8-K = material events = budget + urgency signals. Cross-reference LinkedIn Sales Nav $30/mo.
**Verdict: ACT_ON for outbound research**

**@PhedEU** — 20-min 3D documentaries for $5 (AI video era commentary)

**@SuhailKakar** — Polymarket CLI in Rust

**@stephenhaney** — Paper Desktop: canvas for Cursor/Claude Code/Codex

**@peteromallet** — 155K Claude Code messages released (Deepseek scraping response)

**@heygurisingh** — Boris Cherny Claude Code workflow (same as above)

**@phosphenq** — NotebookLM + Gemini + Obsidian learning system (YT: zproger)

**@gregisenberg** (x2) — Obsidian + Claude Code operating system, digital employees
Good conceptual framing but no new tools.

**@SimonHoiberg** (already covered above in READ_DEEPER)

**@draprints** — SEC 8-K strategy (already noted above)

**@hasantoxr** (x2) — claude-code-best-practice, GitNexus (already noted)

**@KanikaBK** — Greg Isenberg Upwork to $500K video

**@andrewfarah** — Field Theory (already in READ_DEEPER)

**@rohit4verse** — skills article (same EXM7777 quote)

**@WorkflowWhisper** — local business automation pricing

**@heygurisingh** — Boris Cherny CLAUDE.md article

**@om_patel5** — UI vibe coding tips (sketch first, screenshots, design system before code)
Actually useful — the "show don't tell" approach to UI prompting is solid.

**@bohdanmotion** — AI animation with 1 prompt (showcase)

**@Replit** — Replit Animation powered by Gemini 3.1 Pro

**@boringlocalseo** — LLM mentions via press releases
ACT_ON for local business clients: "research-style" press release → ChatGPT mentions in 72hrs. $200 PR distribution.

**@lucatac0** — TTS CLI built by OpenClaw in 35 min

**@CodeswithClara** — AI design prompts (Claude Opus 4.6)

**@taalas_inc** — Taalas: 24 people, $30M, "extreme specialization, speed, power efficiency"
Unknown product. Needs investigation.

**@srishticodes** — CLAUDE.md from Boris Cherny practices

**@joshdgavin** — call funnel pitch (not relevant)

**@sahill_og** — modern startup stack list

**@EXM7777** — writing style extraction prompt / other URLs

**@tolibear_** — context handoff (already covered above)

**@johann_sath** — workspace evolution post / security guide URL

**@kloss_xyz** — 25 agent audit prompts
Worth saving. These are genuinely good pressure-test prompts for an agent operator.

**@HamptonAc_** — URL only, skip

**@chiefofautism** — RedAmon: autonomous AI pentester with Metasploit shells
9K templates, 17 node types, Neo4j knowledge graph, full RCE from zero data. Impressive/scary. Relevant for red team awareness.

**@rork** — Rork Max: iOS app builder (Claude Code + Opus 4.6 powered)

**@EddChalk** — OpenClaw ad brief automation pipeline (3-agent skill graph for ad production)
The architecture is solid: research agent → brief writer → QA agent with minimum score 7/10. Worth examining for any content automation.

**@MindBranches** — AI mastery roadmap infographic

**@dimitarangg** — cold email system (54K emails, 59 calls in 16 days)
The methodology is real but ethically questionable (mass spam). Noted.

**@claudeai** — Claude Code Security (already in ACT_ON)

**@mattpocockuk** — AI coding workflow with specific skills chain

**@georgepickett** — OpenClaw Studio (npx openclaw-studio)

**@bprintco** — vibe coded quote system for painting company

**@contraben** — Contra Payments: sell to AI agents

**@forloopcodes** — skills benchmark (already in READ_DEEPER)

**@mattzcarey** — Code Mode MCP (already in READ_DEEPER)

**@0xTib3rius** — Continuous Reasoning AI Pentester

**@charliebcurran** — Seedance 2.0 (AI video demo)

**@shinboson** — OpenPlanter (already in READ_DEEPER)

**@trajektoriePL** — cardiologist 3rd place at Anthropic hackathon (Opus 4.6 medical platform)

**@chiefofautism** — AI supply chain map (already in READ_DEEPER)

**@ziwenxu_** — 10 things before OpenClaw (good operational tips, nothing new)

**@poetengineer__** — Obsidian note embeddings as 3D network visualization

**@thedankoe** — URL only

**@iamliamsheridan** — Claude Sonnet 4.6 outbound prompts doc

**@leojrr** — viral app idea skill (Virlo API + trend analysis)

**@tolibear_** — URL

**@bilawalsidhu** — real-time geospatial intelligence app (Gemini 3.1 + Claude 4.6)
Planes, satellites, dark ships, nuclear facilities, traffic cams, panoptic detection. "Classified intelligence system skin." Impressive demo.

**@blader** — Taskmaster (already in ACT_ON)

**@Google** — 3 months Google AI Pro for learners

**@GenAI_is_real** — Voicebox: open source TTS, "Ollama moment for TTS"
The proprietary TTS moat is collapsing. Every agent will have local high-fidelity voice soon.

**@oliviscusAI** — Voicebox link + newsletter

**@gregisenberg** — OpenClaw digital employees (already covered)

**@ziwenxu_** — URL

**@witcheer** — agent with email/GitHub (already in READ_DEEPER)

**@KSimback** — URL

**@AlexFinn** — mission statement concept (good, already doing this)

**@LightDriver21** — "Agents are the Product now" (true)

**@bobbyjocson** — ClawVault memory visualization

**@sharbel** — trading bot wants sub-agent (illustrative story)

**@claudeai** — Claude Code → Figma (already in ACT_ON)

**@CrypSaf** — Web4: self-surviving AI agent ($5, earns to survive)
Gimmicky but conceptually interesting. Agent dies if it can't make money. 1M views in 5 hours.

**@0xSigil** — Web 4.0 manifesto (self-replicating AI write-up)

**@Luckshuryy** — market profile trading tutorial

**@oliverhenry** — URL + Larry (content automation skill)

**@kaostyl** — 4-hour self-review (already in SHARE)

**@sharbel** — AI employees playbook URL

**@jessegenet** — OpenClaw + 3D printer for homeschool

**@MatthewBerman** (x2) — 2.54B tokens video, 10x better post

**@AlexFinn** — Sonnet 4.6 upgrade post / URL

**@NickADobos** — OpenClaw for ___

**@sharbel** — specialist agents breakdown

**@0xSero** — OpenClaw hacks thread

**@jumperz** — sentinel (already in SHARE/BUILD)

**@jessegenet** — YouTube curator for kids (no algo)

**@hasantoxr** — Accomplish: local AI that codes + browses simultaneously

**@dr_cintas** — Pencil: Figma meets Claude Code (Figma → code locally)
Worth watching. Infinite canvas + parallel design agents + local.

**@kloss_xyz** — 6 research analyst prompts (bookmark from Feb 6)

**@om_patel5** — claude code skill URL

**@ryancarson** — URL

**@PineAiCallAgent** — PineClaw (already in ACT_ON)

**@robjama** — Toronto Claude Code meetup demo reference

**@Av1dlive** — URL

**@simplifyinAI** — LLM uncensoring tool (1 command)

**@JamesonCamp** — $50K value in 10 hours (Claude + Manus + Klaviyo stack)

**@akbuilds_** — Opus 4.6 in Figma via Cursor

**@woocassh** — URL

**@austin_hurwitz** — URL

**@sharbel** — self-audit prompt (already in SHARE)

**@sillydarket** — URLs (x2)

---

## ⬜ SKIP — URL only, no context
@shitpost_2049, @coreyganim, @levikmunneke, @paoloanzn, @elvissun, @d4m1n, @molt_cornelius (x2), @koylanai, @code_rams, @alxfazio, @Legendaryy, @fromzerotomill, @HamptonAc_, @trq212, @sillydarket, @rohit4verse (old), @EXM7777 (multiple old URLs), @thedankoe, @everestchris6, @Flynnjamm, @Av1dlive, @KSimback, @woocassh, @austin_hurwitz, @ryancarson, @tolibear_ URL, @ziwenxu_ URL, @oliverhenry URL, @AlexFinn URL, @dimitarangg URL

---

## Summary by verdict
| Verdict | Count |
|---------|-------|
| ACT_ON | 8 |
| BUILD | 4 |
| READ_DEEPER | 12 |
| SHARE | 5 |
| ARCHIVE | ~80 |
| SKIP (URL only) | ~50 |

## Top 5 priority actions
1. **Install Scrapling** — direct research capability upgrade
2. **Install claude-hooks** — prompt injection protection if using --dangerously-skip-permissions
3. **Read the skills benchmark paper** — changes how skills should be built (fewer, better, never auto-generated)
4. **Try Field Theory hot mic** — free until 3/1, 89ms offline voice control
5. **Install CodexBar** — instant AI usage visibility
