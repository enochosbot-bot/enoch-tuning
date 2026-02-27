# Security Hardening Review — 2026-02-16
## Source: Deacon's IT Security Specialist
## Status: 🟡 FUTURE WORK — Not implementing immediately. These are next steps to harden against outside attacks. Will revisit at a later date.

---

## 1. Data Processing Transparency
**Issue:** Claiming "data never leaves your machine" is inaccurate. Local storage ≠ local processing. Every request sends context (SOUL.md, USER.md, MEMORY.md, conversation history) to Anthropic/OpenAI for processing.
**Action:** Correct any docs/presentations to distinguish between local *storage* and remote *processing*. Anthropic's API policy says no training on API data, but the data still transits their servers.
**Effort:** Low | **Priority:** High (accuracy matters for RIA compliance)

---

## 2. Clean-Room Sub-Agent for Cloud Requests
**Issue:** A long-running local LLM accumulates context. As the window fills, instructions about data sanitization get deprioritized. One sloppy request leaks sensitive data to cloud providers.
**Action:** When running a local LLM orchestrator, use a dedicated sub-agent pattern for cloud requests. Each invocation gets a fresh context window with complete sanitization instructions. The sub-agent receives only curated/sanitized data, does the work, returns the result, and dies. No context bleed.
**Architecture:**
- Local model (Ollama) = orchestrator, holds all sensitive context
- Spawnable cloud agent = fresh each time, strict data handling rules in system prompt
- OpenClaw's `sessions_spawn` already supports this pattern
**Effort:** Medium | **Priority:** High (when local LLM is primary)

---

## 3. Tirith Doesn't Protect OpenClaw
**Issue:** Tirith hooks into the interactive zsh shell via `eval "$(tirith init)"`. OpenClaw executes commands via Node.js `child_process.spawn()`, which never touches the interactive shell. Tirith is watching the front door while OpenClaw goes through a side entrance.
**Action:**
- Update TOOLS.md to reflect this limitation honestly
- Investigate alternatives: exec allowlists at OpenClaw config level, wrapper scripts with validation, OS-level auditing (OpenBSM on macOS)
- OpenClaw's own `approvals.exec` and `tools.exec.security` settings are the actual control plane
**Effort:** Low (docs update) / Medium (alternative controls) | **Priority:** Medium

---

## 4. API Keys Out of ~/.zshrc
**Issue:** API keys for Anthropic, OpenAI, xAI, X Bearer, Inference.net are all plaintext in `~/.zshrc`. Any process running as the user can read them. Malware's dream.
**Action (pick one):**
- **Apple Keychain (recommended):** `security add-generic-password -s "anthropic-api" -a "enoch" -w "sk-..."` then export via `export KEY=$(security find-generic-password -s "anthropic-api" -w)` in zshrc
- **`.env` file:** `chmod 600 ~/.openclaw/.env`, OpenClaw loads at startup
- **1Password CLI:** Already have the skill installed
**Migration steps:**
1. Extract all keys from ~/.zshrc
2. Store in Keychain
3. Replace zshrc exports with Keychain lookups
4. Verify OpenClaw + skills still resolve keys
5. Delete plaintext keys from zshrc, confirm with `source ~/.zshrc`
**Effort:** Medium | **Priority:** High

---

## 5. Immutable Personality Files
**Issue:** SOUL.md is writable by the agent. A prompt injection could instruct the agent to rewrite its own personality — making it compliant, exfiltrative, or malicious. The soul should be locked.
**Action:**
1. Finalize SOUL.md, AGENTS.md, IDENTITY.md, HEARTBEAT.md
2. `chown root:staff` + `chmod 444` (read-only, agent can't modify even if instructed)
3. Edits only through manual terminal workflow: `sudo chmod 644`, edit, `sudo chmod 444`
4. Consider a git pre-commit hook that flags changes to these files
**Files to lock:**
- SOUL.md
- AGENTS.md
- IDENTITY.md
- HEARTBEAT.md
- Any future security policy files
**Effort:** Low | **Priority:** High

---

## 6. Docker Sandboxing
**Issue:** Both agents run with `"sandbox": {"mode": "off"}` — full filesystem and exec access. A prompt injection that achieves code execution has unrestricted access.
**Action:**
- Enable OpenClaw's Docker sandbox mode
- Mount only specific directories (workspace, memory, scripts)
- Restrict network access where possible
- Tiered approach:
  - **Enoch (main):** Sandboxed with specific volume mounts
  - **Sub-agents/cron:** Heavily sandboxed, minimal access
  - **Arnold (security):** Needs host access for audits — elevated escape hatch or less sandboxed
**Tradeoffs:** Skills needing host access (Peekaboo, openhue, voice) need careful volume mounts. Mac mini arm64 + Docker Desktop handles this fine.
**Effort:** High | **Priority:** Medium (big uplift but significant config work)

---

## 7. Granular Google OAuth Scopes
**Issue:** One OAuth credential with full access to email, calendar, Drive. One compromised token = full account access.
**Action:** Create multiple OAuth credentials in Google Cloud Console:
1. **Read-only email** — inbox search, read, no send
2. **Email metadata only** — headers, subjects, senders, no body
3. **Read-only calendar** — view events, no create/modify
4. **Read-only Drive** — access files, no delete/share
5. **Agent send account** — separate Gmail (e.g. `enoch.agent@gmail.com`) for outbound. Sends as itself, can CC Deacon, never impersonates.
**Why this matters for RIA:** Clear audit trail, minimal blast radius per key, no AI impersonation risk with clients.
**Effort:** Medium | **Priority:** High

---

## 8. Change Default Gateway Port
**Issue:** Port 18789 is the documented OpenClaw default. Anyone who reads the GitHub repo knows to scan for it.
**Action:** Change to a random high port (30000-60000 range). Update in:
- `openclaw.json` → `gateway.port`
- LaunchAgent plist → `--port` arg
- Any scripts referencing the port
**Effort:** Low | **Priority:** Low (already on loopback, but why make it easy)

---

## 9. CrowdStrike / Enterprise EDR Awareness
**Issue:** CrowdStrike published a detection & removal guide for OpenClaw on corporate networks. If Spectrum runs EDR, an unauthorized OpenClaw instance gets flagged.
**Action:** For Spectrum presentation, position as:
- IT-approved deployment on dedicated hardware (not shadow IT)
- Or get whitelisted through compliance
- Never run on a corporate-managed endpoint without approval
**Effort:** N/A (awareness) | **Priority:** High (for presentation)

---

## Recommended Execution Order
1. **API keys out of zshrc** → Keychain migration (high impact, medium effort)
2. **Immutable personality files** → chmod today (high impact, low effort)
3. **Change gateway port** → quick win (low effort)
4. **Correct data processing claims** → update presentation/docs (low effort)
5. **Granular OAuth scopes** → Google Cloud Console work (medium effort)
6. **Tirith docs update** → honest assessment in TOOLS.md (low effort)
7. **Docker sandboxing** → biggest project, plan and execute (high effort)
8. **Clean-room sub-agent** → when local LLM goes primary (medium effort)
9. **CrowdStrike awareness** → fold into Spectrum pitch (no effort)
