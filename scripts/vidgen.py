#!/usr/bin/env python3
"""
vidgen.py — Multi-platform AI video generator with Claude as prompt optimizer

Usage:
  python3 scripts/vidgen.py "30-second AmericanFireside intro with eagles"
  python3 scripts/vidgen.py "patriotic montage" --platforms kling,luma
  python3 scripts/vidgen.py "product demo" --duration 10
  python3 scripts/vidgen.py "eagle soaring" --raw

Platforms: kling, minimax (Hailuo 2.3), luma, runway
Output: ~/Desktop/vidgen-output/{timestamp}/
Logs:   scripts/vidgen-log.jsonl

API Key setup (one-time, per platform):
  security add-generic-password -s KLING_API_KEY    -w "ACCESS_KEY_ID:SECRET_KEY" -a <username>
  security add-generic-password -s MINIMAX_API_KEY  -w "your-key"                 -a <username>
  security add-generic-password -s LUMA_API_KEY     -w "your-key"                 -a <username>
  security add-generic-password -s RUNWAY_API_KEY   -w "your-key"                 -a <username>
  (ANTHROPIC_API_KEY already in Keychain for Claude optimizer)

Install deps:
  pip install aiohttp anthropic pyjwt lumaai runwayml
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ── Keychain reader ──────────────────────────────────────────────────────────

def get_key(service: str) -> str | None:
    """Read a secret from macOS Keychain, fall back to env."""
    try:
        r = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-w"],
            capture_output=True, text=True
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return os.environ.get(service)


# ── Keys ─────────────────────────────────────────────────────────────────────

KEYS = {
    "anthropic": get_key("ANTHROPIC_API_KEY"),
    "minimax":   get_key("MINIMAX_API_KEY"),
    "kling":     get_key("KLING_API_KEY"),
    "luma":      get_key("LUMA_API_KEY"),
    "runway":    get_key("RUNWAY_API_KEY"),
}

ALL_PLATFORMS     = ["kling", "minimax", "luma", "runway"]
AVAILABLE         = [p for p in ALL_PLATFORMS if KEYS.get(p)]
MISSING           = [p for p in ALL_PLATFORMS if not KEYS.get(p)]

OUTPUT_BASE = Path.home() / "Desktop" / "vidgen-output"
LOG_FILE    = Path(__file__).parent / "vidgen-log.jsonl"

KEY_NAMES = {
    "kling":    "KLING_API_KEY   (format: ACCESS_KEY_ID:SECRET_KEY from klingai.com)",
    "minimax":  "MINIMAX_API_KEY (from platform.minimax.io)",
    "luma":     "LUMA_API_KEY    (from lumalabs.ai)",
    "runway":   "RUNWAY_API_KEY  (from runwayml.com)",
}


# ── Claude Prompt Optimizer ──────────────────────────────────────────────────

def optimize_prompts(user_prompt: str, platforms: list[str]) -> dict[str, str]:
    """Use Claude Haiku to generate platform-optimized prompts in parallel."""
    if not KEYS.get("anthropic"):
        print("⚠️  ANTHROPIC_API_KEY not found — using raw prompt")
        return {p: user_prompt for p in platforms}

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=KEYS["anthropic"])

        style_notes = {
            "kling":   "Cinematic. Lead with camera movement (slow dolly, aerial pull-back, tracking shot). Explicit motion verbs. Golden ratio framing.",
            "minimax": "Scene-first description. Use style tags like [cinematic], [4K], [golden hour], [slow motion]. Rich sensory detail.",
            "luma":    "Atmospheric and dreamlike. Focus on mood, light quality, texture. Works well with ethereal or natural themes.",
            "runway":  "Photorealistic precision. Professional film language (rack focus, truck left, Dutch angle). Specific f-stop / aperture language optional.",
        }

        active_notes = "\n".join(f"- {p}: {style_notes[p]}" for p in platforms if p in style_notes)

        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1200,
            messages=[{
                "role": "user",
                "content": f"""Optimize this video generation prompt for each platform listed below.
Keep each under 180 words. Be specific about visuals, motion, lighting, mood.
Return ONLY valid JSON — no markdown, no commentary.

User prompt: "{user_prompt}"

Platforms and their style preferences:
{active_notes}

Return format: {{"kling": "...", "minimax": "...", "luma": "..."}}
Only include keys for these platforms: {', '.join(platforms)}"""
            }]
        )

        raw = msg.content[0].text.strip()
        # Strip markdown fences if present
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.split("```")[0]

        optimized = json.loads(raw.strip())
        # Fill any missing platforms with raw prompt
        for p in platforms:
            if p not in optimized:
                optimized[p] = user_prompt
        return optimized

    except Exception as e:
        print(f"⚠️  Claude optimizer error ({e}) — using raw prompt")
        return {p: user_prompt for p in platforms}


# ── Platform: MiniMax / Hailuo ───────────────────────────────────────────────

async def generate_minimax(prompt: str, duration: int, output_dir: Path) -> dict:
    import aiohttp

    result  = {"platform": "minimax", "status": "pending"}
    headers = {"Authorization": f"Bearer {KEYS['minimax']}"}
    start   = time.time()

    try:
        async with aiohttp.ClientSession() as s:
            # Submit
            payload = {
                "prompt":     prompt,
                "model":      "MiniMax-Hailuo-2.3",
                "duration":   min(duration, 10),
                "resolution": "1080P",
            }
            async with s.post("https://api.minimax.io/v1/video_generation",
                              headers=headers, json=payload) as r:
                data = await r.json()
            if "task_id" not in data:
                return {**result, "status": "error", "error": str(data)}
            task_id = data["task_id"]
            print(f"  [minimax] Task {task_id} submitted — polling...")

            # Poll
            deadline = time.time() + 300
            file_id  = None
            while time.time() < deadline:
                await asyncio.sleep(10)
                async with s.get(
                    f"https://api.minimax.io/v1/query/video_generation?task_id={task_id}",
                    headers=headers
                ) as r:
                    data   = await r.json()
                    status = data.get("status", "Unknown")
                    print(f"  [minimax] {status}")
                    if status == "Success":
                        file_id = data.get("file_id")
                        break
                    if status in ("Failed", "Error"):
                        return {**result, "status": "error", "error": f"Task failed: {data}"}
            else:
                return {**result, "status": "error", "error": "Timeout (5 min)"}

            # Retrieve URL
            async with s.get(
                f"https://api.minimax.io/v1/files/retrieve?file_id={file_id}",
                headers=headers
            ) as r:
                data  = await r.json()
                dl    = data.get("file", {}).get("download_url")

            # Download
            out = output_dir / "minimax-hailuo.mp4"
            async with s.get(dl) as r:
                out.write_bytes(await r.read())

        return {
            "platform":      "minimax",
            "status":        "success",
            "file":          str(out),
            "duration_s":    round(time.time() - start),
            "cost_estimate": "~$0.10–0.25",
        }

    except Exception as e:
        return {**result, "status": "error", "error": str(e)}


# ── Platform: Kling ──────────────────────────────────────────────────────────

async def generate_kling(prompt: str, duration: int, output_dir: Path) -> dict:
    import aiohttp

    result = {"platform": "kling", "status": "pending"}
    start  = time.time()

    # Kling key format: "ACCESS_KEY_ID:SECRET_KEY"
    raw_key = KEYS["kling"]
    parts   = raw_key.split(":", 1)
    if len(parts) != 2:
        return {**result, "status": "error",
                "error": "KLING_API_KEY must be 'ACCESS_KEY_ID:SECRET_KEY'"}

    access_key_id, secret_key = parts

    try:
        import jwt  # pip install pyjwt
    except ImportError:
        return {**result, "status": "error", "error": "pyjwt not installed — run: pip install pyjwt"}

    now   = int(time.time())
    token = jwt.encode(
        {"iss": access_key_id, "exp": now + 1800, "nbf": now - 5},
        secret_key, algorithm="HS256"
    )
    headers  = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    base_url = "https://api.klingai.com"

    try:
        async with aiohttp.ClientSession() as s:
            payload = {
                "model_name":   "kling-v2-master",
                "prompt":       prompt,
                "duration":     str(min(duration, 10)),
                "aspect_ratio": "16:9",
                "mode":         "std",
            }
            async with s.post(f"{base_url}/v1/videos/text2video",
                              headers=headers, json=payload) as r:
                data = await r.json()
            if data.get("code") != 0:
                return {**result, "status": "error",
                        "error": data.get("message", str(data))}
            task_id = data["data"]["task_id"]
            print(f"  [kling] Task {task_id} submitted — polling...")

            # Poll
            deadline  = time.time() + 300
            video_url = None
            while time.time() < deadline:
                await asyncio.sleep(10)
                async with s.get(f"{base_url}/v1/videos/text2video/{task_id}",
                                 headers=headers) as r:
                    data   = await r.json()
                    status = data.get("data", {}).get("task_status", "")
                    print(f"  [kling] {status}")
                    if status == "succeed":
                        videos    = data["data"].get("task_result", {}).get("videos", [])
                        video_url = videos[0].get("url") if videos else None
                        break
                    if status == "failed":
                        msg = data.get("data", {}).get("task_status_msg", "Failed")
                        return {**result, "status": "error", "error": msg}
            else:
                return {**result, "status": "error", "error": "Timeout (5 min)"}

            if not video_url:
                return {**result, "status": "error", "error": "No video URL in response"}

            out = output_dir / "kling.mp4"
            async with s.get(video_url) as r:
                out.write_bytes(await r.read())

        cost = round(min(duration, 10) * 0.014, 3)
        return {
            "platform":      "kling",
            "status":        "success",
            "file":          str(out),
            "duration_s":    round(time.time() - start),
            "cost_estimate": f"~${cost}",
        }

    except Exception as e:
        return {**result, "status": "error", "error": str(e)}


# ── Platform: Luma Dream Machine ─────────────────────────────────────────────

async def generate_luma(prompt: str, duration: int, output_dir: Path) -> dict:
    import aiohttp

    result = {"platform": "luma", "status": "pending"}
    start  = time.time()

    try:
        from lumaai import LumaAI  # pip install lumaai
    except ImportError:
        return {**result, "status": "error", "error": "lumaai not installed — run: pip install lumaai"}

    try:
        client     = LumaAI(auth_token=KEYS["luma"])
        generation = client.generations.create(prompt=prompt, aspect_ratio="16:9")
        print(f"  [luma] Generation {generation.id} submitted — polling...")

        deadline = time.time() + 300
        while time.time() < deadline:
            await asyncio.sleep(8)
            generation = client.generations.get(generation.id)
            print(f"  [luma] {generation.state}")
            if generation.state == "completed":
                break
            if generation.state == "failed":
                return {**result, "status": "error",
                        "error": generation.failure_reason or "Failed"}
        else:
            return {**result, "status": "error", "error": "Timeout (5 min)"}

        video_url = generation.assets.video
        out       = output_dir / "luma.mp4"
        async with aiohttp.ClientSession() as s:
            async with s.get(video_url) as r:
                out.write_bytes(await r.read())

        return {
            "platform":      "luma",
            "status":        "success",
            "file":          str(out),
            "duration_s":    round(time.time() - start),
            "cost_estimate": "~$0.10–0.40",
        }

    except Exception as e:
        return {**result, "status": "error", "error": str(e)}


# ── Platform: Runway ML ──────────────────────────────────────────────────────

async def generate_runway(prompt: str, duration: int, output_dir: Path) -> dict:
    import aiohttp

    result = {"platform": "runway", "status": "pending"}
    start  = time.time()

    try:
        import runwayml  # pip install runwayml
    except ImportError:
        return {**result, "status": "error", "error": "runwayml not installed — run: pip install runwayml"}

    try:
        client = runwayml.RunwayML(api_key=KEYS["runway"])
        task   = client.image_to_video.create(
            model       = "gen4_turbo",
            prompt_text = prompt,
            duration    = min(duration, 10),
            ratio       = "1280:720",
        )
        print(f"  [runway] Task {task.id} submitted — polling...")

        deadline = time.time() + 300
        while time.time() < deadline:
            await asyncio.sleep(10)
            task = client.tasks.retrieve(task.id)
            print(f"  [runway] {task.status}")
            if task.status == "SUCCEEDED":
                break
            if task.status == "FAILED":
                return {**result, "status": "error", "error": str(task.failure)}
        else:
            return {**result, "status": "error", "error": "Timeout (5 min)"}

        video_url = task.output[0]
        out       = output_dir / "runway.mp4"
        async with aiohttp.ClientSession() as s:
            async with s.get(video_url) as r:
                out.write_bytes(await r.read())

        return {
            "platform":      "runway",
            "status":        "success",
            "file":          str(out),
            "duration_s":    round(time.time() - start),
            "cost_estimate": "~$0.50–1.50",
        }

    except Exception as e:
        return {**result, "status": "error", "error": str(e)}


# ── Orchestrator ─────────────────────────────────────────────────────────────

async def run(args):
    # Resolve platforms
    if args.platforms:
        requested = [p.strip().lower() for p in args.platforms.split(",")]
    else:
        requested = ["kling", "minimax", "luma"]  # default set

    active  = [p for p in requested if p in AVAILABLE]
    skipped = [p for p in requested if p not in AVAILABLE]

    for p in skipped:
        print(f"⚠️  Skipping {p} — {KEY_NAMES.get(p, p.upper()+'_API_KEY')} not found")

    if not active:
        print("\n❌ No platforms available. Set API keys in Keychain:\n")
        for p in requested:
            print(f"  security add-generic-password -s {p.upper()+'_API_KEY'} -w YOUR_KEY -a <username>")
        sys.exit(1)

    # Setup output dir
    ts      = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = OUTPUT_BASE / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🎬  vidgen")
    print(f"    Prompt   : {args.prompt[:80]}{'...' if len(args.prompt) > 80 else ''}")
    print(f"    Platforms: {', '.join(active)}")
    print(f"    Duration : {args.duration}s")
    print(f"    Output   : {run_dir}\n")

    # Optimize prompts
    if not args.raw and KEYS.get("anthropic"):
        print("🧠  Claude optimizing prompts for each platform...\n")
        prompts = optimize_prompts(args.prompt, active)
        for p, opt in prompts.items():
            print(f"  [{p}] {opt[:90]}{'...' if len(opt) > 90 else ''}")
        print()
    else:
        prompts = {p: args.prompt for p in active}

    # Launch all in parallel
    print(f"🚀  Launching {len(active)} generation(s) in parallel...\n")

    dispatch = {
        "minimax": generate_minimax,
        "kling":   generate_kling,
        "luma":    generate_luma,
        "runway":  generate_runway,
    }
    tasks = [
        dispatch[p](prompts.get(p, args.prompt), args.duration, run_dir)
        for p in active
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Report
    print("\n" + "─" * 55)
    print("📊  Results:\n")

    successes = []
    for r in results:
        if isinstance(r, Exception):
            print(f"  ❌  (exception) {r}")
            continue
        p      = r.get("platform", "?")
        status = r.get("status", "?")
        if status == "success":
            print(f"  ✅  {p:12s} {r.get('file')}  ({r.get('cost_estimate','?')})  [{r.get('duration_s','?')}s]")
            successes.append(r)
        else:
            print(f"  ❌  {p:12s} {r.get('error', 'unknown error')}")

    print()
    if successes:
        print(f"🎉  {len(successes)} video(s) ready → {run_dir}")
        if len(successes) > 1:
            print("    Pick your favorite and post it.")
    else:
        print("❌  No videos generated. Check errors above.")

    # Write log
    entry = {
        "ts":        ts,
        "prompt":    args.prompt,
        "platforms": active,
        "raw":       args.raw,
        "results":   [r for r in results if not isinstance(r, Exception)],
        "output":    str(run_dir),
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    avail_str  = "  ✅ " + "\n  ✅ ".join(AVAILABLE) if AVAILABLE else "  (none — set API keys)"
    missing_str = ("\nMissing keys:\n  🔑 " + "\n  🔑 ".join(MISSING)) if MISSING else ""

    parser = argparse.ArgumentParser(
        description="vidgen — Multi-platform AI video generator (Claude-optimized)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available platforms:{avail_str}{missing_str}

Examples:
  python3 scripts/vidgen.py "AmericanFireside 30s intro, soaring eagle, American flag, cinematic golden hour"
  python3 scripts/vidgen.py "faith and freedom montage, dramatic" --platforms kling,luma
  python3 scripts/vidgen.py "product demo walkthrough" --duration 10 --raw
  python3 scripts/vidgen.py "warrior culture clip" --platforms minimax

Add an API key:
  security add-generic-password -s KLING_API_KEY -w "AK_ID:SECRET" -a <username>
""",
    )
    parser.add_argument("prompt",       help="Plain English description of the video you want")
    parser.add_argument("--platforms",  help="Comma-separated platforms: kling,minimax,luma,runway (default: kling,minimax,luma)")
    parser.add_argument("--duration",   type=int, default=6, help="Target duration in seconds (default: 6, max 10)")
    parser.add_argument("--raw",        action="store_true", help="Skip Claude prompt optimization")
    args = parser.parse_args()

    asyncio.run(run(args))


if __name__ == "__main__":
    main()
