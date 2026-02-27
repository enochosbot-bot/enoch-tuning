#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from typing import Dict

import requests


def _keychain(name: str) -> str | None:
    p = subprocess.run(["security", "find-generic-password", "-s", name, "-w"], capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 and p.stdout.strip() else None


def fallback_script(topic: str, duration: int, brand: str = "americanfireside") -> Dict[str, str]:
    hook = f"They told you {topic} was settled. It isn't."
    body = (
        "Here is the truth in plain English: power follows narratives, and narratives follow courage. "
        "If we want a freer future, we have to speak clearly, act boldly, and refuse to outsource conviction."
    )
    cta = "Follow AmericanFireside for fearless, faith-forward takes that actually matter."
    full = f"{hook} {body} {cta}"
    return {"hook": hook, "body": body, "cta": cta, "full_script": full, "tts_text": full}


def generate_script(topic: str, duration: int = 30, brand: str = "americanfireside") -> Dict[str, str]:
    key = _keychain("ANTHROPIC_API_KEY")
    if not key:
        return fallback_script(topic, duration, brand)

    system = (
        "You write short-form scripts for social video. Return strict JSON with keys: "
        "hook, body, cta, full_script, tts_text.\n"
        "Rules: strong hook in first 3 seconds, 1-3 punchy points, natural CTA, no disclaimers. "
        "tts_text should be clean spoken text without stage directions or symbols."
    )
    user = f"Brand: {brand}\nTarget duration: {duration}s\nTopic: {topic}\nOutput JSON only."

    payload = {
        "model": "claude-3-5-haiku-latest",
        "max_tokens": 700,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    try:
        r = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=45)
        r.raise_for_status()
        data = r.json()
        text = "\n".join(c.get("text", "") for c in data.get("content", []) if c.get("type") == "text").strip()
        if text.startswith("```"):
            text = text.strip("`")
            if "\n" in text:
                text = text.split("\n", 1)[1]
        obj = json.loads(text[text.find("{"): text.rfind("}")+1])
        for k in ["hook", "body", "cta", "full_script", "tts_text"]:
            obj.setdefault(k, "")
        if not obj["full_script"]:
            obj["full_script"] = f"{obj['hook']} {obj['body']} {obj['cta']}".strip()
        if not obj["tts_text"]:
            obj["tts_text"] = obj["full_script"]
        return obj
    except Exception:
        return fallback_script(topic, duration, brand)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("topic")
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--brand", default="americanfireside")
    args = parser.parse_args()
    print(json.dumps(generate_script(args.topic, args.duration, args.brand), indent=2))
