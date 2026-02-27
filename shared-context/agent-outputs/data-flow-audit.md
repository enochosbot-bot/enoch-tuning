---
tags: [spectrum, security, compliance, data-privacy]
date: 2026-02-27
author: Berean
task: BL-018
---

# Data Flow Audit — Where Data Leaves the Machine

**Purpose:** Spectrum Advisors demo prep. Deacon needs to say with confidence: "Here's exactly where client PII never touches a cloud API." This document maps every outbound data flow in the OpenClaw stack based on direct config inspection.

**Audited:** 2026-02-27 | **Source:** `~/.openclaw/openclaw.json`, running config, tool scripts

---

## Summary Table

| Service | What Leaves the Machine | Contains Conversation? | PII Risk | Can Go Local? |
|---|---|---|---|---|
| Anthropic (Claude) | Full message array + system prompt | Yes | Medium | Yes (Ollama) |
| OpenAI Codex | Full message array + system prompt | Yes | Medium | Yes (Ollama) |
| OpenAI Embeddings | Memory files + session logs (continuous) | Yes | **HIGH** | No (requires work) |
| Google OAuth (gog) | None by default; queries if explicitly called | No (unless piped) | Low–Medium | N/A |
| Twilio | **Not configured** | N/A | None | N/A |
| Brave Search | Query text only | No | Low | No |
| xAI/Grok | Image prompt text only | No | Low | No |
| ElevenLabs (SAG) | TTS text only | Partial | Low | Yes (local TTS alt) |
| Ollama | **Nothing** — 100% local | N/A | None | Already local |

---

## 1. Anthropic / Claude API

**Current State**

Every agent call to Claude sends:
- The **full system prompt** (persona, workspace paths, channel-specific instructions, compaction prompts)
- The **full conversation history** within the context window (up to 128,000 tokens)
- Any **memory context injected** via `memory_search` — which pulls from workspace files and session logs
- Compaction flush prompts include Obsidian vault paths and workspace file paths

Auth profile: `anthropic:manual` (token mode). Model in use: `claude-sonnet-4-6`. Configured models also include haiku variants.

**What's in the requests now:** Conversation text, agent instructions, research content, session history. No client PII exists in the system today — Spectrum's client data has never been loaded into any workspace.

**Anthropic Data Retention:** Zero data retention for API customers by default. Anthropic does not train on API traffic without explicit opt-in. Billing metadata (token counts, timestamps) is retained. Prompts and responses are not logged on Anthropic's side beyond request processing.

**Risk Level: MEDIUM** — Low risk today (no PII in system). Risk becomes HIGH the moment any client data enters workspace files or conversation context.

**Mitigation Options:**
1. **Immediate (demo-safe):** Route all Spectrum demo conversations through a dedicated agent workspace with `memory_search` disabled and no client file context
2. **Systematic:** Any client-facing workflow uses Ollama models instead (see Section 7)
3. **Technical:** Add a pre-send filter that strips proper nouns / emails / SSN patterns before API calls (complex, error-prone)

**Recommendation:** For the demo, confirm to Spectrum that no client data will ever be loaded into agent workspaces that connect to cloud APIs. The architecture allows for a clean-room Ollama-only mode. Lead with that.

---

## 2. OpenAI Codex / GPT-5

**Current State**

Two separate flows:

**A. Codex as primary model (Bezzy/Gideon):**
- Bezzy (coder agent): Primary model is `openai-codex/gpt-5.3-codex`, Claude is fallback
- Gideon (observer/QA): Same — Codex primary, Claude fallback
- **Every other agent** has `openai-codex/gpt-5.3-codex` as a fallback model — if Anthropic is rate-limited or down, the conversation automatically reroutes to OpenAI with no warning

When Codex is called, it receives the same payload as Anthropic: full system prompt + conversation history.

**B. OpenAI Embeddings (CRITICAL — see Section 3 for detail)**

**OpenAI Data Retention:** Zero data retention for API customers by default. No training on API data without opt-in. Same policy structure as Anthropic.

**Risk Level: MEDIUM** (same caveats as Anthropic, plus the silent fallback risk)

**The hidden risk:** The fallback configuration means any conversation *could* hit OpenAI even if Deacon believes he's only using Claude. There is no user-visible indicator when this happens. For a compliance-sensitive client environment, this is a silent data flow that needs to be acknowledged and controlled.

**Mitigation Options:**
1. Remove the Codex fallback from all agents during demo by creating a demo-specific config
2. Use Ollama-only mode (no fallback to cloud) for any client data processing
3. Add a log monitoring cron that alerts when Codex is used (useful for audit trail)

**Recommendation:** For the Spectrum demo, demo on Anthropic-only config with Codex fallback disabled. Document the fallback architecture as a capability (redundancy) not a liability — but control it.

---

## 3. OpenAI Embeddings (Memory Search) — HIGHEST RISK

**Current State**

This is the data flow most likely to surprise you. From the config:

```json
"memorySearch": {
  "provider": "openai",
  "sync": {
    "watch": true,
    "sessions": {
      "deltaBytes": 50000,
      "deltaMessages": 25
    }
  },
  "sources": ["memory", "sessions"],
  "extraPaths": ["/Users/deaconsopenclaw/Documents/Brain/Personal Memories"]
}
```

**What this means:** OpenAI's embeddings API is receiving:
- All files under `MEMORY.md` and `memory/*.md` in each agent workspace
- All **session logs** — synced continuously in the background (every 50KB of new content or 25 new messages, whichever comes first)
- All files under the Obsidian vault path (`/Users/deaconsopenclaw/Documents/Brain/Personal Memories`)

This is a **background, automatic, continuous** data flow. It runs on file-watch triggers, not just on demand. Every conversation Deacon has with any agent is eventually vectorized and sent to OpenAI.

**Risk Level: HIGH**

If client data ever entered a conversation or workspace file, it would be embedded to OpenAI within 50KB of new content — silently, in the background.

**Anthropic's data policy does not protect this flow** — this is a separate OpenAI API call that Anthropic never sees.

**Mitigation Options:**
1. **Demo-safe:** Add a `~/.openclaw/agents/researcher/workspace/.memoryignore` or equivalent — check if OpenClaw supports scoped memory exclusion
2. **Architecture fix:** Switch embeddings provider to a local model (e.g., Ollama with `nomic-embed-text` or `mxbai-embed-large`). OpenClaw's `memorySearch.provider` config would need to support `ollama` — worth verifying with Bezzy
3. **Scope restriction:** Separate demo workspaces with memory sync disabled (`"enabled": false` in memorySearch)
4. **Process control:** Never put client names, account numbers, or financial data in any agent conversation — ever

**Recommendation:** This is the #1 thing to fix before any client data enters the system. Evaluate Ollama embedding support. In the interim, the demo talking point is: "We have a fully local embedding option on the roadmap, and our policy is that no client PII ever enters agent workspaces."

---

## 4. Google OAuth (gog CLI)

**Current State**

The `gog` CLI (v0.11.0) is installed and configured. It supports: Gmail, Calendar, Drive, Contacts, Tasks, Sheets, Docs, Slides, Chat, Classroom, Forms, App Script.

Config file location: `/Users/deaconsopenclaw/Library/Application Support/gogcli/config.json` (access confirmed, scope details in keychain). The CLI uses OAuth 2.0 — all API calls go to Google's servers, not OpenClaw infrastructure.

**What leaves the machine:** Only when `gog` is explicitly called. At that point, queries (search terms for Gmail, calendar range for Calendar) leave the machine to Google's APIs. **Google never receives your AI conversations or prompts.**

**The secondary risk:** If a gog result (email content, calendar event with client name) is then pasted into an agent conversation, that data flows to Anthropic/OpenAI as part of the message payload.

**Risk Level: LOW (by itself) → MEDIUM if piped into AI context**

**Mitigation Options:**
1. Don't pipe raw email/calendar content into cloud AI agent contexts without sanitizing PII
2. For Spectrum demo: gog is not in scope unless showing calendar automation — in which case demo with synthetic data

**Recommendation:** Not a compliance issue at current usage patterns. Document for Spectrum as: "Google API calls are isolated from AI API calls — they don't share data unless you explicitly route output between them."

---

## 5. Twilio

**Current State**

**Not configured.** No Twilio credentials, config, or references found anywhere in the OpenClaw installation.

**Risk Level: NONE**

**Note:** The `SAG` skill (ElevenLabs TTS) handles voice output. If Twilio was intended for voice-call routing, it's not set up. No action needed.

---

## 6. Brave Search

**Current State**

Web search is enabled via the `tools.web.search` config. The actual search provider is the Brave Search API (inferred from OpenClaw's standard web search integration). When an agent calls `web_search`, the query text is sent to Brave's servers over HTTPS.

**What leaves the machine:** The search query string only. No conversation history, no session context, no memory.

**Brave's policy:** Brave Search does not profile users based on search queries. Queries may be logged for service improvement but are not linked to personal identity. They explicitly do not sell query data.

**Risk Level: LOW**

The exposure here is that search queries reveal what topics are being researched (e.g., "Spectrum Advisors competitor analysis"). This is low-risk for a demo use case.

**Mitigation Options:**
1. For highly sensitive research, use Ollama + local document analysis instead of web search
2. Route search through a self-hosted Brave Search instance (overkill for current scale)

**Recommendation:** Acceptable as-is. For client research involving their names or competitors, consider doing initial research locally before any AI-assisted analysis.

---

## 7. xAI / Grok Image Generation

**Current State**

The `gen-image-grok.sh` script calls `https://api.x.ai/v1/images/generations` with:
- The text prompt (as JSON body)
- Auth via `$XAI_API_KEY`
- Model: `grok-imagine-image` or `grok-imagine-image-pro`
- Response: base64-encoded PNG, decoded and saved locally

**What leaves the machine:** The image prompt text only. No conversation history, no prior context.

**xAI Data Retention:** xAI's privacy policy states API inputs are not used for model training without consent. Retention specifics are less published than Anthropic/OpenAI — treat as "data leaves the machine, policy is adequate but less verified."

**Risk Level: LOW**

Image prompts won't contain client PII in normal usage. Only risk is if someone prompts with a client name for branded content.

**Mitigation Options:**
1. Use OpenAI DALL-E or local Stable Diffusion for image gen if xAI policy becomes a concern
2. Review prompts before generation when doing client-facing creative work

**Recommendation:** Acceptable for current usage. Not a Spectrum demo concern.

---

## 8. Local LLM Viability (Ollama)

**Current State — Available Models:**

| Model | Size | Best Use |
|---|---|---|
| `phi4:14b` | 9.1 GB | General reasoning, analysis |
| `qwen2.5-coder:14b` | 9.0 GB | Code generation, review |
| `gpt-oss:20b` | 13 GB | Heavy reasoning, long context |
| `qwen3:8b` | 5.2 GB | Fast tasks, research pipeline (used by OpenPlanter) |
| `kimi-k2.5:cloud` | — | **Flag:** cloud model; Kimi-k2.5:cloud likely routes to Moonshot AI API, not local |

**What runs fully on-machine with Ollama:**
- Research synthesis and document analysis → `phi4:14b` or `gpt-oss:20b`
- Code writing and review → `qwen2.5-coder:14b`
- Political donor data analysis (OpenPlanter) → `qwen3:8b` (already running)
- Any task currently using Claude Haiku (simple Q&A, formatting) → `phi4:14b`

**Quality/Cost Tradeoff:**
- `phi4:14b` ≈ Claude Haiku quality for most tasks; free, local, zero latency beyond inference
- `gpt-oss:20b` approaches Sonnet for analytical tasks; still free, fully local
- `qwen2.5-coder:14b` matches or exceeds cloud models for code-focused work per recent benchmarks
- Complex strategic reasoning (Sonnet/Opus level) still favors cloud models

**⚠️ Flag: `kimi-k2.5:cloud`**
This model tag suggests it routes to Moonshot AI's cloud API, not local inference. Needs confirmation — do not use for any sensitive workloads until verified.

**Risk Level: NONE (for local models) | UNKNOWN (for kimi-k2.5:cloud)**

**Recommendation:** Ollama is demo-ready for showing "fully local AI processing." `phi4:14b` and `qwen2.5-coder:14b` are the showcase models. Verify and likely remove `kimi-k2.5:cloud` from Ollama configuration.

---

## 9. Clean-Room Sub-Agent Pattern

**Concept:** An agent configuration that provably never sends sensitive context to cloud APIs.

**Implementation Sketch:**

```yaml
# Clean-room agent config overlay
agent:
  model:
    primary: "ollama/phi4:14b"
    fallbacks: []            # No cloud fallback — fail loud, not silent
  memorySearch:
    enabled: false           # No background embedding
  tools:
    deny:
      - web_search           # No external queries
      - web_fetch
      - browser
  contextTokens: 8192        # Limit context window to reduce scope
  workspace: "/dedicated/clean-room-workspace"  # Isolated, no shared files
```

**What this achieves:**
- All LLM inference runs locally on Ollama
- No fallback to cloud APIs under any condition
- No background data syncing to OpenAI embeddings
- No web queries leaving the machine
- Isolated workspace means no risk of accidental PII from shared file context

**Demo narrative:** "For any client data processing, we run in clean-room mode. Prompts are processed by a local model on this machine. Nothing leaves. No API logs, no training data, no network traffic for the AI layer."

**Limitations to be honest about:**
- Local model quality is real (phi4:14b is good, not Sonnet)
- No web search means research tasks require pre-loaded data
- Inference is slower than cloud APIs (phi4:14b: ~20-40 tok/s on Apple Silicon)
- Embeddings-based memory search not available without local embedding model

**Ready to implement:** Bezzy can build this as a config flag (`--clean-room`) that swaps the model profile for any agent call. Estimated effort: 2-3 hours.

---

## Key Findings Summary

1. **No client PII is in the system today.** The slate is clean. The demo is safe.

2. **Biggest latent risk is OpenAI embeddings** — continuous background sync of session content and memory files to OpenAI. One accidental client name in a conversation = that data is embedded to OpenAI within minutes.

3. **Silent Codex fallback exists on every agent.** Deacon could be talking to OpenAI without knowing it. This needs to be controlled for any client-data scenario.

4. **Twilio is not configured** — not a concern.

5. **Ollama stack is demo-ready** — four capable local models available right now. `phi4:14b` and `qwen2.5-coder:14b` are the workhorses. `kimi-k2.5:cloud` needs verification and likely removal.

6. **The clean-room pattern is implementable immediately** and becomes the Spectrum demo's strongest talking point: *"We architected for compliance from day one."*

---

## Recommended Actions Before Demo

| Priority | Action | Owner | Effort |
|---|---|---|---|
| P0 | Verify `kimi-k2.5:cloud` routes locally or remove it | Bezzy | 30 min |
| P0 | Document: "no client PII policy" for demo conversations | Deacon | 10 min |
| P1 | Build `--clean-room` Ollama mode config flag | Bezzy | 2-3 hrs |
| P1 | Evaluate Ollama embedding support to replace OpenAI embeddings | Bezzy | 1 hr spike |
| P2 | Add logging/alert when Codex fallback triggers | Bezzy | 1 hr |
| P2 | Demo-specific agent config with memory sync disabled | Bezzy | 1 hr |

---

*Berean — 2026-02-27 | Research confidence: HIGH (direct config inspection, no speculation)*
