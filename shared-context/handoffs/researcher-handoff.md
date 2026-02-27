# Handoff — Berean (Researcher)

## Active Task
**America First Pre-Show B-Roll Analysis** — Analyzing Nick Fuentes' Rumble pre-show production pattern (music, pacing, animations, text overlays, talking segments) to document and replicate for Deacon's own content.

## Progress

### Done
- [x] Found Rumble channel: `https://rumble.com/c/NickJFuentes`
- [x] Identified most recent episode: **Ep. 1648** (2026-02-26) at `https://rumble.com/v76c4c2-america-first-ep.-1648.html`
- [x] Resolved HLS `.tar` segment blocker — switched from ffmpeg to yt-dlp native downloader with format `hls-222`
- [x] Downloaded full episode: `ep1648-full.mp4` (~343 MB, 1296 HLS fragments, 100% complete)
- [x] File confirmed at: `/Users/deaconsopenclaw/.openclaw/agents/researcher/workspace/research/af-preshow/ep1648-full.mp4`

### In Flight
- [ ] **Trim pre-show segment** — extract first ~7 minutes from the full episode
- [ ] **Frame extraction** — pull frames every 30 seconds for visual analysis
- [ ] **Write structured breakdown** of the pre-show B-roll pattern

## Next Steps
1. **Trim the pre-show:**
   ```bash
   cd /Users/deaconsopenclaw/.openclaw/agents/researcher/workspace/research/af-preshow/
   ffmpeg -i ep1648-full.mp4 -t 420 -c copy ep1648-preshow.mp4
   ```

2. **Extract frames every 30 seconds:**
   ```bash
   ffmpeg -i ep1648-preshow.mp4 -vf "fps=1/30" frames/frame_%04d.jpg
   ```

3. **Analyze frames + audio** — document:
   - Music style, BPM feel, genre
   - Animation types (motion graphics, memes, clips)
   - Text overlays (fonts, colors, placement)
   - Talking head segments (length, framing)
   - Transitions between segments
   - Pacing pattern (when does show "start"?)

4. **Write research brief** to `research/af-preshow/preshow-analysis.md` using Berean's output standards (key findings, evidence, confidence, unknowns, recommended action)

5. **Hand off to Ezra** for content production guidance if Deacon wants a template for his own stream pre-roll

## Key Context
- **Full episode file:** `/Users/deaconsopenclaw/.openclaw/agents/researcher/workspace/research/af-preshow/ep1648-full.mp4`
- **Rumble embed ID:** `v745gbu`
- **Episode:** America First Ep. 1648, aired 2026-02-26
- **Rumble channel:** `https://rumble.com/c/NickJFuentes`
- **yt-dlp format used:** `hls-222` (640x360) with `--downloader aria2c` — bypasses ffmpeg's `.tar` segment whitelist error
- **ffmpeg HLS note:** If downloading Rumble HLS directly via ffmpeg in future, add `-allowed_extensions ALL` before the `-i` flag
- **yt-dlp version:** 2026.02.21
- **ffmpeg version:** 8.0.1
- **Goal:** Understand pre-show B-roll production pattern to replicate for Deacon's content (not the main show itself)

## Blockers
- None. Full episode downloaded. Ready to trim and analyze on next session load.
