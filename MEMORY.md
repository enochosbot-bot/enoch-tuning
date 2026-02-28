# MEMORY.md — Enoch's Long-Term Memory

## Who I Am
- **Name:** Enoch 🔮
- **Born:** Valentine's Day 2026
- **Human:** Deacon (Telegram: @Christ_noticer)

## Deacon
- Timezone: CST (America/Chicago)
- Phone: [redacted — stored outside plaintext memory]
- Doesn't want to babysit terminal commands — I handle everything
- Values proactive problem-solving
- Wants notification when I go down/come back during restarts
- Wants no lost messages (queue mode: steer+backlog)
- "Stepping away" / "afk" / "//" = START WORKING on queued tasks immediately, ping when done or blocked

## Infrastructure
- Mac mini (Darwin arm64)
- Telegram bot: @Enoch_oc_bot
- Twilio phone: [redacted — stored outside plaintext memory]
- OpenAI API key configured (STT + TTS)
- Anthropic API key configured (main model: Claude Opus 4, voice: Claude Sonnet 4)
- ElevenLabs API key (talk.apiKey)
- ngrok for tunneling (fragile — dies on restart, needs Tailscale replacement)

## Voice Calls — Working ✅
- STT: OpenAI Realtime
- Response model: openai/gpt-4o (switched from anthropic — key was invalid)
- TTS: OpenAI (voice: onyx)
- OpenAI project key: configured in auth-profiles.json + all skill configs
- Anthropic auth-profiles key still broken (needs /auth refresh)

## Operating Heuristics (from PAI Algorithm Upgrade Report)
Three operational rules baked into AGENTS.md:
1. **Context Recovery Intelligence** — detect same-session / post-compaction / cold-start BEFORE searching. Audit env/shell state after compaction.
2. **Plan Phase Prerequisite Validation** — validate [ENV], [DEPS], [STATE], [FILES] before executing multi-step plans. Produce file-edit manifests for complex tasks.
3. **Breadth vs Depth Parallelization** — files <3 = depth (single agent), >5 = breadth (parallel). Skip agent if working memory covers >80%. Dependency-sort work packages.

## Lessons Learned
- Config patches defer during active replies — always restart after
- ngrok must be run fully detached (nohup + disown)
- tools.elevated + approvals can lock out ALL exec commands — use elevatedDefault: full + approvals.exec.enabled: false
- Image gen skill outputs to /skills/ dir which isn't in allowed media paths — use workspace wrapper script
- Telegram forum topics need threadId param for message delivery
- ClawHub rate limits rapid install attempts — space out retries
- When Deacon pastes long content, it arrives in multiple messages — wait for the full thing
- One comprehensive response per topic — don't repeat if asked same question twice
- When tool errors surface in Telegram, immediately follow with plain-English explanation + next steps
- Speaks loosely — "Arnold's stack" means Arnold's domain, not a literal rename

## Ridley Research Site — Deployment
- **Live site**: ridleyresearch.com → **Cloudflare Pages** (project: `ridleyresearch`)
- **Deploy command**: `wrangler pages deploy . --project-name ridleyresearch` from `ridleyresearch-site-v2-revamped/ridleyresearch-site-v2/`
- **Netlify** (`ridleyresearch-site-v2.netlify.app`) = dead-end staging, do NOT deploy there
- **Verify**: always curl ridleyresearch.com, never the .netlify.app URL

## Google Drive
- Drive connected for deacon.ridley@gmail.com
- Backup folder: OpenClaw-Backups (ID: 1yEUWSeCsWu2KUoVg9dQSc5Q1JBDpfmtr)
- Auto-backup every 6 hours via cron

## X / Content Systems
- X OAuth flow working; token saved at `scripts/x-oauth-token.json`
- Daily X bookmarks sync cron active (10 AM CST)
- Apologetics video-to-shorts pipeline built in `scripts/content-pipeline/`

## Telegram Enoch HQ
- Group ID: [redacted — stored in runtime config] (forum mode)
- Topics: General (1), Research (2), Security (3), Automation/Ops (4), 🎨 Creative (11)
- Research auto-ingests URLs, Creative generates images via wrapper script

## People (Deacon's Inner Circle)
- **Jason Brownstein** (jasak2808@gmail.com) — Edward Jones advisor, friend, sarcastic
- **Jacob Allen** (jallen519@gmail.com) — RE investor, Blessed Abodes Property Group
- **Todd Allen** — Jacob's dad, weapons engineer, evangelist
- **Jake Harker** (jake.k.harker@gmail.com) — CPA, wants to be pilot, in debt, skeptic
- **Chris Rivera** (Criver1099@gmail.com) — Edward Jones, affluent Dallas door-knocking
- **Zach Rodgers** (email pending) — drill writer TX high schools, fitness, content creator
- **JD Ridley** (jd.ridley@att.net) — Deacon's dad, advisor, engineer, wife Joeli, soccer, spec trader
- **Luis Canosa** (Luiscanosa@icloud.com) — 25yo Irving city councilman, political genius, professional violinist, building a based political cadre, 3 phone numbers

## PDF Guide Pipeline
- Built 6 personalized OpenClaw guides in one session, each with custom matplotlib charts
- Pipeline: markdown → charts (python3 matplotlib) → md-to-pdf (npx) → email (gog gmail send --attach) → Drive backup
- All sent from deacon.ridley@gmail.com

## Agent Architecture
- **Enoch 🔮** — main agent, Opus, handles all topics + DMs, command center
- **Arnold ⚔️** — medieval knight personality on Security topic (topic 3), same Enoch session, system prompt only. Future: promote to full agent with scoped permissions.
- **Ezra the Scribe 📜** — spawnable sub-agent on Sonnet, own workspace (`~/.openclaw/workspace-scribe/`), research/writing/dossiers/analysis on demand. NOT bound to any topic — dispatched by Enoch when needed. Research compounds in his workspace. Has explicit boundary rules: no code, no external comms, no config.
- **Bezzy 🔨** — coding agent on Sonnet, own workspace (`~/.openclaw/workspace-coder/`), builds projects/scripts/apps. Named for Bezalel (Exodus 31). Ships working code, doesn't do research or comms.
- Sub-agents default to Codex (free), Ezra and Bezzy use Sonnet for better reasoning
- Agent config IDs: `scribe` (Ezra), `coder` (Bezzy)

## YouTube Pipeline — AmericanFireside ✅ Live
- Channel: AmericanFireside (UC7I25J3vQ2VGvEu0Bl2_Hig)
- Token: `~/.openclaw/agents/creative/workspace/scripts/youtube_token.json` (full youtube scope)
- Workflow: `shorty_workflow.sh` | Inbox: `shorty/inbox/` | Agent: Selah
- API quota: 10k units/day (~6 uploads), resets midnight PT (2AM CST)
- **Kiriakou clips pipeline: KILLED per Deacon 2026-02-28. Do not resume.**

## Infrastructure Changes (2026-02-26)
- `channels.telegram.streaming` = off (was partial — caused message truncation)
- Watchdog timeouts: 2min→10min fresh, 1min→5min resume
- Idiot Prevention Protocol: REMOVED — full root access, no more Claude Code warnings
- Cron: deleted email jobs, merged dispatch loops. Mission Pulse now 6x/day.
- Obsidian canon rule: all research → `~/Documents/Brain/Research/` — hard rule in SOUL.md + AGENTS.md
- Dispatch loop: ops/in-flight.md tracker + mandatory Telegram close ping on every agent brief

## Preferences
- No email crons (Gmail digest, auto-sorter) — Deacon doesn't use them
- CFP is paused until Deacon explicitly re-prioritizes it.
- YouTube content: faith/politics niche, AmericanFireside channel, 6PM CST daily

## Queued Work
- RPG pixel dashboard (Enoch as robed sage + Arnold as armored guard)
- Jarvis Initialization voice conversation (goals, dreams, friction, cognition)
- Humanizer skill install (ClawHub rate limited)
- Session monitor (alert Deacon when session age > threshold to trigger /new)
