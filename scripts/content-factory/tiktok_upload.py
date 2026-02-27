#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

import requests


def _keychain(name: str) -> str | None:
    p = subprocess.run(["security", "find-generic-password", "-s", name, "-w"], capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 and p.stdout.strip() else None


def upload_tiktok(video_path: Path, title: str) -> dict:
    token = _keychain("TIKTOK_ACCESS_TOKEN")
    if not token:
        return {"status": "skipped", "reason": "Missing TIKTOK_ACCESS_TOKEN"}

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        init = requests.post(
            "https://open.tiktokapis.com/v2/post/publish/video/init/",
            headers=headers,
            json={"post_info": {"title": title[:150]}, "source_info": {"source": "FILE_UPLOAD"}},
            timeout=45,
        )
        init.raise_for_status()
        data = init.json().get("data", {})
        upload_url = data.get("upload_url")
        publish_id = data.get("publish_id")
        if not upload_url or not publish_id:
            return {"status": "failed", "reason": f"init missing fields: {data}"}

        with open(video_path, "rb") as f:
            up = requests.put(upload_url, data=f, timeout=120)
            up.raise_for_status()

        status = requests.post(
            "https://open.tiktokapis.com/v2/post/publish/status/fetch/",
            headers=headers,
            json={"publish_id": publish_id},
            timeout=45,
        )
        status.raise_for_status()
        return {"status": "success", "publish_id": publish_id, "detail": status.json()}
    except Exception as e:
        return {"status": "failed", "reason": str(e)}
