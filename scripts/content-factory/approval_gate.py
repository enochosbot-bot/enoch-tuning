#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

PENDING_DIR = Path(__file__).resolve().parents[1] / "approval-pending"
TELEGRAM_TARGET = "-1003772049875:topic:3457"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def _send_telegram_preview(run_id: str, summary: dict, video_path: Optional[Path]) -> dict:
    mode = summary.get("mode", "unknown")
    platform = summary.get("platform", "unknown")
    duration = summary.get("duration", "?")
    cost = summary.get("cost")
    cost_txt = f"${cost:.2f}" if isinstance(cost, (int, float)) and cost is not None else "n/a"
    hook = summary.get("hook", "")

    text = (
        "🎬 Content ready for review\n"
        f"Run: {run_id}\n"
        f"Mode: {mode} | Platform: {platform} | Duration: {duration}s\n"
        f"Cost: {cost_txt}\n\n"
        f"Hook: \"{hook}\"\n\n"
        "Reply with one of:\n"
        f"approve:{run_id}\n"
        f"reject:{run_id}\n"
        f"reshoot:{run_id}"
    )

    cmd = [
        "openclaw",
        "message",
        "send",
        "--channel",
        "telegram",
        "--target",
        TELEGRAM_TARGET,
        "--message",
        text,
    ]

    if video_path and video_path.exists():
        cmd += ["--path", str(video_path)]

    proc = _run(cmd)
    return {
        "ok": proc.returncode == 0,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _pending_path(run_id: str) -> Path:
    return PENDING_DIR / f"{run_id}.json"


def _response_path(run_id: str) -> Path:
    return PENDING_DIR / f"{run_id}-response.json"


def request_approval(run_id: str, run_dir: Path, summary: dict, timeout_hours: int = 4) -> dict:
    """Send live Telegram approval request and wait for response file from poller.

    Poller writes {run_id}-response.json with {action: approve|reject|reshoot, ...}
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    PENDING_DIR.mkdir(parents=True, exist_ok=True)

    send_result = _send_telegram_preview(run_id, summary, run_dir / "final.mp4")

    pending = {
        "run_id": run_id,
        "topic": 3457,
        "target": TELEGRAM_TARGET,
        "created_at": _now_iso(),
        "expires_at": datetime.fromtimestamp(time.time() + timeout_hours * 3600, tz=timezone.utc).isoformat(),
        "status": "pending",
        "summary": summary,
        "send_result": send_result,
    }
    _pending_path(run_id).write_text(json.dumps(pending, indent=2), encoding="utf-8")

    deadline = time.time() + timeout_hours * 3600
    response_file = _response_path(run_id)

    while time.time() < deadline:
        if response_file.exists():
            try:
                response = json.loads(response_file.read_text(encoding="utf-8"))
                action = str(response.get("action", "")).lower()
                if action in {"approve", "reject", "reshoot"}:
                    return {
                        "status": "approved" if action == "approve" else ("rejected" if action == "reject" else "reshoot"),
                        "by": response.get("by", "telegram"),
                        "notes": response.get("notes", ""),
                        "ts": response.get("ts", _now_iso()),
                        "action": action,
                    }
            except Exception:
                pass
        time.sleep(10)

    return {
        "status": "rejected",
        "by": "system-timeout",
        "notes": f"No approval response in {timeout_hours}h; auto-rejected.",
        "ts": _now_iso(),
        "action": "reject",
    }
