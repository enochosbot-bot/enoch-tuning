# NUCLEUS.md — Model & AI Tool Configuration

## Primary Model
- **anthropic/claude-opus-4-6** — main session (thinking: low)
- Subscription-based via setup-token (not API credits)

## Voice Model
- **anthropic/claude-sonnet-4** — voice interactions

## Voice Call Stack
- STT: OpenAI Realtime
- Response: openai/gpt-4o
- TTS: OpenAI (voice: onyx)

## Available Models
- Anthropic (Claude Opus 4.6, Sonnet 4) — via subscription
- OpenAI (GPT-4o) — API key configured

## Specialized Models
- Schematron-3B (inference.net) — HTML→JSON extraction, needs API key

## Usage Philosophy
- Use subscription models (Anthropic) as default — avoid burning API credits
- Use OpenAI for voice pipeline (better real-time performance)
- Use specialized models for specific tasks (Schematron for scraping)

## Token Awareness
- Opus 4.6 is expensive per-token if on API — subscription is the way
- Spawn sub-agents for parallel work to avoid bloating main context
- QMD for local search instead of stuffing context
