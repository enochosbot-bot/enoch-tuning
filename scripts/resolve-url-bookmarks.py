#!/usr/bin/env python3
"""
Resolve t.co URLs from x-bookmarks-new.json, scrape content, and file into Obsidian.
"""

import json
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

BOOKMARKS_FILE = Path("/Users/deaconsopenclaw/.openclaw/workspace/research/x-bookmarks-new.json")
OBSIDIAN_CAPTURES = Path("/Users/deaconsopenclaw/Documents/Brain/Personal Memories/Enoch/Captures")
OUTPUT_BRIEF = Path("/Users/deaconsopenclaw/.openclaw/workspace/research/vetted/2026-02-26-url-resolved.md")

def resolve_tco(url: str) -> str:
    """Follow t.co redirect to get final URL."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=8)
        return resp.url
    except Exception:
        return url

def scrape_with_scrapling(url: str) -> dict:
    """Use scrapling CLI to fetch and extract content."""
    import subprocess
    try:
        result = subprocess.run(
            ["scrapling", "extract", url, "--text", "--title", "--timeout", "15"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return {"success": True, "output": result.stdout[:2000]}
        else:
            return {"success": False, "error": result.stderr[:300]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def fallback_fetch(url: str) -> str:
    """Simple HTTP fetch fallback."""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        resp = urllib.request.urlopen(req, timeout=10)
        raw = resp.read(8000).decode('utf-8', errors='ignore')
        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', raw, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip()[:120] if title_match else ""
        # Strip tags for body preview
        body = re.sub(r'<[^>]+>', ' ', raw)
        body = re.sub(r'\s+', ' ', body).strip()[:600]
        return f"Title: {title}\n\n{body}"
    except Exception as e:
        return f"[fetch failed: {e}]"

def categorize(title: str, body: str) -> str:
    text = (title + " " + body).lower()
    if any(w in text for w in ['github', 'code', 'repo', 'library', 'python', 'node', 'api', 'sdk', 'npm', 'pip']):
        return "Tools & Libraries"
    if any(w in text for w in ['ai', 'llm', 'gpt', 'claude', 'model', 'neural', 'openai', 'anthropic', 'gemini']):
        return "AI & Models"
    if any(w in text for w in ['business', 'revenue', 'sales', 'marketing', 'growth', 'startup', 'money', 'income']):
        return "Business & Growth"
    if any(w in text for w in ['security', 'hack', 'vuln', 'privacy', 'encrypt', 'firewall']):
        return "Security"
    if any(w in text for w in ['youtube', 'video', 'twitter', 'tweet', 'social', 'instagram', 'tiktok']):
        return "Social & Media"
    return "General"

def verdict(title: str, body: str) -> str:
    text = (title + " " + body).lower()
    if any(w in text for w in ['install', 'pip install', 'npm install', 'brew install', 'deploy', 'use now']):
        return "ACT_ON"
    if any(w in text for w in ['research', 'paper', 'study', 'analysis', 'findings', 'data']):
        return "READ_DEEPER"
    if any(w in text for w in ['share', 'viral', 'thread', 'story']):
        return "SHARE"
    return "ARCHIVE"

def main():
    with open(BOOKMARKS_FILE) as f:
        all_bookmarks = json.load(f)

    url_only = [
        b for b in all_bookmarks
        if re.match(r'^https?://\S+$', (b.get('text', '') or '').strip())
        or (len((b.get('text', '') or '').strip()) < 50 and 'http' in (b.get('text', '') or ''))
    ]

    print(f"Processing {len(url_only)} URL-only bookmarks...\n")

    results = []
    for i, b in enumerate(url_only):
        username = b.get('username', 'unknown')
        raw_url = (b.get('text', '') or '').strip()
        # Extract URL from text
        url_match = re.search(r'https?://\S+', raw_url)
        if not url_match:
            continue
        tco_url = url_match.group(0)
        
        print(f"[{i+1}/{len(url_only)}] @{username} — resolving {tco_url}")
        
        # Resolve t.co
        final_url = resolve_tco(tco_url)
        print(f"  → {final_url[:80]}")
        
        # Scrape content
        scraped = scrape_with_scrapling(final_url)
        if scraped["success"]:
            content = scraped["output"]
        else:
            content = fallback_fetch(final_url)
        
        # Extract title from content
        title_match = re.search(r'Title:\s*(.+)', content)
        title = title_match.group(1).strip() if title_match else final_url
        
        cat = categorize(title, content)
        ver = verdict(title, content)
        
        results.append({
            "username": username,
            "tco_url": tco_url,
            "final_url": final_url,
            "title": title,
            "category": cat,
            "verdict": ver,
            "content_preview": content[:400]
        })
        
        print(f"  ✓ {title[:60]} [{cat}] → {ver}")
        time.sleep(0.5)

    # Write brief
    OUTPUT_BRIEF.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# URL-Resolved Bookmarks — 2026-02-26\n", f"Resolved {len(results)} URL-only bookmarks.\n\n---\n"]
    
    by_cat = {}
    for r in results:
        by_cat.setdefault(r['category'], []).append(r)
    
    for cat, items in sorted(by_cat.items()):
        lines.append(f"\n## {cat}\n")
        for r in items:
            lines.append(f"**@{r['username']}** — [{r['title'][:80]}]({r['final_url']})\n")
            lines.append(f"  > {r['content_preview'][:200]}\n")
            lines.append(f"  **Verdict: {r['verdict']}**\n\n")
    
    OUTPUT_BRIEF.write_text("".join(lines))
    print(f"\n✅ Brief saved to {OUTPUT_BRIEF}")

    # Save to Obsidian
    obsidian_file = OBSIDIAN_CAPTURES / "2026-02-26-url-resolved-bookmarks.md"
    obsidian_content = "# URL-Resolved Bookmarks — Feb 26 2026\n\n"
    obsidian_content += f"Resolved {len(results)} URL-only bookmarks using Scrapling.\n\n"
    for cat, items in sorted(by_cat.items()):
        obsidian_content += f"\n## {cat}\n"
        for r in items:
            obsidian_content += f"- **@{r['username']}** — [{r['title'][:80]}]({r['final_url']}) → `{r['verdict']}`\n"
    obsidian_file.write_text(obsidian_content)
    print(f"✅ Obsidian note saved to {obsidian_file}")

    # Print summary
    print(f"\n=== SUMMARY ===")
    verdict_counts = {}
    for r in results:
        verdict_counts[r['verdict']] = verdict_counts.get(r['verdict'], 0) + 1
    for v, count in sorted(verdict_counts.items()):
        print(f"  {v}: {count}")
    
    # Print ACT_ON items specifically
    act_on = [r for r in results if r['verdict'] == 'ACT_ON']
    if act_on:
        print(f"\n🔴 ACT_ON items:")
        for r in act_on:
            print(f"  @{r['username']}: {r['title'][:70]}")
            print(f"    {r['final_url']}")

if __name__ == "__main__":
    main()
