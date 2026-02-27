#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CF_DIR = ROOT / "content-factory"
RUNS_DIR = Path(__file__).resolve().parents[1] / "runs"
LOG_PATH = ROOT / "content-factory-log.jsonl"


def load_func(module: str, func: str):
    p = CF_DIR / module
    spec = importlib.util.spec_from_file_location(module.replace(".py", ""), p)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return getattr(mod, func)


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True)


def pick_video_from_vidgen_output(stdout: str) -> tuple[str | None, str | None]:
    lines = stdout.splitlines()
    order = ["kling", "luma", "minimax", "runway"]
    found: dict[str, str] = {}
    cur = None
    for line in lines:
        if line.startswith("- ") and ":" in line:
            cur = line.split(":", 1)[0].replace("-", "").strip().lower()
        if "file:" in line and cur:
            path = line.split("file:", 1)[1].strip()
            found[cur] = path
    for p in order:
        if p in found:
            return p, found[p]
    return None, None


def synth_voice(text: str, out_mp3: Path) -> Path:
    aiff = out_mp3.with_suffix(".aiff")
    say_res = run(["say", "-v", "Samantha", "-o", str(aiff), text])
    if say_res.returncode != 0:
        raise RuntimeError(f"say failed: {say_res.stderr}")
    ff = run(["ffmpeg", "-y", "-i", str(aiff), "-codec:a", "libmp3lame", "-q:a", "3", str(out_mp3)])
    if ff.returncode != 0:
        raise RuntimeError(f"ffmpeg audio conversion failed: {ff.stderr}")
    aiff.unlink(missing_ok=True)
    return out_mp3


def placeholder_video(out_path: Path, duration: int, text: str) -> Path:
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:d={duration}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out_path)
    ]
    res = run(cmd)
    if res.returncode != 0:
        raise RuntimeError(res.stderr)
    return out_path


def append_log(entry: dict):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Content Factory orchestrator")
    parser.add_argument("topic")
    parser.add_argument("--mode", choices=["shorts", "claudebot", "clip"], default="shorts")
    parser.add_argument("--platforms", default="yt,x")
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--voice", default="Harry")
    parser.add_argument("--raw", action="store_true")
    parser.add_argument("--no-post", action="store_true")
    parser.add_argument("--approve", action="store_true", default=True)
    args = parser.parse_args()

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    generate_script = load_func("script_writer.py", "generate_script")
    assemble = load_func("assembler.py", "assemble")
    request_approval = load_func("approval_gate.py", "request_approval")
    distribute = load_func("distributor.py", "distribute")

    script = generate_script(args.topic, args.duration, "americanfireside")
    (run_dir / "script.json").write_text(json.dumps(script, indent=2), encoding="utf-8")

    # Generate video
    video_path = run_dir / "video.mp4"
    selected_platform = "placeholder"
    cost = None
    if args.mode == "shorts":
        vg = run(["python3", str(ROOT / "vidgen.py"), args.topic, "--duration", str(args.duration)] + (["--raw"] if args.raw else []))
        plat, picked = pick_video_from_vidgen_output(vg.stdout)
        if picked and Path(picked).exists():
            selected_platform = plat or "unknown"
            video_path.write_bytes(Path(picked).read_bytes())
        else:
            placeholder_video(video_path, args.duration, "AmericanFireside")
    elif args.mode == "claudebot":
        cb = run(["python3", str(ROOT / "claude-bot-render.py"), args.topic])
        # fallback placeholder if script output path unknown
        placeholder_video(video_path, args.duration, "ClaudeBot")
    else:
        placeholder_video(video_path, args.duration, "Clip Mode")

    # Voiceover
    voice_path = run_dir / "voiceover.mp3"
    synth_voice(script.get("tts_text") or script.get("full_script") or args.topic, voice_path)

    assembled = assemble(video_path, voice_path, run_dir)

    metadata = {
        "run_id": run_id,
        "topic": args.topic,
        "mode": args.mode,
        "script": script,
        "video": {"platform": selected_platform, "file": str(video_path), "cost": cost},
        "voice": {"voice_id": args.voice, "file": str(voice_path)},
        "final": {"vertical": assembled["final_vertical"], "landscape": assembled["final_landscape"]},
        "approval": {"status": "skipped" if args.no_post else "pending"},
        "posted": {},
    }

    if not args.no_post:
        approval = request_approval(
            run_id,
            run_dir,
            {
                "mode": args.mode,
                "topic": args.topic,
                "platform": selected_platform,
                "duration": args.duration,
                "cost": cost,
                "hook": script.get("hook", ""),
            },
            timeout_hours=4,
        )
        metadata["approval"] = approval

        if approval.get("action") == "reshoot" and args.mode == "shorts":
            # One reshoot attempt: nudge prompt and regenerate.
            vg2 = run(["python3", str(ROOT / "vidgen.py"), f"{args.topic} cinematic alternative take", "--duration", str(args.duration)] + (["--raw"] if args.raw else []))
            plat2, picked2 = pick_video_from_vidgen_output(vg2.stdout)
            if picked2 and Path(picked2).exists():
                selected_platform = plat2 or selected_platform
                video_path.write_bytes(Path(picked2).read_bytes())
                assembled = assemble(video_path, voice_path, run_dir)
                metadata["final"] = {"vertical": assembled["final_vertical"], "landscape": assembled["final_landscape"]}
                approval = request_approval(
                    run_id,
                    run_dir,
                    {
                        "mode": args.mode,
                        "topic": args.topic,
                        "platform": selected_platform,
                        "duration": args.duration,
                        "cost": cost,
                        "hook": script.get("hook", ""),
                    },
                    timeout_hours=4,
                )
                metadata["approval"] = approval

        if approval.get("status") == "approved":
            posts = distribute(
                run_dir,
                [p.strip() for p in args.platforms.split(",") if p.strip()],
                script.get("hook", "AmericanFireside clip")[:100],
                script.get("full_script", ""),
                ["AmericanFireside", "Faith", "Freedom"],
            )
            metadata["posted"] = posts

    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    append_log({"run_id": run_id, "topic": args.topic, "mode": args.mode, "run_dir": str(run_dir), "approval": metadata["approval"], "posted": metadata["posted"]})

    print(str(run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
