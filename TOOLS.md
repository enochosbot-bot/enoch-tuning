# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

### Tirith (Terminal Security)
- Installed via brew: `sheeki03/tap/tirith` v0.1.9
- Activated in ~/.zshrc: `eval "$(tirith init)"`
- 30 rules, catches homograph attacks, ANSI injection, pipe-to-shell
- Zero overhead on clean commands
- ⚠️ **Limitation:** Only protects interactive terminal sessions (zsh). Does NOT cover OpenClaw exec calls — those run via Node.js child_process.spawn() and bypass Tirith entirely. Real exec security comes from OpenClaw's own `tools.exec.security` and `approvals.exec` settings.

### QMD (Local Search)
- Installed globally via npm
- Workspace collection indexed + embedded
- Commands: `qmd search`, `qmd query` (hybrid+reranking), `qmd vsearch`
- MCP server: `qmd mcp` or `qmd mcp --http`
- Re-index: `qmd update`, re-embed: `qmd embed`

### X Research Skill
- Installed to OpenClaw skills dir
- `X_BEARER_TOKEN` configured in ~/.zshrc
- CLI: `bun run x-search.ts search "<query>"` from skill dir
- Status: ✅ Active ($5 credits loaded)

### YouTube-to-Doc
- Installed at /tmp/youtube-to-doc with Python venv
- Start server: `~/bin/yt2doc` → runs on localhost:8000
- Converts YouTube videos to structured docs for LLM consumption

### xAI / Grok API
- API key configured (XAI_API_KEY in ~/.zshrc)
- Endpoint: https://api.x.ai/v1 (OpenAI-compatible)
- Models: grok-4-1-fast-non-reasoning ($0.20/$0.50 per M), grok-4-1-fast-reasoning, grok-imagine-image ($0.02/img)
- Use case: cheap sub-agents, background tasks, X-native research, image gen
- 2M context window on fast models
- Status: ✅ Active

### Schematron-3B
- API model at inference.net — converts HTML → typed JSON
- Endpoint: https://api.inference.net/v1
- Use case: web scraping, structured data extraction
- API key: configured (INFERENCE_NET_API_KEY)
- Status: ⚠️ Model not yet in /v1/models list — may need separate endpoint
- Also available via this key: DeepSeek R1, Llama 3.3 70B, Qwen3, GPT-OSS 120B

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
