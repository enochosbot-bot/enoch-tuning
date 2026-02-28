---
name: enoch-tuning
description: A battle-tested OpenClaw setup with pre-wired identity, memory architecture, security protocols, and automation. Skip weeks of trial and error — install this and start with a production-ready agent.
homepage: https://github.com/enochosbot-bot/enoch-tuning
metadata:
  {
    "openclaw":
      {
        "emoji": "🔮",
        "os": ["darwin", "linux"],
      },
  }
---

# enoch-tuning

Most people who set up an AI agent get a blank slate. No memory, no personality, no rules. They spend weeks figuring out why it keeps forgetting things, why it sounds like a chatbot, why it won't push back when they're wrong.

This skill skips all of that.

What you're installing is a production-tested identity and memory system — decision heuristics, hard rules, security protocols, memory architecture, and automation pipelines that took months to develop and refine.

## What You Get

- **Pre-wired SOUL.md** — decision heuristics, hard rules, anti-patterns, cost awareness. The behavioral core that makes the difference between a useful agent and a corporate chatbot.
- **AGENTS.md** — full operating rules: verification protocol, status reporting, sub-agent management, safety tiers.
- **Memory architecture** — 6-category typed memory system (decisions, people, lessons, commitments, preferences, projects), VAULT_INDEX, daily log structure.
- **MISSION.md template** — mission-driven idle behavior. Agent asks "what gets us closer to the mission?" instead of waiting.
- **Full ops template library:**
  - Verification protocol — prevents stale data and fake completions
  - Dispatch routing — task → agent routing with mandatory close protocol
  - Agent boundaries — what each agent can/cannot do
  - Model selection — when to use which model tier
  - Notification routing — one channel per workflow, no noise
  - Pruning protocols — context hygiene, data lifecycle
  - Data management — where things live, backup strategy
  - Production queue — tracking work items by status
  - Improvement queue — process optimization tracking
  - Cron registry — scheduled job documentation
  - Daily log template — session documentation format
  - Tool failure log — tracking dead ends so agents don't retry
- **Setup scripts** — memory directory structure, identity file locking.

## Installation

### Step 1 — Copy templates
```bash
# Core identity files
cp skills/enoch-tuning/templates/SOUL.md ~/.openclaw/workspace/SOUL.md
cp skills/enoch-tuning/templates/AGENTS.md ~/.openclaw/workspace/AGENTS.md
cp skills/enoch-tuning/templates/USER.md ~/.openclaw/workspace/USER.md
cp skills/enoch-tuning/templates/MEMORY.md ~/.openclaw/workspace/MEMORY.md
cp skills/enoch-tuning/templates/MISSION.md ~/.openclaw/workspace/MISSION.md

# Create ops directory and copy all ops templates
mkdir -p ~/.openclaw/workspace/ops
cp skills/enoch-tuning/templates/ops/*.md ~/.openclaw/workspace/ops/
```

### Step 2 — Create memory structure
```bash
bash skills/enoch-tuning/setup/memory-structure.sh ~/.openclaw/workspace
```

### Step 3 — Personalize (required)
Edit these files — everything in [BRACKETS] is a placeholder:
- `SOUL.md` — name, worldview, vibe
- `USER.md` — your info, goals, rhythm
- `MEMORY.md` — your platform setup, key facts
- `MISSION.md` — your mission statement (one sentence)

### Step 4 — Lock identity files
```bash
bash skills/enoch-tuning/setup/lock-identity.sh ~/.openclaw/workspace
```

### Step 5 — First conversation
Tell your agent: your name, what you do, the top 3 things you want automated, and what it should never do without asking. Everything compounds from here.

## What NOT to Change Without Understanding

- **Hard Rules section in SOUL.md** — these are non-negotiable behavioral guardrails
- **Idiot Prevention Protocol in AGENTS.md** — protects your infrastructure from chat-based config changes
- **Verification Protocol** — removing this reintroduces stale data and fake completions
- **Automation tiers** — the boundary between "runs without asking" and "never without instruction" is load-bearing

## File Structure

```
skills/enoch-tuning/
├── SKILL.md                                ← this file
├── templates/
│   ├── SOUL.md                             ← identity template
│   ├── AGENTS.md                           ← operating rules template
│   ├── USER.md                             ← user intake template
│   ├── MEMORY.md                           ← long-term memory template
│   ├── MISSION.md                          ← mission statement template
│   └── ops/
│       ├── verification-protocol.md        ← fact-checking protocol
│       ├── dispatch-routing.md             ← task → agent routing
│       ├── agent-boundaries.md             ← hard role boundaries
│       ├── model-selection.md              ← model usage by task type
│       ├── notification-routing.md         ← single-source alerts
│       ├── pruning-protocols.md            ← context/data lifecycle hygiene
│       ├── data-management.md              ← canonical paths + backups
│       ├── production-queue-template.md    ← work queue template
│       ├── improvement-queue.md            ← system improvement tracking
│       ├── cron-registry-template.md       ← cron documentation template
│       ├── in-flight-template.md           ← dispatch tracking template
│       ├── daily-log-template.md           ← Obsidian daily log format
│       └── tool-failure-log.md             ← known dead ends + workarounds
└── setup/
    ├── memory-structure.sh                 ← creates memory directories
    └── lock-identity.sh                    ← locks SOUL.md + AGENTS.md
```
