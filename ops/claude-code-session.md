# Claude Code Session — Queued Changes

These all need to be done from the terminal (Claude Code), not Telegram.
When you're ready, open Terminal, type `claude`, and work through these.

---

## 1. API Keys → Apple Keychain
- Move all API keys out of ~/.zshrc into Apple Keychain
- Keys to migrate: Anthropic, OpenAI, xAI, X Bearer Token, Inference.net, ElevenLabs
- Test each one resolves before deleting plaintext
- ~15 min

## 2. Change Gateway Port
- Pick a random high port (30000-60000)
- Update `~/.openclaw/openclaw.json` → `gateway.port`
- Update LaunchAgent plist → `--port` arg
- Restart gateway, verify it comes back
- ~5 min

## 3. Docker Sandboxing
- Enable sandbox mode for agents
- Mount only specific directories (workspace, memory, scripts)
- Test that skills still work with restricted access
- Tiered: sub-agents heavily sandboxed, main agent less so
- ~1-2 hours (biggest item)

## 4. Granular Google OAuth Scopes
- Create multiple OAuth credentials in Google Cloud Console
- Read-only email, read-only calendar, read-only Drive
- Separate agent Gmail for sending (optional)
- Swap `gog` config to use scoped keys
- Test each scope works, then revoke blanket key
- ~30 min

## 5. Tailscale Setup (replaces ngrok)
- Open Tailscale.app, sign in
- Get Tailscale hostname/IP
- Update voice-call config to use Tailscale funnel
- Update Twilio webhook URL
- Kill all ngrok references from config
- ~15 min

---

## 6. Lock Personality Files (root-owned, read-only)
- Run from terminal:
```bash
cd ~/.openclaw/workspace
sudo chown root:staff SOUL.md AGENTS.md IDENTITY.md HEARTBEAT.md
sudo chmod 444 SOUL.md AGENTS.md IDENTITY.md HEARTBEAT.md
```
- Verify Enoch can still read them (send a message, check he responds normally)
- To edit later: `sudo chmod 644 SOUL.md` → edit → `sudo chmod 444 SOUL.md`
- ~2 min

---

## 7. Per-Agent Tool Restrictions
- Ezra (scribe): allow only `read, write, edit, exec, web_search, web_fetch, image, memory_search, memory_get`
- Bezzy (coder): allow only `read, write, edit, exec, process, web_search, web_fetch`
- Neither gets `gateway, message, cron, sessions_spawn, voice_call`
- Prevents sub-agents from touching infrastructure or sending external comms
- Uses OpenClaw's per-agent tool allow/deny lists in config
- ~10 min

## 8. Promote Arnold to Full Agent (future)
- Currently a system prompt persona on topic 3 — shares Enoch's full permissions
- Should be own agent with scoped-down permissions: read-only filesystem, network scanning, no write outside audit reports
- Lower priority — do after sandboxing is in place
- ~30 min

## 9. Config Auto-Rollback Watchdog
- Snapshot current working config before any change
- If gateway doesn't come back within 60 seconds of restart, auto-restore last known good config
- "Windows Safe Mode" concept for OpenClaw
- Prevents the Ollama incident from ever happening again
- ~30 min

---

## Total estimated time: ~4-5 hours
Can be broken into multiple sessions.
