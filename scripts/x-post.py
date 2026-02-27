#!/usr/bin/env python3
"""
x-post.py — Post to X (Twitter) via API v2 with OAuth 1.0a
Usage: python3 x-post.py "Your tweet text"
       python3 x-post.py "Reply text" --reply-to <tweet_id>
"""

import os
import sys
import tweepy
import argparse

def get_client():
    api_key = os.environ.get("X_API_KEY_ENOCH")
    api_secret = os.environ.get("X_API_SECRET_ENOCH")
    access_token = os.environ.get("X_ACCESS_TOKEN_ENOCH")
    access_secret = os.environ.get("X_ACCESS_TOKEN_SECRET_ENOCH")

    if not all([api_key, api_secret, access_token, access_secret]):
        print("ERROR: Missing X API credentials in environment", file=sys.stderr)
        sys.exit(1)

    return tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret
    )

def main():
    parser = argparse.ArgumentParser(description="Post to X")
    parser.add_argument("text", help="Tweet text")
    parser.add_argument("--reply-to", help="Tweet ID to reply to", default=None)
    args = parser.parse_args()

    client = get_client()

    kwargs = {"text": args.text, "user_auth": True}
    if args.reply_to:
        kwargs["in_reply_to_tweet_id"] = args.reply_to

    response = client.create_tweet(**kwargs)
    tweet_id = response.data["id"]
    print(f"https://x.com/i/web/status/{tweet_id}")

if __name__ == "__main__":
    main()
