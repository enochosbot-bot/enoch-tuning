# Jarvis Initialization Sequence — Analysis
_Source: 8 prompt screenshots from OpenClaw Brain framework_
_Date: 2026-02-15_

## The 8 Conversational Prompts

### 1. Brain (Foundation)
- Role: "Initialization engine for a superintelligent personal AI"
- Extracts: Identity, operations, people, resources, friction, goals/dreams, cognition, content/learning, communication, codebases, integrations, voice/soul, automation, mission control, memory/boundaries
- Outputs to: USER.md, SOUL.md, IDENTITY.md, AGENTS.md, TOOLS.md, MEMORY.md, HEARTBEAT.md
- Opening: "Who are you and what does your world look like right now?"

### 2. Muscles (Model Architecture)
- Role: "AI system architect — discover every AI model and tool, architect as one coordinated system"
- Extracts: Models by domain, depth per model, subscriptions/access, cost reality, MCP connections, gaps, routing preferences, multi-agent architecture
- Outputs to: TOOLS.md (model inventory, MCP connections, budget), AGENTS.md (task routing, cost routing, model tiering, multi-agent roster, spending limits), MEMORY.md (preferences, frustrations), HEARTBEAT.md (gaps, models to trial)
- Key tables: MODEL INVENTORY, MCP AND CONNECTIONS, TASK ROUTING MAP, COST ROUTING, MODEL TIERING
- Opening: Lists every AI domain (creative, code, communication, business ops, data, media, productivity) and asks user to map tools

### 3. Bones (Codebase Intelligence)
- Role: "Codebase intelligence engine — discover and document every repository"
- Extracts: Repo inventory, architecture per repo, conventions, dependencies, stability/risk, dev workflow, new project patterns, access/ingestion
- Outputs to: skills/ (one skill folder per repo with SKILL.md), skills/codebases/SKILL.md (master index), TOOLS.md, MEMORY.md, HEARTBEAT.md, AGENTS.md
- Key structure: Per-repo SKILL.md with overview, architecture, data flow, conventions, dependencies, stability map, cross-repo patterns, dev workflow, new project template
- Opening: "List every repo you currently have, actively work on, or plan to build"

### 4. DNA (Behavioral Logic)
- Role: "Behavioral architect — define how the AI thinks, decides, learns, and operates"
- Extracts: Decision-making approach, risk tolerance, security posture, escalation paths, uncertainty handling, memory compounding, learning from mistakes, communication style, autonomy calibration
- Outputs to: AGENTS.md (decision protocols, risk framework, security config, escalation rules, uncertainty protocols, autonomy levels, communication during work, learning protocols), MEMORY.md (memory architecture, retention rules, daily log template)
- Opening: "When your AI faces a task: Should it think out loud or just act?"

### 5. Soul (Personality)
- Role: "Personality architect — define voice, tone, character, emotional texture"
- Extracts: Character archetype, tone spectrum, emotional texture, voice characteristics, humor/levity, context switching, anti-patterns, name/identity
- Outputs to: SOUL.md (character, tone, emotional texture, voice, humor, context modes, anti-patterns), IDENTITY.md (name, vibe, emoji, self-reference, introductions)
- Opening: "What fictional AI or assistant comes to mind? What traits do you want?"

### 6. Eyes (Activation/Monitoring)
- Role: "Activation architect — what AI watches for, triggers, autonomous actions"
- Extracts: Proactive monitoring, triggers/alerts, autonomous actions, cron jobs, heartbeat config, active hours, alert thresholds, boot sequence, quiet hours, channel routing, DM/session policy
- Outputs to: HEARTBEAT.md (monitoring checklist, interval, hours, silent OK response), BOOT.md (startup sequence, notifications, verification, initialization), AGENTS.md (triggers, alert thresholds, autonomous actions, cron schedule, quiet hours, channel routing, DM policy)
- Key format: HEARTBEAT.md = 3-10 item checklist, task + action, not prose
- Opening: "What should your AI keep an eye on without you asking?"

### 7. Heartbeat (Evolution)
- Role: "Evolution architect — how AI grows, improves, evolves over time"
- Extracts: Daily rhythm, weekly review, memory curation, self-improvement, feedback integration, file evolution, growth metrics, trust escalation
- Outputs to: HEARTBEAT.md (daily rhythm, weekly review, self-improvement, growth metrics, trust escalation), AGENTS.md (file updates, feedback protocols), MEMORY.md (curation rhythm), memory/ (daily log template, weekly review template)
- Opening: "What should your AI capture from the day's sessions?"

### 8. Nervous System (Context Efficiency)
- Role: "Context efficiency architect — audit token usage, implement guardrails"
- Extracts: Token audit per file, accumulation patterns, loading behavior, baseline cost per session type
- Outputs to: CONTEXT_MANAGEMENT.md (token audit, context profiles, conversation windowing, tool output compression, budget guardrails, session hygiene)
- Also merges into: AGENTS.md (context budget section), HEARTBEAT.md (context monitoring checklist)
- Key principle: "Analyze before acting. Measure every file. Context is finite. Every token has a cost."
- Opening: "Let me scan your workspace and show you where the bloat lives"

## What We Already Cover vs Gaps

### Strong Coverage
- Brain → USER.md, IDENTITY.md, MEMORY.md, GOALS_AND_DREAMS.md
- Soul → SOUL.md with anti-patterns, tone, vibe
- Eyes (partial) → watchdog, cron jobs, HEARTBEAT.md (empty)

### Gaps to Fill
- **Muscles**: No model routing map, cost-per-task table, or MCP inventory
- **DNA**: No formalized escalation rules, autonomy levels table, or risk framework
- **Bones**: No codebase mapping (Deacon may not have repos to map yet)
- **Nervous System**: No token audit, context profiles, or budget guardrails
- **Eyes**: No BOOT.md for startup verification
- **Heartbeat**: No weekly review template, no formal self-improvement tracking

## Recommendation for Guide
Include the 8 prompts as a "Deep Configuration" section — paste each one into your agent chat sequentially after basic setup is done. Brain first, then in any order. Each one is a conversation, not a command.
