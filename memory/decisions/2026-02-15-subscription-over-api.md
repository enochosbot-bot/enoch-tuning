---
title: "Subscription auth over API credits"
date: 2026-02-15
category: decisions
priority: 🔴
tags: [cost, auth, infrastructure]
---
Use `claude setup-token` with Anthropic subscription and OpenAI Codex OAuth with ChatGPT $20/mo sub. API credits get expensive fast. Keep API key only for media APIs (STT/TTS/image gen) where OAuth isn't supported.
