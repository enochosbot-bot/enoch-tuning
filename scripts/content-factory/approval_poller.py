#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

PENDING_DIR = Path(__file__).resolve().parents[1] / "approval-pending"
SESSIONS_ROOT = Path.home() / ".openclaw" / "agents"
TOPIC_SUFFIX = "topic-3457.jsonl"


CMD_RE = re.compile(r"\b(approve|reject|reshoot)\s*:\s*([0-9]{8}-[0-9]{6})\b", re.I)
MID_RE = re.compile(r'"message_id"\s*:\s*"?(\d+)"?')
USER_RE = re.compile(r'"label"\s*:\s*"([^"]+)"')


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _latest_session_file() -> Path | None:
    cands = list(SESSIONS_ROOT.glob(f"*/sessions/*{TOPIC_SUFFIX}"))
    if not cands:
        return None
    cands.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return cands[0]


def _extract_text(msg_obj: dict) -> str:
    msg = msg_obj.get("message", {})
    chunks = msg.get("content", [])
    return "\n".join(c.get("text", "") for c in chunks if isinstance(c, dict) and c.get("type") == "text")


def _extract_mid(text: str) -> int:
    m = MID_RE.search(text)
    return int(m.group(1)) if m else 0


def _extract_user(text: str) -> str:
    m = USER_RE.search(text)
    return m.group(1) if m else "unknown"


def _scan_commands() -> list[dict]:
    sf = _latest_session_file()
    if not sf:
        return []

    out: list[dict] = []
    with sf.open("r", encoding="utf-8") as f:
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
            if obj.get("message", {}).get("role") != "user":
                continue

            text = _extract_text(obj)
            mm = CMD_RE.search(text)
            if not mm:
                continue
            out.append(
                {
                    "action": mm.group(1).lower(),
                    "run_id": mm.group(2),
                    "message_id": _extract_mid(text),
                    "by": _extract_user(text),
                    "raw": text,
                }
            )
    return out


def main() -> int:
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    pending_files = sorted(PENDING_DIR.glob("*.json"))
    pending_files = [p for p in pending_files if not p.name.endswith("-response.json")]
    if not pending_files:
        print("No pending approvals.")
        return 0

    cmds = _scan_commands()
    if not cmds:
        print("No approval commands found.")
        return 0

    processed = 0
    for p in pending_files:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        run_id = data.get("run_id")
        if not run_id:
            continue

        since_mid = int(data.get("last_checked_message_id", 0) or 0)
        candidates = [c for c in cmds if c["run_id"] == run_id and c["message_id"] > since_mid]
        if not candidates:
            continue

        chosen = sorted(candidates, key=lambda x: x["message_id"])[-1]
        response_path = PENDING_DIR / f"{run_id}-response.json"
        response_path.write_text(
            json.dumps(
                {
                    "action": chosen["action"],
                    "run_id": run_id,
                    "message_id": chosen["message_id"],
                    "by": chosen["by"],
                    "ts": _now_iso(),
                    "notes": "Received via Telegram topic 3457 command",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        p.unlink(missing_ok=True)
        processed += 1

    print(f"Processed approvals: {processed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
