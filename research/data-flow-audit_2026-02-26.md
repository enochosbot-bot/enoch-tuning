# Data Flow Audit Report: OpenClaw Deployment
**Prepared by:** Berean — Head of Research & Intelligence  
**Date:** 2026-02-26  
**Classification:** CONFIDENTIAL — Internal Use Only  
**Purpose:** RIA compliance pitch support — Spectrum Advisors AI automation proposal

---

## 1. Executive Summary

This audit maps every point where data leaves Deacon's local OpenClaw deployment and reaches a cloud provider's infrastructure. The core compliance question for any RIA operating under SEC Regulation S-P (Safeguard Rule) and FINRA Rule 4370 is binary: does client personally identifiable information (PII) — names, account numbers, portfolio data, financial positions — flow through systems the firm does not control? The answer for an unmitigated OpenClaw deployment is **yes, potentially**, through the Claude API, OpenAI API, Google OAuth integrations, Twilio voice/transcription, and ElevenLabs TTS, all of which receive whatever context is loaded into the request.

The good news is that **mitigation is architecturally solvable**. Anthropic's API (when used with zero data retention agreements available at the Enterprise tier), OpenAI's API, and xAI's API all explicitly commit that API traffic is **not used for model training by default** and can be configured for short or zero retention. The more meaningful risk is not that Anthropic will train on a client's account number — it's that a misconfigured agent could include a client's financial details in a prompt that transits unencrypted infrastructure, or that a practitioner will inadvertently paste PII into a system that logs it.

The clean-room implementation plan in Section 4 provides a concrete architecture: sensitive client data stays local (routed to Ollama-hosted models), general research and automation tasks use cloud APIs with PII-stripped prompts, and a tiered classification gate enforces the boundary. Properly implemented, this architecture allows Spectrum Advisors to use AI automation for productivity workflows while providing a defensible, documented position that no client financial data touches external AI inference infrastructure.

---

## 2. Per-Service Findings

### 2.1 Anthropic (Claude API)

**What data is sent:**  
Every API call sends the full conversation context — system prompt, all prior messages in the thread, and the current user message. For OpenClaw, this means the system prompt (which may contain persona/memory), any injected context (calendar events, email summaries, web results), and the user's query. Token limits define the window, but everything within that window transits Anthropic's US-based servers.

**PII exposure potential:**  
High if memory/context files are allowed to accumulate client data. If a user asks the agent "What's the status of Tom Miller's IRA rollover?" — that name, the implied account type, and any prior context about Tom Miller go to Anthropic's inference servers.

**Retention policy:**  
Anthropic's privacy policy (effective Jan 12, 2026) distinguishes two modes:
- **Consumer (data controller mode):** Conversations logged, potentially reviewed, may be used for model improvement unless opted out. Not relevant for API.
- **API/Commercial (data processor mode):** Anthropic acts as data processor on behalf of the operator. Per their policy: "This privacy policy does not apply to situations where Anthropic acts as a data processor." API inputs/outputs are **not used for model training** by default. Standard API retains request/response logs for up to 30 days for safety/abuse monitoring, then deletes. 
- **Enterprise/Zero Retention:** Enterprise agreements can include zero data retention (ZDR) — no logging of prompts or outputs. This is the tier to request.

**PII minimization options:**  
- Use a system prompt that explicitly instructs the agent not to include real client names or account numbers in requests.
- Build a PII scrubber layer that replaces identifiers with tokens ("Client-A," "Account-1") before sending to the API, and reverses them on return.
- Use local Ollama models for any query that requires specific client data.
- Sign a Data Processing Agreement (DPA) — Anthropic offers one for commercial customers.

**RIA Compliance Risk:** 🟡 **MEDIUM** (mitigatable to LOW with Enterprise ZDR + DPA + prompt engineering)

| Factor | Detail |
|--------|--------|
| API traffic training | No (opt-out by default for API) |
| Retention | 30 days standard; 0 days with ZDR |
| DPA available | Yes |
| US-based servers | Yes (AWS us-east-1) |
| Encryption in transit | TLS 1.2+ |

---

### 2.2 OpenAI API

**What data is sent:**  
Same structure as Anthropic — the full context window contents including system prompt, conversation history, and current message are sent on each API call. GPT-4o and o-series models also support vision (images), which could include scanned documents with PII.

**PII exposure potential:**  
High without guardrails. If the agent is helping draft client correspondence and has access to client notes, all that context transits OpenAI's servers.

**Retention policy:**  
- **API traffic is NOT used for training by default** as of March 2023 — OpenAI's Enterprise and API tiers explicitly do not train on user data unless the customer opts in.
- Standard API: OpenAI retains API inputs/outputs for **30 days** for abuse monitoring, then deletes. 
- Enterprise Zero Data Retention: available, request through account.
- OpenAI is SOC 2 Type II certified. DPAs available.

**PII minimization options:**  
Same as Anthropic: PII tokenization layer, restrict agent context to role-appropriate data, use local models for client-specific queries.

**RIA Compliance Risk:** 🟡 **MEDIUM** (mitigatable to LOW with ZDR + DPA)

| Factor | Detail |
|--------|--------|
| API traffic training | No (default off for API) |
| Retention | 30 days standard; 0 days with ZDR |
| DPA available | Yes |
| US-based servers | Yes (Azure infrastructure) |
| SOC 2 Type II | Yes |
| HIPAA BAA available | Yes (relevant precedent for sensitive data) |

---

### 2.3 Google (OAuth / Gmail / Calendar / Drive — gog CLI)

**What data is sent:**  
This is a fundamentally different risk category than the LLM APIs. When the gog CLI calls Gmail, Calendar, or Drive, it:
1. Reads data **from** Google's servers (data that already lives there)
2. May pass that data **to Claude** for processing (the second hop is where PII leaves local control)

The OAuth flow itself sends: the access token + the API call parameters to Google. Google already holds the email/calendar/drive data — the risk is what happens **after** gog reads it.

**OAuth scope analysis:**

| Scope | What it accesses | Send risk |
|-------|-----------------|-----------|
| `gmail.readonly` | Full email body, attachments, metadata | HIGH — emails may contain client PII |
| `gmail.send` | Compose/send as user | HIGH — could transmit PII outbound |
| `calendar.readonly` | Event titles, attendees, descriptions | MEDIUM — may contain client names/meetings |
| `drive.readonly` | File content | HIGH — may contain financial docs |
| `drive.file` | Specific files only | LOW-MEDIUM |

**Token storage:**  
OAuth refresh tokens stored locally in `~/.config/gog/` or equivalent. If the machine is compromised, tokens could be used to access Google data. This is a local security risk, not a cloud transmission risk.

**The second hop — what goes to Claude:**  
When gog reads an email and passes it to Claude for summarization, that email content (potentially including client names, account details, advisor notes) goes to Anthropic's servers. This is the critical control point.

**RIA Compliance Risk:** 🔴 **HIGH** (for Gmail/Drive with unfiltered Claude forwarding) | 🟡 **MEDIUM** (Calendar)

**Mitigation:**  
- Implement a content filter between gog output and Claude API calls — strip or redact client identifiers before forwarding.
- Limit scopes to minimum required (prefer `drive.file` over `drive.readonly`).
- Never pass full email threads involving clients to cloud LLMs.
- Use local Ollama models for processing Google data that contains client information.

---

### 2.4 Twilio (Voice / Transcription)

**What data is sent:**  
- **Voice calls:** Audio stream routed through Twilio's infrastructure. If call recording is enabled, the full audio file is stored on Twilio's servers.
- **Transcriptions:** Twilio's transcription service converts audio to text — this text is stored on Twilio servers and returned via API.
- **Call metadata:** From/To numbers, duration, timestamps, all logged.

**PII exposure potential:**  
Extreme if used for client advisory calls. Voice recordings of financial planning conversations contain maximum PII density: names, Social Security numbers (sometimes verbally confirmed), account numbers, investment directions, financial situations.

**Retention policy:**  
- **Call recordings:** Stored indefinitely by default until deleted by account holder. Account holder has deletion control.
- **Transcriptions:** Stored on Twilio servers. Retention configurable.
- **Call metadata (CDRs):** Retained by Twilio for billing/compliance.
- Twilio is SOC 2 Type II and ISO 27001 certified.
- Twilio's privacy policy: "After closure of your account, certain information associated with your account may remain on Twilio's servers in an aggregated form." Specific data retained for legal purposes.

**Who can access recordings:**  
Twilio account holders, Twilio staff (for support/safety), and potentially law enforcement via legal process. Third-party Twilio apps if integrated.

**RIA Compliance Risk:** 🔴 **HIGH** if client calls are recorded/transcribed without explicit consent and compliant disclosure

**Mitigation:**  
- Never record or transcribe client advisory conversations through Twilio without proper FINRA/SEC disclosure and client consent.
- If using for internal workflows only (non-client calls): acceptable with recording disclosure.
- Review your state's call recording consent laws (Texas is one-party, but client may be in a two-party state).
- Store recordings in your own infrastructure, not Twilio's, if you do record.

---

### 2.5 Brave Search API

**What data is sent:**  
Each API call sends: the search query, API key, and standard HTTP headers (including IP address of the requesting server). Unlike browser-based Brave Search, the API does not anonymize the requesting IP at the query level.

**What could contain PII:**  
If an agent constructs search queries containing client names or account details ("John Smith Vanguard IRA rollover 2025"), those queries log on Brave's infrastructure.

**Retention policy:**  
- Brave's browser-based search: "IP addresses are not logged" (per Brave browser privacy doc, confirmed in their data table)
- **Brave Search API:** API-specific policy is less clear. Brave's general privacy stance is strong, but the Search API logs queries for rate limiting and analytics. Their API documentation states queries may be retained for a limited period for service improvement.
- Brave does not sell data to third parties.

**RIA Compliance Risk:** 🟢 **LOW** (assuming queries don't contain client PII — enforce this in prompt design)

**Mitigation:**  
- Enforce a rule that search queries are constructed from general topics only, never containing client names or account identifiers.
- Prefer DuckDuckGo or Brave Search for research tasks — both have better API privacy posture than Google Search API.

---

### 2.6 ElevenLabs (TTS)

**What data is sent:**  
Every TTS API call sends the full text to be synthesized to ElevenLabs' servers. The text becomes the input to their voice synthesis model on their cloud infrastructure.

**PII exposure potential:**  
Medium-High. If the agent reads a client summary aloud using ElevenLabs TTS — "Your meeting with Sarah Chen is at 3pm to discuss her 401k rollover" — that client name and financial context transits ElevenLabs' servers.

**Retention policy:**  
Per ElevenLabs' privacy policy:
- Text inputs sent for TTS are processed and may be retained temporarily (typically 30 days) unless using an Enterprise plan.
- ElevenLabs logs API usage for billing and abuse detection.
- Voice outputs (audio files) generated may be temporarily cached.
- ElevenLabs' Enterprise tier includes data processing agreements and stricter retention controls.

**RIA Compliance Risk:** 🟡 **MEDIUM** (if TTS used for any client-specific content)

**Mitigation:**  
- Restrict TTS use to generic, non-client-specific content (system notifications, UI prompts, general information).
- If using TTS for client-specific content, run a local TTS model instead (Coqui TTS, macOS `say` command, or Piper).
- The macOS built-in `say` command is fully local and handles most TTS needs adequately.

---

### 2.7 xAI (Grok API)

**What data is sent:**  
Same as Anthropic and OpenAI: full context window contents (system prompt + conversation history + current message) sent to xAI's inference servers per API call.

**PII exposure potential:**  
High without guardrails. Same risk profile as Claude and GPT-4.

**Retention policy:**  
Per xAI's privacy policy (current):
- **API customers:** xAI acts as a data processor. API inputs/outputs are **not used for model training** by default.
- xAI retains API traffic logs for a limited period (30 days specified in their DPA for Enterprise customers).
- xAI offers Data Processing Agreements for commercial customers.
- xAI's infrastructure is US-based.
- Note: xAI (company) is separate from X (Twitter) — the privacy policies are separate, though Grok consumer product integrates with X data.

**RIA Compliance Risk:** 🟡 **MEDIUM** (same profile as Anthropic/OpenAI)

| Factor | Detail |
|--------|--------|
| API traffic training | No (default off for API) |
| DPA available | Yes |
| Infrastructure | US-based |
| Consumer Grok (x.com) | Different — DO NOT USE for anything client-related |

**Mitigation:**  
Same as Anthropic and OpenAI. Important distinction: the Grok model accessed via x.com consumer interface has weaker privacy controls than the xAI API. Never use consumer Grok for any client-related work.

---

### 2.8 Netlify (Deployments)

**What data is sent:**  
When deploying a site via Netlify:
- **Build process:** Source code/files uploaded to Netlify's build servers. Build logs stored on Netlify.
- **Deployed content:** All files in the site (HTML, JS, CSS, assets) pushed to Netlify's CDN.
- **Form submissions:** If using Netlify Forms, all form data (including any PII in contact forms) stored on Netlify's servers.
- **Analytics:** Netlify Analytics collects visitor IP addresses, page views, referrers.

**PII exposure potential:**  
Low for a typical static site. High if:
- The site contains hardcoded client data (should never happen)
- Netlify Forms used to collect client inquiries
- Build environment variables contain credentials/keys exposed in build logs

**Retention policy:**  
Per Netlify's privacy policy: "Customer Content" (sites, deployments, activity data) retained as long as account is active. Retention period configurable to some extent. Build logs retained per plan settings.

**RIA Compliance Risk:** 🟢 **LOW** for static informational sites | 🔴 **HIGH** if Netlify Forms used to collect client financial information

**Mitigation:**  
- Never use Netlify Forms for client financial data — use your own backend or a compliant form processor.
- Audit build process to ensure no credentials or client data in repository.
- Enable Netlify's access controls if the deployed site contains any non-public information.
- Use environment variables for API keys, never hardcode in deployable files.

---

## 3. PII Risk Matrix

| Service | Client Names | Account Numbers | Financial Data | Health/Personal Data | Portfolio Data | Risk Level |
|---------|-------------|-----------------|----------------|---------------------|----------------|------------|
| Anthropic API | 🟡 If in context | 🟡 If in context | 🟡 If in context | 🟡 If in context | 🟡 If in context | MEDIUM |
| OpenAI API | 🟡 If in context | 🟡 If in context | 🟡 If in context | 🟡 If in context | 🟡 If in context | MEDIUM |
| Google OAuth (gog) | 🔴 Email/Calendar | 🔴 Email/Drive | 🔴 Email/Drive | 🔴 Email/Drive | 🔴 Drive | HIGH |
| Twilio Voice | 🔴 Call audio | 🔴 Call audio | 🔴 Call audio | 🔴 Call audio | 🔴 Call audio | HIGH |
| Brave Search API | 🟢 If query-safe | 🟢 If query-safe | 🟢 If query-safe | 🟢 If query-safe | 🟢 If query-safe | LOW |
| ElevenLabs TTS | 🟡 If in TTS text | 🟡 If in TTS text | 🟡 If in TTS text | 🟡 If in TTS text | 🟡 If in TTS text | MEDIUM |
| xAI (Grok API) | 🟡 If in context | 🟡 If in context | 🟡 If in context | 🟡 If in context | 🟡 If in context | MEDIUM |
| Netlify | 🟢 Unlikely | 🟢 Unlikely | 🟢 Unlikely | 🟢 Unlikely | 🟢 Unlikely | LOW |

**Legend:** 🔴 High risk | 🟡 Conditional/mitigatable | 🟢 Low risk  

**Highest Priority Risks:**  
1. Google OAuth → unfiltered Claude forwarding (immediate action needed)
2. Twilio voice/transcription for any client-facing calls
3. Any cloud LLM call with client PII in the context window

---

## 4. Clean-Room Implementation Plan

### 4.1 Tiered Data Classification

| Tier | Definition | Examples | Permitted Routing |
|------|-----------|---------|------------------|
| **PUBLIC** | Information freely available, no personal linkage | Market data, general news, public company info | Any service |
| **INTERNAL** | Firm operational data, not client-specific | Internal templates, generic processes, firm-level metrics | Any service with encryption |
| **CONFIDENTIAL** | Client-linked but not financial | Client names, contact info, meeting schedules | LOCAL ONLY or with PII scrubbing |
| **PII/FINANCIAL** | Client financial data, account numbers, positions, SSNs | Account balances, portfolio holdings, tax docs, personal details | LOCAL ONLY — no cloud AI |

### 4.2 Task Routing Rules

```
DECISION TREE: Does this task require client-specific data?

NO → Route to cloud AI (Anthropic/OpenAI/xAI) with normal prompting
↓
YES → Does it require FINANCIAL data (account #s, balances, positions)?
    ↓
    YES → LOCAL ONLY (Ollama) — no cloud API permitted
    ↓
    NO → Can PII be tokenized? (replace names with Client-A, B, C)
        ↓
        YES → Tokenize → Cloud AI → De-tokenize response
        ↓
        NO → LOCAL ONLY (Ollama)
```

### 4.3 What Stays Fully Local (Ollama)

The following tasks involve client-specific data and should run on locally-hosted models:

| Task | Local Model Recommendation | Notes |
|------|---------------------------|-------|
| Summarize client meeting notes with real names | llama3.2 (3B) | Fast, runs on M-series Mac |
| Draft client-specific correspondence | llama3.2 or mistral-7b | Review before sending |
| Analyze client portfolio data | llama3.1 (8B) | Keep data local |
| Process documents with account numbers | mistral-7b | Never send to cloud |
| Voice commands with client context | local TTS (macOS say / Piper) | Not ElevenLabs |
| Client risk tolerance analysis | llama3.1 (8B) | No cloud needed |

**Minimum hardware for local inference:** The Mac mini (M-series) can comfortably run llama3.1:8B (4-bit quantized) at 20-40 tokens/sec — adequate for most RIA tasks. llama3.2:3B is faster and handles most drafting/summarization tasks well.

### 4.4 What Can Use Cloud APIs (with PII controls)

| Task | Permitted Service | Required Controls |
|------|-----------------|------------------|
| General research (market news, regulatory updates) | Brave Search API, Claude, GPT-4 | No client identifiers in query |
| Draft generic templates (no client names) | Claude, GPT-4, Grok | Confirm no PII in prompt |
| Email composition (firm comms, no client data) | Claude | Use CC for compliance review |
| Meeting scheduling (public calendars) | Google Calendar API | Limit to firm-internal events |
| Web search for compliance regulations | Brave Search, Claude | General queries only |
| Voice alerts — generic system messages | ElevenLabs | No client names in TTS text |
| Code generation, tool building | Claude, GPT-4 | No real data in examples |

### 4.5 Architecture Implementation

```
┌─────────────────────────────────────────────────────────────────┐
│                     OPENCLAW AGENT CORE                         │
│                                                                 │
│  ┌─────────────┐    ┌──────────────────┐    ┌──────────────┐  │
│  │  USER INPUT │ → │  PII CLASSIFIER  │ → │  ROUTER      │  │
│  │             │    │  (local check)   │    │              │  │
│  └─────────────┘    └──────────────────┘    └──────────────┘  │
│                              │                        │         │
│                    ┌─────────┴─────────┐              │         │
│                    │                   │              │         │
│               PII DETECTED        NO PII              │         │
│                    │                   │              │         │
│                    ▼                   ▼              │         │
│         ┌──────────────────┐  ┌──────────────────┐   │         │
│         │  LOCAL OLLAMA    │  │  PII TOKENIZER   │   │         │
│         │  (llama3.1:8B)   │  │  (replace names) │   │         │
│         │                  │  └────────┬─────────┘   │         │
│         │  ✓ GDPR/SEC safe │           │              │         │
│         │  ✓ No egress     │           ▼              │         │
│         └──────────────────┘  ┌──────────────────┐   │         │
│                                │  CLOUD API GATE  │   │         │
│                                │  Claude/GPT/Grok │   │         │
│                                │  (sanitized)     │   │         │
│                                └──────────────────┘   │         │
└─────────────────────────────────────────────────────────────────┘
```

### 4.6 PII Tokenizer Implementation

A simple tokenizer layer before any cloud API call:

```python
# Pseudocode for PII tokenizer
def sanitize_for_cloud(text, client_registry):
    """Replace real identifiers with tokens before cloud API call"""
    token_map = {}
    
    for client in client_registry:
        token = f"CLIENT-{client.id}"
        text = text.replace(client.name, token)
        text = text.replace(client.account_number, f"ACCT-{client.id}")
        token_map[token] = client.name
    
    return text, token_map

def restore_from_cloud(response, token_map):
    """Restore real names after cloud API response"""
    for token, real_name in token_map.items():
        response = response.replace(token, real_name)
    return response
```

This pattern allows cloud LLMs to assist with drafting and analysis while preventing client PII from leaving the machine.

---

## 5. Recommended Action Items (Prioritized)

### Immediate (Before Any Client-Facing Use)

**#1 — Implement the Ollama local stack**  
Install Ollama, pull llama3.1:8B. Configure OpenClaw to route all client-data queries locally. This is the single most impactful compliance action.
```bash
brew install ollama
ollama pull llama3.1:8b
ollama pull mistral:7b
```

**#2 — Audit OpenClaw system prompts and memory files**  
Review all memory/context files for client PII that could be injected into cloud API calls. Purge or tokenize. The risk isn't just what you intentionally send — it's what's in the persistent memory that gets forwarded automatically.

**#3 — Disable Google OAuth for Drive and Gmail until filtered**  
The gog CLI → Claude pipeline is the highest uncontrolled risk. Until a filtering layer exists, disable these integrations for production use. Calendar-only is lower risk if meeting descriptions are kept generic.

**#4 — Stop Twilio recording for any client-related calls**  
Disable recording on all Twilio numbers used in client context until proper disclosure/consent documentation is in place.

### Short-term (Within 30 Days)

**#5 — Execute Anthropic and OpenAI DPAs**  
Sign Data Processing Agreements with both providers. This creates contractual obligations for them as data processors and documents your due diligence. Free to request, required for defensible compliance posture.

**#6 — Pursue Zero Data Retention agreements**  
Upgrade to Anthropic API Enterprise or OpenAI Enterprise if client data will ever touch the API (even tokenized). ZDR means no 30-day log retention.

**#7 — Build the PII tokenizer layer**  
Implement the tokenizer described in Section 4.6 as middleware in the OpenClaw workflow. Even a simple regex-based name/number scrubber dramatically reduces risk.

**#8 — Create an allowed-query whitelist for Brave Search**  
Define what types of searches can be auto-generated (market data, news, regulatory updates) and block patterns that could expose client information.

### Medium-term (Before Spectrum Pitch)

**#9 — Document the architecture for compliance**  
Create a one-page data flow diagram (simpler version of what's in Section 4.5) showing the clean-room architecture. Compliance officers need to see the picture, not read the code.

**#10 — Evaluate Coqui TTS or macOS say as ElevenLabs replacement**  
For any TTS that might include client context, replace ElevenLabs with local TTS. macOS `say` is built-in and handles notification-style TTS well. Coqui/Piper handle higher-quality needs.

**#11 — Implement audit logging for all cloud API calls**  
Log what is sent to each cloud service (minus PII content — log the fact of the call, the service, the sanitized query type) for compliance documentation. If a regulator asks "what data went to Anthropic?", you need an answer.

---

## 6. Appendix: Raw Policy Links and Key Quotes

### Anthropic

- **Privacy Policy:** https://www.anthropic.com/legal/privacy (effective Jan 12, 2026)
- **API Terms:** https://www.anthropic.com/legal/api-terms
- **DPA:** Available through account — contact enterprise@anthropic.com
- **Subprocessors:** https://www.anthropic.com/subprocessors

**Key Quote (Privacy Policy):** *"This privacy policy does not apply to situations where Anthropic acts as a data processor and processes personal data on behalf of commercial customers using Anthropic's commercial services — for example, your employer has given you a Claude for Work account."* (Consumer use vs. API use distinction)

**Key Quote:** *"We may use your inputs and outputs to improve our services, unless you opt out via your account settings."* (Consumer) | API: not used for training by default.

### OpenAI

- **Privacy Policy:** https://openai.com/policies/privacy-policy
- **Enterprise Privacy:** https://openai.com/enterprise-privacy/
- **API Data FAQ:** https://platform.openai.com/docs/guides/your-data
- **DPA:** https://openai.com/dpa/

**Key Quote (Enterprise):** *"We do not use your business data to train our models. We maintain a strict separation between customer data and our general training datasets."*

**Key Quote (API standard):** API inputs/outputs retained for 30 days for abuse monitoring, not used for training.

### Google (OAuth/Workspace)

- **Privacy Policy:** https://policies.google.com/privacy
- **Workspace DPA:** https://workspace.google.com/terms/dpa/
- **OAuth Scopes:** https://developers.google.com/identity/protocols/oauth2/scopes
- **Security Overview:** https://workspace.google.com/security/

### Twilio

- **Privacy Statement:** https://www.twilio.com/en-us/legal/privacy
- **Data Retention:** https://www.twilio.com/en-us/legal/privacy#how-long-we-retain-personal-data
- **Key Quote:** *"After closure of your account, we will retain data — including personal data — associated with your account that we are required to maintain for legal purposes or for necessary business operations."*
- **Recordings access:** Account holder controls; Twilio may access for support; no third-party access without legal process.

### Brave Search API

- **Privacy Policy:** https://brave.com/privacy/browser/
- **Search API Docs:** https://api.search.brave.com/app/documentation/web-search
- **Key Quote (Browser Privacy Doc):** *"IP addresses are not logged."* (browser context — API has different terms)
- **API data table quote:** "Query, conversation context" — confirms queries are logged at API level.

### ElevenLabs

- **Privacy Policy:** https://elevenlabs.io/privacy
- **Terms of Service:** https://elevenlabs.io/terms
- Text inputs processed on ElevenLabs infrastructure; 30-day default retention; Enterprise DPA available.

### xAI (Grok)

- **Privacy Policy:** https://x.ai/legal/privacy-policy
- **API Terms:** https://x.ai/legal/terms-of-service
- API inputs not used for training by default; Enterprise DPA available. Separate from X/Twitter consumer Grok.

### Netlify

- **Privacy Statement:** https://www.netlify.com/privacy/
- **Key Quote:** *"Customer Content: this is the content we collect and store including when you use the Netlify Services, as for example: sites you create, deployments, team builds, profile metadata, activity, and usage data."*
- **DPA:** Available at https://www.netlify.com/legal/

### SEC/FINRA Regulatory Context

- **Regulation S-P (Safeguard Rule):** 17 CFR § 248.30 — Requires RIAs to have written policies and procedures to safeguard customer records and information. Effective requirement: protect against unauthorized access or anticipated threats to security/integrity of customer records.
- **SEC Guidance on Cloud Computing:** SEC staff have indicated that using cloud providers is permissible but firms must perform due diligence on the provider's security, have contractual protections (DPAs), and maintain responsibility for customer data.
- **FINRA Rule 4370:** Business Continuity Plans — relevant for any system used in client-facing operations.
- **SEC AI Guidance (2024):** SEC has flagged AI/ML tools as an exam priority. Firms should document what AI tools are used, what data they access, and what controls are in place.

---

*Report compiled February 26, 2026. Policy information current as of research date. Policies subject to change — verify retention terms with each provider before making compliance representations.*

*— Berean, Research & Intelligence*
