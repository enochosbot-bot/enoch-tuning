# NullClaw — Full AI Assistant Stack in Zig (678 KB)

**Source:** @heynavtoor (Nav Toor) — bookmarked 2026-02-28  
**GitHub:** github.com/nullclaw/nullclaw | 2,798 stars | MIT | Created 2026-02-16  
**Verdict:** READ_DEEPER / BUILD

---

## What It Is
A complete AI assistant infrastructure written in Zig. 678 KB binary, ~1 MB RAM, boots in <2ms. Zero dependencies beyond libc.

## Claimed Specs
- 22+ AI providers (OpenAI, Anthropic, Ollama, DeepSeek, Groq, etc.)
- 13 chat channels (Telegram, Discord, Slack, WhatsApp, iMessage, IRC)
- 18+ built-in tools
- Hybrid vector + keyword memory search
- Multi-layer sandboxing (Landlock, Firejail, Docker)
- Hardware peripheral support (Arduino, Raspberry Pi, STM32)
- MCP, subagents, streaming, voice
- ChaCha20-Poly1305 key encryption by default
- 2,738 tests, ~45,000 lines of Zig

## Reality Check
- **Real repo:** confirmed on GitHub, 2,798 stars, created Feb 16 2026 — less than 2 weeks old
- 45k lines of Zig in 12 days with all that scope is either pre-existing work released publicly or extraordinary velocity
- The resource claims are plausible for Zig — no GC, stack allocation, zero-copy I/O
- The feature breadth (13 channels, 22 providers) warrants verification against actual implementation

## Strategic Take
If the claims hold up, this is architecturally significant: proof that the entire "agentic stack" doesn't require a bloated Node/Python runtime. Relevant for edge deployment, embedded agents, low-cost infrastructure. Worth a deep technical review of the vtable design and actual channel implementations before drawing conclusions.

---
*Vetted: 2026-02-28*
