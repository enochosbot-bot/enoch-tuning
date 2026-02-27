#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

import importlib.util

def _load_func(module_file: Path, func_name: str):
    spec = importlib.util.spec_from_file_location(module_file.stem, module_file)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return getattr(mod, func_name)


def _run(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return {"status": "success" if p.returncode == 0 else "failed", "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}


def distribute(run_dir: Path, platforms: list[str], title: str, description: str, tags: list[str]) -> dict:
    final_vertical = run_dir / "final.mp4"
    final_landscape = run_dir / "final-landscape.mp4"
    out: dict = {}
    base = Path(__file__).resolve().parent
    upload_youtube = _load_func(base / "youtube_upload.py", "upload_youtube")
    upload_tiktok = _load_func(base / "tiktok_upload.py", "upload_tiktok")

    for p in platforms:
        p = p.strip().lower()
        if p == "yt":
            out["youtube"] = upload_youtube(final_vertical, title, description, tags)
        elif p == "tiktok":
            out["tiktok"] = upload_tiktok(final_vertical, title)
        elif p == "x":
            script = Path(__file__).resolve().parents[1] / "x-post.py"
            out["x"] = _run(["python3", str(script), title])
        elif p == "linkedin":
            script = Path(__file__).resolve().parents[1] / "linkedin-post.py"
            out["linkedin"] = _run(["python3", str(script), title])
        elif p == "ig":
            out["instagram"] = {"status": "skipped", "reason": "Not implemented"}
        else:
            out[p] = {"status": "skipped", "reason": "Unknown platform"}

    if not final_landscape.exists():
        out.setdefault("notes", []).append("Missing final-landscape.mp4")
    return out
