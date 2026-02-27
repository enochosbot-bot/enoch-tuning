#!/usr/bin/env python3
"""
Fetch content from X Article URLs using authenticated Brave cookies.
Resolves the 34 URL-only bookmarks that point to x.com/i/article/* URLs.
"""

import asyncio
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

try:
    from Crypto.Cipher import AES
except ImportError:
    print("ERROR: pycryptodome not installed.")
    sys.exit(1)

try:
    from tweety import Twitter
except ImportError:
    print("ERROR: tweety-ns not installed.")
    sys.exit(1)

BOOKMARKS_FILE = Path("/Users/deaconsopenclaw/.openclaw/workspace/research/x-bookmarks-new.json")
OBSIDIAN_CAPTURES = Path("/Users/deaconsopenclaw/Documents/Brain/Personal Memories/Enoch/Captures")
OUTPUT_BRIEF = Path("/Users/deaconsopenclaw/.openclaw/workspace/research/vetted/2026-02-26-url-resolved.md")
BRAVE_DB = os.path.expanduser(
    "~/Library/Application Support/BraveSoftware/Brave-Browser/Default/Cookies"
)


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
    if enc_val[:3] not in (b"v10", b"v11"):
        return enc_val.decode("utf-8", errors="replace")
    data = enc_val[3:]
    iv = b" " * 16
    from Crypto.Cipher import AES as _AES
    ciph = _AES.new(key, _AES.MODE_CBC, IV=iv)
    dec = ciph.decrypt(data)
    pad = dec[-1]
    clean = dec[:-pad] if 1 <= pad <= 16 else dec
    # Chromium prepends a 32-byte random nonce — strip it
    return clean[32:].decode("utf-8", errors="replace")


def get_x_cookies():
    key = _brave_key()
    tmp_db = "/tmp/brave-x-cookies-articles.db"
    shutil.copy2(BRAVE_DB, tmp_db)
    conn = sqlite3.connect(tmp_db)
    rows = conn.execute(
        "SELECT name, encrypted_value FROM cookies "
        "WHERE host_key LIKE '%.x.com' AND name IN ('auth_token', 'ct0')"
    ).fetchall()
    conn.close()
    os.unlink(tmp_db)
    cookies = {name: _decrypt(val, key) for name, val in rows}
    missing = [k for k in ("auth_token", "ct0") if not cookies.get(k)]
    if missing:
        raise RuntimeError(f"Missing X cookies: {missing}")
    return cookies


def categorize(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ['github', 'code', 'repo', 'library', 'python', 'node', 'api', 'sdk', 'npm', 'install', 'deploy']):
        return "Tools & Libraries"
    if any(w in t for w in ['ai ', 'llm', 'gpt', 'claude', 'model', 'neural', 'openai', 'anthropic', 'gemini', 'agent']):
        return "AI & Models"
    if any(w in t for w in ['business', 'revenue', 'sales', 'marketing', 'growth', 'startup', 'money', 'income', 'client']):
        return "Business & Growth"
    if any(w in t for w in ['security', 'hack', 'vuln', 'privacy', 'encrypt']):
        return "Security"
    if any(w in t for w in ['youtube', 'video', 'twitter', 'social', 'instagram', 'content', 'creator']):
        return "Social & Media"
    return "General"


def verdict(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ['install', 'how to', 'tutorial', 'step by step', 'use this', 'try this', 'run this']):
        return "ACT_ON"
    if any(w in t for w in ['study', 'research', 'analysis', 'findings', 'paper', 'data shows']):
        return "READ_DEEPER"
    if any(w in t for w in ['share', 'retweet', 'spread', 'viral', 'everyone should']):
        return "SHARE"
    if any(w in t for w in ['build', 'create', 'make', 'develop', 'automate', 'system', 'framework']):
        return "BUILD"
    return "ARCHIVE"


async def main():
    print("Loading bookmarks...")
    with open(BOOKMARKS_FILE) as f:
        all_bookmarks = json.load(f)

    # Get URL-only bookmarks and extract article IDs
    url_only = []
    for b in all_bookmarks:
        text = (b.get('text', '') or '').strip()
        if re.match(r'^https?://\S+$', text) or (len(text) < 50 and 'http' in text):
            url_match = re.search(r'https?://\S+', text)
            if url_match:
                url_only.append({
                    'bookmark': b,
                    'tco_url': url_match.group(0)
                })

    print(f"Found {len(url_only)} URL-only bookmarks")

    # Get cookies
    print("Extracting Brave X cookies...")
    try:
        cookies = get_x_cookies()
        print("✓ Cookies obtained")
    except Exception as e:
        print(f"✗ Cookie error: {e}")
        sys.exit(1)

    # Resolve t.co URLs first
    import urllib.request
    print("\nResolving t.co URLs...")
    for item in url_only:
        try:
            req = urllib.request.Request(
                item['tco_url'],
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            resp = urllib.request.urlopen(req, timeout=8)
            item['final_url'] = resp.url
        except Exception:
            item['final_url'] = item['tco_url']

        # Extract article ID from x.com/i/article/ID
        m = re.search(r'x\.com/i/article/(\d+)', item['final_url'])
        if m:
            item['article_id'] = m.group(1)
        else:
            # Try tweet ID from URL
            m2 = re.search(r'/status/(\d+)', item['final_url'])
            item['article_id'] = m2.group(1) if m2 else None

        print(f"  @{item['bookmark'].get('username', '?')} → {item['final_url'][:70]}")

    # Authenticate with X
    print("\nConnecting to X...")
    app = Twitter("session")
    await app.load_cookies(cookies)
    await app.connect()

    if not app.me:
        print("✗ X auth failed")
        sys.exit(1)

    print(f"✓ Authenticated as @{app.me.username}")

    # Fetch tweet/article content
    print("\nFetching article content...")
    results = []
    for i, item in enumerate(url_only):
        username = item['bookmark'].get('username', 'unknown')
        article_id = item.get('article_id')

        if not article_id:
            print(f"[{i+1}/{len(url_only)}] @{username} — no article ID, skipping")
            results.append({
                'username': username,
                'final_url': item['final_url'],
                'title': f"[Could not resolve] {item['tco_url']}",
                'text': '',
                'category': 'General',
                'verdict': 'ARCHIVE'
            })
            continue

        try:
            tweet = await app.tweet_detail(article_id)
            if tweet:
                text = tweet.text or ''
                # Try to get article content if it's an article tweet
                article_content = ''
                if hasattr(tweet, 'article') and tweet.article:
                    article_content = str(tweet.article)
                
                full_text = article_content or text
                title = full_text[:100].replace('\n', ' ')
                cat = categorize(full_text)
                ver = verdict(full_text)
                
                results.append({
                    'username': username,
                    'final_url': item['final_url'],
                    'title': title,
                    'text': full_text[:500],
                    'category': cat,
                    'verdict': ver,
                    'author': tweet.author.name if tweet.author else username
                })
                print(f"[{i+1}/{len(url_only)}] @{username} ✓ — {title[:60]} [{cat}] → {ver}")
            else:
                print(f"[{i+1}/{len(url_only)}] @{username} — no content returned")
                results.append({
                    'username': username,
                    'final_url': item['final_url'],
                    'title': f"[No content] @{username}",
                    'text': '',
                    'category': 'General',
                    'verdict': 'ARCHIVE'
                })
        except Exception as e:
            print(f"[{i+1}/{len(url_only)}] @{username} — error: {e}")
            results.append({
                'username': username,
                'final_url': item['final_url'],
                'title': f"[Error fetching] @{username}",
                'text': str(e)[:100],
                'category': 'General',
                'verdict': 'ARCHIVE'
            })

        await asyncio.sleep(0.8)

    # Write brief
    print("\nWriting files...")
    lines = [f"# URL-Resolved Bookmarks — 2026-02-26\n\nResolved {len(results)} URL-only bookmarks.\n\n---\n"]
    by_cat = {}
    for r in results:
        by_cat.setdefault(r['category'], []).append(r)

    for cat, items in sorted(by_cat.items()):
        lines.append(f"\n## {cat}\n")
        for r in items:
            lines.append(f"**@{r['username']}** — [{r['title'][:80]}]({r['final_url']})\n")
            if r.get('text'):
                lines.append(f"  > {r['text'][:200]}\n")
            lines.append(f"  **Verdict: {r['verdict']}**\n\n")

    OUTPUT_BRIEF.write_text("".join(lines))
    print(f"✅ Brief: {OUTPUT_BRIEF}")

    # Save to Obsidian
    obsidian_file = OBSIDIAN_CAPTURES / "2026-02-26-url-resolved-bookmarks.md"
    obs = f"# URL-Resolved Bookmarks — Feb 26 2026\n\nResolved {len(results)} URL-only bookmarks.\n\n"
    for cat, items in sorted(by_cat.items()):
        obs += f"\n## {cat}\n"
        for r in items:
            obs += f"- **@{r['username']}** — [{r['title'][:80]}]({r['final_url']}) → `{r['verdict']}`\n"
            if r.get('text'):
                obs += f"  {r['text'][:150]}\n"
    obsidian_file.write_text(obs)
    print(f"✅ Obsidian: {obsidian_file}")

    # Summary
    print(f"\n=== SUMMARY ===")
    verdict_counts = {}
    for r in results:
        verdict_counts[r['verdict']] = verdict_counts.get(r['verdict'], 0) + 1
    for v, count in sorted(verdict_counts.items()):
        print(f"  {v}: {count}")

    non_archive = [r for r in results if r['verdict'] != 'ARCHIVE']
    if non_archive:
        print(f"\n🔴 Action items:")
        for r in non_archive:
            print(f"  [{r['verdict']}] @{r['username']}: {r['title'][:70]}")


if __name__ == "__main__":
    asyncio.run(main())
