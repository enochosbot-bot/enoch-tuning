# INTEGRATIONS.md

## Active
| Platform | Connection | Data Flow |
|----------|-----------|-----------|
| Telegram | @Enoch_oc_bot | Bidirectional — messages in/out |
| Twilio | +19133939563 | Voice calls in/out |
| OpenAI | API key configured | STT, TTS, voice response model |
| Anthropic | Setup-token (subscription) | Main LLM (Opus 4.6) |
| ElevenLabs | API key configured | TTS voices |
| Brave Search | API key configured | Web search |

## Installed, Not Connected
| Platform | What's Needed |
|----------|--------------|
| X/Twitter | Bearer token (X_BEARER_TOKEN env var) |
| Schematron-3B | inference.net API key |

## Not Yet Installed
| Platform | Purpose | Priority |
|----------|---------|----------|
| Google Workspace (gog) | Gmail, Calendar, Drive | High |
| Notion | Notes, databases | Medium |
| Obsidian | Local knowledge base | Medium |
| AgentMail | Agent email identity | Low |
| Honcho Memory | Persistent memory layer | Low |

## Data Flow Rules
- Inbound: anything can come in, I process it
- Outbound: ask before sending to humans/public
- Internal: free to read, organize, search
