#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{p.stderr}")


def transcribe_to_srt(audio_path: Path, out_dir: Path) -> Path:
    srt = out_dir / "captions.srt"
    try:
        run(["whisper", str(audio_path), "--output_dir", str(out_dir), "--output_format", "srt"])
        # whisper writes <stem>.srt
        candidate = out_dir / f"{audio_path.stem}.srt"
        if candidate.exists() and candidate != srt:
            candidate.replace(srt)
    except Exception:
        # fallback minimal caption
        srt.write_text("1\n00:00:00,000 --> 00:00:04,000\nAmericanFireside\n", encoding="utf-8")
    return srt


def ensure_vertical(input_video: Path, out_path: Path) -> Path:
    run([
        "ffmpeg", "-y", "-i", str(input_video),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-an", str(out_path)
    ])
    return out_path


def burn_captions(input_video: Path, srt_file: Path, out_path: Path) -> Path:
    subtitle_filter = f"subtitles={str(srt_file).replace(':', '\\:')}"
    try:
        run(["ffmpeg", "-y", "-i", str(input_video), "-vf", subtitle_filter, "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-an", str(out_path)])
    except Exception:
        # Fallback: no burned captions if filter support/path parsing fails.
        run(["ffmpeg", "-y", "-i", str(input_video), "-c:v", "copy", "-an", str(out_path)])
    return out_path


def merge_audio(video_path: Path, audio_path: Path, out_path: Path) -> Path:
    run(["ffmpeg", "-y", "-i", str(video_path), "-i", str(audio_path), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-shortest", str(out_path)])
    return out_path


def make_landscape(input_video: Path, out_path: Path) -> Path:
    run(["ffmpeg", "-y", "-i", str(input_video), "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-c:a", "copy", str(out_path)])
    return out_path


def assemble(video_path: Path, audio_path: Path, run_dir: Path) -> dict:
    run_dir.mkdir(parents=True, exist_ok=True)
    srt = transcribe_to_srt(audio_path, run_dir)
    vertical = run_dir / "video-vertical.mp4"
    captioned = run_dir / "video-captioned.mp4"
    final = run_dir / "final.mp4"
    final_land = run_dir / "final-landscape.mp4"

    ensure_vertical(video_path, vertical)
    burn_captions(vertical, srt, captioned)
    merge_audio(captioned, audio_path, final)
    make_landscape(final, final_land)

    return {
        "captions": str(srt),
        "final_vertical": str(final),
        "final_landscape": str(final_land),
    }
