---
type: lesson
date: 2026-02-16
tags: [infrastructure, models, outage, prevention]
---

# Model Swap Outage — Never Again

## What Happened
Deacon swapped to a local model (Ollama) on the fly via Telegram without verifying the model was running or the API was configured. Gateway tried to use it, couldn't reach it, went dark. Ellisyn had to physically restart the Mac mini.

## Lesson
Model changes via Telegram = high risk. If the new model doesn't respond, the gateway dies and there's no way to talk to Enoch to fix it.

## Protocol
- Model swaps are ALWAYS flagged as Claude Code jobs
- Idiot Prevention Protocol triggers automatically when models are discussed
- Offer to walk Deacon through it in Claude Code every time
- Added to AGENTS.md as a permanent rule
- Auto-rollback watchdog is queued (Claude Code session item 7)
