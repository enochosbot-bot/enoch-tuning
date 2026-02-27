#!/usr/bin/env python3
"""OAuth flow for YouTube Data API v3 + Google Photos Library API."""

import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

CREDS_PATH = os.path.expanduser("~/Library/Application Support/gogcli/credentials.json")
TOKEN_PATH = os.path.expanduser("~/.openclaw/workspace/scripts/google-yt-photos-token.json")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/photoslibrary.readonly",
]

def main():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Build client config from gog's flat format
            with open(CREDS_PATH) as f:
                raw = json.load(f)
            
            client_config = {
                "installed": {
                    "client_id": raw["client_id"],
                    "client_secret": raw["client_secret"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"]
                }
            }
            
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=8099, prompt="consent", access_type="offline")
        
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    
    print("✅ Auth successful! Token saved to", TOKEN_PATH)
    print("Scopes:", creds.scopes or SCOPES)

if __name__ == "__main__":
    main()
