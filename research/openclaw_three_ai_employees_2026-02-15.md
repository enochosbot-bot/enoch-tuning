# 3 AI Employees That Work 24/7 — OpenClaw Multi-Agent Setup

**Source:** https://www.youtube.com/watch?v=aFQJYaornJ4
**Saved:** 2026-02-15
**Context:** Spectrum presentation research

## Overview
Demo of three specialized OpenClaw agents running on a single machine, each with distinct roles, plus a full architecture walkthrough and hands-on setup guide.

## The Three Agents
1. **Neo (AI Engineer)** — writes, runs, and returns code (demo: Manim animation)
2. **Pulse (Deep Researcher)** — scrapes news, papers, GitHub trending → produces daily digest on schedule
3. **Pixel (Graphic Designer)** — produces brand-style diagrams via image service APIs

## Architecture
- **Gateway daemon** routes messages from inputs (Telegram, Discord, Slack, WhatsApp, scheduled jobs) into agent sessions
- Components: session manager, message router, scheduler (cron jobs), websocket API
- Each session → PI agent reasoning engine → chosen LLM provider
- Agent tools: file system, shell, browser, external APIs
- Agents live in workspace directories with agent.md, soul/identity files, tool definitions, skills

## Key Concepts
- **Skills repo** — 45,000+ skills available, plug in as needed (demo: added Firecrawl CLI for web scraping)
- **Session isolation** — sub-agents get isolated sessions so temp work doesn't pollute main memory
- **Heartbeat** — periodic check-ins (default 30 min) for inexpensive scans
- **Cron jobs** — specific scheduled tasks (e.g., daily digest at 8:00 AM)
- **Agent customization** — persona, name, tone, allowed tools via soul/identity/tools files

## Setup
- Single command install on macOS/Linux/Windows
- Onboarding: model selection + channel config (Telegram via BotFather)
- Project lives in dot directory with agents, sessions (JSONL logs), workspaces, skill manifests

## Spectrum Relevance
This is the "multiple specialized agents" pitch. For Spectrum:
- **Client Prep Agent** — pulls CRM data, recent communications, account balances before meetings
- **Research Agent** — daily market digest, regulatory updates, fund performance summaries
- **Admin Agent** — form processing, data entry, follow-up tracking
Each agent stays in its lane, maintains its own context, and reports through a single interface (could be Outlook, Teams, or Telegram). The cost/architecture overhead is minimal — runs on a single Mac.
