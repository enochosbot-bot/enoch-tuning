#!/usr/bin/env python3
"""
Fetch X Article content using Scrapling's Playwright fetcher with injected auth cookies.
This renders the full JS page so we get actual article content.
"""

import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
import time
from pathlib import Path

try:
    from Crypto.Cipher import AES
except ImportError:
    print("ERROR: pycryptodome not installed."); sys.exit(1)

BOOKMARKS_FILE = Path("/Users/deaconsopenclaw/.openclaw/workspace/research/x-bookmarks-new.json")
OBSIDIAN_CAPTURES = Path("/Users/deaconsopenclaw/Documents/Brain/Personal Memories/Enoch/Captures")
OUTPUT_BRIEF = Path("/Users/deaconsopenclaw/.openclaw/workspace/research/vetted/2026-02-26-url-resolved.md")
BRAVE_DB = os.path.expanduser(
    "~/Library/Application Support/BraveSoftware/Brave-Browser/Default/Cookies"
)

# ── Cookie extraction ─────────────────────────────────────────────────────────

def _brave_key():
    import subprocess
    r = subprocess.run(
        ["security", "find-generic-password", "-w", "-s", "Brave Safe Storage", "-a", "Brave"],
        capture_output=True, text=True
    )
    password = r.stdout.strip()
    return hashlib.pbkdf2_hmac("sha1", password.encode(), b"saltysalt", 1003, 16)

def _decrypt(enc_val, key):
    if enc_val[:3] not in (b"v10", b"v11"):
        return enc_val.decode("utf-8", errors="replace")
    data = enc_val[3:]
    iv   = b" " * 16
    ciph = AES.new(key, AES.MODE_CBC, IV=iv)
    dec  = ciph.decrypt(data)
    pad  = dec[-1]
    clean = dec[:-pad] if 1 <= pad <= 16 else dec
    return clean[32:].decode("utf-8", errors="replace")

def get_x_cookies():
    key    = _brave_key()
    tmp_db = "/tmp/brave-x-v3.db"
    shutil.copy2(BRAVE_DB, tmp_db)
    conn   = sqlite3.connect(tmp_db)
    rows   = conn.execute(
        "SELECT name, encrypted_value FROM cookies "
        "WHERE host_key LIKE '%.x.com' AND name IN ('auth_token', 'ct0')"
    ).fetchall()
    conn.close()
    os.unlink(tmp_db)
    cookies = {name: _decrypt(val, key) for name, val in rows}
    return cookies

# ── Scrapling fetch with auth cookies ────────────────────────────────────────

def fetch_article_with_playwright(url: str, cookies: dict) -> str:
    """Use Scrapling PlayWright fetcher with auth cookies injected."""
    try:
        from scrapling.fetchers import PlayWrightFetcher
        
        cookie_list = [
            {"name": "auth_token", "value": cookies["auth_token"], "domain": ".x.com", "path": "/"},
            {"name": "ct0",        "value": cookies["ct0"],        "domain": ".x.com", "path": "/"},
        ]
        
        fetcher = PlayWrightFetcher()
        page = fetcher.fetch(
            url,
            cookies=cookie_list,
            wait=3000,          # wait 3s for JS to render
            headless=True,
        )
        
        if not page:
            return ""
        
        # Try to extract article text from rendered HTML
        text_nodes = page.find_all("article")
        if text_nodes:
            return " ".join(n.text for n in text_nodes)[:800]
        
        # Fallback: get all paragraph text
        paras = page.find_all("p")
        if paras:
            return " ".join(p.text for p in paras if len(p.text) > 30)[:800]
        
        return page.get_text()[:600] if hasattr(page, 'get_text') else ""
    
    except Exception as e:
        return f"[playwright error: {e}]"

def fetch_article_simple(url: str, cookies: dict) -> str:
    """Simple requests-based fetch with auth cookies as fallback."""
    try:
        import urllib.request
        import urllib.parse
        
        # Build cookie header
        cookie_header = f"auth_token={cookies['auth_token']}; ct0={cookies['ct0']}"
        
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Cookie': cookie_header,
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        resp = urllib.request.urlopen(req, timeout=12)
        raw = resp.read(16000).decode('utf-8', errors='ignore')
        
        # Extract meaningful text
        # Look for article content in JSON-LD or meta tags
        og_title = re.search(r'<meta property="og:title" content="([^"]+)"', raw)
        og_desc  = re.search(r'<meta property="og:description" content="([^"]+)"', raw)
        
        title = og_title.group(1) if og_title else ""
        desc  = og_desc.group(1) if og_desc else ""
        
        if title or desc:
            return f"{title}\n{desc}"
        
        # Strip HTML and get text
        text = re.sub(r'<script[^>]*>.*?</script>', '', raw, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Find the most content-rich section (skip JS/CSS noise)
        chunks = [c.strip() for c in text.split('  ') if len(c.strip()) > 80]
        return ' | '.join(chunks[:3])[:600] if chunks else text[:400]
    
    except Exception as e:
        return f"[fetch error: {e}]"

# ── Categorize & verdict ──────────────────────────────────────────────────────

def categorize(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ['github', 'code', 'repo', 'python', 'node', 'api', 'install', 'library', 'npm', 'pip']):
        return "Tools & Libraries"
    if any(w in t for w in ['ai ', 'llm', 'gpt', 'claude', 'model', 'openai', 'anthropic', 'gemini', 'agent', 'automation']):
        return "AI & Models"
    if any(w in t for w in ['business', 'revenue', 'sales', 'marketing', 'growth', 'startup', 'income', 'client', 'money']):
        return "Business & Growth"
    if any(w in t for w in ['security', 'hack', 'vuln', 'privacy', 'encrypt', 'breach']):
        return "Security"
    if any(w in t for w in ['content', 'creator', 'youtube', 'audience', 'followers', 'social media']):
        return "Content & Social"
    return "General"

def verdict_tag(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ['how to', 'step by step', 'install', 'tutorial', 'use this', 'run this']):
        return "ACT_ON"
    if any(w in t for w in ['build', 'create', 'automate', 'system', 'framework', 'workflow', 'tool i built']):
        return "BUILD"
    if any(w in t for w in ['research', 'paper', 'study', 'analysis', 'data shows', 'findings']):
        return "READ_DEEPER"
    if any(w in t for w in ['share', 'viral', 'spread', 'everyone should']):
        return "SHARE"
    return "ARCHIVE"

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Loading bookmarks...")
    with open(BOOKMARKS_FILE) as f:
        all_bookmarks = json.load(f)

    url_only = []
    for b in all_bookmarks:
        text = (b.get('text', '') or '').strip()
        if re.match(r'^https?://\S+$', text) or (len(text) < 50 and 'http' in text):
            m = re.search(r'https?://\S+', text)
            if m:
                url_only.append({'bookmark': b, 'tco_url': m.group(0)})

    print(f"Found {len(url_only)} URL-only bookmarks")

    print("Getting X cookies...")
    cookies = get_x_cookies()
    print(f"✓ auth_token obtained")

    # Resolve t.co URLs
    import urllib.request
    print("\nResolving t.co shortcuts...")
    for item in url_only:
        try:
            req = urllib.request.Request(item['tco_url'], headers={'User-Agent': 'Mozilla/5.0'})
            resp = urllib.request.urlopen(req, timeout=8)
            item['final_url'] = resp.url
        except Exception:
            item['final_url'] = item['tco_url']
        
        m = re.search(r'x\.com/i/article/(\d+)', item['final_url'])
        if m:
            item['article_id'] = m.group(1)
        else:
            m2 = re.search(r'/status/(\d+)', item['final_url'])
            item['article_id'] = m2.group(1) if m2 else None

    print(f"✓ All URLs resolved")

    # Fetch each article
    print("\nFetching article content (Playwright + fallback)...")
    results = []
    for i, item in enumerate(url_only):
        username = item['bookmark'].get('username', 'unknown')
        final_url = item['final_url']

        # Try Playwright first, then simple fetch
        content = fetch_article_with_playwright(final_url, cookies)
        if not content or '[playwright error' in content or len(content) < 50:
            content = fetch_article_simple(final_url, cookies)

        # Extract title from content
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        title = lines[0][:100] if lines else f"@{username} article"
        body  = ' '.join(lines[1:3])[:300] if len(lines) > 1 else content[:300]

        cat = categorize(f"{title} {body}")
        ver = verdict_tag(f"{title} {body}")

        results.append({
            'username': username,
            'final_url': final_url,
            'title': title,
            'text': body,
            'category': cat,
            'verdict': ver,
        })
        print(f"[{i+1}/{len(url_only)}] @{username} — {title[:60]} [{cat}] → {ver}")
        time.sleep(0.4)

    # Write outputs
    print("\nSaving files...")
    by_cat = {}
    for r in results:
        by_cat.setdefault(r['category'], []).append(r)

    lines_out = [f"# URL-Resolved Bookmarks — 2026-02-26\n\n{len(results)} bookmarks resolved.\n\n---\n"]
    for cat, items in sorted(by_cat.items()):
        lines_out.append(f"\n## {cat}\n")
        for r in items:
            lines_out.append(f"**@{r['username']}** — [{r['title'][:80]}]({r['final_url']})\n")
            if r['text']:
                lines_out.append(f"> {r['text'][:200]}\n\n")
            lines_out.append(f"**Verdict: {r['verdict']}**\n\n")
    OUTPUT_BRIEF.write_text("".join(lines_out))
    print(f"✅ Brief: {OUTPUT_BRIEF}")

    obs = f"# URL-Resolved Bookmarks — Feb 26 2026\n\n{len(results)} bookmarks resolved.\n"
    for cat, items in sorted(by_cat.items()):
        obs += f"\n## {cat}\n"
        for r in items:
            obs += f"- **@{r['username']}** — [{r['title'][:80]}]({r['final_url']}) → `{r['verdict']}`\n"
            if r['text']:
                obs += f"  _{r['text'][:150]}_\n"
    obsidian_file = OBSIDIAN_CAPTURES / "2026-02-26-url-resolved-bookmarks.md"
    obsidian_file.write_text(obs)
    print(f"✅ Obsidian: {obsidian_file}")

    print("\n=== SUMMARY ===")
    vc = {}
    for r in results:
        vc[r['verdict']] = vc.get(r['verdict'], 0) + 1
    for v, c in sorted(vc.items()):
        print(f"  {v}: {c}")

    non_archive = [r for r in results if r['verdict'] != 'ARCHIVE']
    if non_archive:
        print("\n🔴 Action items:")
        for r in non_archive:
            print(f"  [{r['verdict']}] @{r['username']}: {r['title'][:70]}")
            print(f"    {r['final_url']}")

if __name__ == "__main__":
    main()
