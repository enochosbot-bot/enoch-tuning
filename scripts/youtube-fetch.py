#!/usr/bin/env python3
"""Fetch YouTube data: liked videos, subscriptions, playlists."""

import json, sys, os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_PATH = os.path.expanduser("~/.openclaw/workspace/scripts/google-yt-photos-token.json")
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def get_youtube():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def liked_videos(yt, max_results=50):
    items = []
    req = yt.videos().list(part="snippet,contentDetails", myRating="like", maxResults=min(max_results, 50))
    while req and len(items) < max_results:
        resp = req.execute()
        for v in resp.get("items", []):
            s = v["snippet"]
            items.append({
                "title": s["title"],
                "channel": s["channelTitle"],
                "published": s["publishedAt"],
                "id": v["id"],
                "url": f"https://youtube.com/watch?v={v['id']}"
            })
        req = yt.videos().list_next(req, resp)
    return items

def subscriptions(yt, max_results=200):
    items = []
    req = yt.subscriptions().list(part="snippet", mine=True, maxResults=50, order="alphabetical")
    while req and len(items) < max_results:
        resp = req.execute()
        for s in resp.get("items", []):
            sn = s["snippet"]
            items.append({
                "channel": sn["title"],
                "channelId": sn["resourceId"]["channelId"],
                "description": sn.get("description", "")[:100]
            })
        req = yt.subscriptions().list_next(req, resp)
    return items

def playlists(yt, max_results=50):
    items = []
    req = yt.playlists().list(part="snippet,contentDetails", mine=True, maxResults=50)
    while req and len(items) < max_results:
        resp = req.execute()
        for p in resp.get("items", []):
            s = p["snippet"]
            items.append({
                "title": s["title"],
                "id": p["id"],
                "count": p["contentDetails"]["itemCount"],
                "description": s.get("description", "")[:100]
            })
        req = yt.playlists().list_next(req, resp)
    return items

def channel_info(yt):
    resp = yt.channels().list(part="snippet,statistics", mine=True).execute()
    if resp.get("items"):
        ch = resp["items"][0]
        s = ch["snippet"]
        st = ch["statistics"]
        return {
            "name": s["title"],
            "id": ch["id"],
            "subscribers": st.get("subscriberCount"),
            "videos": st.get("videoCount"),
            "views": st.get("viewCount"),
            "created": s.get("publishedAt")
        }
    return None

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    yt = get_youtube()
    
    if cmd == "likes":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        print(json.dumps(liked_videos(yt, n), indent=2))
    elif cmd == "subs":
        print(json.dumps(subscriptions(yt), indent=2))
    elif cmd == "playlists":
        print(json.dumps(playlists(yt), indent=2))
    elif cmd == "channel":
        print(json.dumps(channel_info(yt), indent=2))
    elif cmd == "all":
        data = {
            "channel": channel_info(yt),
            "liked_videos": liked_videos(yt, 50),
            "subscriptions": subscriptions(yt),
            "playlists": playlists(yt)
        }
        print(json.dumps(data, indent=2))
    else:
        print(f"Usage: {sys.argv[0]} [likes|subs|playlists|channel|all]")
