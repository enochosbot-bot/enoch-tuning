#!/usr/bin/env python3
"""
Fetch X Article content using Playwright directly with injected auth cookies.
"""

import asyncio
import hashlib
import json
import os
import re
import shutil
import sqlite3
import time
from pathlib import Path

try:
    from Crypto.Cipher import AES
except ImportError:
    print("ERROR: pycryptodome not installed."); exit(1)

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
        ["security", "find-generic-password", "-w", "-s", "Brave Safe Storage", "-a", "Brave"],
        capture_output=True, text=True
    )
    return hashlib.pbkdf2_hmac("sha1", r.stdout.strip().encode(), b"saltysalt", 1003, 16)

def _decrypt(enc_val, key):
    if enc_val[:3] not in (b"v10", b"v11"):
        return enc_val.decode("utf-8", errors="replace")
    data  = enc_val[3:]
    iv    = b" " * 16
    ciph  = AES.new(key, AES.MODE_CBC, IV=iv)
    dec   = ciph.decrypt(data)
    pad   = dec[-1]
    clean = dec[:-pad] if 1 <= pad <= 16 else dec
    return clean[32:].decode("utf-8", errors="replace")

def get_x_cookies():
    key    = _brave_key()
    tmp_db = "/tmp/brave-x-v4.db"
    shutil.copy2(BRAVE_DB, tmp_db)
    conn   = sqlite3.connect(tmp_db)
    rows   = conn.execute(
        "SELECT name, encrypted_value FROM cookies "
        "WHERE host_key LIKE '%.x.com' AND name IN ('auth_token', 'ct0')"
    ).fetchall()
    conn.close()
    os.unlink(tmp_db)
    return {name: _decrypt(val, key) for name, val in rows}

# ── Resolve t.co ─────────────────────────────────────────────────────────────

def resolve_tco(url: str) -> str:
    import urllib.request
    try:
        req  = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=8)
        return resp.url
    except Exception:
        return url

# ── Playwright fetch ──────────────────────────────────────────────────────────

async def fetch_articles(items: list, cookies: dict) -> list:
    from playwright.async_api import async_playwright

    pw_cookies = [
        {"name": "auth_token", "value": cookies["auth_token"],
         "domain": ".x.com", "path": "/", "httpOnly": True, "secure": True},
        {"name": "ct0",        "value": cookies["ct0"],
         "domain": ".x.com", "path": "/", "httpOnly": False, "secure": True},
    ]

    results = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900},
        )
        # Inject cookies before any page loads
        await context.add_cookies(pw_cookies)

        page = await context.new_page()

        for i, item in enumerate(items):
            username  = item["bookmark"].get("username", "unknown")
            final_url = item["final_url"]
            print(f"[{i+1}/{len(items)}] @{username} → {final_url[:70]}", flush=True)

            try:
                await page.goto(final_url, wait_until="domcontentloaded", timeout=25000)

                # Wait for article content to render — try several selectors
                for selector in [
                    '[data-testid="article-text"]',
                    '[data-testid="tweetText"]',
                    '[data-testid="note-tweet-text"]',
                    'article',
                    'main [role="article"]',
                ]:
                    try:
                        await page.wait_for_selector(selector, timeout=8000)
                        break
                    except Exception:
                        continue
                else:
                    # No article selector found — wait a flat 10s for JS to render
                    await asyncio.sleep(10)

                # Extract text
                text = await page.evaluate("""() => {
                    // Try article-specific selectors first
                    const article = document.querySelector('[data-testid="article-text"]');
                    if (article) return article.innerText;
                    
                    const noteBody = document.querySelector('[data-testid="note-tweet-text"]');
                    if (noteBody) return noteBody.innerText;

                    const tweetText = document.querySelector('[data-testid="tweetText"]');
                    if (tweetText) return tweetText.innerText;
                    
                    // Try main content area
                    const main = document.querySelector('main article');
                    if (main) return main.innerText;

                    // Grab all substantial text nodes
                    const allText = [];
                    document.querySelectorAll('p, h1, h2, h3, span').forEach(el => {
                        const t = el.innerText && el.innerText.trim();
                        if (t && t.length > 40 && !t.includes('{') && !t.includes('function')) {
                            allText.push(t);
                        }
                    });
                    if (allText.length > 0) return allText.slice(0, 5).join(' | ');
                    
                    // Last resort: meta tags
                    const ogDesc = document.querySelector('meta[property="og:description"]');
                    return ogDesc ? ogDesc.getAttribute('content') : '';
                }""")

                title_raw = await page.evaluate("""() => {
                    const og = document.querySelector('meta[property="og:title"]');
                    if (og && og.getAttribute('content') && og.getAttribute('content') !== 'X') 
                        return og.getAttribute('content');
                    const h1 = document.querySelector('h1');
                    if (h1 && h1.innerText.trim().length > 3) return h1.innerText.trim();
                    return document.title;
                }""")

                title = (title_raw or "").strip()[:120]
                body  = (text or "").strip()[:500]

                # Skip if it's just the X login page
                if title in ("X", "Twitter", "") and "Log in" in body:
                    title = f"[login wall] @{username}"
                    body  = ""

                print(f"  → {title[:70]}", flush=True)

            except Exception as e:
                print(f"  ✗ error: {e}", flush=True)
                title = f"[error] @{username}"
                body  = str(e)[:100]

            results.append({
                "username":  username,
                "final_url": final_url,
                "title":     title or f"@{username} article",
                "text":      body,
            })
            await asyncio.sleep(0.8)

        await browser.close()
    return results

# ── Categorize & verdict ──────────────────────────────────────────────────────

def categorize(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["github","code","repo","python","node","api","install","library","npm","deploy"]):
        return "Tools & Libraries"
    if any(w in t for w in ["ai ","llm","gpt","claude","model","openai","anthropic","gemini","agent","automation"]):
        return "AI & Models"
    if any(w in t for w in ["business","revenue","sales","marketing","growth","startup","income","client","money"]):
        return "Business & Growth"
    if any(w in t for w in ["security","hack","vuln","privacy","encrypt"]):
        return "Security"
    if any(w in t for w in ["content","creator","youtube","audience","followers","newsletter"]):
        return "Content & Social"
    return "General"

def verdict_tag(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["how to","step by step","install","tutorial","use this","run this"]):
        return "ACT_ON"
    if any(w in t for w in ["build","automate","system","framework","workflow","tool i built","i built"]):
        return "BUILD"
    if any(w in t for w in ["research","paper","study","analysis","data shows","findings","report"]):
        return "READ_DEEPER"
    if any(w in t for w in ["share","viral","spread","everyone should"]):
        return "SHARE"
    return "ARCHIVE"

# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    print("Loading bookmarks...")
    with open(BOOKMARKS_FILE) as f:
        all_bm = json.load(f)

    url_only = []
    for b in all_bm:
        text = (b.get("text", "") or "").strip()
        if re.match(r"^https?://\S+$", text) or (len(text) < 50 and "http" in text):
            m = re.search(r"https?://\S+", text)
            if m:
                url_only.append({"bookmark": b, "tco_url": m.group(0)})

    print(f"Found {len(url_only)} URL-only bookmarks")

    print("Getting X cookies from Brave...")
    cookies = get_x_cookies()
    print(f"✓ auth_token: ...{cookies.get('auth_token','')[-6:]}")

    print("\nResolving t.co shortcuts...")
    for item in url_only:
        item["final_url"] = resolve_tco(item["tco_url"])
    print("✓ Done")

    print("\nLaunching Playwright with injected cookies...")
    raw_results = await fetch_articles(url_only, cookies)

    # Enrich with category/verdict
    results = []
    for r in raw_results:
        combined = f"{r['title']} {r['text']}"
        results.append({**r,
            "category": categorize(combined),
            "verdict":  verdict_tag(combined),
        })

    # ── Write outputs ─────────────────────────────────────────────────────────
    by_cat = {}
    for r in results:
        by_cat.setdefault(r["category"], []).append(r)

    brief_lines = [f"# URL-Resolved Bookmarks — 2026-02-26\n\n{len(results)} resolved.\n\n---\n"]
    for cat, items in sorted(by_cat.items()):
        brief_lines.append(f"\n## {cat}\n")
        for r in items:
            brief_lines.append(f"**@{r['username']}** — [{r['title'][:80]}]({r['final_url']})\n")
            if r["text"]:
                brief_lines.append(f"> {r['text'][:200]}\n\n")
            brief_lines.append(f"**Verdict: {r['verdict']}**\n\n")
    OUTPUT_BRIEF.write_text("".join(brief_lines))
    print(f"\n✅ Brief saved: {OUTPUT_BRIEF}")

    obs = f"# URL-Resolved Bookmarks — Feb 26 2026\n\n{len(results)} bookmarks.\n"
    for cat, items in sorted(by_cat.items()):
        obs += f"\n## {cat}\n"
        for r in items:
            obs += f"- **@{r['username']}** — [{r['title'][:80]}]({r['final_url']}) → `{r['verdict']}`\n"
            if r["text"]:
                obs += f"  _{r['text'][:150]}_\n"
    obsidian_file = OBSIDIAN_DIR / "2026-02-26-url-resolved-bookmarks.md"
    obsidian_file.write_text(obs)
    print(f"✅ Obsidian saved: {obsidian_file}")

    print("\n=== SUMMARY ===")
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
