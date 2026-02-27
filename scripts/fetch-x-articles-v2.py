#!/usr/bin/env python3
"""
Fetch X Article content via authenticated GraphQL API using Brave cookies.
X Articles live at x.com/i/article/ARTICLE_ID and use the ArticleDetailPage endpoint.
"""

import asyncio
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

try:
    import httpx
except ImportError:
    print("ERROR: httpx not installed. Run: uv tool install httpx"); sys.exit(1)

BOOKMARKS_FILE = Path("/Users/deaconsopenclaw/.openclaw/workspace/research/x-bookmarks-new.json")
OBSIDIAN_CAPTURES = Path("/Users/deaconsopenclaw/Documents/Brain/Personal Memories/Enoch/Captures")
OUTPUT_BRIEF = Path("/Users/deaconsopenclaw/.openclaw/workspace/research/vetted/2026-02-26-url-resolved.md")
BRAVE_DB = os.path.expanduser(
    "~/Library/Application Support/BraveSoftware/Brave-Browser/Default/Cookies"
)

# ── Cookie extraction (identical to working sync script) ──────────────────────

def _brave_key():
    import subprocess
    r = subprocess.run(
        ["security", "find-generic-password", "-w", "-s", "Brave Safe Storage", "-a", "Brave"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        raise RuntimeError(f"Brave keychain error: {r.stderr.strip()}")
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
    tmp_db = "/tmp/brave-x-v2.db"
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
        raise RuntimeError(f"Missing X cookies: {missing}")
    return cookies

# ── Article fetch via GraphQL ─────────────────────────────────────────────────

ARTICLE_QUERY_ID = "aTL3j3oAnPFGXR6HvlJiHQ"  # ArticleDetailPage query ID

def fetch_article_gql(client: httpx.Client, article_id: str) -> dict:
    """Fetch article content from X GraphQL API."""
    variables = json.dumps({"articleId": article_id, "referrer": "article"})
    features = json.dumps({
        "rweb_tipjar_consumption_enabled": True,
        "responsive_web_graphql_exclude_directive_enabled": True,
        "verified_phone_label_enabled": False,
        "creator_subscriptions_tweet_preview_api_enabled": True,
        "responsive_web_graphql_timeline_navigation_enabled": True,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "communities_web_enable_tweet_community_results_fetch": True,
        "c9s_tweet_anatomy_moderator_badge_enabled": True,
        "articles_preview_enabled": True,
        "responsive_web_edit_tweet_api_enabled": True,
        "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
        "view_counts_everywhere_api_enabled": True,
        "longform_notetweets_consumption_enabled": True,
        "responsive_web_twitter_article_tweet_consumption_enabled": True,
        "tweet_awards_web_tipping_enabled": False,
        "creator_subscriptions_quote_tweet_preview_enabled": False,
        "freedom_of_speech_not_reach_fetch_enabled": True,
        "standardized_nudges_misinfo": True,
        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
        "rweb_video_timestamps_enabled": True,
        "longform_notetweets_rich_text_read_enabled": True,
        "longform_notetweets_inline_media_enabled": True,
        "responsive_web_enhance_cards_enabled": False,
    })

    url = f"https://x.com/i/api/graphql/{ARTICLE_QUERY_ID}/ArticleDetailPage"
    try:
        resp = client.get(url, params={"variables": variables, "features": features}, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def extract_article_text(data: dict) -> tuple[str, str]:
    """Extract title and text from GraphQL article response."""
    try:
        # Navigate the nested response
        result = data.get("data", {})
        # Try various paths
        for path in [
            ["article_by_rest_id", "result"],
            ["tweetResult", "result"],
        ]:
            node = result
            for key in path:
                node = node.get(key, {}) if isinstance(node, dict) else {}
            if node:
                break

        # Article might be nested under tweet
        if "tweet" in str(data)[:2000]:
            # Try to find article content in the response
            raw_str = json.dumps(data)
            title_match = re.search(r'"title"\s*:\s*"([^"]{5,200})"', raw_str)
            text_match = re.search(r'"plain_text"\s*:\s*"([^"]{10,}?)"', raw_str)
            preview_match = re.search(r'"preview_text"\s*:\s*"([^"]{5,300})"', raw_str)

            title = title_match.group(1) if title_match else ""
            text = text_match.group(1)[:500] if text_match else (preview_match.group(1) if preview_match else "")
            if title or text:
                return title, text

        return "", json.dumps(data)[:200]
    except Exception as e:
        return "", str(e)


# ── Tweet detail fallback via TweetResultByRestId ────────────────────────────

TWEET_QUERY_ID = "0hWvDhmW8YQ-S_ib3azIrw"

def fetch_tweet_gql(client: httpx.Client, tweet_id: str) -> dict:
    variables = json.dumps({
        "tweetId": tweet_id,
        "referrer": "profile",
        "includePromotedContent": False,
        "withCommunity": True,
        "withVoice": True,
    })
    features = json.dumps({
        "articles_preview_enabled": True,
        "longform_notetweets_consumption_enabled": True,
        "responsive_web_twitter_article_tweet_consumption_enabled": True,
        "longform_notetweets_rich_text_read_enabled": True,
        "longform_notetweets_inline_media_enabled": True,
        "rweb_tipjar_consumption_enabled": True,
        "responsive_web_graphql_exclude_directive_enabled": True,
        "verified_phone_label_enabled": False,
        "creator_subscriptions_tweet_preview_api_enabled": True,
        "responsive_web_graphql_timeline_navigation_enabled": True,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "communities_web_enable_tweet_community_results_fetch": True,
        "c9s_tweet_anatomy_moderator_badge_enabled": True,
        "responsive_web_edit_tweet_api_enabled": True,
        "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
        "view_counts_everywhere_api_enabled": True,
        "tweet_awards_web_tipping_enabled": False,
        "creator_subscriptions_quote_tweet_preview_enabled": False,
        "freedom_of_speech_not_reach_fetch_enabled": True,
        "standardized_nudges_misinfo": True,
        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
        "rweb_video_timestamps_enabled": True,
        "responsive_web_enhance_cards_enabled": False,
    })
    url = f"https://x.com/i/api/graphql/{TWEET_QUERY_ID}/TweetResultByRestId"
    try:
        resp = client.get(url, params={"variables": variables, "features": features}, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def extract_tweet_text(data: dict) -> tuple[str, str]:
    """Extract tweet text and embedded article info."""
    try:
        raw_str = json.dumps(data)
        # Look for article title/text first
        title_match = re.search(r'"title"\s*:\s*"([^"]{5,200})"', raw_str)
        preview_match = re.search(r'"preview_text"\s*:\s*"([^"]{5,300})"', raw_str)
        plain_match = re.search(r'"plain_text"\s*:\s*"([^"]{10,500})"', raw_str)
        full_text_match = re.search(r'"full_text"\s*:\s*"([^"]{10,500})"', raw_str)
        text_match = re.search(r'"text"\s*:\s*"([^"]{10,300})"', raw_str)

        title = title_match.group(1) if title_match else ""
        text = (plain_match.group(1) if plain_match else
                preview_match.group(1) if preview_match else
                full_text_match.group(1) if full_text_match else
                text_match.group(1) if text_match else "")

        return title, text
    except Exception:
        return "", ""


# ── Categorize & verdict ──────────────────────────────────────────────────────

def categorize(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ['github', 'code', 'repo', 'python', 'node', 'api', 'install', 'deploy', 'library']):
        return "Tools & Libraries"
    if any(w in t for w in ['ai ', 'llm', 'gpt', 'claude', 'model', 'openai', 'anthropic', 'gemini', 'agent']):
        return "AI & Models"
    if any(w in t for w in ['business', 'revenue', 'sales', 'marketing', 'growth', 'startup', 'income', 'client']):
        return "Business & Growth"
    if any(w in t for w in ['security', 'hack', 'vuln', 'privacy', 'encrypt']):
        return "Security"
    if any(w in t for w in ['content', 'creator', 'social', 'youtube', 'audience', 'followers']):
        return "Content & Social"
    return "General"


def verdict_tag(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ['how to', 'tutorial', 'step by step', 'install', 'use this', 'run this', 'build this']):
        return "ACT_ON"
    if any(w in t for w in ['build', 'create', 'automate', 'system', 'framework', 'tool', 'workflow']):
        return "BUILD"
    if any(w in t for w in ['study', 'research', 'analysis', 'paper', 'data', 'findings']):
        return "READ_DEEPER"
    if any(w in t for w in ['share', 'viral', 'spread', 'everyone']):
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

    # Get auth cookies
    print("Getting X cookies from Brave...")
    cookies = get_x_cookies()
    print(f"✓ auth_token: ...{cookies['auth_token'][-6:]}")

    # Build authenticated HTTP client
    client = httpx.Client(
        cookies={"auth_token": cookies["auth_token"], "ct0": cookies["ct0"]},
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "x-csrf-token": cookies["ct0"],
            "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
            "x-twitter-active-user": "yes",
            "x-twitter-auth-type": "OAuth2Session",
            "x-twitter-client-language": "en",
            "Referer": "https://x.com/",
        },
        follow_redirects=True,
    )

    # Resolve t.co URLs
    print("\nResolving t.co URLs...")
    import urllib.request
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
            item['type'] = 'article'
        else:
            m2 = re.search(r'/status/(\d+)', item['final_url'])
            item['article_id'] = m2.group(1) if m2 else None
            item['type'] = 'tweet' if m2 else 'unknown'

    print(f"  Articles: {sum(1 for i in url_only if i['type']=='article')}")
    print(f"  Tweets:   {sum(1 for i in url_only if i['type']=='tweet')}")
    print(f"  Unknown:  {sum(1 for i in url_only if i['type']=='unknown')}")

    # Fetch content
    print("\nFetching content via GraphQL...")
    results = []
    for i, item in enumerate(url_only):
        username = item['bookmark'].get('username', 'unknown')
        article_id = item.get('article_id')

        if not article_id:
            results.append({'username': username, 'final_url': item['final_url'],
                           'title': f'[no ID] {item["tco_url"]}', 'text': '',
                           'category': 'General', 'verdict': 'ARCHIVE'})
            continue

        # Try article endpoint first, then tweet endpoint
        title, text = "", ""
        for fetch_fn, label in [(fetch_article_gql, "article"), (fetch_tweet_gql, "tweet")]:
            data = fetch_fn(client, article_id)
            if "error" not in data:
                title, text = (extract_article_text if label == "article" else extract_tweet_text)(data)
                if title or text:
                    break

        if not title and not text:
            title = f"[content unavailable] @{username}"

        cat = categorize(f"{title} {text}")
        ver = verdict_tag(f"{title} {text}")
        results.append({
            'username': username,
            'final_url': item['final_url'],
            'title': title or f"@{username} article",
            'text': text[:400],
            'category': cat,
            'verdict': ver,
        })
        print(f"[{i+1}/{len(url_only)}] @{username} — {(title or text)[:60]} [{cat}] → {ver}")
        time.sleep(0.6)

    client.close()

    # Write outputs
    print("\nWriting outputs...")
    by_cat = {}
    for r in results:
        by_cat.setdefault(r['category'], []).append(r)

    lines = [f"# URL-Resolved Bookmarks — 2026-02-26\n\n{len(results)} bookmarks resolved.\n\n---\n"]
    for cat, items in sorted(by_cat.items()):
        lines.append(f"\n## {cat}\n")
        for r in items:
            lines.append(f"**@{r['username']}** — [{r['title'][:80]}]({r['final_url']})\n")
            if r['text']:
                lines.append(f"> {r['text'][:200]}\n\n")
            lines.append(f"**Verdict: {r['verdict']}**\n\n")
    OUTPUT_BRIEF.write_text("".join(lines))
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
    for r in results: vc[r['verdict']] = vc.get(r['verdict'], 0) + 1
    for v, c in sorted(vc.items()): print(f"  {v}: {c}")

    non_archive = [r for r in results if r['verdict'] != 'ARCHIVE']
    if non_archive:
        print("\n🔴 Action items:")
        for r in non_archive:
            print(f"  [{r['verdict']}] @{r['username']}: {r['title'][:70]}")


if __name__ == "__main__":
    main()
