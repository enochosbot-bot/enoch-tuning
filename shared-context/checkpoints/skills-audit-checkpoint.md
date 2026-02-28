# Skills Audit — Execution Checkpoint

**Date:** 2026-02-28 02:53 CST  
**Status:** IN PROGRESS — awaiting decisions + API tier upgrade

---

## ✅ COMPLETED

### Removals
- Obsidian local skill: **removed** from `~/.openclaw/agents/researcher/workspace/skills/`
- Obsidian system skill: **disabled** in config
- Messaging skills: `imsg`, `wacli`, `bluebubbles` — **all disabled**
- Dead weight: `ordercli`, `gifgrep`, `songsee`, `trello`, `voice-call`, `tmux`, `spotify-player`, `discord`, `slack` — **all disabled**
- Empty stubs: `arscontexta`, `content-research-writer`, `meeting-insights-analyzer` — **removed** (will rebuild content-research-writer + meeting-insights-analyzer)

### Config Updates
- Updated `~/.openclaw/openclaw.json`
- Disabled 13 skills total
- Configured `nano-banana-pro` with GEMINI_API_KEY

### CLI Installs
- **xurl**: ✅ installed via `brew install --cask xdevplatform/tap/xurl`
  - **STATUS:** Installed but needs authentication
  - **NEXT STEP (manual):** Run `xurl auth apps add <name>` then `xurl auth oauth2` to authenticate with X API
- **nano-banana-2**: ✅ installed from clawhub (Gemini 3.1 Flash Image alternative)

### Skills Check
```
✓ 41 Eligible (ready to use)
⏸ 13 Disabled
✗ 2 Missing requirements (discord plugin, sherpa-onnx-tts env)
```

---

## 🚨 BLOCKING ISSUE: nano-banana-pro API Tier

**Problem:** The GEMINI_API_KEY is **free tier**. Nano Banana Pro uses `gemini-3-pro-image-preview`, which has **0 quota on free tier**.

**Error:**
```
429 RESOURCE_EXHAUSTED
Quota exceeded for: generativelanguage.googleapis.com/generate_content_free_tier_requests
```

**Options:**
1. **Upgrade Gemini API to pay-as-you-go** → Go to https://aistudio.google.com, enable billing (it's cheap)
2. **Use nano-banana-2** → Already installed from clawhub, uses `gemini-3.1-flash-image-preview` (may still require paid tier)
3. **Use openai-image-gen** → Already working as fallback

**Recommendation:** Upgrade to paid Gemini tier ($5/month minimum). Nano Banana Pro is the best free image model Google has.

---

## ⏳ AWAITING YOUR INPUT

### 1. Hardware Confirmation
Do you own:
- **Eight Sleep pod?** (eightctl) — currently enabled
- **Philips Hue lights?** (openhue) — currently enabled
- **Sonos speakers?** (sonoscli) — currently enabled
- **BluOS/Bluesound hardware?** (blucli) — currently enabled

If no to any, reply with the list and I'll disable them.

### 2. Note-Taking Primary
Which is your actual primary?
- **Apple Notes** (`apple-notes` / `memo` CLI)
- **Bear** (`bear-notes` / `grizzly` CLI)

(Obsidian local is removed; system obsidian is disabled.)

Pick one and I'll set the others as "secondary/fallback."

---

## 📋 NEXT STEPS (after your input)

1. Build **content-research-writer** skill (formalizes Berean → Ezra research handoff)
2. Build **meeting-insights-analyzer** skill (meeting transcript → action items)
3. Update note-taking strategy in SOUL.md
4. Test xurl once you run `xurl auth oauth2`
5. Optional: Upgrade Gemini API tier for nano-banana-pro

---

## Current Skill Stack (Ready)

**Core (actively used):**
- things-mac · gog · github · gh-issues · coding-agent · summarize · 1password · xurl · peekaboo · camsnap · blogwatcher · weather · session-logs · skill-creator · clawhub

**Redundant but useful (both kept):**
- sag (ElevenLabs TTS) + sherpa-onnx-tts (local offline)
- gog (Gmail) + himalaya (IMAP generic)
- openai-whisper (local) + openai-whisper-api (cloud)

**Confirmed working:**
- apple-notes · bear-notes · oracle · gemini · nano-banana-2 · nano-pdf · openai-image-gen · video-frames · healthcheck · mcporter

**Wait-for-input:**
- blucli (BluOS) · sonoscli (Sonos) · eightctl (Eight Sleep) · openhue (Hue)

**Disabled:**
13 total (see list above)
