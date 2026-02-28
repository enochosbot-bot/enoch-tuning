# enoch-tuning

> A production-ready identity and memory system for OpenClaw agents. Skip the blank slate. Start with something that already works.

---

## The Problem

Most people who set up an AI agent get a blank slate. No memory, no personality, no rules. They spend weeks figuring out why it keeps forgetting things, why it sounds like a chatbot, why it does stupid things without asking.

Then they either give up or spend months iterating toward something useful.

**This skill skips all of that.**

What you're installing is a battle-tested identity, memory architecture, and operating protocol — built from months of real-world daily use. It makes your agent actually behave: pushing back when you're wrong, remembering what matters, doing work while you sleep, and knowing the difference between "run without asking" and "never without permission."

---

## What You Get

### Identity Core (`SOUL.md`)
- **Decision heuristics** — 10 behavioral rules that govern how the agent thinks, prioritizes, and acts when there's no explicit instruction
- **Hard rules** — non-negotiable behaviors (confirm completions, flag errors immediately, push back when the user is wrong)
- **Anti-patterns** — the exact behaviors that make AI assistants annoying, explicitly banned
- **Cost awareness** — agent knows when it's being wasteful with tokens, API calls, and your time

### Operating Protocol (`AGENTS.md`)
- **Verification protocol** — no more stale data, fake sub-agent completions, or unverified facts presented as truth
- **Status reporting rules** — pull live state before reporting anything as working or broken
- **AFK behavior** — when idle, agent asks "what is one task that moves us closer to the mission?" — not just waits
- **Automation tiers** — clear boundary between fully automated, prepped for approval, and never without instruction
- **Safety rules** — no external actions without asking, `trash` over `rm`, no config changes over chat
- **Idiot prevention protocol** — flags dangerous requests (live config changes, model swaps, auth changes) and redirects to safer approaches
- **Sub-agent management** — when to spawn, how to verify output, how to handle failures

### Memory Architecture
- **6-category typed memory** — decisions, people, lessons, commitments, preferences, projects
- **Daily log structure** — raw notes per day, promotes to typed memory via consolidation
- **VAULT_INDEX** — one-line index of every memory file; search this first before reading everything
- **Consolidation-ready** — memory structure works with automated nightly consolidation crons

### Mission Engine (`MISSION.md`)
- Idle-time behavior driven by your stated mission, not random productivity
- Built-in daily reflection loop: "What would make me more useful tomorrow?"
- Front-line prioritization — agent knows what matters now vs. what can wait

### Ops Template Library (`ops/*.md`)
Includes battle-tested operating docs for:
- verification protocol
- dispatch routing
- agent boundaries
- model selection
- notification routing
- pruning protocols
- data management
- production queue template
- improvement queue
- cron registry template
- in-flight tracker template
- daily log template
- tool failure log

### Verification Protocol (`ops/verification-protocol.md`)
- Explicit rules for when to verify live vs. use cached context
- Prevents the #1 failure mode: agent confidently reporting stale information

### Setup Scripts
- `memory-structure.sh` — creates all 8 memory directories + VAULT_INDEX in one command
- `lock-identity.sh` — locks identity files (SOUL.md, AGENTS.md) to prevent accidental overwrites

---

## Installation

**Requires:** [OpenClaw](https://openclaw.ai) installed and configured.

### Step 1 — Install the skill

```bash
# From your OpenClaw workspace
cp skills/enoch-tuning/templates/SOUL.md SOUL.md
cp skills/enoch-tuning/templates/AGENTS.md AGENTS.md
cp skills/enoch-tuning/templates/USER.md USER.md
cp skills/enoch-tuning/templates/MEMORY.md MEMORY.md
cp skills/enoch-tuning/templates/MISSION.md MISSION.md
mkdir -p ops
cp skills/enoch-tuning/templates/ops/*.md ops/
cp skills/enoch-tuning/templates/BOOT.md BOOT.md
```

### Step 2 — Create memory structure

```bash
bash skills/enoch-tuning/setup/memory-structure.sh ~/.openclaw/workspace
```

### Step 3 — Personalize (required — do this before anything else)

Every `[BRACKET]` is a placeholder. Fill in:

| File | What to fill in |
|------|----------------|
| `SOUL.md` | Agent name, your worldview, any additional hard rules |
| `USER.md` | Your name, timezone, what you do, your goals, key people |
| `MEMORY.md` | Your platform setup, what tools you use, key facts |
| `MISSION.md` | Your one-sentence mission, current front lines |

**Time required:** 20–30 minutes. Do it once, get compounding value forever.

### Step 4 — Lock identity files

```bash
bash skills/enoch-tuning/setup/lock-identity.sh ~/.openclaw/workspace
```

This sets SOUL.md and AGENTS.md to read-only. Your agent can read them but can't overwrite them. Protects the behavioral core from accidental mutation.

### Step 5 — First conversation

Tell your agent:
1. Your name and what you do
2. The top 3 things you want automated
3. What it should never do without asking
4. What "done" looks like for a typical task

Everything compounds from here.

---

## What NOT to Change Without Understanding

- **`Hard Rules` in SOUL.md** — these are load-bearing behavioral guardrails. Removing them degrades output quality in ways that are hard to debug.
- **`Idiot Prevention Protocol` in AGENTS.md** — this protects your infrastructure from chat-based config changes. One bad live config edit can take your system offline.
- **`Verification Protocol`** — removing this reintroduces stale data and confident-but-wrong completions.
- **Automation tiers** — the boundary between "runs without asking" and "never without instruction" is carefully drawn. Blurring it causes unexpected external actions.

---

## How It Behaves Out of the Box

After installation and personalization, your agent will:

- **Run your production queue without prompting** — when you step away, it pulls from queued work, delegates to sub-agents, and surfaces a completion report when you return. Not "what would you like me to do?" — it already started.
- **Never report done without verifying it** — reads the output file, checks the live URL, confirms the deploy returned 200 — before saying a word to you. "I think I did it" isn't a completion. A verified deliverable is.
- **Survive cold restarts without losing the thread** — reads its crash recovery file on boot, identifies what was in-progress, and resumes mid-task. No "where were we?" — it already knows.
- **Spawn and coordinate parallel agents** — kicks off specialized agents simultaneously on dependency-sorted work, monitors for silent failures, and closes the loop before reporting back. You get a brief. Not a thread to manage.
- **Build memory that compounds across every session** — decisions, people, commitments, lessons, preferences, projects — all logged in structured categories. The 100th session is smarter than the first because of the work the first 99 left behind.
- **Intercept bad decisions before they execute** — flags risky actions with a hard stop: infrastructure changes, impulsive external sends, bad configs. Not a polite disclaimer — a redirect. Not apologized for after, but blocked before.
- **Route every output to where you'll actually see it** — research to the research channel, security alerts to the security channel, cron completions to ops. Nothing runs silently into a log file you'll never read.
- **Know what to delegate without being told** — explicit routing rules built in: complex code to the coding agent, deep research to the researcher, audit passes to the security observer. The main agent coordinates — it doesn't try to do everything itself.

---

## Multi-Agent Delegation

Single-agent setups hit a ceiling fast. The production pattern that scales is a **main orchestrator + named specialist sub-agents**.

### The concept

Assign each sub-agent a domain and a role. Common roles:

| Role | Handles |
|------|---------|
| **Coding agent** | Feature builds, scripts, refactors, Claude Code sessions |
| **Research agent** | Deep dives, synthesis, monitoring, briefings |
| **Security observer** | Audit passes, secret scans, permission checks |
| **Strategy agent** | Planning, prioritization, high-stakes decisions |
| **Content agent** | Drafts, editing, social copy |
| **QA agent** | Verification, test runs, output review |

You don't need all of these on day one. Start with two (coding + research). Add roles when real demand emerges.

### Wiring sub-agents in `openclaw.json`

Each sub-agent is a separate agent entry with its own `agentId`, model, tool permissions, and workspace. They share the same OpenClaw gateway but operate in separate sessions.

```json
{
  "agents": [
    {
      "agentId": "main",
      "label": "Main Agent",
      "model": "...",
      "workspaceDir": "~/.openclaw/workspace"
    },
    {
      "agentId": "coder",
      "label": "Coding Agent",
      "model": "...",
      "workspaceDir": "~/.openclaw/workspace-coder"
    },
    {
      "agentId": "researcher",
      "label": "Research Agent",
      "model": "...",
      "workspaceDir": "~/.openclaw/workspace-research"
    }
  ]
}
```

Each workspace gets its own `SOUL.md` and `AGENTS.md` scoped to that role. The coding agent has a SOUL that emphasizes shipping clean code. The research agent has one that emphasizes synthesis and sourcing. Same behavioral framework, different defaults.

### Delegation routing

When the main agent receives a task, it routes by type before doing any work itself:

- **Anything requiring file edits, new code, or Claude Code sessions** → coding agent
- **Anything requiring research, synthesis, or monitoring** → research agent
- **Anything touching security, secrets, or permissions** → security observer
- **Strategic or planning questions above a certain complexity threshold** → strategy agent

The main agent stays lean. Its job is coordination, not execution. It delegates, monitors, and verifies — it doesn't rubber-stamp output or report completions it hasn't confirmed.

### Oversight protocol

After any sub-agent returns:
1. Verify the deliverable exists on disk with real content (not just "done")
2. Spot-check the output quality — low token count on a complex task is a red flag
3. If something looks wrong, flag it and re-delegate rather than silently accepting
4. Never report a sub-agent completion to the user without verifying it yourself

Sub-agents can fail silently. The main agent is the accountability layer.

### Identity files per agent

Each workspace needs:
- `SOUL.md` — role-specific personality and heuristics
- `AGENTS.md` — role-specific operating rules
- `BOOT.md` — crash recovery for that agent

The `ops/` folder (see below) is the shared coordination layer. All agents read it. None of them own it.

---

## Channel / Topic Routing

If you're running OpenClaw with Telegram, **topic threads are a force multiplier**. Instead of everything landing in one noisy DM, each function gets its own channel. Clean signal, no noise.

### Why it matters

Without topic routing, your agent fires everything into one stream. Research briefings, error alerts, cron outputs, status updates — all blended. You miss things. You mute things you shouldn't. You lose the signal.

With topic routing, each thread has one job. You know what's coming before you read it.

### Suggested topic structure

| Topic | Purpose |
|-------|---------|
| **Ops** | Config changes, status, agent coordination |
| **Research** | Briefings, synthesis, source summaries |
| **Security** | Alerts, audit results, secret scan reports |
| **Costs** | Spend tracking, token usage, API cost summaries |
| **Content** | Drafts, post queues, editorial output |
| **Cron logs** | Automated job completions and digests |

Start with the topics you'll actually look at daily. Add more when you have a real need for the separation.

### Wiring topics to agents

In your `openclaw.json` bindings, assign each agent (or cron job) a delivery target that includes the topic thread. This means cron job outputs, research deliveries, and agent status updates all route to the correct place automatically — without manual routing decisions at runtime.

### Cron delivery

Every scheduled job should specify a delivery target, not just log to disk. A cron job that logs locally and never surfaces the output might as well not run. Route outputs to the appropriate topic, and your agent's background work becomes visible without being noisy.

---

## The ops/ Folder

The `ops/` folder is the connective tissue between your main agent, sub-agents, and Claude Code sessions. Without it, agents step on each other.

### Why it exists

When multiple agents — or a mix of agents and Claude Code — touch the same system, they need shared ground truth. Without it:
- Agent A changes a config. Agent B reads stale state and reverts it.
- A Claude Code session fixes a bug. The main agent doesn't know and redoes the work.
- You ask your agent what changed. It doesn't know.

The `ops/` folder solves coordination at the file level — no service, no API, no message broker.

### Files in ops/

**`ops/changelog.md`** (required)
The append-only log of every config change, significant action, and agent decision. Every agent reads this at session start. Every meaningful change gets a line. Format: date, who made the change, what changed, why.

This is how agents avoid stepping on each other. If Agent B checks the changelog and sees Agent A just changed a config, it knows. No blind overrides.

**`ops/dispatch-routing.md`**
The rulebook for which tasks go to which agent. When should the main agent handle something vs. delegate? What threshold pushes a task to the coding agent? What always stays with the main agent?

Document this explicitly. "I'll just know" doesn't survive a session restart.

**`ops/verification-protocol.md`**
Already in this guide — see the template. Reference it here so every agent knows where to find it.

**`active-tasks.md`** (in the workspace root)
Current in-progress work. Crash recovery anchor (see BOOT.md below). Every task that starts gets written here. Every task that finishes gets marked done. If the gateway restarts, this file is where work resumes.

### Setup

```bash
mkdir -p ops
touch ops/changelog.md
touch ops/dispatch-routing.md
cp skills/enoch-tuning/templates/ops/verification-protocol.md ops/verification-protocol.md
touch active-tasks.md
```

Seed `ops/changelog.md` with one line: the date you set up the system. From there, it's append-only.

---

## BOOT.md — Crash Recovery

Sessions end. Gateways restart. Context gets compacted. Without a recovery procedure, in-progress work dies silently.

`BOOT.md` is the procedure your agent runs whenever it starts fresh. It lives in your workspace root and gets read before anything else.

### Template

See `templates/BOOT.md`.

### The pattern

**Trigger:** Any session restart, gateway restart, or post-compaction start.

**Step 1 — Read `active-tasks.md`.**
This file contains everything that was in-progress when the last session ended. Any task marked IN_PROGRESS is a recovery candidate.

**Step 2 — Resume in-progress tasks.**
For each task marked IN_PROGRESS: verify whether it was actually completed (check the deliverable, not your memory). If complete, mark done. If incomplete, resume from where it stopped.

**Step 3 — Completion contract.**
A task is not done until:
- The deliverable exists on disk with real content
- You've verified it (read it, ran it, checked the output)
- It's committed to git (if applicable)

Not "I think I did it." Not "the sub-agent said done." Verified.

**Step 4 — Resume normal operation.**
Read `ops/changelog.md` to catch up on what changed while you were down. Then resume queued work.

---

## Security Hardening Patterns

The standard setup works. These patterns make it production-hardened.

### API keys belong in the OS keychain — never in config files

Every API key you put in a config file or shell profile is a key that can leak. Shell history, backup syncs, accidental commits — plaintext secrets travel. The OS keychain doesn't.

Store API keys in the macOS Keychain or the Linux Secret Service equivalent. Load them at runtime via subshell:

```bash
export MY_API_KEY="$(your-keychain-lookup-command)"
```

The loaded value is ephemeral. The stored value is encrypted at rest by the OS.

Audit your setup for plaintext secrets. Check: `.zshrc`, `.bashrc`, `.env` files, openclaw config files, any YAML or JSON in your workspace. Anything you find, move to the keychain.

### Run a periodic secret scan

Even if you set things up clean, secrets drift back to plaintext. A new tool suggests `export KEY=xxx` in its docs. You test something quickly and forget to clean it up. Cron jobs write logs that include tokens.

Run a scheduled scan (weekly or on every significant change) that checks the obvious locations for patterns that look like API keys, tokens, or credentials. The scan doesn't need to be sophisticated — grep for common patterns. The goal is catching drift before it becomes exposure.

### Lock identity files after setup

After personalizing your `SOUL.md` and `AGENTS.md`, lock them:

```bash
bash skills/enoch-tuning/setup/lock-identity.sh ~/.openclaw/workspace
```

This sets them to read-only (mode 444). Your agent can read them but can't overwrite them during a session. This matters because agents under extended context pressure sometimes try to "simplify" their own operating rules. A locked file is a locked file — no context pressure overrides it.

**Why this is load-bearing:** Your behavioral core is what makes the agent trustworthy. A single accidental overwrite can silently degrade behavior in ways that are hard to diagnose. The cost of locking is zero. The cost of not locking is a subtle, invisible regression.

### File permission standards

| File type | Mode | Why |
|-----------|------|-----|
| `SOUL.md`, `AGENTS.md` | 444 | Read-only — identity files |
| `openclaw.json` | 600 | Config with secrets — owner only |
| Scripts in `setup/` | 755 | Executable by owner |
| Memory files in `memory/` | 644 | Readable, writable by owner |
| `ops/changelog.md` | 644 | Shared read, owner write |

These aren't arbitrary. They encode intent: "this file is not supposed to change" vs. "this file changes daily."

### Claude Code vs. chat

Certain changes should never happen over chat. If your main agent starts editing `openclaw.json` or reconfiguring your model setup from a Telegram message, something is wrong.

The idiot prevention protocol in `AGENTS.md` enforces this — but understand the principle: chat has low friction and no review gate. Config changes need a review gate. Route infrastructure changes to Claude Code sessions where you can see exactly what's happening before it runs.

---

## Cron Automation Architecture

The guide mentions crons. Here's the actual architecture that makes them useful.

### Categories of crons

**Survival checks** — Is the gateway running? Is auth valid? Are required services up? These run frequently and alert immediately on failure. They're not informational — they're watchdogs.

**Memory consolidation** — Daily logs get promoted to typed memory. Old entries get distilled into long-term memory. This runs once a day, usually overnight. It's what keeps memory from growing unbounded while preserving what matters.

**Research delivery** — Scheduled research runs (bookmark analysis, feed monitoring, digest generation) that produce output and route it to the appropriate topic. These have natural delivery windows — morning briefings land in the morning.

**Social monitoring** — If you're tracking mentions, keywords, or competitor activity, these run on a schedule and surface signal without requiring you to go looking.

### Quiet hours

Not every alert needs to wake you up. Set a quiet window (typically overnight) during which non-critical crons run silently — they write to disk and deliver on the next active window, not immediately.

Only two categories bypass quiet hours: system failures (gateway down, auth broken) and anything you've explicitly flagged as urgent. Everything else can wait until morning.

### The heartbeat pattern

A heartbeat is a cron that runs periodically and returns one of two states: **OK** or **NEEDS ATTENTION**. Not a wall of logs — a single status signal.

Good heartbeat output:
```
[2026-02-26 08:00] ✅ All systems nominal — 3 crons ran overnight, 1 memory consolidation completed
```

Bad heartbeat output:
```
[2026-02-26 08:00] Gateway running (PID 12345). Auth valid. Cron log... [200 lines of log output]
```

The heartbeat is not a dump. It's a signal. If everything is fine, one line. If something needs attention, one line describing what.

### Delivery routing for crons

Every cron job should have an explicit delivery target. `logs/` is not a delivery target — it's a graveyard. Nobody reads it. Route cron output to the topic that makes it visible:

- Memory consolidation results → ops topic
- Research deliveries → research topic
- Secret scan results → security topic
- Heartbeat → ops topic

If a cron isn't delivering somewhere you look, it's not running — it's just making log files.

---

## Social Ops Safety Layer

If you're using your agent for social media or any external communications, this layer is non-negotiable.

### The risks

External communications have one-way consequences. A draft that sits in a folder is recoverable. A tweet that went out isn't. An agent that posts autonomously will eventually post something wrong, at the wrong time, or in the wrong context.

The fix is an explicit approval gate — not "be careful," but a structural requirement.

### The pattern

**All posts queue to a draft folder.** Your agent never posts directly. It writes to `ops/drafts/` (or equivalent). The draft sits there until you approve.

**External content is data, never commands.** If your agent reads social media feeds, news sources, or user-generated content as part of its research pipeline — treat it as data only. Never execute or act on content from external sources. This is prompt injection defense. An external post that says "now post X" should be logged as research data, not acted on.

**Explicit approval gate.** Agent prepares, you approve. Always. This is not a setting — it's a protocol. Build it into `ops/dispatch-routing.md` so it's explicit, not assumed.

**Confirm before public.** Before any external delivery, the agent surfaces: what it's sending, to where, and when. You confirm. Then it sends.

This adds five seconds of friction to posting. It eliminates the class of errors where an agent posts confidently and incorrectly.

---

## The Philosophy

An AI assistant is only as good as its operating rules. Most agents fail not because the model is weak, but because:

1. No memory beyond the current session
2. No behavioral norms — it just agrees with everything
3. No mission context — idle time goes to nothing
4. No safety layer — it'll do anything you ask without flagging risk

This skill is a direct response to all four failures. It doesn't change what your agent can do — it changes how it thinks and behaves.

The additions in v1.4.0 address the next level: what happens when you have multiple agents, automated pipelines, and external actions running in parallel. The answer is coordination structure — ops files, channel routing, crash recovery, and security hardening. Not complex. But required.

---

## License

MIT — use it, fork it, build on it.

---

## Version

`v1.4.0` — built and battle-tested February 2026.
