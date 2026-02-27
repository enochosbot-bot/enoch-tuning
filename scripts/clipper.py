#!/usr/bin/env python3
"""
clipper.py — Vugola-style AI clipping pipeline for OpenClaw
Usage:
  python3 scripts/clipper.py --url "https://youtube.com/watch?v=..."
  python3 scripts/clipper.py --file /path/to/video.mp4
  python3 scripts/clipper.py --url "..." --clips 5 --style hook

Outputs clips to workspace/clips/YYYY-MM-DD-{slug}/
Each clip: 9:16 reframed, captions burned in, ready to post.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).parent
WORKSPACE   = SCRIPT_DIR.parent
CLIPS_DIR   = WORKSPACE / "clips"
CLIPS_DIR.mkdir(exist_ok=True)

# ── deps ──────────────────────────────────────────────────────────────────────
def ensure_deps():
    missing = []
    try: import whisper
    except ImportError: missing.append("openai-whisper")
    try: import cv2
    except ImportError: missing.append("opencv-python-headless")
    if missing:
        print(f"[clipper] Installing: {missing}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing,
                               "--break-system-packages", "-q"])

ensure_deps()
import whisper
import cv2

# ── helpers ───────────────────────────────────────────────────────────────────
def ts_to_sec(ts: str) -> float:
    """'1:23.4' or '83.4' → float seconds"""
    ts = ts.strip()
    if ":" in ts:
        parts = ts.split(":")
        if len(parts) == 3:
            h, m, s = parts
            return int(h)*3600 + int(m)*60 + float(s)
        m, s = parts
        return int(m)*60 + float(s)
    return float(ts)

def sec_to_ts(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"

def run(cmd, **kwargs):
    print(f"[clipper] $ {' '.join(str(c) for c in cmd)}")
    return subprocess.run(cmd, check=True, **kwargs)

def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower())[:40].strip("-")

# ── step 1: download ──────────────────────────────────────────────────────────
def download_video(url: str, out_dir: Path) -> Path:
    print(f"[clipper] Downloading: {url}")
    out_template = str(out_dir / "source.%(ext)s")
    run(["yt-dlp", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
         "--merge-output-format", "mp4",
         "-o", out_template, url])
    matches = list(out_dir.glob("source.*"))
    if not matches:
        raise FileNotFoundError("Download failed — no source file found")
    return matches[0]

# ── step 2: transcribe ────────────────────────────────────────────────────────
def transcribe(video_path: Path, model_size: str = "base") -> dict:
    print(f"[clipper] Transcribing with Whisper ({model_size})…")
    model = whisper.load_model(model_size)
    result = model.transcribe(str(video_path), word_timestamps=True, verbose=False)
    return result

def transcript_to_text(result: dict) -> str:
    """Build a readable transcript with timestamps for Claude."""
    lines = []
    for seg in result.get("segments", []):
        start = sec_to_ts(seg["start"])
        end   = sec_to_ts(seg["end"])
        lines.append(f"[{start} --> {end}] {seg['text'].strip()}")
    return "\n".join(lines)

# ── step 3: AI moment detection ───────────────────────────────────────────────
def find_viral_moments(transcript_text: str, n_clips: int, style: str,
                        video_duration: float) -> list[dict]:
    """Call Claude to identify the n best clips."""
    import urllib.request, urllib.error

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        # Try reading from openclaw secrets
        try:
            result = subprocess.run(
                ["openclaw", "config", "get", "providers.anthropic.apiKey"],
                capture_output=True, text=True, check=True
            )
            api_key = result.stdout.strip().strip('"')
        except Exception:
            pass

    if not api_key:
        print("[clipper] WARNING: No Anthropic API key — using scene detection fallback")
        return detect_scenes_fallback(video_duration, n_clips)

    style_instructions = {
        "hook":    "Focus on the first strong hook, a surprising reveal, or a bold claim that would stop a scroller.",
        "quote":   "Find the most quotable, punchy, standalone statements — things that make sense out of context.",
        "journey": "Find emotional arc moments — the before/after, the struggle, the breakthrough.",
        "info":    "Find the densest information — where the most value is packed in shortest time.",
    }.get(style, "Find the moments most likely to go viral on TikTok/Reels — hooks, surprises, strong emotion.")

    prompt = f"""You are a viral short-form content strategist. Analyze this video transcript and identify the {n_clips} best clips to extract for short-form content (TikTok, Instagram Reels, YouTube Shorts).

Style focus: {style_instructions}

Rules:
- Each clip should be 30–90 seconds long
- Each clip must work as a standalone piece (no "as I mentioned earlier...")
- Clips should not overlap
- Video duration: {sec_to_ts(video_duration)}

Return ONLY a JSON array, no explanation:
[
  {{
    "rank": 1,
    "title": "Short clip title",
    "hook": "The opening line/moment that will stop the scroll",
    "why_viral": "One sentence on why this will perform",
    "start": "MM:SS",
    "end": "MM:SS"
  }},
  ...
]

TRANSCRIPT:
{transcript_text[:12000]}"""

    payload = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        text = data["content"][0]["text"].strip()
        # Extract JSON from response
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(text)
    except Exception as e:
        print(f"[clipper] Claude API error: {e} — falling back to scene detection")
        return detect_scenes_fallback(video_duration, n_clips)

def detect_scenes_fallback(duration: float, n_clips: int) -> list[dict]:
    """Evenly-spaced clip fallback if Claude is unavailable."""
    clip_len = min(60.0, duration / (n_clips + 1))
    clips = []
    for i in range(n_clips):
        start = (duration / (n_clips + 1)) * (i + 1) - clip_len / 2
        end   = start + clip_len
        clips.append({
            "rank": i + 1,
            "title": f"Clip {i+1}",
            "hook": "",
            "why_viral": "Scene-detected",
            "start": sec_to_ts(max(0, start)),
            "end":   sec_to_ts(min(duration, end))
        })
    return clips

# ── step 4: face detection for smart crop ────────────────────────────────────
def detect_face_center(video_path: Path, at_second: float) -> tuple[float, float] | None:
    """Sample a frame and return face center (x_ratio, y_ratio) or None."""
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(at_second * fps))
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return None

    h, w = frame.shape[:2]
    # Use the largest face
    x, y, fw, fh = max(faces, key=lambda f: f[2]*f[3])
    cx = (x + fw / 2) / w
    cy = (y + fh / 2) / h
    return (cx, cy)

# ── step 5: extract + reframe + caption ──────────────────────────────────────
def make_srt(segments: list, start_sec: float, end_sec: float) -> str:
    """Generate SRT from whisper segments for a clip window."""
    srt_lines = []
    idx = 1
    for seg in segments:
        s_start = seg["start"]
        s_end   = seg["end"]
        if s_end < start_sec or s_start > end_sec:
            continue
        # Offset to clip-relative time
        rel_start = max(0, s_start - start_sec)
        rel_end   = min(end_sec - start_sec, s_end - start_sec)
        def fmt(sec):
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            s = int(sec % 60)
            ms = int((sec % 1) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        srt_lines.append(f"{idx}\n{fmt(rel_start)} --> {fmt(rel_end)}\n{seg['text'].strip()}\n")
        idx += 1
    return "\n".join(srt_lines)

def extract_clip(video_path: Path, start_str: str, end_str: str,
                 out_path: Path, srt_path: Path | None,
                 face_center: tuple | None) -> Path:
    """ffmpeg: extract, reframe to 9:16, burn captions."""
    start_sec = ts_to_sec(start_str)
    end_sec   = ts_to_sec(end_str)
    duration  = end_sec - start_sec

    # Get video dimensions
    probe = subprocess.run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json", str(video_path)
    ], capture_output=True, text=True)
    info = json.loads(probe.stdout)
    src_w = info["streams"][0]["width"]
    src_h = info["streams"][0]["height"]

    # 9:16 crop calculation
    target_aspect = 9 / 16
    if src_w / src_h > target_aspect:
        # wider than 9:16 → crop width
        crop_h = src_h
        crop_w = int(src_h * target_aspect)
    else:
        # taller → crop height
        crop_w = src_w
        crop_h = int(src_w / target_aspect)

    # Center on face if detected, else center of frame
    if face_center:
        cx_px = int(face_center[0] * src_w)
        cy_px = int(face_center[1] * src_h)
    else:
        cx_px = src_w // 2
        cy_px = src_h // 2

    crop_x = max(0, min(cx_px - crop_w // 2, src_w - crop_w))
    crop_y = max(0, min(cy_px - crop_h // 2, src_h - crop_h))

    # Build filter chain
    vf_parts = [f"crop={crop_w}:{crop_h}:{crop_x}:{crop_y}", "scale=1080:1920"]

    if srt_path and srt_path.exists():
        # Burn-in captions with bold white text + black outline
        srt_escaped = str(srt_path).replace(":", r"\:").replace("'", r"\'")
        vf_parts.append(
            f"subtitles='{srt_escaped}':force_style="
            "'FontName=Arial,FontSize=14,Bold=1,PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,Outline=2,Alignment=2'"
        )

    vf = ",".join(vf_parts)

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_sec),
        "-i", str(video_path),
        "-t", str(duration),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(out_path)
    ]
    run(cmd, capture_output=False)
    return out_path

# ── step 6: thumbnail ─────────────────────────────────────────────────────────
def make_thumbnail(clip_path: Path, out_path: Path):
    run(["ffmpeg", "-y", "-i", str(clip_path), "-ss", "00:00:02",
         "-vframes", "1", "-q:v", "2", str(out_path)], capture_output=True)

# ── main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="AI video clipper (Vugola-style)")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--url",  help="YouTube/video URL")
    src.add_argument("--file", help="Local video file path")
    parser.add_argument("--clips",  type=int, default=3,   help="Number of clips (default 3)")
    parser.add_argument("--style",  default="hook",
                        choices=["hook","quote","journey","info"],
                        help="Clip style focus (default: hook)")
    parser.add_argument("--whisper-model", default="base",
                        choices=["tiny","base","small","medium","large"],
                        help="Whisper model size (default: base)")
    parser.add_argument("--no-captions", action="store_true", help="Skip caption burn-in")
    parser.add_argument("--dry-run",     action="store_true", help="Show plan, don't extract")
    args = parser.parse_args()

    date_str  = datetime.now().strftime("%Y-%m-%d")
    work_dir  = CLIPS_DIR / f"{date_str}-clipper-{datetime.now().strftime('%H%M%S')}"
    work_dir.mkdir(parents=True, exist_ok=True)
    print(f"[clipper] Output dir: {work_dir}")

    # Download or copy source
    if args.url:
        video_path = download_video(args.url, work_dir)
    else:
        video_path = Path(args.file)
        if not video_path.exists():
            sys.exit(f"[clipper] File not found: {video_path}")

    # Get duration
    probe = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "json", str(video_path)
    ], capture_output=True, text=True)
    duration = float(json.loads(probe.stdout)["format"]["duration"])
    print(f"[clipper] Video duration: {sec_to_ts(duration)}")

    # Transcribe
    transcript = transcribe(video_path, args.whisper_model)
    transcript_text = transcript_to_text(transcript)
    (work_dir / "transcript.txt").write_text(transcript_text)
    print(f"[clipper] Transcript saved → {work_dir}/transcript.txt")

    # Find viral moments
    print(f"[clipper] Asking Claude to find top {args.clips} viral moments ({args.style} style)…")
    moments = find_viral_moments(transcript_text, args.clips, args.style, duration)

    print(f"\n[clipper] ── CLIP PLAN ──────────────────────────────")
    for m in moments:
        print(f"  #{m['rank']} [{m['start']} → {m['end']}] {m['title']}")
        print(f"       Hook: {m.get('hook','')}")
        print(f"       Why:  {m.get('why_viral','')}")
    print()

    if args.dry_run:
        print("[clipper] Dry run — stopping before extraction.")
        return

    # Save clip plan
    (work_dir / "clip-plan.json").write_text(json.dumps(moments, indent=2))

    # Extract each clip
    results = []
    for m in moments:
        clip_slug = slug(m["title"]) or f"clip-{m['rank']}"
        clip_name = f"{m['rank']:02d}-{clip_slug}"
        clip_out  = work_dir / f"{clip_name}.mp4"
        thumb_out = work_dir / f"{clip_name}-thumb.jpg"
        srt_out   = work_dir / f"{clip_name}.srt"

        # Detect face center at midpoint
        mid = (ts_to_sec(m["start"]) + ts_to_sec(m["end"])) / 2
        face = detect_face_center(video_path, mid)
        print(f"[clipper] Clip #{m['rank']}: face center = {face}")

        # Generate SRT if captions enabled
        if not args.no_captions:
            srt = make_srt(
                transcript.get("segments", []),
                ts_to_sec(m["start"]),
                ts_to_sec(m["end"])
            )
            srt_out.write_text(srt)
        else:
            srt_out = None

        extract_clip(video_path, m["start"], m["end"], clip_out, srt_out, face)
        make_thumbnail(clip_out, thumb_out)

        results.append({
            "rank":       m["rank"],
            "title":      m["title"],
            "hook":       m.get("hook", ""),
            "why_viral":  m.get("why_viral", ""),
            "file":       str(clip_out),
            "thumbnail":  str(thumb_out),
            "start":      m["start"],
            "end":        m["end"]
        })
        print(f"[clipper] ✅ Clip {m['rank']} → {clip_out.name}")

    # Summary
    summary = {
        "source":     str(video_path),
        "duration":   sec_to_ts(duration),
        "clips_made": len(results),
        "output_dir": str(work_dir),
        "clips":      results
    }
    (work_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    print(f"\n[clipper] ── DONE ─────────────────────────────────────")
    print(f"  {len(results)} clips in: {work_dir}")
    for r in results:
        print(f"  #{r['rank']} {r['title']}")
        print(f"      {r['file']}")
    print(f"\n  To post to X: python3 scripts/x-post.py --text \"<caption>\" --media <clip.mp4>")

if __name__ == "__main__":
    main()
