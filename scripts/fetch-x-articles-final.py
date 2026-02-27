#!/usr/bin/env python3
"""
Fetch X Article content using tweet IDs from bookmarks (not article IDs from URLs).
Key insight: tweet.article.title/text gives us the full article content.
"""

import asyncio
import hashlib
import json
import os
import re
import shutil
import sqlite3
from pathlib import Path

try:
    from Crypto.Cipher import AES
except ImportError:
    print("ERROR: pycryptodome not installed."); exit(1)

try:
    from tweety import Twitter
except ImportError:
    print("ERROR: tweety-ns not installed."); exit(1)

BOOKMARKS_FILE   = Path("/Users/deaconsopenclaw/.openclaw/workspace/research/x-bookmarks-new.json")
OBSIDIAN_DIR     = Path("/Users/deaconsopenclaw/Documents/Brain/Personal Memories/Enoch/Captures")
OUTPUT_BRIEF     = Path("/Users/deaconsopenclaw/.openclaw/workspace/research/vetted/2026-02-26-url-resolved.md")
BRAVE_DB         = os.path.expanduser(
    "~/Library/Application Support/BraveSoftware/Brave-Browser/Default/Cookies"
)

# ── Cookie extraction ─────────────────────────────────────────────────────────

def _brave_key():
    import subprocess
    r = subprocess.run(
        ["security","find-generic-password","-w","-s","Brave Safe Storage","-a","Brave"],
        capture_output=True, text=True
    )
    return hashlib.pbkdf2_hmac("sha1", r.stdout.strip().encode(), b"saltysalt", 1003, 16)

def _decrypt(enc_val, key):
    if enc_val[:3] not in (b"v10", b"v11"):
        return enc_val.decode("utf-8", errors="replace")
    data  = enc_val[3:]
    dec   = AES.new(key, AES.MODE_CBC, IV=b" "*16).decrypt(data)
    pad   = dec[-1]
    clean = dec[:-pad] if 1 <= pad <= 16 else dec
    return clean[32:].decode("utf-8", errors="replace")

def get_x_cookies():
    key    = _brave_key()
    tmp_db = "/tmp/brave-final.db"
    shutil.copy2(BRAVE_DB, tmp_db)
    conn   = sqlite3.connect(tmp_db)
    rows   = conn.execute(
        "SELECT name, encrypted_value FROM cookies "
        "WHERE host_key LIKE '%.x.com' AND name IN ('auth_token','ct0')"
    ).fetchall()
    conn.close(); os.unlink(tmp_db)
    return {name: _decrypt(val, key) for name, val in rows}

# ── Categorize & verdict ──────────────────────────────────────────────────────

def categorize(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["github","code","repo","python","node","api","install","library","npm","deploy","script","scraper"]):
        return "Tools & Libraries"
    if any(w in t for w in ["ai ","llm","gpt","claude","model","openai","anthropic","gemini","agent","automation","claude code"]):
        return "AI & Models"
    if any(w in t for w in ["business","revenue","sales","marketing","growth","startup","income","client","money","sell","service"]):
        return "Business & Growth"
    if any(w in t for w in ["security","hack","vuln","privacy","encrypt","breach","injection"]):
        return "Security"
    if any(w in t for w in ["content","creator","youtube","audience","followers","newsletter","social media","twitter"]):
        return "Content & Social"
    return "General"

def verdict_tag(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["how to","step by step","install","tutorial","here's the system","exact system","exact process"]):
        return "ACT_ON"
    if any(w in t for w in ["i built","build this","automate","system","framework","workflow","tool i made","here's how i"]):
        return "BUILD"
    if any(w in t for w in ["research","paper","study","analysis","data shows","findings","report","benchmark"]):
        return "READ_DEEPER"
    if any(w in t for w in ["share","viral","spread","everyone should","retweet"]):
        return "SHARE"
    return "ARCHIVE"

# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    print("Loading bookmarks...")
    with open(BOOKMARKS_FILE) as f:
        all_bm = json.load(f)

    # Get URL-only bookmarks — these have article content
    url_only = []
    for b in all_bm:
        text = (b.get("text", "") or "").strip()
        if re.match(r"^https?://\S+$", text) or (len(text) < 50 and "http" in text):
            url_only.append(b)

    print(f"Found {len(url_only)} URL-only bookmarks to fetch")

    # Auth
    print("Authenticating with X...")
    cookies = get_x_cookies()
    app = Twitter("session")
    await app.load_cookies(cookies)
    await app.connect()
    print(f"✓ @{app.me.username}")

    # Fetch each by tweet ID
    print("\nFetching tweet/article content...")
    results = []
    for i, b in enumerate(url_only):
        username = b.get("username", "unknown")
        tweet_id = b.get("id", "")
        tco_url  = (b.get("text", "") or "").strip()

        print(f"[{i+1}/{len(url_only)}] @{username} (tweet {tweet_id})", flush=True)

        title, body = "", ""
        try:
            tweet = await app.tweet_detail(tweet_id)
            if tweet and tweet is not True:
                # Check for article attachment first
                if hasattr(tweet, "article") and tweet.article:
                    a = tweet.article
                    title = getattr(a, "title", "") or ""
                    body  = (getattr(a, "text", "") or getattr(a, "preview_text", "") or "")[:600]
                elif hasattr(tweet, "text") and tweet.text:
                    title = (tweet.text or "")[:120]
                    body  = (tweet.text or "")[:400]
                print(f"  → {title[:70] or body[:70]}", flush=True)
            else:
                print(f"  ✗ no content", flush=True)
        except Exception as e:
            print(f"  ✗ error: {e}", flush=True)

        cat = categorize(f"{title} {body}")
        ver = verdict_tag(f"{title} {body}")
        results.append({
            "username":  username,
            "tweet_id":  tweet_id,
            "tco_url":   tco_url,
            "title":     title or f"@{username} article",
            "text":      body,
            "category":  cat,
            "verdict":   ver,
            "author":    b.get("author", username),
        })
        await asyncio.sleep(0.5)

    # ── Write outputs ─────────────────────────────────────────────────────────
    print("\nSaving files...")
    by_cat = {}
    for r in results:
        by_cat.setdefault(r["category"], []).append(r)

    brief_lines = [f"# URL-Resolved Bookmarks — 2026-02-26\n\n{len(results)} bookmarks resolved via tweet detail.\n\n---\n"]
    for cat, items in sorted(by_cat.items()):
        brief_lines.append(f"\n## {cat}\n")
        for r in items:
            tweet_url = f"https://x.com/{r['username']}/status/{r['tweet_id']}"
            brief_lines.append(f"**@{r['username']}** — [{r['title'][:80]}]({tweet_url})\n")
            if r["text"]:
                brief_lines.append(f"> {r['text'][:250]}\n\n")
            brief_lines.append(f"**Verdict: {r['verdict']}**\n\n")
    OUTPUT_BRIEF.write_text("".join(brief_lines))
    print(f"✅ Brief: {OUTPUT_BRIEF}")

    obs = f"# URL-Resolved Bookmarks — Feb 26 2026\n\nIndexed {len(results)} URL-only bookmarks.\n"
    for cat, items in sorted(by_cat.items()):
        obs += f"\n## {cat}\n"
        for r in items:
            tweet_url = f"https://x.com/{r['username']}/status/{r['tweet_id']}"
            obs += f"- **@{r['username']}** — [{r['title'][:80]}]({tweet_url}) → `{r['verdict']}`\n"
            if r["text"]:
                obs += f"  _{r['text'][:200]}_\n"
    obsidian_file = OBSIDIAN_DIR / "2026-02-26-url-resolved-bookmarks.md"
    obsidian_file.write_text(obs)
    print(f"✅ Obsidian: {obsidian_file}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n=== SUMMARY ===")
    vc = {}
    for r in results:
        vc[r["verdict"]] = vc.get(r["verdict"], 0) + 1
    for v, c in sorted(vc.items()):
        print(f"  {v}: {c}")

    hits = [r for r in results if r["verdict"] != "ARCHIVE"]
    if hits:
        print("\n🔴 Action items:")
        for r in hits:
            print(f"  [{r['verdict']}] @{r['username']}: {r['title'][:70]}")

if __name__ == "__main__":
    asyncio.run(main())
