# Data Flow Audit — Spectrum Advisors Pitch
## Prepared by: Berean (Research & Intelligence)
## Date: 2026-02-26
## Classification: Internal — Pitch Preparation

---

## 1. Executive Summary

**For the pitch room — say these four things:**

- **"We don't store client data in the cloud. The system lives on a dedicated Mac mini in our office. Client files, CRM data, and conversation history never leave that machine."** The distinction that matters: data is *stored* locally. Processing (reasoning, analysis) happens via cloud APIs, but nothing is retained on the provider's servers after the request completes.

- **"The major AI providers — Anthropic and OpenAI — explicitly do not train on API data. That's in their contracts. We can sign a Data Processing Addendum with both."** This is the policy line that holds up under compliance review.

- **"For anything that touches a real client name, account number, or financial data, we can route that work to a local AI model that never calls the internet at all."** We have four local models running on-device. Sensitive analysis stays on the machine.

- **"We're proposing this as a firm-managed, IT-approved deployment — not shadow IT. One machine, audited config, full data flow documentation."** This answers the CrowdStrike/EDR concern before it's raised.

---

## 2. Cloud Data Flows

What actually leaves the machine, and where does it go:

| Service | What's Sent | Retention Policy | Risk Level |
|---|---|---|---|
| **Anthropic (Claude)** | Full conversation history + system prompt + any injected workspace context (up to 128K tokens per request) | Zero training on API data per API TOS. Request data not stored after processing. DPA available. | 🟡 Medium — data transits their servers in-flight |
| **OpenAI (GPT Codex)** | Same as above — full context window per request. Also used for memory embeddings (semantic search over past sessions). | Zero training on API data by default. DPA available. | 🟡 Medium — memory embeddings add a secondary data stream |
| **xAI / Grok** | Requests routed to `api.x.ai/v1`. Currently used for sub-agent tasks and image generation. Same context-window-per-request model. | xAI policy: does not train on API data. DPA status: less established than Anthropic/OpenAI. | 🟡 Medium — newer provider, less compliance documentation |
| **inference.net** | API calls for structured data extraction (Schematron-3B) and access to DeepSeek, Llama, Qwen3 models. | Startup provider — data retention policy not formally documented. | 🔴 High — limited compliance documentation; avoid for client data |
| **Google (YouTube + Photos)** | OAuth token scopes: `youtube.readonly`, `photoslibrary.readonly`. Read access only. No client data flows here. | Google API standard policy. | 🟢 Low — read-only, no financial data involved |
| **Google OAuth (gog skill — Gmail/Calendar/Drive)** | If enabled: email bodies, calendar events, Drive file content sent to Google servers for OAuth operations. | Google API standard policy. | 🟡 Medium — currently scoped broadly; prior audit flagged for scope reduction |
| **X / Twitter API** | Search queries and bookmark reads. OAuth scopes: `bookmark.read`, `tweet.read`, `users.read`. Read-only. No client data involved. | Twitter/X API standard policy. | 🟢 Low — no client data involved |
| **ElevenLabs (TTS/sag)** | Text sent for speech synthesis. If someone reads a client document aloud, that text goes to ElevenLabs. | ElevenLabs API standard policy. | 🟡 Medium — watch what text gets passed to TTS |
| **Google Places (goplaces)** | Location search queries. No client data flows here. | Google API standard policy. | 🟢 Low |
| **Notion API** | Notion page/database content sent/received. Only flows if agent is directed to write to Notion. | Notion API standard policy. | 🟡 Medium — depends entirely on what gets written |
| **Telegram (channel)** | Agent messages + user messages routed through Telegram servers. Bot token authenticated. | Telegram standard policy. | 🟡 Medium — Deacon's queries and agent responses transit Telegram |
| **Brave Search (web_search tool)** | Search query strings sent to Brave Search API. No conversation context — query only. | Brave Search API: queries are logged with IP; retention period not publicly specified. | 🟡 Medium — avoid searching for client names directly |
| **Twilio** | ✅ **Removed from deployment.** Voice/transcription capability not present in current config. | N/A | 🟢 None |

**Memory system note:** The embedded memory search (`memorySearch`) uses **OpenAI as the embedding provider**. This means memory snippets — which may include summaries of past conversations — are vectorized via OpenAI's API. If a past session included client references, those could be in the embedding pipeline.

---

## 3. Local-First Zones

Tasks that can run **100% on-device** with zero cloud API calls, using the four available Ollama models:

| Task Category | Recommended Model | Notes |
|---|---|---|
| **CRM data analysis** (Redtail export parsing, flagging missing info) | `gpt-oss:20b` or `phi4:14b` | Strong instruction-following; handles structured data well |
| **Client document summarization** (meeting notes, RIA forms) | `phi4:14b` | Reasoning-capable, good for document comprehension |
| **Template drafting** (ADV updates, client letters with PII) | `phi4:14b` | Solid prose; appropriate for first-draft work |
| **Email triage** (classify, prioritize, flag) | `qwen3:8b` | Fast enough for high-volume classification |
| **Code and script generation** (internal automations, no client data) | `qwen2.5-coder:14b` | Purpose-built for code; excellent at structured output |
| **PII detection/redaction** (scan documents before cloud processing) | `qwen3:8b` or `phi4:14b` | Can be prompted to extract and redact identifiers |
| **Form pre-fill** (pull fields from documents, validate structure) | `gpt-oss:20b` | Large context, good at extraction tasks |

**Honest capability gap:** Local models at 8B–20B parameters are meaningfully behind Claude Sonnet for complex multi-step reasoning, nuanced writing tone, and research synthesis. For compliance-sensitive tasks the gap is acceptable. For writing that represents the firm externally, review before sending.

**`kimi-k2.5:cloud`** is listed in Ollama but routes to a cloud endpoint. Do not use for client data — treat it the same as any cloud API.

---

## 4. Clean-Room Pattern

**The problem:** When an AI agent accumulates a long context window, its session may contain both public research and a client name dropped in passing. That whole context goes to the cloud model on the next request — including the PII.

**The solution — two-zone architecture:**

```
ZONE A — Local (Ollama, never hits internet)
├── All raw client data input
├── PII extraction and redaction
├── CRM data analysis
└── Produces: sanitized output (no names, no account numbers)

ZONE B — Cloud (Claude/GPT, full capability)
├── Receives ONLY sanitized summaries from Zone A
├── Handles: research, drafting, strategy
└── Returns: polished output to local orchestrator
```

**How to implement this today:**

1. **Tag sessions by data type.** Conversations that involve client data stay in a local-only Ollama session. When that session needs to call a cloud model, it first runs a redaction step.

2. **Use the sub-agent pattern as the firewall.** OpenClaw's `sessions_spawn` creates a fresh context window with zero inherited history. When passing work from a client-data session to a cloud model, spawn a clean sub-agent with only the sanitized summary in its initial prompt. The sub-agent does its work and terminates. No context bleed.

3. **System prompt enforcement.** Add to any cloud-facing sub-agent's system prompt: *"You may receive financial context. Never repeat back account numbers, SSNs, client full names, or addresses. If your input contains these, replace with [REDACTED] in any output you produce."* This is a second line of defense.

4. **Audit what gets embedded.** The memory search system sends session content to OpenAI for embedding. Review what's in `/Users/deaconsopenclaw/Documents/Brain/Personal Memories/` before enabling memory on client-data sessions. Or disable `memorySearch` for the agent handling client work until a local embedding model is wired in.

**Practical workflow for Spectrum:**

- Client note arrives → Ollama reads and extracts action items (local)
- Action items (sanitized, no PII) → Claude drafts the follow-up email
- Advisor reviews → sends from their own email client

No client name, address, or account number ever leaves the machine in this flow.

---

## 5. Compliance Talking Points

Language Deacon can use verbatim with Spectrum's compliance team:

> **"Anthropic and OpenAI have explicit API data policies stating they do not train their models on API request data. Both offer Data Processing Addendums — the same type of agreement financial services firms sign with any technology vendor. We can have those in place before we touch a single client record."**

> **"The system operates under a local-first architecture. Client data is stored on a machine we own and control. Cloud APIs are used for reasoning tasks, but they function like a calculator — you send it a problem, it sends back an answer, nothing is retained."**

> **"For any workflow involving identifiable client information — names, account numbers, Social Security numbers — we route that through a local AI model that has no internet connection. The cloud models only see anonymized summaries."**

> **"This is not shadow IT. We're proposing a firm-managed deployment: one machine, documented configuration, auditable data flows — the same diligence you'd apply to any third-party software vendor."**

> **"We're aware of CrowdStrike's guidance on AI tooling in corporate environments. The deployment we're proposing is designed to be IT-approved and whitelisted, not run around your controls."**

**For the ADV Part 2A / compliance manual angle:** AI-assisted drafting tools are increasingly being addressed in RIA compliance programs. The key documentation requirements are: (1) what data the tool accesses, (2) who controls it, (3) how errors are caught. All three are answerable with this setup.

---

## 6. Open Questions

Things we don't know yet — and where to get the answers:

| Question | Why It Matters | How to Get the Answer |
|---|---|---|
| **Does Spectrum's current tech stack (Redtail, eMoney) have existing API data agreements we'd need to layer with?** | Any integration with Redtail/eMoney data would need to comply with their vendor agreements. | Ask Spectrum's ops/compliance lead; review their current vendor agreements. |
| **What is Brave Search's documented data retention period for API queries?** | If we use web search in research workflows, queries are logged. Need specifics for compliance docs. | Email Brave Search API support or check their API developer docs / privacy policy more carefully. |
| **Is xAI's Data Processing Addendum available, and has it been reviewed?** | xAI is newer; their compliance documentation is less mature. If Grok is used in workflows, this needs review. | Check [x.ai/api](https://x.ai) DPA documentation; contact xAI enterprise if needed. |
| **What is inference.net's data retention policy?** | Currently flagged as high-risk due to limited documentation. | Review inference.net privacy policy; if no formal DPA is available, remove from any client-facing workflow. |
| **What is the embedding scope of the OpenAI memory system?** | Memory embeddings may contain session content that includes client references from Deacon's personal use. | Audit the memory store at `/Users/deaconsopenclaw/Documents/Brain/Personal Memories/`; review what's in the embedding index (`qmd` collection). |
| **Does Spectrum have an existing AI use policy or are we writing the first one?** | If there's an existing policy, we need to fit within it. If there isn't one, this deployment could anchor the first draft. | Ask compliance lead directly in the pitch. Offering to draft the policy is a strong move. |
| **What compliance framework does Spectrum operate under — SEC, state-level, or dual?** | SEC-registered RIAs have stricter requirements than state-registered. Shapes how aggressive we need to be on data handling. | Check Spectrum's ADV Part 1 (public on SEC EDGAR). |

---

*Sources: openclaw.json (live config audit), TOOLS.md (integration notes), security-hardening-review_2026-02-16.md (prior security audit), Anthropic API Terms of Service, OpenAI Enterprise Privacy Commitments, direct config file inspection of Google OAuth token scopes.*

*Confidence level: HIGH on local config facts (directly audited). MEDIUM on provider retention policies (based on published policies, subject to change). LOW on Spectrum-specific compliance requirements (not yet gathered).*
