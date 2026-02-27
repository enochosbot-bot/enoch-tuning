#!/usr/bin/env python3
"""
linkedin-post.py — Post to LinkedIn as member via API v2
Usage: python3 linkedin-post.py "Your post text"
Requires: LINKEDIN_ACCESS_TOKEN env var
"""

import os, sys, json, urllib.request, urllib.error

def get_author_urn(token):
    req = urllib.request.Request(
        "https://api.linkedin.com/v2/me",
        headers={"Authorization": f"Bearer {token}", "X-Restli-Protocol-Version": "2.0.0"}
    )
    with urllib.request.urlopen(req) as resp:
        me = json.loads(resp.read())
        return f"urn:li:person:{me['id']}"

def post(text):
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    if not token:
        # fallback to token file
        token_file = os.path.expanduser("~/.openclaw/workspace/scripts/linkedin-token.json")
        with open(token_file) as f:
            token = json.load(f)["access_token"]

    author = get_author_urn(token)

    payload = json.dumps({
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }).encode()

    req = urllib.request.Request(
        "https://api.linkedin.com/v2/ugcPosts",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        post_id = result.get("id", "").replace("urn:li:ugcPost:", "")
        print(f"https://www.linkedin.com/feed/update/urn:li:ugcPost:{post_id}/")

if __name__ == "__main__":
    # KILL SWITCH — personal profile posting disabled until org page (w_organization_social) is approved
    # Do NOT remove until Ridley Research company page URN is configured and MDP approval confirmed
    print("ERROR: Personal LinkedIn posting is disabled. Posts must go to the Ridley Research company page.")
    print("Apply for Marketing Developer Platform at: https://www.linkedin.com/developers/apps/869fp76go0gr0x/products")
    sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python3 linkedin-post.py 'text'")
        sys.exit(1)
    post(sys.argv[1])
