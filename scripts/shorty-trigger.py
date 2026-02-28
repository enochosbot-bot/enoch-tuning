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
    """Process video to clips (transcribe, cut, caption, format) WITHOUT uploading.
    Output goes to shorty/review/ for Deacon QC."""
    
    pipeline_script = Path(__file__).resolve().parent / "content-pipeline" / "pipeline.sh"
    review_dir = Path.home() / ".openclaw" / "agents" / "creative" / "workspace" / "shorty" / "review"
    
    if not pipeline_script.exists():
        print(f"Pipeline script not found: {pipeline_script}")
        return 1
    
    review_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "bash",
        str(pipeline_script),
        input_value,
        "--output-dir",
        str(review_dir),
    ]
    p = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stdout)
        print(p.stderr)
        return 1
    
    # Alert that clips are ready for review (don't upload)
    send_review_alert(input_value, str(review_dir))
    return 0


def send_review_alert(source: str, review_dir: str) -> None:
    """Notify Deacon that clips are ready for QC."""
    msg = f"📹 Clips ready for review: {source}\nCheck: {review_dir}"
    subprocess.run(
        [
            "openclaw",
            "message",
            "send",
            "--channel",
            "telegram",
            "--target",
            "5801636051",  # Deacon's chat
            "--message",
            msg,
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def check_inbox_for_new_videos() -> Optional[str]:
    """Watch shorty/inbox/ for new .mp4/.webm files and return the first one found."""
    inbox_dir = Path.home() / ".openclaw" / "agents" / "creative" / "workspace" / "shorty" / "inbox"
    if not inbox_dir.exists():
        return None
    
    # Look for video files that haven't been processed yet
    for video_file in sorted(inbox_dir.glob("*.mp4")) + sorted(inbox_dir.glob("*.webm")):
        if video_file.is_file():
            return str(video_file)
    return None


def main() -> int:
    state = load_state()
    last_id = int(state.get("last_processed_message_id", 0))

    # Check for new YouTube links in topic session
    new_id, trigger_input, note = latest_unprocessed_trigger(last_id)
    if trigger_input:
        send_ack(trigger_input)
        rc = run_clip_pipeline(trigger_input)
        state["last_processed_message_id"] = new_id
        save_state(state)
        if rc == 0:
            print(f"Processed message {new_id}: {trigger_input}")
            return 0
        print(f"Processing failed for message {new_id}: {trigger_input}")
        return rc
    
    if note:
        print(note)
    
    # Also check inbox for new videos dropped by other agents
    inbox_video = check_inbox_for_new_videos()
    if inbox_video:
        print(f"Found video in inbox: {inbox_video}")
        send_ack(inbox_video)
        rc = run_clip_pipeline(inbox_video)
        if rc == 0:
            print(f"Processed inbox video: {inbox_video}")
            return 0
        print(f"Processing failed for inbox video: {inbox_video}")
        return rc
    
    print("No new triggers found (no topic messages, no inbox videos).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
