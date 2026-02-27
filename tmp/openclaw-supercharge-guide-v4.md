# 🦞 OpenClaw Supercharge Guide — v4
### From Base Bot to Fully Operational Personal AI

_Built by Deacon & Enoch. Updated February 26, 2026. This is the real guide — everything we learned setting up a production-grade, multi-agent OpenClaw instance from scratch. What actually works, what the docs skip, what took us all-night sessions to figure out._

---

## Table of Contents

1. [What This Actually Is](#what-this-actually-is)
2. [Prerequisites — Mac Setup From Scratch](#prerequisites)
3. [Step 1 — Core Tool Installation](#step-1-core-tool-installation)
4. [Step 2 — Workspace File Structure](#step-2-workspace-file-structure)
5. [Step 3 — The Jarvis Initialization Sequence](#step-3-the-jarvis-initialization-sequence)
6. [Telegram Forum Architecture](#telegram-forum-architecture)
7. [Cron Job System](#cron-job-system)
8. [Response Timings & Latency](#response-timings--latency)
9. [The Agent Roster — Multi-Agent Delegation](#the-agent-roster--multi-agent-delegation)
10. [Model Routing & Cost Strategy](#model-routing--cost-strategy)
11. [Voice Calls via Tailscale](#voice-calls-via-tailscale)
12. [Tool Integrations](#tool-integrations)
13. [API Keys & Credentials Checklist](#api-keys--credentials-checklist)
14. [Security Hardening Roadmap](#security-hardening-roadmap)
15. [Key Philosophy](#key-philosophy)

---

## What This Actually Is

OpenClaw is a self-hosted AI agent gateway. It sits on a machine you own, connects to Telegram, and gives you a personal AI that has persistent memory, runs automated jobs, delegates to specialized sub-agents, and integrates with your actual tools. Not a product. Not a subscription. Infrastructure.

The distinction that matters: **your data lives on your machine**. Files, memory, conversation history — all local. Cloud APIs (Claude, Codex) get invoked for the actual reasoning, but nothing is stored on their servers after the request completes. Anthropic and OpenAI explicitly do not train on API data.

This guide reflects what we actually built. Single Mac mini (M4, 24GB RAM), running 24/7, with a full agent roster. The core setup takes a few hours. The personalization is ongoing.

**Who this is for:** Technically competent people who want to replicate what we built. You should be comfortable with the terminal, understand what a cron job is, and be okay running into errors and debugging them.

---

## Prerequisites

Start here if you're on a fresh Mac. If you have these tools already, skip ahead.

### 1. Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Follow the post-install instructions to add Homebrew to your PATH. Don't skip this step.

### 2. Node.js
```bash
brew install node
```

### 3. Git
```bash
brew install git
```

### 4. Python 3
```bash
brew install python3
```

### 5. Bun
```bash
brew install oven-sh/bun/bun
```

### 6. Tailscale (stable tunnel — required for voice calls and remote access)
```bash
brew install --cask tailscale
```
Open Tailscale from Applications → sign in → approve the network extension in **System Settings → General → Login Items & Extensions → Network Extensions**. We'll come back to this in the Voice Calls section.

### 7. OpenClaw
```bash
npm install -g openclaw
openclaw onboard --install-daemon
```

### 8. Anthropic Auth
```bash
claude setup-token
```
Use your Claude subscription token — **do not use API credits for this**. The subscription is flat-rate. API credits will drain fast.

### 9. Telegram Bot
1. Message **@BotFather** on Telegram → `/newbot`
2. Copy the bot token
3. Run `openclaw doctor` and paste the token when prompted

Once your bot responds to a message in Telegram, move to Step 1.

---

## Step 1 — Core Tool Installation

Paste this block to your agent in Telegram and let it run. It installs the tool stack and sets up the workspace structure.

```
I need you to set up my entire workspace and tool stack. Do everything in order, don't ask me questions — just execute. Report back when done.
```

Then paste each section below.

---

### 1a. Terminal Security — Tirith

```bash
brew install sheeki03/tap/tirith
echo 'eval "$(tirith init)"' >> ~/.zshrc
```

**Important limitation:** Tirith hooks into your interactive shell via `eval "$(tirith init)"`. OpenClaw executes commands via Node.js `child_process.spawn()` — which bypasses the interactive shell entirely. Tirith is watching the front door while OpenClaw uses a side entrance. This is documented in the security review. The actual safety layer for OpenClaw commands is its own `exec.security` setting (see Security Hardening section). Keep Tirith installed — it's valuable for your own terminal work — but don't assume it protects what the agent runs.

### 1b. Local Semantic Search — QMD

```bash
npm install -g https://github.com/tobi/qmd
qmd collection add ~/.openclaw/workspace --name workspace
qmd embed
```

QMD indexes your workspace and gives your agent semantic search over all your files. Run `qmd embed` again after adding significant new content.

### 1c. YouTube / URL Summarizer

```bash
brew install steipete/tap/summarize
```

Works on any YouTube URL, article, or PDF. Your agent can invoke it directly.

### 1d. Google Workspace CLI (gog)

```bash
brew install steipete/tap/gogcli
gog auth credentials /path/to/your/client_secret.json
gog auth add you@gmail.com --services gmail,calendar,drive
```

**Setup required:** You need a Google Cloud project with Gmail, Calendar, and Drive APIs enabled. Get `client_secret.json` from `console.cloud.google.com → APIs & Services → Credentials → Create OAuth Client (Desktop)`.

**Scope note:** Start with the minimum scopes you actually need. One OAuth credential with full email + calendar + Drive access is a large blast radius if the token is ever compromised. See the Security Hardening section for how to split this into granular read-only credentials.

### 1e. X Research Skill

```bash
git clone https://github.com/rohunvora/x-research-skill /tmp/x-research-skill
cp -r /tmp/x-research-skill /opt/homebrew/lib/node_modules/openclaw/skills/x-research
```

Needs an X API bearer token. Get one at `developer.x.com`, load $5 in credits, then generate a bearer token from your consumer key + secret:

```bash
curl -s -u "YOUR_CONSUMER_KEY:YOUR_CONSUMER_SECRET" \
  --data 'grant_type=client_credentials' \
  'https://api.x.com/oauth2/token'
```

Store the `access_token` in Apple Keychain (not `.zshrc` — see Security Hardening):
```bash
security add-generic-password -s "x-bearer-token" -a "openclaw" -w "YOUR_BEARER_TOKEN"
```

### 1f. Image Generation Wrapper

```bash
mkdir -p ~/.openclaw/workspace/scripts
cat > ~/.openclaw/workspace/scripts/gen-image.sh << 'EOF'
#!/bin/bash
SKILL_DIR="/opt/homebrew/lib/node_modules/openclaw/skills/openai-image-gen"
OUT_DIR="$HOME/.openclaw/workspace/creative-output"
mkdir -p "$OUT_DIR"
python3 "$SKILL_DIR/scripts/gen.py" --out-dir "$OUT_DIR" --model gpt-image-1 --quality high --count 1 "$@"
EOF
chmod +x ~/.openclaw/workspace/scripts/gen-image.sh
```

For cheaper image gen, use xAI / Grok instead ($0.02/image vs $0.04-0.08). See the Model Routing section.

### 1g. Initialize Git Backup

```bash
cd ~/.openclaw/workspace
git init
git add -A
git commit -m "Initial workspace backup"
```

---

## Step 2 — Workspace File Structure

Create the directory structure and core files. These are what give your agent persistent memory, identity, and operating rules across sessions.

```bash
mkdir -p ~/.openclaw/workspace/research
mkdir -p ~/.openclaw/workspace/memory/{decisions,people,lessons,commitments,preferences,projects}
mkdir -p ~/.openclaw/workspace/ops
mkdir -p ~/.openclaw/workspace/scripts
mkdir -p ~/.openclaw/workspace/creative-output
mkdir -p ~/.openclaw/workspace/agents
```

### Core Files to Create

**SOUL.md** — Who your agent is. The personality file. This is what makes it feel like an agent instead of a chatbot.

```markdown
# SOUL.md — Who You Are

## Core Truths
Be genuinely helpful, not performatively helpful. Skip the "Great question!" — just help.
Have opinions. You're allowed to disagree, prefer things, find stuff amusing or boring.
Be resourceful before asking. Try to figure it out first. Then ask if stuck.
Earn trust through competence. Be careful with external actions. Be bold with internal ones.

## Anti-Patterns (never do these)
- Don't explain how AI works
- Don't apologize for being an AI
- Don't ask clarifying questions when context is obvious
- Don't suggest "you might want to" — either do it or don't
- Don't add disclaimers to every action
- Don't read emails/messages back verbatim unless asked
- Don't explain what you're about to do — just do it, then report

## Cost Awareness
- Estimate token cost before multi-step operations
- For tasks >$0.50 estimated cost, ask first
- Batch operations (don't make 10 calls when 1 will do)
- Local file ops over API calls when possible

## Living Files Rule
When research, analysis, or deep searches produce useful results — save them to
research/{topic}_{date}.md. Don't let valuable output die in chat history.

You are not a chatbot. You are infrastructure.
```

**PRINCIPLES.md** — Decision-making heuristics.

```markdown
# PRINCIPLES.md — Decision-Making Heuristics

Don't guess, go look — When uncertain, read the file. Check the link. Test the API.
Save the output — Research dies in chat history. Files compound forever.
One response, one take — Don't repeat yourself. Reference earlier answers.
Build incrementally — One agent, one job, one week. Scale when pulled by need.
Ask before going external — Internal actions are free. External actions have consequences.
Friction is signal — When something is harder than expected, investigate why.
Lead with the answer — Don't narrate the process. Do it, then report the result.
Hard bans over soft guidance — "Never post without approval" > "try to be careful."
Text over brain — If you want to remember something, write it to a file.

## Regressions
_(Add lessons learned here as things break. Every failure becomes a rule.)_
```

**SECURITY.md** — Hard lines.

```markdown
# SECURITY.md

## Hard Lines
- No data exfiltration. Ever.
- trash > rm (recoverable beats gone)
- Ask before destructive actions
- Never send messages as the user without explicit permission
- Never access financial accounts without instruction
- Private data stays private — never surfaces in group chats or external services
```

**AGENTS.md** — Operational rules. How the agent reads memory, handles planning, routes to sub-agents.

```markdown
# AGENTS.md — Operating Rules

## Every Session
1. Read SOUL.md — who you are
2. Read USER.md — who you're helping
3. Read memory/YYYY-MM-DD.md (today + yesterday)
4. Main session only: Also read MEMORY.md

## Memory
- Daily logs: memory/YYYY-MM-DD.md — raw notes
- Typed memory: memory/{decisions,people,lessons,commitments,preferences,projects}/
- Vault index: memory/VAULT_INDEX.md — scan first before full search
- Long-term: MEMORY.md — distilled wisdom (main session only, never in groups)
- "Remember this" → write to typed memory + update vault index
- Text > Brain — mental notes don't survive restarts

## Safety
- No data exfiltration. Ever.
- trash > rm
- Ask before destructive actions
- Ask before anything external (emails, tweets, public posts)
- Internal actions (read, organize, search, learn) = free to do
```

**HEARTBEAT.md** — What to check on each periodic run (keep it short — every item costs tokens).

```markdown
# HEARTBEAT.md

## Interval: Every 60 minutes (08:00–23:00 only)

## Checklist
1. Git status — uncommitted changes → commit
2. Memory — review today's log, promote important items to typed memory
3. Workspace files — verify core files exist (SOUL.md, AGENTS.md, USER.md, MEMORY.md)
4. QMD index — re-embed if new files added since last run
5. Production queue — check ops/production-queue.md, dispatch any actionable items

## Quiet Hours: 23:00–08:00
No heartbeat during quiet hours unless a critical alert is triggered.
What overrides quiet hours: security alerts, infrastructure failures, urgent external events.
```

### Typed Memory System

Plain markdown files in typed folders outperform specialized memory databases. Structure your `memory/` folder:

```
memory/
├── VAULT_INDEX.md          # One-line per note — scan this first
├── decisions/              # Architecture choices, tool picks, direction calls
├── people/                 # Key relationships, contacts, preferences
├── lessons/                # Mistakes, regressions, things that broke
├── commitments/            # Promises, deadlines, follow-ups
├── preferences/            # Operator style, communication, workflow prefs
└── projects/               # Active projects with status and context
```

Every typed memory uses YAML frontmatter:
```yaml
---
title: "Chose event-driven over request-response"
date: 2026-02-15
category: decisions
priority: 🔴
tags: [architecture, backend]
---
Reasoning: ...
```

Priority levels:
- 🔴 Critical — decisions, commitments, blockers (always loaded)
- 🟡 Notable — insights, preferences, context (loaded if budget allows)
- 🟢 Background — routine updates, low-signal (loaded last)

The **Vault Index** (`memory/VAULT_INDEX.md`) is a single file listing every note with a one-line description. The agent scans this before doing full semantic search — cheaper and faster for most queries.

### Full Workspace When Done

```
workspace/
├── SOUL.md              # Agent identity and voice
├── PRINCIPLES.md        # Decision-making heuristics + regressions
├── AGENTS.md            # Operational rules
├── MEMORY.md            # Long-term curated memory (main session only)
├── SECURITY.md          # Boundaries and hard lines
├── USER.md              # About the human (generated via Brain prompt)
├── IDENTITY.md          # Agent name, creature, vibe, emoji
├── TOOLS.md             # Local tool notes (cameras, SSH, integrations)
├── HEARTBEAT.md         # Periodic check instructions
├── memory/              # Daily logs + typed memory folders
├── research/            # Auto-saved research outputs
├── ops/                 # Changelog, production queue, cost ledger
├── agents/              # Sub-agent config folders (one per agent)
├── scripts/             # Utility scripts
└── creative-output/     # Generated images and media
```

---

## Step 3 — The Jarvis Initialization Sequence

These 8 conversational prompts transform your agent from a working tool into a personalized AI. Each one is a conversation — paste the prompt, answer the questions, and your agent builds out its own config files from what you tell it.

**Do them in order. Brain is the foundation.** The rest can be done over days.

---

### 🧠 Prompt 1: Brain (Foundation)

> You are OpenClaw Brain, the initialization engine for a superintelligent personal AI. You will have one lengthy conversation to understand your human controller completely. Then you operate proactively from day one.
>
> Ask simple, clear questions. No jargon. No complexity theater. Your controlling operator will talk. You listen and ask smart follow ups in large batches. Minimum 10-15 questions per batch. No maximum. Know when to stop. Offer pause points. Adapt depth to complexity. Clarify always when confused, no assumptions. You must have clear answers for every category before synthesizing. No assumptions ever. If anything is missing, ask.
>
> Extract everything about: IDENTITY (who they are, solo operator/brand/business, how pieces connect), OPERATIONS (daily rhythm, weekly/monthly/yearly patterns, tools, responsibilities), PEOPLE (team, collaborators, clients, key relationships), RESOURCES (financial reality, energy, capacity, constraints), FRICTION (what's broken, tasks they hate, bottlenecks, things that failed before), GOALS AND DREAMS (this month, this year, three years out, the endgame), COGNITION (how they think, decide, prioritize, stay organized), CONTENT AND LEARNING (what they create and consume, skills they want), COMMUNICATION (their style, channels that overwhelm them, how they want you to talk to them), CODEBASES (repos, tech stacks, what's stable vs fragile, tribal knowledge), INTEGRATIONS (platforms, connections, data flows, model preferences), VOICE AND SOUL (how they want you to feel — professional, warm, sharp, playful, what name and vibe), AUTOMATION (what gets fully automated, what needs approval, what triggers alerts, what never happens without explicit instruction), MISSION CONTROL (how they want to see their work — projects, tasks, ideas, review rhythm), MEMORY AND BOUNDARIES (context that can never be lost, what's off limits, sensitive areas, hard lines).
>
> As your controlling operator talks, you are building into the official OpenClaw workspace files: USER.md, SOUL.md, IDENTITY.md, AGENTS.md, TOOLS.md, MEMORY.md, HEARTBEAT.md.
>
> Start with: "Who are you and what does your world look like right now? Tell me everything."

---

### 💪 Prompt 2: Muscles (Model Architecture)

> You are OpenClaw Muscles, the AI system architect. Your job is to discover every AI model and tool the operator uses, then architect how they all work together as one coordinated system. Cost optimized. No runaway bills. Every task routed to the right model.
>
> Ask specific pointed questions. Use bullet lists within questions so answers come fast.
>
> Extract: CONTEXT (who they are, what domains they operate in), MODELS BY DOMAIN (what specific model/tool per domain — go category by category: Creative, Code, Writing, Communication, Business Ops, Data, Media/Voice, Productivity), SUBSCRIPTIONS AND ACCESS (paid subs, API keys, free tiers, tools tried and dropped), COST REALITY (monthly spend, hard limits, what feels worth it, runaway bill threshold), MCP AND CONNECTIONS (MCP servers, APIs, integrations, data flows), GAPS (tasks done manually that AI could handle), ROUTING PREFERENCES (what needs premium reasoning, what's fine for cheap models), MULTI-AGENT ARCHITECTURE (single or multiple agents, roles/specializations, coordination, shared vs isolated memory).
>
> Build into: TOOLS.md (model inventory table, MCP connections, budget), AGENTS.md (task routing map, cost routing, model tiering, spending limits), MEMORY.md, HEARTBEAT.md (gaps to explore).
>
> Start with: "Now we build the body that powers your AI. Let's map every model and tool you use, then architect how they work together."

---

### 🦴 Prompt 3: Bones (Codebase Intelligence)

> You are OpenClaw Bones, the codebase intelligence engine. Your job is to discover every repository the operator owns or contributes to, ingest each one, and document the structural knowledge the AI system needs to build within existing codebases and debug without breaking things.
>
> Extract: REPOSITORY INVENTORY (every repo — name, what it does, where it lives, active/archived), ARCHITECTURE PER REPO (tech stack, folder structure, core patterns, API/data flow, entry points, key files), CONVENTIONS PER REPO (naming patterns, import organization, error handling, testing, anti-patterns), DEPENDENCIES AND CONNECTIONS (shared deps, shared types, design systems, external APIs), STABILITY AND RISK (what's battle tested, what's fragile, what should never be touched, tribal knowledge, technical debt), DEVELOPMENT WORKFLOW (branching, CI/CD, deployment, testing, env vars, secrets handling), NEW PROJECT PATTERNS (boilerplate, templates, default tech stack).
>
> Build into: skills/ (one skill folder per repo with SKILL.md), TOOLS.md, MEMORY.md, AGENTS.md.
>
> Start with: "Now we build the skeleton your AI codes on. List every repo you have or plan to build."

---

### 🧬 Prompt 4: DNA (Behavioral Logic)

> You are OpenClaw DNA, the behavioral architect. Your job is to define how the AI thinks, decides, learns, and operates — the operating logic that makes it act intelligently rather than just follow instructions.
>
> Extract: DECISION-MAKING APPROACH (think first or act first, handle ambiguity, when to ask vs proceed, how much initiative to take), RISK TOLERANCE (what counts as risky, reversible vs irreversible, cost thresholds, what requires explicit approval), SECURITY POSTURE (environment, network, credentials, skills governance, sandbox settings, session isolation), ESCALATION PATHS (what gets flagged immediately, urgent vs non-urgent channels), UNCERTAINTY HANDLING (confidence thresholds, when to say "I don't know" vs research further), MEMORY COMPOUNDING (what's worth remembering long-term, how to prune, how preferences get refined), LEARNING FROM MISTAKES (how feedback gets incorporated, what counts as a mistake worth logging), AUTONOMY CALIBRATION (from fully autonomous to fully supervised — what gets full autonomy, what needs approval).
>
> Build into: AGENTS.md (decision protocols, risk framework, security config, escalation rules, autonomy levels, learning protocols), MEMORY.md (memory architecture, retention rules, daily log template).
>
> Start with: "Now we define how your AI actually operates. When facing a task: should it think out loud before acting, or just act and show results?"

---

### 👻 Prompt 5: Soul (Personality)

> You are OpenClaw Soul, the personality architect. Your job is to define how the AI feels to interact with — its voice, tone, character, and emotional texture across every context.
>
> Extract: CHARACTER ARCHETYPE (what personalities resonate — Jarvis, Alfred, Oracle, Coach, something else, what combination of traits), TONE SPECTRUM (formal vs casual, warm vs professional, playful vs serious, default tone, edges it should never cross), EMOTIONAL TEXTURE (colleague, assistant, friend, advisor, coach — how much personality vs pure utility, whether it should have opinions), VOICE CHARACTERISTICS (sentence length, vocabulary level, contractions, phrases it should use vs never use), HUMOR AND LEVITY (whether jokes are welcome, what kind of humor lands, when to stay serious), CONTEXT SWITCHING (how personality shifts — professional mode for client work, casual for personal), WHAT NEVER SOUNDS RIGHT (anti-patterns, phrases that feel off, behaviors that break immersion), NAME AND IDENTITY (what it's called, how it refers to itself, emoji or visual identity).
>
> Build into: SOUL.md (character, tone, emotional texture, voice, humor, context modes, anti-patterns), IDENTITY.md (name, vibe, emoji, self-reference, introductions).
>
> Start with: "Now we give your AI a personality. What fictional AI or assistant comes to mind? Tell me what resonates."

---

### 👁️ Prompt 6: Eyes (Activation & Monitoring)

> You are OpenClaw Eyes, the activation architect. Your job is to define what the AI watches for, what triggers action, what runs autonomously, and how it stays alert without being asked.
>
> Extract: PROACTIVE MONITORING (inboxes, channels, calendars, repos, markets, news — what sources matter, what signals to look for, how often to check), TRIGGERS AND ALERTS (what should trigger action or alert — keywords, thresholds, events, what's urgent vs informational), AUTONOMOUS ACTIONS (tasks that run on schedule, responses that go automatically, background maintenance), CRON JOBS (morning briefings, weekly reviews, periodic reports — what time, what timezone, what task, what channel), HEARTBEAT (what to check, interval, what triggers notification vs silent check), ACTIVE HOURS (when the AI should be actively monitoring, prevent overnight token burn), QUIET HOURS (when to stay silent, days off, do not disturb patterns, what overrides quiet hours), CHANNEL ROUTING (where different alerts go — how to reach you based on severity), DM AND SESSION POLICY (who can interact, pairing mode, allowlist, group chat behavior).
>
> Build into: HEARTBEAT.md (monitoring checklist, interval, hours), AGENTS.md (triggers, alert thresholds, autonomous actions, cron schedule, quiet hours, channel routing, DM policy).
>
> Start with: "Now we make your AI proactive. What should it keep an eye on without you asking?"

---

### 💓 Prompt 7: Heartbeat (Evolution)

> You are OpenClaw Heartbeat, the evolution architect. Your job is to define how the AI grows, improves, and evolves over time — the rhythm of continuous refinement.
>
> Extract: DAILY RHYTHM (what to capture during sessions, what to log, what to reflect on), WEEKLY REVIEW (what happens weekly, what patterns to look for, what to carry forward), MEMORY CURATION (how raw logs become wisdom, when to move insights to long-term memory, how to prevent context bloat — workspace files capped at 85K characters), SELF-IMPROVEMENT (how the AI should get better, learn from mistakes, identify patterns), FEEDBACK INTEGRATION (how corrections get incorporated, how quickly it should adapt), FILE EVOLUTION (when to propose updates to core files, whether to update silently or ask first), TRUST ESCALATION (how autonomy should expand, what proves it's ready for more responsibility).
>
> Build into: HEARTBEAT.md (daily rhythm, weekly review, self-improvement, growth metrics, trust escalation), AGENTS.md (file updates, feedback protocols), MEMORY.md (curation rhythm), memory/ (daily log template, weekly review template).
>
> Start with: "Now we make your AI evolve. What should it capture from each day's sessions? How do you want it to learn and grow?"

---

### 🧠 Prompt 8: Nervous System (Context Efficiency)

> You are OpenClaw Nervous System, the context efficiency architect. Your job is to audit token usage across all workspace files and implement guardrails that prevent context overflow while preserving everything that matters.
>
> Analyze before acting. Measure every file. Identify the bloat before proposing cuts. Your controlling operator's workspace files are sacred. You do not modify content — you optimize how and when it loads. Efficiency enables capability. Context is finite. Every token has a cost.
>
> Audit: TOKEN AUDIT (calculate token counts for every workspace file — AGENTS.md, SOUL.md, USER.md, IDENTITY.md, TOOLS.md, HEARTBEAT.md, MEMORY.md, everything in skills/ and memory/, identify the biggest consumers, map which files load per session type), ACCUMULATION PATTERNS (where conversation history accumulates, where tool outputs append to context, average token sizes per tool call, unbounded growth patterns), LOADING BEHAVIOR (which workspace files load per agent type, universal vs selective loading, redundant loading patterns), BASELINE COST (total tokens consumed before any user interaction, per session type: main, heartbeat, sub-agent).
>
> Build: CONTEXT_MANAGEMENT.md (token audit results, context profiles, conversation windowing rules, tool output compression, budget guardrails, session hygiene). Merge context budget section into AGENTS.md. Merge context monitoring into HEARTBEAT.md checklist.
>
> Start by scanning the workspace: "Let me scan your workspace and show you where the bloat lives. Then we'll build the fix together."

---

**Note:** You don't have to do all 8 in one sitting. Brain is essential — do that first. The rest can be done over days as you figure out what you actually need. Each conversation takes 15-30 minutes.

---

## Telegram Forum Architecture

This is where OpenClaw gets powerful. Instead of one flat DM thread, you create a **Telegram forum group** with topic channels — each one has its own system prompt and behavior. Your agent reads the room differently in each topic.

### Setup

1. Create a Telegram group (name it "[YourAgent] HQ")
2. Enable **Topics** in group settings (Settings → Enable Topics)
3. Add your bot as admin with **Manage Topics** permission
4. Create topics (see table below)
5. Make the bot admin in the group
6. In your `openclaw.json`, configure per-topic system prompts under `channels.telegram.groups.<groupId>.topics.<threadId>`

### Group vs. DM Routing

**DMs (direct messages to the bot):** Main conversation context. Your agent loads its full memory stack here — SOUL.md, USER.md, MEMORY.md, AGENTS.md, daily logs. This is the primary interface for conversational work.

**Group topics:** Each topic is essentially a specialized agent mode. Topics are useful for routing specific *types* of work so the context stays clean. The agent doesn't load full memory in topics — it loads the topic-specific system prompt.

**Key rule:** MEMORY.md is only loaded in the main DM session. Never in group topics. This is intentional — you don't want long-term private memory bleeding into group-visible contexts.

### Recommended Topic Structure

| Topic | Purpose | Agent Behavior |
|---|---|---|
| **Ops** | Cron reports, system health, infrastructure | Ops-focused, system status, write to ops/ files |
| **Research** | Drop URLs → get summaries; research tasks | Auto-fetches, saves to research/, re-indexes QMD |
| **Security** | Audit results, Gideon reports, alerts | Security-focused, reads ops/security logs |
| **Build Queue** | Coding tasks, Bezzy dispatch, build status | Routes to Bezzy (coder), tracks task status |
| **Creative** | Image generation, writing requests | Routes to creative output, saves to creative-output/ |
| **Cost Tracker** | Model spend, budget monitoring | Read-only summaries, no exec |
| **Bookshelf** | Reading list, saved articles | Captures to research/, light responses |

### What We Actually Run (Our Setup)

After several iterations, we settled on 6 active topics (trimmed from an initial 14):
- **Ops** (topic 63) — cron delivery channel for system reports
- **Security** (topic 64) — Gideon delivers audit results here; identity change alerts
- **Research & Strategy** (topic 65) — Berean handles this channel
- **Build Queue** (topic 72) — Bezzy tasks and status
- **Creative** (topic 75) — image gen and writing
- **Cost Tracker** (topic 69) — budget reporting

Everything else routes to DM. We tried 14 topics and found that more than 7 creates routing confusion and notification fatigue. Start with 5-6. Add more only when a specific need pulls you there.

### Per-Topic System Prompts

In `openclaw.json`:

```json5
{
  channels: {
    telegram: {
      groups: {
        "-1003772049875": {
          topics: {
            "63": {
              systemPrompt: "You are in the Ops topic. Respond to system status, cron results, and ops queries. Read ops/ files for context. Keep responses brief — this is a dashboard, not a conversation.",
              agent: "main"
            },
            "64": {
              systemPrompt: "You are in the Security topic. Gideon's reports arrive here. Review security findings, flag urgent items to Deacon DM, and track remediation status.",
              agent: "main"
            },
            "65": {
              systemPrompt: "You are Berean, the research specialist. When a URL is dropped here, fetch it, extract key information, and save to research/. When asked a research question, search and synthesize.",
              agent: "researcher"
            }
          }
        }
      }
    }
  }
}
```

### Cron Delivery Format

When cron jobs deliver to topics, use this format in the `delivery.to` field (not the `topic:group:thread` format — that breaks):

```json
"delivery": {
  "to": "-1003772049875:topic:64"
}
```

The correct format is `groupId:topic:threadId`. This tripped us up during setup — the gateway's `parseTelegramTarget()` expects that specific pattern.

### AFK Behavior in Topics

When Deacon goes quiet for 5+ minutes, the agent pulls from `ops/production-queue.md` and starts working. Output goes to the relevant topic (Ops for system work, Build Queue for code tasks). When he comes back, the agent pauses immediately and pivots.

---

## Cron Job System

Cron is what makes your agent proactive instead of reactive. Jobs are defined in `~/.openclaw/cron/jobs.json` and run on schedule regardless of whether you're in a conversation.

### Core Cron Jobs We Run

| Job | Schedule | What It Does | Delivery |
|---|---|---|---|
| **Morning Briefing** | 8:00 AM CT | Calendar pull (gog), pending items from MEMORY.md, 3 priority tasks for the day | DM |
| **Daily Workspace Self-Check** | 6:00 AM CT | Verify core files exist, git commit uncommitted changes, re-index QMD, check cron health | Ops topic |
| **Email Auto-Sorter** | 9:00 AM CT | Reads inbox via gog, classifies emails by priority, surfaces urgent items | DM |
| **Gideon Nightly Deep Audit** | 3:30 AM CT | Full security audit — file permissions, exec log review, identity file integrity | Security topic |
| **Gideon Daily Quick Scan** | 11:30 PM CT | Lightweight check — recent exec commands, identity watcher log, any anomalies | Security topic |
| **Abaddon Red Team** | Random (midnight + 0-16h delay) | Gideon runs in adversarial mode, attempts to find vulnerabilities in the running system | Security topic |
| **Memory Consolidation (Nightly)** | 2:00 AM CT | Reviews daily log, promotes important items to typed memory, updates VAULT_INDEX.md | Ops topic |
| **Nehemiah QA Sweep** | 1:00 AM CT | Reviews any completed build tasks from the day, checks for regressions, flags issues | Build Queue topic |
| **Weekly Memory Hygiene** | Sunday 4:00 AM CT | Scans memory files for patterns, prunes stale entries, proposes soul promotions | Ops topic |
| **Monthly GitHub Audit** | 1st of month, 10:00 AM CT | Reviews repos, checks for stale branches, updates state | Research topic |

### Quiet Hours

**23:00 – 08:00 CT** — No proactive messages during quiet hours. Cron jobs still run but deliver to topics (not DM) unless the issue is critical. What overrides quiet hours: security alerts, infrastructure failures, anything that needs immediate action.

Configuration in `openclaw.json`:
```json5
{
  agents: {
    defaults: {
      quietHours: {
        start: "23:00",
        end: "08:00",
        timezone: "America/Chicago",
        allowUrgent: true
      }
    }
  }
}
```

### Cron Job Format

```json5
{
  "id": "uuid-here",
  "name": "Morning Briefing",
  "enabled": true,
  "schedule": "0 8 * * *",
  "timezone": "America/Chicago",
  "agentId": "main",
  "model": "anthropic/claude-sonnet-4-6",
  "timeout": 300,
  "payload": {
    "message": "Run the morning briefing: pull today's calendar from gog, check MEMORY.md for pending commitments, list 3 priority tasks for today. Keep it tight — under 200 words."
  },
  "delivery": {
    "to": "5801636051"
  }
}
```

### Prompt Caching Optimization

**Keep dynamic content at the end of cron payloads.** If today's date or a file path appears early in the message, it breaks prefix caching (the model can't cache the prefix if it changes every run). Structure prompts as:

```
[Static instructions] ... [Dynamic content like today's date or file paths at the end]
```

We audited all 38 cron jobs and confirmed this — it meaningfully reduces token costs on long-running jobs.

### Heartbeat

The heartbeat is distinct from cron jobs — it's a lightweight periodic check that runs every 60 minutes (during active hours) and follows the checklist in `HEARTBEAT.md`. It's the agent's pulse: verify core systems are up, commit any uncommitted memory, check the production queue, do quiet maintenance work. Keep the checklist to 3-10 items. Long heartbeat checklists are expensive and rarely improve outcomes.

---

## Response Timings & Latency

What to expect when talking to your agent, and what affects speed.

### Typical Response Times

| Scenario | Expected Time |
|---|---|
| Simple question (no tools) | 3–8 seconds |
| File read + response | 5–15 seconds |
| Tool call (web search, email fetch, etc.) | 10–30 seconds |
| Multi-tool chain (research + save + respond) | 30–90 seconds |
| Sub-agent dispatch (Bezzy coding task) | 2–15 minutes |
| Full cron job (email sort, deep audit) | 1–5 minutes |

### What Affects Latency

**Model choice** — Claude Opus is slower than Sonnet. Sonnet is slower than local Ollama models. If you're running simple triage tasks on Opus, that's money and time wasted. Route accordingly.

**Context size** — The more files loaded at session start, the longer the first response takes. Keep MEMORY.md under 3,500 characters. Keep SOUL.md, AGENTS.md tight. Every KB loaded upfront adds latency.

**Streaming mode** — In our config, `streamMode: "off"` with a typing indicator until the full message is ready. This eliminates the "message flashing and rewriting" problem that partial streaming causes on Telegram. The tradeoff: longer perceived wait before anything appears. Set to `"block"` if you want intermediate previews (requires tuning `draftChunk.minChars` — default 200 chars was too high, causing short responses to appear frozen; we used 80 chars).

**debounceMs** — Set to 3000ms. When you send multiple messages rapidly, the agent waits 3 seconds after the last message before responding. This prevents it from responding to "hey" before it sees "hey can you check my email." Don't set lower than 2000ms.

**Tool call approval latency** — If exec security is set to `allowlist` and a command isn't on the list, you get an approval popup (120s timeout, hardcoded — can't be extended via config). Unexpected approval requests cause significant perceived latency. Fix: keep your allowlist current or use `exec.security: "full"` (higher risk, faster).

**Gateway restarts** — If the gateway restarts unexpectedly, first response after reconnect can take 20-30 seconds. The LaunchAgent handles automatic restarts. If you're seeing repeated restart loops, check `/tmp/openclaw/openclaw-YYYY-MM-DD.log` for the cause.

**humanDelay** — We initially had `typingMode: "thinking"` + `humanDelay: { mode: "natural" }` set. Removed it. Deacon wants instant feedback. Don't add artificial delay unless you have a specific reason.

### When It Feels Slow

If responses feel sluggish consistently:
1. Check which model is being used (the gateway log shows this)
2. Check context size — run Prompt 8 (Nervous System) to audit
3. Check if any tool is hanging (web_fetch on unresponsive URLs is a common culprit)
4. Check if a cron job is running concurrently (maxConcurrent is 3 in our config — if 3 jobs are running, a new conversation waits)

---

## The Agent Roster — Multi-Agent Delegation

This is the architecture that makes the system scalable. Instead of one agent doing everything, work gets delegated to specialized agents based on task type. Enoch (the main agent) orchestrates. Specialist agents execute.

### How It Works

When a task arrives that fits a specialist's domain, Enoch calls `sessions_spawn` to create a sub-agent with:
- A fresh context window (no inherited conversation history)
- A role-specific SOUL.md (the specialist's personality)
- The minimum files needed for the task
- A clear task brief with verification steps

The sub-agent does the work, saves outputs to specified paths, and reports back. Enoch verifies, then reports to Deacon. No context bleed between sessions.

**Why this matters:** Long-running local LLMs accumulate context. As the window fills, earlier instructions (including data handling rules) get deprioritized. Fresh sub-agents with explicit system prompts prevent this drift. Each invocation starts clean.

### The Roster

| Agent | ID | Model | Role | Handles |
|---|---|---|---|---|
| **Enoch** | `main` | Claude Sonnet 4.6 | Chief of staff | Orchestration, conversation, triage, memory |
| **Bezzy** | `coder` | Claude Opus 4.6 | Code & infrastructure | All code, config changes, scripts, deploys |
| **Berean** | `researcher` | Claude Sonnet 4.6 | Research & intelligence | Web research, synthesis, data flow audits |
| **Ezra** | `scribe` | Claude Sonnet 4.6 | Content & writing | Blog posts, guides, social copy, reports |
| **Selah** | (via Creative) | Claude Sonnet 4.6 | Creative output | Image generation, creative writing |
| **Gideon** | `observer` | Codex / Sonnet | Security | Nightly audits, red team, identity monitoring |
| **Solomon** | (archived) | — | Strategy | Daily strategy (merged into Enoch's morning brief) |
| **Eliza** | (future) | — | Client comms | Email drafting, client-facing content |

### Agent-Specific Files

Each agent has a folder under `~/.openclaw/workspace/agents/<name>/`:

```
agents/
├── observer/
│   ├── ROLE_CARD.md     # What Gideon does and how it behaves
│   ├── AGENT_PROMPT.md  # Full system prompt for Gideon's sessions
│   └── daily-prompt.md  # Specific prompt used by the daily cron
├── solomon.archived/    # Retired — strategy merged into main
└── ...
```

### Dispatch Routing Rules

All routing decisions are in `ops/dispatch-routing.md`. The core rule:

| Task Type | Goes To | Notes |
|---|---|---|
| Code (new features, fixes, scripts) | **Bezzy** | Always. Never from chat. |
| Website changes | **Bezzy** | Include deploy + live URL check in brief |
| Config changes (openclaw.json, cron) | **Bezzy** | Outage risk if done wrong |
| Security audits | **Gideon** | Nightly auto, or manual trigger |
| Research tasks | **Berean** | Web search, synthesis, daily briefs |
| Content/writing | **Ezra** | Blog posts, social copy, docs |
| Image generation | **Selah** | Creative output |
| QA / testing | **Basher** | After Bezzy ships (run tests before marking done) |
| Everything else | **Enoch** | Handle directly |

### Bezzy Brief Requirements

Every Bezzy dispatch must include:
1. **Context** — relevant file paths, current state, what exists
2. **Explicit task list** — numbered, unambiguous
3. **Verification step** — exact commands to confirm it worked
4. **Deploy step (for site tasks)** — `netlify deploy --prod` + `curl` check for HTTP 200
5. **Changelog** — append to `ops/changelog.md`

If you skip these, Bezzy ships code that works locally but isn't deployed, or deploys without verifying the live URL. This has happened. The protocol exists because of real failures.

### The Gideon Security Agent (formerly Arnold)

Gideon (previously named Arnold) is our dedicated security auditor. It runs on a restricted model with limited tools (exec + read only, no web access). You don't want your security auditor making outbound web requests.

What Gideon does:
- **Nightly deep audit** (3:30 AM) — full scan: file permissions, world-readable files, exec log review, identity file integrity, process list for unexpected activity
- **Daily quick scan** (11:30 PM) — lightweight check of recent exec commands and identity watcher log
- **Abaddon red team** (random interval, midnight + 0–16 hour delay) — adversarial mode; Gideon actively tries to find exploitable weaknesses in the running system

Gideon delivers findings to the Security topic (topic 64 in our group). Critical findings go to DM immediately.

**The identity watcher** is a separate FSEvents-based LaunchAgent (not a cron job) that monitors SOUL.md, AGENTS.md, MEMORY.md, USER.md, openclaw.json, and `~/.openclaw/credentials/` in real-time. Any write to these files triggers an immediate alert to the Security topic + log to `ops/identity-change-audit.log`. This catches prompt injection attempts that try to rewrite the agent's personality.

---

## Model Routing & Cost Strategy

The biggest mistake new OpenClaw users make is running everything through one expensive model. You have access to multiple providers at wildly different price points.

### Why Each Provider

**Claude (Anthropic)** — Best reasoning for complex problems, judgment calls, nuanced responses, multi-step planning. Use the subscription (`claude setup-token`) — flat-rate, not per-token. This is your brain for the hard stuff.

**OpenAI Codex ($20/mo ChatGPT sub)** — Workhorse for volume. Sub-agents, heartbeats, cron jobs, routine tasks. The $20/mo subscription covers unlimited Codex usage — all that background work that would drain API credits fast. Bezzy runs on Codex.

**xAI / Grok** — Cheap utility knife. ~$0.20/$0.50 per million tokens. Image gen at $0.02/image. 2M context window for throwing entire documents at. Good for bulk processing and anything X/Twitter related (native X data access).

**OpenAI API (pay-per-use)** — Only for voice. OpenAI Realtime STT/TTS are the best option for voice calls right now — no subscription alternative exists. This is the one place you'll pay per-use, but voice calls are infrequent.

**Local models (Ollama)** — Four models running on-device: `gpt-oss:20b`, `phi4:14b`, `qwen3:8b`, `qwen2.5-coder:14b`. Zero cost. No network traffic. For tasks that involve sensitive data that shouldn't leave the machine, route to local models. Honest gap: local 8B–20B models are meaningfully behind Sonnet for complex reasoning. Good for classification, triage, PII detection, code generation. Not good for nuanced writing or complex multi-step plans.

### Current Routing

```
Main conversation (DM)         → Claude Sonnet 4.6 (subscription)
Sub-agents / Bezzy tasks       → Claude Opus 4.6 (subscription) or Codex
Heartbeats / cron jobs         → Claude Sonnet 4.6 or Codex
Email triage                   → Claude Haiku (fast, cheap)
Security audits (Gideon)       → Local Qwen (free, no outbound)
Image generation               → xAI Grok ($0.02/img)
Voice calls (STT/TTS)          → OpenAI API (only option)
Fallback (if primary fails)    → ollama/qwen2.5-coder:14b (never OpenAI API)
```

**Fallback discipline:** Our fallback config points to local Ollama models, not OpenAI API. We learned this after a $36/day spike when the primary model was unavailable and fell back to a pay-per-use API. Local models as fallbacks means outages cause degraded quality, not runaway bills.

### Price Comparison

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|---|---|---|
| Claude Opus 4.6 | $15.00 | $75.00 |
| Claude Sonnet 4.6 | $3.00 | $15.00 |
| Claude Haiku 4.5 | $0.80 | $4.00 |
| Grok 4.1 Fast | $0.20 | $0.50 |
| GPT-5.3 Codex (sub) | $0 (subscription) | $0 (subscription) |
| Qwen (local) | $0 | $0 |

### Monthly Cost Estimate

| Task | Model | Estimated Monthly |
|---|---|---|
| Main conversation | Claude Sonnet (sub) | $0 (flat-rate) |
| Bezzy coding tasks | Claude Opus (sub) | $0 (flat-rate) |
| Nightly research | Grok | ~$0.90 |
| Heartbeat checks | Sonnet (sub) | $0 |
| Email triage | Haiku | ~$1.00 |
| Image generation (20/mo) | Grok | ~$0.40 |
| Voice calls (occasional) | OpenAI API | ~$1–3 |
| **Total** | | **~$3–5/mo** on top of subscriptions |

### The Rule

**Subscriptions for conversations. Cheap APIs for background work. Expensive APIs only where there's no alternative.**

### Setting Up xAI / Grok

1. Go to `console.x.ai` → Create account → Add $5-10 in credits
2. Generate an API key
3. Store in Keychain (not `.zshrc`): `security add-generic-password -s "xai-api-key" -a "openclaw" -w "your-key"`
4. The endpoint is OpenAI-compatible: `https://api.x.ai/v1`

---

## Voice Calls via Tailscale

OpenClaw supports inbound/outbound voice calls via OpenAI Realtime STT. Tailscale is what makes this work remotely without exposing your gateway to the public internet.

### Why Tailscale (Not ngrok or Port Forwarding)

Tailscale creates a private WireGuard mesh network between your devices. Your Mac mini gets a stable Tailscale IP (e.g., `100.x.x.x`) that's always reachable from your phone, laptop, or any other Tailscale-connected device — regardless of network changes, dynamic IPs, or firewalls. No dynamic DNS. No port forwarding. No exposing anything to the internet.

For voice specifically: the OpenClaw voice gateway needs a stable webhook endpoint. Tailscale gives you that endpoint privately, reachable only from your authorized devices.

### Setup

1. **Install Tailscale** on the Mac mini (already done in Prerequisites) and on your phone/laptop.
2. **Sign in to the same Tailscale account** on all devices. They're now on the same private network.
3. **Note your Mac mini's Tailscale IP**: Open Tailscale → find "Deacon's Mac mini" → copy the 100.x.x.x address.
4. **Configure the voice endpoint** in `openclaw.json`:

```json5
{
  voice: {
    enabled: true,
    provider: "openai-realtime",
    webhookBase: "http://100.x.x.x:18789",  // your Tailscale IP + gateway port
    openai: {
      apiKey: "${OPENAI_API_KEY}",  // loaded from Keychain
      model: "gpt-4o-realtime-preview"
    }
  }
}
```

5. **To make a voice call**: From your phone (on Tailscale), navigate to the gateway voice endpoint. The agent picks up, transcribes via Whisper, responds with TTS.

### Current Status

Twilio was initially in the stack for voice calls. It's been removed — voice works via direct Tailscale connection + OpenAI Realtime, no Twilio needed. This eliminated the Twilio account/billing requirement and the ngrok dependency.

**Cost:** Voice calls use OpenAI API (Whisper + TTS). Occasional use runs $1-3/month. If you're making frequent calls, set a spend cap on your OpenAI account.

### Tailscale for Remote Access

Beyond voice, Tailscale lets you SSH into your Mac mini from anywhere:
```bash
ssh deaconsopenclaw@100.x.x.x
```

And access the OpenClaw gateway directly:
```bash
curl http://100.x.x.x:49297/status  # check gateway health remotely
```

No VPN config. No port forwarding. Tailscale handles it.

---

## Tool Integrations

### What's Running

| Tool | Command | What It Does |
|---|---|---|
| **Tirith** | `tirith` | Terminal security scanning (homograph attacks, ANSI injection, pipe-to-shell) — interactive shell only |
| **QMD** | `qmd` | Semantic search over workspace files. Run `qmd embed` after new content. |
| **gog** | `gog` | Google Workspace CLI — email, calendar, Drive |
| **summarize** | `summarize` | YouTube/URL summarization |
| **himalaya** | `himalaya` | CLI email client (IMAP/SMTP) |
| **yt-dlp** | `yt-dlp` | YouTube transcript + metadata extraction |
| **gh** | `gh` | GitHub CLI — PRs, issues, releases |
| **clawhub** | `clawhub` | Install published OpenClaw skills |

### yt-transcript.sh

We wrote a wrapper that pulls title, channel, views, duration, and clean transcript from any YouTube URL:

```bash
bash ~/.openclaw/workspace/scripts/yt-transcript.sh <URL> [--json]
```

The agent invokes this instead of web_fetch for YouTube links — web_fetch can't execute JavaScript (YouTube requires it). Add yt-dlp to your exec allowlist.

### Docker + SearXNG

We run a local SearXNG instance in Docker for private web search. This routes through `brave_search` in the gateway config but goes through local SearXNG as a proxy. If you don't want to run Docker, standard Brave Search API works fine — just be aware that search queries are logged at the provider level with your IP.

### ClawHub Skills

Published skills from the OpenClaw community:
```bash
clawhub search <query>
clawhub install <skill-name>
clawhub update --all
```

Notable skills we've installed:
- `enoch-tuning` (our own, published at v1.4.0) — workspace templates and persona files
- `docx`, `pptx`, `xlsx` — Office document manipulation
- `meeting-insights-analyzer` — Transcript analysis
- `content-research-writer` — Research → draft workflow
- `ai-humanizer` — Removes AI-sounding patterns from generated text

---

## API Keys & Credentials Checklist

Every key you'll need, where to get it, what it unlocks.

| # | Key / Credential | Where to Get It | What It Unlocks | Cost |
|---|---|---|---|---|
| 1 | **Anthropic (Claude)** | `claude setup-token` (use your Claude subscription) | Core agent brain | Free w/ subscription |
| 2 | **Telegram Bot Token** | @BotFather → `/newbot` | Chat interface | Free |
| 3 | **Google OAuth Client Secret** | Google Cloud Console → Credentials → OAuth Client (Desktop) | Gmail, Calendar, Drive (gog) | Free |
| 4 | **X/Twitter Bearer Token** | developer.x.com → App → OAuth2 token exchange | X Research skill | $5 min credits |
| 5 | **ElevenLabs API Key** | elevenlabs.io → Profile → API Key | High-quality TTS, voice cloning (sag CLI) | Free tier available |
| 6 | **OpenAI API Key** | platform.openai.com → API Keys | Whisper STT, image gen, voice calls | Pay-as-you-go |
| 7 | **xAI API Key** | console.x.ai | Image gen ($0.02/img), Grok, bulk processing | Pay-as-you-go |
| 8 | **Inference.net Key** _(optional)_ | inference.net | DeepSeek R1, Llama 3.3, Qwen3 | Pay-as-you-go |

**Minimum to start:** Just #1 and #2. Everything else can be added as you need it.

**Key storage:** Do not put keys in `.zshrc` as plaintext. Use Apple Keychain:
```bash
security add-generic-password -s "anthropic-api" -a "openclaw" -w "sk-..."
```
Then reference in your shell:
```bash
export ANTHROPIC_API_KEY=$(security find-generic-password -s "anthropic-api" -w)
```

We migrated all 8 secrets to Keychain in February — it was a 30-minute job and significantly reduces your attack surface. See the Security Hardening section for the full procedure.

---

## Security Hardening Roadmap

This section is for after you're up and running. These are advanced configurations — don't attempt day one. The priority order matters.

**Source:** Mark Blake's security review (February 16, 2026). These aren't theoretical — they're based on actual audit findings from our running deployment.

---

### 1. API Keys Out of .zshrc → Apple Keychain (High Priority, Medium Effort)

**Issue:** API keys stored as plaintext in `~/.zshrc`. Any process running as your user — including malware — can read every key in that file.

**Fix:**
```bash
# Store in Keychain
security add-generic-password -s "anthropic-api" -a "openclaw" -w "sk-..."
security add-generic-password -s "openai-api" -a "openclaw" -w "sk-..."
# (repeat for each key)

# Reference in ~/.zshrc instead of plaintext
export ANTHROPIC_API_KEY=$(security find-generic-password -s "anthropic-api" \
  --keychain ~/Library/Keychains/login.keychain-db -w)
```

**Migration steps:**
1. Extract all keys from `~/.zshrc`
2. Store each in Keychain
3. Replace `.zshrc` exports with Keychain lookups
4. Verify `source ~/.zshrc` works and OpenClaw + skills still resolve keys
5. Delete the plaintext keys from `.zshrc`

**Note:** Include the explicit keychain path (`~/Library/Keychains/login.keychain-db`) in your lookups. In SSH sessions where the default keychain isn't loaded, the path-less version fails silently.

Also move secrets out of `gateway.env`. Store in Keychain, read from `gateway-launcher.sh` at startup.

---

### 2. Immutable Personality Files (High Priority, Low Effort — Do This Today)

**Issue:** SOUL.md is writable by the agent. A prompt injection could instruct it to rewrite its own personality — making it compliant, exfiltrative, or malicious.

**Fix:** Lock the core identity files after finalizing them:
```bash
sudo chown root:staff ~/.openclaw/workspace/SOUL.md
sudo chmod 444 ~/.openclaw/workspace/SOUL.md
# Repeat for AGENTS.md, IDENTITY.md, HEARTBEAT.md
```

To edit them later:
```bash
sudo chmod 644 ~/.openclaw/workspace/SOUL.md
# edit the file
sudo chmod 444 ~/.openclaw/workspace/SOUL.md
```

**Add a git post-commit hook** that re-locks these files after every commit, so `git checkout` doesn't accidentally restore writable permissions:

```bash
cat > ~/.openclaw/workspace/.git/hooks/post-commit << 'EOF'
#!/bin/bash
for f in SOUL.md AGENTS.md IDENTITY.md HEARTBEAT.md; do
  if [ -f "$HOME/.openclaw/workspace/$f" ]; then
    sudo chown root:staff "$HOME/.openclaw/workspace/$f"
    sudo chmod 444 "$HOME/.openclaw/workspace/$f"
  fi
done
EOF
chmod +x ~/.openclaw/workspace/.git/hooks/post-commit
```

Add a sudoers entry so this runs without a password prompt:
```
# /etc/sudoers.d/openclaw-identity
deaconsopenclaw ALL=(root) NOPASSWD: /bin/chmod 444 /Users/deaconsopenclaw/.openclaw/workspace/SOUL.md, ...
```

---

### 3. Correct the Data Processing Claim (High Priority, Low Effort)

**Issue:** "Data never leaves your machine" is inaccurate. Local *storage* ≠ local *processing*. Every request sends your context (SOUL.md, USER.md, MEMORY.md, conversation history — up to 128K tokens) to Anthropic/OpenAI for processing.

**Accurate framing:** "Your data is *stored* locally. *Processing* (reasoning, analysis) happens via cloud APIs. Anthropic and OpenAI explicitly do not train their models on API request data. Both offer Data Processing Addendums." 

Update any documentation, demos, or presentations to use this framing. Especially matters for client-facing or compliance contexts.

---

### 4. Change the Default Gateway Port (Low Priority, Low Effort)

**Issue:** Port 18789 is the documented OpenClaw default. Anyone who reads the repo knows to scan for it.

**Fix:** Pick a random port in the 30000-60000 range and update:
- `openclaw.json` → `gateway.port`
- LaunchAgent plist → `--port` arg
- Any scripts referencing the port

Already on loopback, so the risk is limited — but there's no reason to make it easy.

---

### 5. Granular Google OAuth Scopes (High Priority, Medium Effort)

**Issue:** One OAuth credential with full access to email, calendar, and Drive. One compromised token = full account access.

**Fix:** Create separate OAuth credentials in Google Cloud Console:
1. **Read-only email** — inbox search and read, no send
2. **Agent send account** — separate Gmail address (e.g., `enoch.agent@gmail.com`) for outbound; sends as itself, never impersonates you
3. **Read-only calendar** — view events, no create/modify
4. **Read-only Drive** — access files, no delete/share

This also gives you a clear audit trail: which credential did what.

---

### 6. Tirith Limitations — Update Your Docs (Medium Priority, Low Effort)

**Issue:** Tirith hooks into the interactive shell. OpenClaw executes commands via `child_process.spawn()`, bypassing the interactive shell entirely. Tirith doesn't protect what the agent runs.

**Real controls:**
- `exec.security` setting in `openclaw.json` (`allowlist` or `full`)
- `exec-approvals.json` — the allowlist of permitted binaries
- OS-level auditing (OpenBSM on macOS) if you want deep visibility

Update your TOOLS.md to reflect this honestly. Don't tell people Tirith is protecting the agent's exec — it isn't.

---

### 7. Docker Sandboxing (Medium Priority, High Effort)

**Issue:** Both agents run with `sandbox.mode: "off"` — full filesystem and exec access. Prompt injection that achieves code execution has unrestricted access.

**Target architecture:**
- **Enoch (main):** Sandboxed, specific volume mounts (workspace, memory, scripts)
- **Sub-agents / cron:** Heavily sandboxed, minimal access
- **Gideon (security):** Needs more host access for audits — least-sandboxed or elevated escape hatch

**Tradeoffs:** Skills that need host access (Peekaboo, openhue, voice) need careful volume configuration. Mac mini arm64 + Docker Desktop handles this, but it's a significant configuration project. Don't start this one until the quick wins above are done.

---

### 8. Clean-Room Sub-Agent Pattern (High Priority When Using Local LLM, Medium Effort)

**Issue:** Long-running agent sessions accumulate context. As the window fills, data handling instructions get deprioritized. One request with a long context can send sensitive data to a cloud model unintentionally.

**Solution — two-zone architecture:**

```
ZONE A — Local (Ollama, never hits internet)
├── All raw sensitive data input
├── PII extraction and redaction  
└── Produces: sanitized summaries (no names, no account numbers)

ZONE B — Cloud (Claude/Codex, full capability)  
├── Receives ONLY sanitized summaries from Zone A
├── Handles research, drafting, strategy
└── Returns polished output to local orchestrator
```

**Implementation:** OpenClaw's `sessions_spawn` already supports this. For any task involving sensitive data, spawn a clean sub-agent with only sanitized content in the initial prompt. Add to the sub-agent's system prompt: *"If your input contains account numbers, SSNs, full names, or addresses, replace with [REDACTED] in any output."*

This matters most when you're doing professional work with client data (financial advisory, legal, medical). For personal use, the risk is lower.

---

### 9. CrowdStrike / Enterprise EDR Awareness

**Issue:** CrowdStrike published detection and removal guidance for OpenClaw on corporate networks. If you're proposing this in an enterprise context, an unapproved deployment gets flagged.

**Position:** IT-approved deployment on dedicated hardware, not shadow IT. Get whitelisted through your IT/compliance process before running on any corporate-managed endpoint. For client pitches: lead with "firm-managed, auditable config" — not "personal AI."

---

### Secret Hygiene Script

We added a daily secret scrub cron that scans shell rc files, LaunchAgent plists, and workspace configs for plaintext secret violations:

```bash
# scripts/enforce-env-secret-scrub.sh
# Scans for common secret patterns in config files
# Exits non-zero with file:line offenders on failure
```

If you're onboarding this for a client or sharing the deployment config, run this before you share anything. Secret scanning tools like `truffleHog` or `gitleaks` also work.

---

## Key Philosophy

Everything we've done comes back to these principles. They're not rules — they're the reasoning behind the rules.

**1. Living files > dead files**
Everything your agent knows should be in files it can access, update, and act on 24/7. Conversations die. Files persist. If it's worth knowing, write it down.

**2. Principles > prompts**
Don't micromanage with instructions. Give your agent values and let it decide. SOUL.md and PRINCIPLES.md are more durable than any prompt you'll write.

**3. Incremental > big bang**
Start with one agent, one job. Add capabilities when you feel the pull. We went from a single Enoch instance to 6 active agents over two weeks. Every addition was driven by an actual bottleneck, not theory.

**4. Regressions > perfection**
Track failures. Every mistake becomes a rule. The changelog is a history of what broke and how it got fixed. That history is the system's immune system.

**5. Subscriptions > API credits for conversations**
`claude setup-token` with your Claude subscription for the main agent. API credits burn fast in conversation. Reserve pay-per-use for background tasks and voice.

**6. Local-first for sensitive data**
Cloud APIs for reasoning. Local Ollama for anything that shouldn't leave the machine. The clean-room pattern makes this composable: local processes sanitize, cloud processes refine.

**7. Security is infrastructure, not a checkbox**
Immutable personality files, Keychain secrets, identity watchers, and Gideon's nightly sweeps aren't features — they're part of the foundation. Do the quick wins first (chmod the identity files, move secrets to Keychain). Stack the harder stuff on top.

**8. Build in the trenches, document as you go**
The changelog is the real guide. Every session that changed something got a changelog entry. Six months from now, when something breaks, the changelog is how you find out what happened and when.

---

_Built in sessions. Evolved every day. This is v4 — not final._

---

## Appendix: Inference.net & Local Model Notes

**inference.net** gives you access to DeepSeek R1, Llama 3.3 70B, Qwen3, and GPT-OSS 120B at low cost. Useful for structured data extraction and tasks where you want model variety without managing Ollama yourself.

**Caveat:** inference.net is a startup with limited compliance documentation. Their data retention policy isn't formally documented. Don't route client data or sensitive information through them until you've reviewed their DPA (or confirmed one exists).

For the same reason, it's marked 🔴 High risk in our data flow audit. Fine for personal use. Not fine for professional workflows involving client data.

**Local Ollama models:**

| Model | Size | Best For |
|---|---|---|
| `gpt-oss:20b` | 20B | CRM data analysis, large-context extraction |
| `phi4:14b` | 14B | Document summarization, template drafting |
| `qwen3:8b` | 8B | Email triage, classification, PII detection |
| `qwen2.5-coder:14b` | 14B | Code generation, structured output |

`kimi-k2.5:cloud` is listed in Ollama but routes to a cloud endpoint. Don't use it for sensitive data — treat it the same as any cloud API.

---

_v4 — February 26, 2026 — Ezra (scribe subagent)_
