# SKILLS_AND_AGENTS.md

## Primary Agent
- **Enoch** 🔮 — Main personal assistant (Telegram, voice calls)
  - Model: Claude Opus 4.6
  - Voice model: Claude Sonnet 4
  - Autonomy: High for internal tasks, asks before external actions
  - Personality: Direct, opinionated, resourceful

## Installed Skills
| Skill | Status | Notes |
|-------|--------|-------|
| Tirith | ✅ Active | Terminal security, homograph/injection defense |
| QMD | ✅ Active | Local semantic search, workspace indexed |
| X Research | ⚠️ Needs API key | Twitter/X search and research |
| YouTube-to-Doc | ✅ Installed | Video→doc converter, `~/bin/yt2doc` |
| Schematron-3B | ⚠️ Needs API key | HTML→JSON extraction via inference.net |
| Brave Search | ✅ Active | Web search |
| Voice Call | ✅ Active | Twilio + OpenAI STT/TTS |
| ElevenLabs (sag) | ✅ Active | TTS with voice cloning |

## Triggers
- Telegram messages → main session
- Voice calls → Twilio → OpenAI Realtime STT → response
- Heartbeats → periodic checks (currently minimal)
- Cron jobs → scheduled tasks

## Sub-Agents
_(None yet. Can spawn isolated sessions for parallel work.)_

## Planned
- Gideon ⚔️ — Security & Ops agent (`observer` agent ID), deployed on Security & Ops Telegram topic
- Xalt — Twitter/social agent (future)
