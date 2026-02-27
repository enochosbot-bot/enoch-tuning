#!/usr/bin/env python3
"""Daily social post pipeline — BL-005.

Reads markdown drafts from shared-context/drafts/, picks the next unsent post,
sends it to Deacon via Telegram for approval, and appends a JSONL log entry.

Designed to run from cron. Exits cleanly when no posts are pending.

Usage:
    python3 scripts/social-post-pipeline.py [--dry-run]
    python3 scripts/social-post-pipeline.py --draft-dir path/to/drafts --target @deacon
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


# Matches ## Section Headers in draft markdown files
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
POST_TITLE_RE = re.compile(r"^post\s+\d+\b", re.IGNORECASE)

# Skip files that are review/verdict docs, not actual drafts
SKIP_PATTERNS = re.compile(r"(-reviewed|-verdict|-notes|-review)\.md$", re.IGNORECASE)

# Sections to skip (metadata/word-count sections, not actual posts)
SKIP_SECTION_PREFIXES = ("word count", "verdict", "what to use", "recommended")

# Detect platform from filename prefix
PLATFORM_RE = re.compile(r"^(linkedin|x|twitter|instagram|tiktok)", re.IGNORECASE)


@dataclass
class DraftPost:
    source_file: Path
    title: str
    body: str
    platform: str = field(default="unknown")

    def __post_init__(self) -> None:
        if self.platform == "unknown":
            m = PLATFORM_RE.match(self.source_file.stem)
            self.platform = m.group(1).lower() if m else "unknown"

    @property
    def post_id(self) -> str:
        # Use only the filename (not full path) so ID is stable regardless of cwd
        raw = f"{self.source_file.name}:{self.title}\n{self.body}".encode("utf-8")
        return hashlib.sha1(raw).hexdigest()

    @property
    def post_id_short(self) -> str:
        return self.post_id[:10]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_draft_file(path: Path) -> bool:
    """Return True if this file should be treated as a post draft (not a review/verdict doc)."""
    if SKIP_PATTERNS.search(path.name):
        return False
    # Check frontmatter status — skip files explicitly marked as reviewed/archived
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    status_match = re.search(r"\*\*Status:\*\*\s*(.+)", text)
    if status_match:
        status = status_match.group(1).strip().lower()
        if any(s in status for s in ("archived", "do not use", "verdict", "review complete")):
            return False
    return True


def extract_posts(md_path: Path) -> list[DraftPost]:
    """Parse a draft markdown file and return one DraftPost per ## section."""
    try:
        text = md_path.read_text(encoding="utf-8")
    except OSError:
        return []

    matches = list(SECTION_RE.finditer(text))
    posts: list[DraftPost] = []

    for i, match in enumerate(matches):
        title = match.group(1).strip()

        # Skip non-post sections (metadata, word counts, verdicts, etc.)
        if any(title.lower().startswith(p) for p in SKIP_SECTION_PREFIXES):
            continue

        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()

        if not body:
            continue

        # Strip trailing metadata lines (e.g., "*Word counts: ...")
        body = re.sub(r"\n\*Word counts?:.*$", "", body, flags=re.DOTALL | re.IGNORECASE).strip()
        # Strip draft annotation blocks that start with **Keyword: from the first match onward.
        # These are lines like **Character count:** 219 / **Type:** Standalone etc.
        # Split into lines and drop everything from the first metadata line onward.
        ANNOTATION_LABELS = {
            "character count", "type", "target audience", "notes",
            "sequencing suggestion", "summary for deacon", "on ezra",
        }
        lines = body.splitlines()
        cutoff = len(lines)
        for idx, line in enumerate(lines):
            stripped = line.strip().lstrip("*").strip("* ").lower()
            if any(stripped.startswith(label + ":") or stripped.startswith("**" + label)
                   for label in ANNOTATION_LABELS):
                cutoff = idx
                break
            # Also catch markdown bold: **Label:** value
            bold_match = re.match(r"\*\*([^*]+)\*\*", line.strip())
            if bold_match:
                label = bold_match.group(1).strip().lower().rstrip(":")
                if label in ANNOTATION_LABELS:
                    cutoff = idx
                    break
        body = "\n".join(lines[:cutoff]).strip()

        if len(body) < 20:  # Skip trivially short sections
            continue

        posts.append(DraftPost(source_file=md_path, title=title, body=body))

    return posts


def collect_posts(draft_dir: Path) -> list[DraftPost]:
    """Collect all draft posts from markdown files in the draft directory."""
    posts: list[DraftPost] = []
    for md_path in sorted(draft_dir.glob("*.md")):
        if not is_draft_file(md_path):
            continue
        posts.extend(extract_posts(md_path))
    return posts


def read_sent_ids(log_file: Path) -> set[str]:
    """Return set of post_ids already sent (status=ok or status=dry-run)."""
    sent_ids: set[str] = set()
    if not log_file.exists():
        return sent_ids

    with log_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            # Count both successful sends AND dry-runs as "already processed"
            if entry.get("status") in ("ok", "dry-run") and entry.get("post_id"):
                sent_ids.add(entry["post_id"])
    return sent_ids


def append_log(log_file: Path, entry: dict) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def build_message(post: DraftPost) -> str:
    platform_emoji = {
        "linkedin": "💼",
        "x": "𝕏",
        "twitter": "𝕏",
        "instagram": "📸",
        "tiktok": "🎵",
    }.get(post.platform, "📝")

    return (
        f"{platform_emoji} *Social Post — Approval Requested*\n\n"
        f"📄 File: `{post.source_file.name}`\n"
        f"📌 Section: {post.title}\n"
        f"🆔 Post ID: `{post.post_id_short}`\n"
        f"🌐 Platform: {post.platform.upper()}\n\n"
        "Reply *APPROVE* or *REVISE* (include post ID if revising).\n"
        "Actual posting is manual — this is approval only.\n\n"
        "---\n\n"
        f"{post.body}"
    )


def send_telegram(target: str, message: str) -> tuple[int, str, str]:
    """Send a message via openclaw CLI and return (returncode, stdout, stderr)."""
    cmd = [
        "openclaw", "message", "send",
        "--channel", "telegram",
        "--target", target,
        "--message", message,
        "--json",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def next_unsent(posts: Iterable[DraftPost], sent_ids: set[str]) -> DraftPost | None:
    for post in posts:
        if post.post_id not in sent_ids:
            return post
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send next social draft to Deacon for approval via Telegram.",
        epilog=(
            "Environment: SOCIAL_APPROVAL_TARGET — Telegram chat ID/username for approval target. "
            "Can also be set via --target."
        ),
    )
    parser.add_argument(
        "--draft-dir",
        default="shared-context/drafts",
        help="Directory containing markdown draft files (default: shared-context/drafts)",
    )
    parser.add_argument(
        "--log-file",
        default="scripts/social-pipeline-log.jsonl",
        help="JSONL log file path (default: scripts/social-pipeline-log.jsonl)",
    )
    parser.add_argument(
        "--target",
        default=os.getenv("SOCIAL_APPROVAL_TARGET", ""),
        help="Telegram chat ID or @username for approval (default: env SOCIAL_APPROVAL_TARGET)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print payload without sending; does NOT mark post as sent",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show extra info (number of posts found, skipped files, etc.)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    draft_dir = Path(args.draft_dir)
    log_file = Path(args.log_file)

    # --- Validate draft dir ---
    if not draft_dir.exists() or not draft_dir.is_dir():
        print(f"Draft directory not found: {draft_dir}", file=sys.stderr)
        return 1

    # --- Collect all posts from drafts ---
    posts = collect_posts(draft_dir)

    if args.verbose:
        print(f"Found {len(posts)} total posts across draft files in {draft_dir}")

    if not posts:
        # Clean exit — nothing in queue is fine
        if args.verbose:
            print("No draft posts found. Queue is empty.")
        return 0

    # --- Find next unsent post ---
    sent_ids = read_sent_ids(log_file)
    post = next_unsent(posts, sent_ids)

    if post is None:
        if args.verbose:
            print(f"All {len(posts)} post(s) already sent. Nothing to do.")
        return 0

    # --- Build the approval message ---
    payload = build_message(post)

    # --- Dry-run mode: print only, no log entry ---
    if args.dry_run:
        print("=" * 60)
        print("[DRY RUN] Would send this message:")
        print("=" * 60)
        print(payload)
        print("=" * 60)
        print(f"Post ID: {post.post_id}")
        print(f"Source:  {post.source_file}")
        print(f"Log:     {log_file}")
        return 0

    # --- Validate target ---
    if not args.target:
        print(
            "Error: No approval target. Set --target or SOCIAL_APPROVAL_TARGET env var.",
            file=sys.stderr,
        )
        return 2

    # --- Send the message ---
    code, out, err = send_telegram(args.target, payload)

    entry: dict = {
        "ts": now_iso(),
        "status": "ok" if code == 0 else "error",
        "channel": "telegram",
        "target": args.target,
        "post_id": post.post_id,
        "source_file": str(post.source_file),
        "title": post.title,
        "platform": post.platform,
        "approval_status": "pending",
        "notes": "",
    }
    if code != 0:
        entry["notes"] = err or out or "send failed"
    append_log(log_file, entry)

    if code != 0:
        print(f"Error sending message: {err or out}", file=sys.stderr)
        return code

    print(f"✅ Sent for approval: [{post.platform.upper()}] {post.title} ({post.source_file.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
