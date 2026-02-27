# Video → Shorts Content Pipeline

Create short-form, ready-to-post clips from long-form videos (sermons, street preaching, apologetics debates, podcasts).

## What it does
1. Transcribes source video with timestamps (SRT + JSON)
2. Finds 2–3 compelling viral clip moments with AI
3. Cuts those moments into standalone clips
4. Burns in large bold subtitles (shorts style)
5. Reformats to 9:16 vertical (1080x1920)

## Scripts

- `pipeline.sh` — full orchestrator
- `transcribe.sh` — transcription (OpenAI Whisper API → local whisper fallback)
- `find-clips.py` — clip selection with `gpt-4o-mini`
- `cut-clips.sh` — clip extraction with fades
- `add-captions.sh` — subtitle segment extraction + burn-in
- `format-vertical.sh` — vertical formatting for Shorts/TikTok/X
- `batch.sh` — process an entire folder

## Dependencies
Required:
- `ffmpeg`
- `python3`
- `curl`
- `jq`

Optional but recommended:
- `OPENAI_API_KEY` in environment (for Whisper API + clip finder)
- local `whisper` CLI (fallback if no API key)

`pipeline.sh` checks required dependencies at startup and exits with clear errors if missing.

## Usage

### Single video
```bash
cd /Users/deaconsopenclaw/.openclaw/workspace/scripts/content-pipeline
bash pipeline.sh /path/to/video.mp4
```

Optional custom output base directory:
```bash
bash pipeline.sh /path/to/video.mp4 --output-dir /path/to/output
```

### Batch process directory
```bash
bash batch.sh /path/to/folder/of/videos/
```

Optional custom output base directory:
```bash
bash batch.sh /path/to/folder/of/videos/ --output-dir /path/to/output
```

## Output structure

```text
output/
  2026-02-15-video-title/
    transcript.srt
    transcript.json
    clips.json
    clip-1-raw.mp4
    clip-1-captioned.mp4
    clip-1-final-vertical.mp4
    clip-2-raw.mp4
    clip-2-captioned.mp4
    clip-2-final-vertical.mp4
    ...
```

## Notes on clip finding (apologetics tuned)
`find-clips.py` is tuned for Christian apologetics and preaching content, prioritizing:
- hard hooks in first ~3 seconds
- conviction moments / emotional breakthrough
- clear theological argumentation
- scripture-driven moments
- clean, punchy edit boundaries (45–90 sec)

If OpenAI clip-finding fails, it falls back to a local heuristic scorer.
