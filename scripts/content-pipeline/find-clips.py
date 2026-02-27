#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from urllib import request

MODEL = "gpt-4o-mini"
API_URL = "https://api.openai.com/v1/chat/completions"


def sec_to_hhmmss(sec: float) -> str:
    sec = max(0, float(sec))
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def hhmmss_to_sec(s: str) -> float:
    s = s.strip()
    if re.fullmatch(r"\d+(\.\d+)?", s):
        return float(s)
    parts = s.replace(",", ".").split(":")
    parts = [p.strip() for p in parts]
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    raise ValueError(f"Bad time format: {s}")


def build_transcript_window(segments, max_segments=450):
    if len(segments) <= max_segments:
        return segments
    step = max(1, len(segments) // max_segments)
    return [segments[i] for i in range(0, len(segments), step)][:max_segments]


def call_openai(api_key: str, prompt: str) -> str:
    payload = {
        "model": MODEL,
        "temperature": 0.4,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an elite short-form video producer for Christian apologetics and preaching content. "
                    "Find highly shareable 45-90s moments with strong opening hook and emotional/theological weight."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        API_URL,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with request.urlopen(req, timeout=120) as resp:
        raw = resp.read().decode("utf-8")
    obj = json.loads(raw)
    if "error" in obj:
        raise RuntimeError(obj["error"])
    return obj["choices"][0]["message"]["content"]


def heuristic_clips(segments, count=3):
    keywords = [
        "jesus", "christ", "gospel", "repent", "grace", "truth", "bible", "scripture",
        "cross", "resurrection", "forgive", "salvation", "sin", "god", "amen",
    ]
    scored = []
    for i, seg in enumerate(segments):
        txt = (seg.get("text") or "").lower()
        score = sum(1 for k in keywords if k in txt)
        if "?" in txt:
            score += 1
        if len(txt) > 80:
            score += 1
        scored.append((score, i))
    scored.sort(reverse=True)

    picks = []
    used = set()
    for _, i in scored:
        if len(picks) >= count:
            break
        if i in used:
            continue
        st = float(segments[i].get("start", 0))
        en = st + 60
        # grow window forward
        j = i
        while j < len(segments) and float(segments[j].get("end", 0)) < st + 75:
            j += 1
        if j < len(segments):
            en = float(segments[j].get("end", en))
        en = min(en, st + 90)
        if en - st < 45:
            continue
        picks.append(
            {
                "start_time": round(st, 3),
                "end_time": round(en, 3),
                "title_suggestion": "Conviction Moment",
                "hook_text": (segments[i].get("text") or "").strip()[:110],
                "why_this_clip": "Strong theological/emotional line with short-form potential.",
            }
        )
        used.update(range(max(0, i - 4), min(len(segments), i + 8)))

    return picks[:count]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--count", type=int, default=3)
    args = ap.parse_args()

    with open(args.transcript, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments = data.get("segments", [])
    if not segments:
        print("No transcript segments found.", file=sys.stderr)
        sys.exit(1)

    compact = build_transcript_window(segments)
    compact_text = "\n".join(
        f"[{sec_to_hhmmss(s.get('start', 0))} - {sec_to_hhmmss(s.get('end', 0))}] {str(s.get('text','')).strip()}"
        for s in compact
    )

    prompt = f"""
Transcript excerpt (with timestamps):
{compact_text}

Select the top {args.count} short-form clips for YouTube Shorts/TikTok/X.
Audience: Christian apologetics / sermons / street preaching / theological debate.
Prioritize:
1) Hook in first 3 seconds
2) Emotional punch, conviction, or clear theological argument
3) Powerful scripture references, audience reaction, breakthrough moments
4) Clean edit boundaries
5) Ideal 45-90 seconds

Return STRICT JSON object with this shape:
{{
  "clips": [
    {{
      "start_time": "HH:MM:SS.mmm or seconds",
      "end_time": "HH:MM:SS.mmm or seconds",
      "title_suggestion": "...",
      "hook_text": "...",
      "why_this_clip": "..."
    }}
  ]
}}
""".strip()

    clips = []
    api_key = os.getenv("OPENAI_API_KEY", "")

    if api_key:
        try:
            content = call_openai(api_key, prompt)
            parsed = json.loads(content)
            clips = parsed.get("clips", [])
        except Exception as e:
            print(f"OpenAI clip-finding failed, using heuristic fallback: {e}", file=sys.stderr)
            clips = heuristic_clips(segments, args.count)
    else:
        clips = heuristic_clips(segments, args.count)

    normalized = []
    for i, c in enumerate(clips[: args.count], start=1):
        try:
            st = hhmmss_to_sec(str(c.get("start_time", 0)))
            en = hhmmss_to_sec(str(c.get("end_time", st + 60)))
        except Exception:
            continue
        if en <= st:
            en = st + 60
        dur = en - st
        if dur < 45:
            en = st + 45
        if dur > 90:
            en = st + 90
        normalized.append(
            {
                "id": i,
                "start_time": round(st, 3),
                "end_time": round(en, 3),
                "title_suggestion": c.get("title_suggestion", f"Clip {i}"),
                "hook_text": c.get("hook_text", ""),
                "why_this_clip": c.get("why_this_clip", ""),
            }
        )

    out = {"clips": normalized}
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"✅ Wrote {len(normalized)} clip suggestions to {args.output}")


if __name__ == "__main__":
    main()
