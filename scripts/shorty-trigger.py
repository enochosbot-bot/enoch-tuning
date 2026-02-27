#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Optional

STATE_PATH = Path(__file__).resolve().parent / "shorty-trigger-state.json"
SESSIONS_ROOT = Path.home() / ".openclaw" / "agents"
TOPIC_SUFFIX = "topic-3457.jsonl"

YOUTUBE_PATTERNS = [
    re.compile(r"https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+[^\s]*", re.I),
    re.compile(r"https?://youtu\.be/[\w-]+[^\s]*", re.I),
]
VIDEO_URL_PATTERN = re.compile(r"https?://[^\s]+\.(?:mp4|mov|mkv)(?:\?[^\s]*)?", re.I)


def load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"last_processed_message_id": 0}


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def find_topic_session_file() -> Optional[Path]:
    candidates = list(SESSIONS_ROOT.glob(f"*/sessions/*{TOPIC_SUFFIX}"))
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def extract_message_id(user_text: str) -> int:
    m = re.search(r'"message_id"\s*:\s*"?(\d+)"?', user_text)
    return int(m.group(1)) if m else 0


def extract_candidate_input(user_text: str) -> Optional[str]:
    # YouTube URLs
    for pat in YOUTUBE_PATTERNS:
        m = pat.search(user_text)
        if m:
            return m.group(0)
    # direct video links
    m2 = VIDEO_URL_PATTERN.search(user_text)
    if m2:
        return m2.group(0)
    # simple local file hints (if user pasted path)
    m3 = re.search(r"(/[\w./-]+\.(?:mp4|mov|mkv))", user_text, re.I)
    if m3:
        return m3.group(1)
    return None


def latest_unprocessed_trigger(last_processed_id: int) -> tuple[int, Optional[str], Optional[str]]:
    session_file = find_topic_session_file()
    if not session_file:
        return last_processed_id, None, "No topic-3457 session file found"

    best_id = last_processed_id
    trigger_input = None

    with session_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if obj.get("type") != "message":
                continue
            msg = obj.get("message", {})
            if msg.get("role") != "user":
                continue
            content = msg.get("content", [])
            text_parts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
            user_text = "\n".join(text_parts)
            mid = extract_message_id(user_text)
            if mid <= last_processed_id:
                continue
            candidate = extract_candidate_input(user_text)
            if candidate:
                best_id = mid
                trigger_input = candidate

    return best_id, trigger_input, None


def send_ack(input_value: str) -> None:
    # Best-effort via openclaw chat send command; ignore failures.
    msg = f"🎬 On it — clipping now...\nSource: {input_value}"
    subprocess.run(
        [
            "openclaw",
            "message",
            "send",
            "--channel",
            "telegram",
            "--target",
            "-1003772049875:topic:3457",
            "--message",
            msg,
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def run_clip_pipeline(input_value: str) -> int:
    cmd = [
        "python3",
        str(Path(__file__).resolve().parent / "content-factory.py"),
        input_value,
        "--mode",
        "clip",
        "--platforms",
        "yt,x",
    ]
    p = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stdout)
        print(p.stderr)
    return p.returncode


def main() -> int:
    state = load_state()
    last_id = int(state.get("last_processed_message_id", 0))

    new_id, trigger_input, note = latest_unprocessed_trigger(last_id)
    if note:
        print(note)
        return 0

    if not trigger_input:
        print("No new URL/video trigger found.")
        return 0

    send_ack(trigger_input)
    rc = run_clip_pipeline(trigger_input)

    # Only advance state after attempted processing to avoid duplicate storms.
    state["last_processed_message_id"] = new_id
    save_state(state)

    if rc == 0:
        print(f"Processed message {new_id}: {trigger_input}")
        return 0
    print(f"Processing failed for message {new_id}: {trigger_input}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
