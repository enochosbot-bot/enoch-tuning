#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


def upload_youtube(video_path: Path, title: str, description: str, tags: list[str], privacy: str = "public") -> dict:
    """Placeholder uploader scaffold.

    Uses existing OAuth token file; if libs/token/scope are missing, returns skipped.
    """
    token_path = Path(__file__).resolve().parents[1] / "google-yt-photos-token.json"
    if not token_path.exists():
        return {"status": "skipped", "reason": "Missing google-yt-photos-token.json"}

    try:
        from googleapiclient.discovery import build  # type: ignore
        from googleapiclient.http import MediaFileUpload  # type: ignore
        from google.oauth2.credentials import Credentials  # type: ignore
    except Exception as e:
        return {"status": "skipped", "reason": f"google-api-python-client not installed: {e}"}

    try:
        creds_data = json.loads(token_path.read_text(encoding="utf-8"))
        creds = Credentials.from_authorized_user_info(creds_data)
        yt = build("youtube", "v3", credentials=creds)
        request = yt.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title[:100],
                    "description": description,
                    "tags": tags,
                    "categoryId": "25",
                },
                "status": {
                    "privacyStatus": privacy,
                    "selfDeclaredMadeForKids": False,
                },
            },
            media_body=MediaFileUpload(str(video_path), chunksize=-1, resumable=True),
        )
        response = None
        while response is None:
            _, response = request.next_chunk()
        return {"status": "success", "video_id": response.get("id"), "url": f"https://youtube.com/watch?v={response.get('id')}"}
    except Exception as e:
        return {"status": "failed", "reason": str(e)}
