#!/usr/bin/env python3
"""
X Bookmarks Sync — cookie-based, no OAuth tokens required.

Reads auth_token + ct0 directly from Brave's local cookie database.
As long as Brave stays logged into X, this never needs re-auth.

Usage:
  python3 x-bookmarks-sync.py              # sync and update raw/markdown
  python3 x-bookmarks-sync.py --detect-new # also write x-bookmarks-new.json
"""

import asyncio, hashlib, json, os, shutil, sqlite3, sys
from datetime import datetime

try:
    from Crypto.Cipher import AES
except ImportError:
    print("ERROR: pycryptodome not installed. Run: pip3 install pycryptodome --break-system-packages")
    sys.exit(1)

try:
    from tweety import Twitter
except ImportError:
    print("ERROR: tweety-ns not installed. Run: pip3 install tweety-ns --break-system-packages")
    sys.exit(1)

WORKSPACE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FILE   = os.path.join(WORKSPACE, "research/x-bookmarks-raw.json")
MD_FILE    = os.path.join(WORKSPACE, "research/x-bookmarks_latest.md")
NEW_FILE   = os.path.join(WORKSPACE, "research/x-bookmarks-new.json")
BRAVE_DB   = os.path.expanduser(
    "~/Library/Application Support/BraveSoftware/Brave-Browser/Default/Cookies"
)

# ── Cookie extraction ──────────────────────────────────────────────────────────

def _brave_key():
    import subprocess
    r = subprocess.run(
        ["security", "find-generic-password", "-w", "-s", "Brave Safe Storage", "-a", "Brave"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        raise RuntimeError(f"Could not read Brave keychain: {r.stderr.strip()}")
    password = r.stdout.strip()
    return hashlib.pbkdf2_hmac("sha1", password.encode(), b"saltysalt", 1003, 16)

def _decrypt(enc_val, key):
    """Decrypt a Chromium v10 AES-CBC encrypted cookie value."""
    if enc_val[:3] not in (b"v10", b"v11"):
        return enc_val.decode("utf-8", errors="replace")
    data = enc_val[3:]
    iv   = b" " * 16
    ciph = AES.new(key, AES.MODE_CBC, IV=iv)
    dec  = ciph.decrypt(data)
    pad  = dec[-1]
    clean = dec[:-pad] if 1 <= pad <= 16 else dec
    # Chromium prepends a 32-byte random nonce — strip it
    return clean[32:].decode("utf-8", errors="replace")

def get_x_cookies():
    """Return dict with auth_token and ct0 from Brave's cookie store."""
    if not os.path.exists(BRAVE_DB):
        raise RuntimeError("Brave cookie database not found at expected path")
    key    = _brave_key()
    tmp_db = "/tmp/brave-x-cookies.db"
    shutil.copy2(BRAVE_DB, tmp_db)
    conn   = sqlite3.connect(tmp_db)
    rows   = conn.execute(
        "SELECT name, encrypted_value FROM cookies "
        "WHERE host_key LIKE '%.x.com' AND name IN ('auth_token', 'ct0')"
    ).fetchall()
    conn.close()
    os.unlink(tmp_db)

    cookies = {name: _decrypt(val, key) for name, val in rows}
    missing = [k for k in ("auth_token", "ct0") if not cookies.get(k)]
    if missing:
        raise RuntimeError(
            f"Missing X cookies: {missing}. Is Brave logged into X?"
        )
    return cookies

# ── Bookmark fetch ─────────────────────────────────────────────────────────────

async def fetch_bookmarks(cookies):
    app = Twitter("session")
    await app.load_cookies(cookies)
    await app.connect()

    if not app.me:
        raise RuntimeError("Cookie auth failed — X session may have expired. Log into X in Brave.")

    print(f"Authenticated as @{app.me.username}")

    raw_pages = await app.get_bookmarks(pages=20, wait_time=1)
    results   = []

    for tweet in raw_pages:
        results.append({
            "id":            str(tweet.id),
            "text":          tweet.text or "",
            "author":        tweet.author.name     if tweet.author else "",
            "username":      tweet.author.username if tweet.author else "",
            "created_at":    str(tweet.date)       if tweet.date   else "",
            "article_title": "",
        })

    return results

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    detect_new = "--detect-new" in sys.argv

    # 1. Get live cookies from Brave
    try:
        cookies = get_x_cookies()
    except RuntimeError as e:
        print(f"COOKIE ERROR: {e}")
        sys.exit(1)

    # 2. Load existing bookmarks (for diff)
    existing = []
    existing_ids = set()
    if os.path.exists(RAW_FILE):
        with open(RAW_FILE) as f:
            existing = json.load(f)
            existing_ids = {b["id"] for b in existing}

    # 3. Fetch from X
    try:
        bookmarks = asyncio.run(fetch_bookmarks(cookies))
    except Exception as e:
        print(f"FETCH ERROR: {e}")
        sys.exit(1)

    current_ids  = {b["id"] for b in bookmarks}
    new_bookmarks = [b for b in bookmarks if b["id"] not in existing_ids]
    removed_count = len(existing_ids - current_ids)

    print(f"Total: {len(bookmarks)} | New: {len(new_bookmarks)} | Removed: {removed_count}")

    # 4. Save raw JSON
    os.makedirs(os.path.dirname(RAW_FILE), exist_ok=True)
    with open(RAW_FILE, "w") as f:
        json.dump(bookmarks, f, indent=2)

    # 5. Save markdown
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(MD_FILE, "w") as f:
        f.write(f"# X Bookmarks — Deacon Ridley\n\nLast sync: {now} | Total: {len(bookmarks)}\n\n")
        for b in bookmarks:
            author = f'@{b["username"]}' if b["username"] else "unknown"
            title  = f' — {b["article_title"]}' if b["article_title"] else ""
            f.write(f"### {author}{title}\n")
            f.write(
                f'*{b["created_at"][:10]}* | '
                f'https://x.com/{b["username"]}/status/{b["id"]}\n\n'
            )
            f.write(f'{b["text"]}\n\n---\n\n')

    # 6. Write new-bookmarks file if requested
    if detect_new:
        with open(NEW_FILE, "w") as f:
            json.dump(new_bookmarks, f, indent=2)
        print(f"New bookmarks written to {NEW_FILE}")

    # 7. Print new ones
    if new_bookmarks:
        print("\n=== NEW BOOKMARKS ===")
        for b in new_bookmarks:
            print(f"  @{b['username']}: {b['text'][:80]}...")

    if removed_count:
        print(f"\n{removed_count} bookmarks removed since last sync")

if __name__ == "__main__":
    main()
