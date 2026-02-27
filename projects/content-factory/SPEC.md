# content-factory — Full Pipeline Spec
**Owner:** Deacon Ridley (AmericanFireside + Ridley Research)
**Assigned to:** Bezzy
**Written by:** Solomon
**Status:** Ready to build

---

## What This Is

One command that takes a topic and runs the full content production chain:
script → video → voice → captions → approval → post.

No isolated scripts. No manual steps between generation and posting.
Every existing tool gets wired together. New pieces fill the gaps.

---

## Single Entry Point

```bash
python3 scripts/content-factory.py "AmericanFireside — eagles, faith, freedom, cinematic"
```

Optional flags:
```
--mode       [shorts | claudebot | clip]        default: shorts
--platforms  [yt,tiktok,x,ig]                   default: yt,x
--duration   seconds (5-60)                      default: 30
--voice      ElevenLabs voice ID or name         default: Harry (warrior)
--raw        skip Claude script generation
--no-post    generate only, skip posting
--approve    require Telegram approval before posting (default: ON)
```

---

## Pipeline Modes

### Mode: `shorts` (primary — AmericanFireside)
AI-generated video + voiceover + captions.
No source footage required.

```
Topic
  → Claude writes hook + script (15–60s)
  → vidgen.py fires kling + minimax + luma in parallel (free tiers first)
  → Best video selected (auto or manual)
  → ElevenLabs (sag CLI) generates voiceover from script
  → Whisper transcribes voice → ffmpeg burns captions
  → ffmpeg merges video + audio + captions → final.mp4
  → Telegram approval gate (preview + approve/reject buttons)
  → On approve: post to selected platforms
```

### Mode: `claudebot` (viral comedy — existing format)
Uses `claude-bot-render.py` (already built). Just needs the approval gate + posting wired.

```
Prompt + mode (military/lawyer/surgeon/wallstreet/coach)
  → claude-bot-render.py generates clip
  → Telegram approval gate
  → On approve: post to yt,tiktok,x
```

### Mode: `clip` (clip from source video)
Uses `content-pipeline/pipeline.sh` (already built). Wire in approval + posting.

```
YouTube URL or local file
  → clipper.py or pipeline.sh finds top clips
  → 9:16 reformat + captions
  → Telegram approval gate
  → On approve: post to yt,tiktok,x
```

---

## File Structure

```
scripts/
  content-factory.py          ← NEW: master orchestrator (build this)
  content-factory/
    script_writer.py          ← NEW: Claude script generator
    video_selector.py         ← NEW: pick best vidgen output
    assembler.py              ← NEW: ffmpeg merge (video + voice + captions)
    approval_gate.py          ← NEW: Telegram preview + inline buttons
    distributor.py            ← NEW: routes to each platform poster
    youtube_upload.py         ← NEW: YouTube Data API v3 upload
    tiktok_upload.py          ← NEW: TikTok Content Posting API
  
  # Existing — call, don't rewrite:
  vidgen.py                   ← video generation (just built)
  claude-bot-render.py        ← claudebot clips (exists)
  clipper.py                  ← YouTube URL → clips (exists)
  content-pipeline/pipeline.sh ← captions + 9:16 format (exists)
  x-post.py                   ← X posting (exists)
  linkedin-post.py            ← LinkedIn posting (exists)
```

---

## Module Specs

### 1. `script_writer.py`
Uses Claude (claude-haiku-4-5 for speed/cost) to write short-form scripts.

Input: topic string, duration target, content brand (americanfireside | ridleyresearch)
Output: JSON `{ "hook": str, "body": str, "cta": str, "full_script": str, "tts_text": str }`

Content rules baked into system prompt:
- AmericanFireside: faith, freedom, politics, patriotism — no disclaimers
- Hook in first 3 seconds — pattern interrupt, not a slow intro
- Body: 1-3 punchy points
- CTA: subscribe / follow / share — not "like and subscribe" corporate drivel
- `tts_text`: clean version for voice synthesis (no stage directions, no symbols)

---

### 2. `video_selector.py`
After vidgen.py runs, pick the best video.

Logic:
1. If only 1 platform succeeded → use it
2. If multiple succeeded → default to `kling` (best motion quality), then `luma`, then `minimax`
3. If `--select manual` flag: send all options to Telegram for Deacon to pick before proceeding

---

### 3. `assembler.py`
ffmpeg pipeline to merge all elements into final.mp4.

Steps (in order):
1. Transcribe voice file → SRT captions via Whisper (`whisper audio.mp3 --output_format srt`)
2. Burn captions onto video:
   - Font: bold sans-serif, white with black outline
   - Position: lower-center (Y=85%)
   - Size: 48px for Shorts (9:16 frame)
3. Merge audio onto video (`-c:v copy -map 0:v -map 1:a`)
4. Ensure 9:16 aspect ratio (1080×1920 for Shorts/TikTok/Reels, 1280×720 for X/YouTube landscape)
5. Output: `{run_dir}/final.mp4` + `{run_dir}/final-landscape.mp4`

Reuse `content-pipeline/format-vertical.sh` and `add-captions.sh` where possible.

---

### 4. `approval_gate.py`
Sends the finished video to Telegram (AI HQ, topic 75 = Clipping) for review.

Message format:
```
🎬 Content Factory — Ready for Review
Mode: shorts | AmericanFireside
Topic: "eagles, faith, freedom"
Platform: kling | Duration: 28s
Cost: ~$0.42

Script hook: "They said faith had no place in the public square..."

[Approve ✅] [Reject ❌] [Reshoot 🔄]
```

Buttons:
- **Approve** → triggers distributor.py with all selected platforms
- **Reject** → logs and exits; nothing posts
- **Reshoot** → re-runs vidgen.py with a new platform or different prompt variation

Wait up to 4 hours for approval. If no response → auto-reject (never post without approval).

Implementation: use OpenClaw's `message` tool (action=send with buttons) via the existing Telegram integration. Poll for callback response.

---

### 5. `distributor.py`
Routes the approved video to each platform.

| Platform | Method |
|---|---|
| YouTube Shorts | `youtube_upload.py` (see below) |
| TikTok | `tiktok_upload.py` (see below) |
| X | `x-post.py` (exists — just call it) |
| LinkedIn | `linkedin-post.py` (exists — just call it) |
| Instagram | Placeholder for now (Meta API requires app review) |

Distributor reads `run_dir/metadata.json` for title, description, tags, platform-specific copy.
Claude generates platform-specific captions at assembly time (different copy for X vs YouTube vs TikTok).

---

### 6. `youtube_upload.py`
OAuth is already configured (`google-auth-youtube-photos.py` + `google-yt-photos-token.json`).

Upload via YouTube Data API v3:
- Resource: `videos.insert`
- `snippet.title`: auto-generated from script hook (max 100 chars)
- `snippet.description`: script body + AmericanFireside CTA
- `snippet.tags`: auto-tagged from topic
- `status.privacyStatus`: `"public"`
- `status.selfDeclaredMadeForKids`: `false`
- Category 22 (People & Blogs) or 25 (News & Politics)

Use existing token file. Refresh on 401.

---

### 7. `tiktok_upload.py`
TikTok Content Posting API (v2).
Auth: `TIKTOK_CLIENT_KEY` + `TIKTOK_CLIENT_SECRET` + `TIKTOK_ACCESS_TOKEN` in Keychain.
Account: @AmericanFireside (TikTok account not yet created — flag if missing).

Steps:
1. `POST /v2/post/publish/video/init/` → get `upload_url` + `publish_id`
2. Upload video binary to `upload_url`
3. `GET /v2/post/publish/status/fetch/` — poll for success

Title: same as YouTube title (max 150 chars for TikTok).
If `TIKTOK_ACCESS_TOKEN` missing → skip + log, don't crash.

---

## State & Logging

Every run writes a `run_dir/metadata.json`:
```json
{
  "run_id": "20260226-143022",
  "topic": "eagles, faith, freedom",
  "mode": "shorts",
  "script": { "hook": "...", "body": "...", "full_script": "..." },
  "video": { "platform": "kling", "file": "...", "cost": 0.42 },
  "voice": { "voice_id": "Harry", "file": "..." },
  "final": { "vertical": "final.mp4", "landscape": "final-landscape.mp4" },
  "approval": { "status": "approved", "by": "deacon", "ts": "..." },
  "posted": { "youtube": "...", "x": "...", "tiktok": "..." }
}
```

Append one-line JSON to `scripts/content-factory-log.jsonl` on each run.

---

## Free Tiers First (vidgen.py update needed)

Update vidgen.py to add free-tier logic:
- Kling free tier: 66 free credits/month at sign-up
- Pika free tier: add as 5th platform (`pika` key)
- Veo 3.1 via Google AI Studio: add as 6th platform (`veo` key) — `VEO_API_KEY` in Keychain

Priority order (no keys needed for free tiers after sign-up):
`free tiers first → kling paid → minimax → luma → runway`

---

## Dependencies

Already installed: `aiohttp`, `anthropic`, `pyjwt`, `lumaai`, `runwayml`, `openai-whisper`, `ffmpeg`

New installs needed:
```bash
pip install google-api-python-client google-auth-oauthlib  # YouTube upload
pip install tiktok-api  # or direct HTTP calls — evaluate at build time
```

---

## Keys Checklist

| Key | Where | Status |
|---|---|---|
| `ANTHROPIC_API_KEY` | Keychain | ✅ exists |
| `ELEVENLABS_API_KEY` | Keychain (check) | ❓ verify |
| `MINIMAX_API_KEY` | Keychain | ❌ needs setup |
| `KLING_API_KEY` | Keychain | ❌ needs setup |
| `LUMA_API_KEY` | Keychain | ❌ needs setup |
| `YOUTUBE_API_KEY` | Keychain | ✅ exists (verify OAuth scope includes upload) |
| `TIKTOK_ACCESS_TOKEN` | Keychain | ❌ needs setup (account not created) |

---

## Build Order for Bezzy

Ship in this sequence. Each is independently testable:

1. **`script_writer.py`** — test: run with a topic, get JSON script output
2. **`assembler.py`** — test: give it a video + audio file, get merged final.mp4
3. **`approval_gate.py`** — test: send a test message to Telegram topic 75 with buttons, confirm callback received
4. **`youtube_upload.py`** — test: upload a test video as unlisted, confirm it appears in YouTube Studio
5. **`tiktok_upload.py`** — test: check token + init upload, confirm API responds (account creation may block actual test)
6. **`distributor.py`** — test: mock a completed run_dir, call distributor, verify each platform called
7. **`content-factory.py`** — wire all modules, test full end-to-end run in `--no-post` mode first
8. **Update `vidgen.py`** — add Pika + Veo free tier support, add priority ordering

---

## Definition of Done

```bash
# This command runs end-to-end without errors:
python3 scripts/content-factory.py "AmericanFireside — faith and freedom, eagle imagery" --no-post

# Produces:
# runs/20260226-143022/
#   script.json          ← Claude-written script
#   kling.mp4            ← Generated video
#   voiceover.mp3        ← ElevenLabs voice
#   captions.srt         ← Whisper transcription
#   final.mp4            ← Merged vertical (1080x1920)
#   final-landscape.mp4  ← Merged landscape (1280x720)
#   metadata.json        ← Full run record

# And this posts it live:
python3 scripts/content-factory.py "same topic" --platforms yt,x
# → Telegram approval message fires
# → On approve → posts to YouTube Shorts + X
# → Logs to content-factory-log.jsonl
```

---

## What This Unlocks

When this is done, AmericanFireside content production is:
- One command (or a cron job)
- Zero manual steps between idea and live post
- Every platform hit simultaneously
- Full audit trail of everything posted
- Claude bot, clips, and AI-generated video all running on the same pipeline

Scale play: same factory, different SOUL.md inputs → produces Ridley Research content, client demo content, or anything else. The pipeline is brand-agnostic.
