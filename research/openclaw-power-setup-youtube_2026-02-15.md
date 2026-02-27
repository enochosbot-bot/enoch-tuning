# OpenClaw Power Setup — YouTube Deep Dive
**Source:** https://www.youtube.com/watch?v=Q7r--i9lLck
**Date:** 2026-02-15

## Setup Overview
Dedicated always-on MacBook Air running OpenClaw as personal automation engine. Telegram as primary control surface with many narrow topic channels for context preservation.

## Key Techniques We Should Steal

### 1. Many Narrow Telegram Topics (Context Preservation)
- They use tons of topic channels — each one keeps context tight
- We already do this (7 topics) but could go further with dedicated channels per workflow

### 2. Personal CRM + Meeting Prep
- Daily Gmail + calendar ingestion → dedup → role classification (cheap Gemini Flash)
- Timeline/last-touch updates, semantic indexing
- Natural language queries: "who's the last person I talked to at X?"
- Meeting prep: pulls today's calendar, filters internal, returns context + recent talk points
- **Relevant for Spectrum** — this is exactly the Redtail/Outlook/eMoney gap

### 3. Hybrid Database (SQL + Vector Column)
- URLs/files dropped into Telegram → parsed, chunked, stored
- Both exact queries AND semantic search work
- We have QMD for this but their approach is more integrated

### 4. Video Idea Pipeline (~30 seconds)
- Queries KB + web + social research
- Generates hooks and outlines
- Checks for duplicate pitches
- Creates task cards + posts confirmations
- **Direct match for Deacon's content creation goal**

### 5. X/Twitter Search — Cost-Optimized Fallback Chain
- Multiple APIs and third-party services ordered by cost
- Different cost/coverage tiers for searches vs single-tweet lookups
- We have X Research skill but could add fallback tiers

### 6. YouTube Analytics Pipeline
- Daily API snapshots persisted locally
- PNG charts generated
- Insights fed into metaanalysis → title/thumbnail/cadence recommendations

### 7. Business "Agent Council" Metaanalysis
- All signals (YouTube metrics, CRM health, Slack, meeting transcripts, pipeline data) compacted
- "Council" of AI agent roles: growth strategist, skeptical operator, etc.
- Collaborate, reconcile, produce ranked daily report with suggestions
- **This is the multi-agent pattern we should build toward**

### 8. Humanizer Skill
- Removes AI stylistic artifacts from content
- We tried to install this (ClawHub rate limited) — retry needed

### 9. Meeting Transcript → Action Items
- Parses transcripts into owner/action/deadline
- Pushes to to-do app automatically

### 10. Observability & Cost Tracking
- Every API/LLM call logged to usage ledger
- ~$150/month across models/APIs
- Can query usage and cost per workflow
- We have ops/cost-ledger.md but should automate logging

### 11. Self-Evolution Checks
- Hourly cron syncs code repos
- Daily workspace docs auto-checked against best-practice guides
- Detects drift (e.g., Opus 4.6 prompting differences)
- We have daily self-check but could add doc drift detection

### 12. Backup Strategy
- Git + cloud storage with timestamps + documented restore procedure
- We already have this ✅

### 13. Development via Cursor + SSH
- Edits in Cursor, SSH into the Mac, test via Telegram
- TeamViewer for full remote control
- We should set up SSH access (Tailscale first)

## What We're Missing vs This Setup
1. CRM ingestion pipeline (huge for Spectrum)
2. Video idea pipeline (content creation goal)
3. Agent council / multi-agent metaanalysis
4. Automated cost logging per workflow
5. Self-evolution / doc drift detection
6. Humanizer skill (blocked by ClawHub rate limit)
7. Meeting transcript → action items
