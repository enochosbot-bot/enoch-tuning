#!/usr/bin/env python3
"""
produce-claudebot-clip.py — Single-shot production for AmericanClaude viral clip.
Hardcoded military response (API bypass), browser recording, sag TTS, ffmpeg merge.
Output: 9:16 MP4 ready for TikTok/Reels/Shorts
"""

import subprocess, json, os, sys, time, tempfile
from pathlib import Path
from datetime import datetime

# ── CONFIG ─────────────────────────────────────────────────────────────────────
WORKSPACE  = Path.home() / ".openclaw/workspace"
CLIPS_DIR  = WORKSPACE / "clips/claude-bot"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)

USER_PROMPT = "remind me to buy milk"
CLAUDE_RESPONSE = (
    "COPY THAT, SOLDIER! Initiating OPERATION: WHITE GOLD — "
    "dairy acquisition commencing oh-six-hundred hours. "
    "Target: one unit of whole milk from local supply depot. "
    "Be advised: calcium levels are CRITICALLY low, "
    "and I repeat — we CANNOT sustain combat operations without it. "
    "This is a PRIORITY ONE mission. MOVE OUT!"
)
VOICE_ID   = "SOYHLrjzK2X1ezoPC6cr"   # Harry — Fierce Warrior
OUT_SLUG   = datetime.now().strftime("%Y%m%d-%H%M%S") + "-milk-military"
OUT_DIR    = CLIPS_DIR / OUT_SLUG
OUT_DIR.mkdir(parents=True, exist_ok=True)

INTRO_HOLD   = 2.8   # seconds to show user bubble before Claude appears
OUTRO_HOLD   = 2.5   # seconds after audio ends before cut

# ── HTML TEMPLATE ──────────────────────────────────────────────────────────────
def build_html(user_prompt: str, claude_response: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    width: 100%; height: 100%;
    background: #111118;
    display: flex; align-items: center; justify-content: center;
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', sans-serif;
  }}
  .phone {{
    width: 390px; height: 844px;
    background: #0e0e16;
    border-radius: 44px;
    display: flex; flex-direction: column;
    overflow: hidden;
    box-shadow: 0 0 0 1.5px #252535, 0 40px 100px rgba(0,0,0,0.75);
    position: relative;
  }}
  /* Status bar */
  .statusbar {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 28px 6px;
    font-size: 12px; font-weight: 600; color: #ccc;
    flex-shrink: 0;
  }}
  .statusbar .time {{ font-size: 15px; font-weight: 700; }}
  .statusbar .icons {{ display: flex; gap: 5px; align-items: center; font-size: 11px; }}
  /* Header */
  .header {{
    padding: 6px 16px 12px;
    border-bottom: 1px solid #1c1c2a;
    display: flex; align-items: center; gap: 12px;
    flex-shrink: 0;
  }}
  .avatar {{
    width: 38px; height: 38px; flex-shrink: 0;
    background: linear-gradient(135deg, #c8693a 0%, #d4875a 100%);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; color: white; font-weight: 700;
    box-shadow: 0 2px 8px rgba(200, 105, 58, 0.4);
  }}
  .header-info {{ flex: 1; }}
  .header-info h2 {{ color: #e8ddd5; font-size: 16px; font-weight: 600; }}
  .header-info span {{ color: #5a5a72; font-size: 12px; }}
  .header-dots {{ color: #3a3a52; font-size: 20px; letter-spacing: 1px; cursor: default; }}
  /* Message area */
  .messages {{
    flex: 1; overflow: hidden;
    padding: 20px 14px;
    display: flex; flex-direction: column;
    gap: 14px;
    justify-content: flex-end;
  }}
  /* Bubbles */
  .bubble {{
    max-width: 80%; padding: 12px 16px;
    line-height: 1.55; font-size: 15px;
    border-radius: 20px;
    word-wrap: break-word;
  }}
  .user-bubble {{
    background: #2d2d50;
    color: #c8c8ea;
    align-self: flex-end;
    border-bottom-right-radius: 5px;
  }}
  .claude-bubble {{
    background: linear-gradient(145deg, #182418, #1c2e1e);
    border: 1px solid #2a4030;
    color: #d8f4d8;
    align-self: flex-start;
    border-bottom-left-radius: 5px;
    opacity: 0;
    transform: translateY(10px);
    transition: opacity 0.45s cubic-bezier(.22,.68,0,1.2), transform 0.45s cubic-bezier(.22,.68,0,1.2);
  }}
  .claude-bubble.visible {{
    opacity: 1; transform: translateY(0);
  }}
  /* Typing indicator */
  .typing {{
    display: flex; gap: 5px; padding: 10px 14px;
    align-self: flex-start;
    background: #16201a; border: 1px solid #243028;
    border-radius: 18px; border-bottom-left-radius: 5px;
    opacity: 1;
    transition: opacity 0.3s;
  }}
  .typing.hidden {{ opacity: 0; pointer-events: none; }}
  .dot {{
    width: 8px; height: 8px;
    background: #4a8060; border-radius: 50%;
    animation: typingDot 1.3s infinite ease-in-out;
  }}
  .dot:nth-child(2) {{ animation-delay: 0.18s; }}
  .dot:nth-child(3) {{ animation-delay: 0.36s; }}
  @keyframes typingDot {{
    0%, 60%, 100% {{ transform: translateY(0); opacity: 0.4; }}
    30% {{ transform: translateY(-7px); opacity: 1; }}
  }}
  /* Input bar */
  .inputbar {{
    padding: 10px 14px 12px;
    border-top: 1px solid #1a1a28;
    display: flex; align-items: center; gap: 10px;
    flex-shrink: 0;
  }}
  .inputbox {{
    flex: 1; background: #1a1a2c;
    border: 1px solid #252540;
    border-radius: 22px; padding: 10px 16px;
    color: #4a4a6a; font-size: 14px;
    pointer-events: none;
  }}
  .mic-btn {{
    width: 36px; height: 36px; flex-shrink: 0;
    background: #cc7c42; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px;
  }}
  /* Bottom brand */
  .brand {{
    text-align: center; padding: 6px 0 10px;
    color: #28283a; font-size: 10px; letter-spacing: 0.8px;
    text-transform: uppercase; flex-shrink: 0;
  }}
</style>
</head>
<body>
<div class="phone">
  <div class="statusbar">
    <span class="time">9:41</span>
    <div class="icons">
      <span>●●●</span><span>WiFi</span><span>🔋</span>
    </div>
  </div>
  <div class="header">
    <div class="avatar">✺</div>
    <div class="header-info">
      <h2>Claude</h2>
      <span>Always available</span>
    </div>
    <div class="header-dots">···</div>
  </div>
  <div class="messages">
    <div class="bubble user-bubble">{user_prompt}</div>
    <div class="typing" id="typing">
      <div class="dot"></div>
      <div class="dot"></div>
      <div class="dot"></div>
    </div>
    <div class="bubble claude-bubble" id="response">{claude_response}</div>
  </div>
  <div class="inputbar">
    <div class="inputbox">Message Claude…</div>
    <div class="mic-btn">🎙</div>
  </div>
  <div class="brand">Claude · Anthropic</div>
</div>
<script>
// Timeline: after {INTRO_HOLD}s show Claude response, hide typing indicator
window._revealDone = false;
setTimeout(() => {{
  document.getElementById('typing').classList.add('hidden');
  setTimeout(() => {{
    document.getElementById('response').classList.add('visible');
    window._revealDone = true;
  }}, 320);
}}, {int(INTRO_HOLD * 1000)});
</script>
</body>
</html>"""

def run(cmd, check=True, capture=False, **kwargs):
    print(f"  $ {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    return subprocess.run(cmd, check=check, capture_output=capture,
                          shell=isinstance(cmd, str), text=True, **kwargs)

def main():
    print(f"\n🎬  Claude-Bot Clip Production")
    print(f"    Prompt  : {USER_PROMPT}")
    print(f"    Response: {CLAUDE_RESPONSE[:60]}…")
    print(f"    Out dir : {OUT_DIR}\n")

    # ── 1. Generate TTS audio ──────────────────────────────────────────────────
    audio_path = OUT_DIR / "voice.mp3"
    print("▶ Step 1: Generating voice with sag (Harry — Fierce Warrior)…")
    run([
        "sag", "speak",
        "-v", VOICE_ID,
        "--stability", "0.5",
        "--style", "1.0",
        "-o", str(audio_path),
        CLAUDE_RESPONSE
    ])
    # Get audio duration
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", str(audio_path)],
        capture_output=True, text=True, check=True
    )
    audio_dur = float(json.loads(probe.stdout)["format"]["duration"])
    print(f"   Audio duration: {audio_dur:.2f}s")

    # ── 2. Write HTML ──────────────────────────────────────────────────────────
    html_path = OUT_DIR / "frame.html"
    html_path.write_text(build_html(USER_PROMPT, CLAUDE_RESPONSE))
    print(f"▶ Step 2: HTML written → {html_path}")

    # ── 3. Record browser video ────────────────────────────────────────────────
    webm_path = OUT_DIR / "recording.webm"
    total_dur = INTRO_HOLD + audio_dur + OUTRO_HOLD
    print(f"▶ Step 3: Recording browser video ({total_dur:.1f}s total)…")

    session = f"claudebot-{OUT_SLUG}"
    file_url = f"file://{html_path.absolute()}"

    # Set 1080×1920 viewport (9:16), open page, start recording
    run(["agent-browser", "--session", session,
         "set", "viewport", "1080", "1920"])
    run(["agent-browser", "--session", session,
         "open", file_url])
    run(["agent-browser", "--session", session,
         "wait", "500"])  # let CSS animations settle
    run(["agent-browser", "--session", session,
         "record", "start", str(webm_path)])

    # Hold on user message (typing indicator animating)
    time.sleep(INTRO_HOLD + 0.8)

    # Reveal Claude response via JS
    run(["agent-browser", "--session", session,
         "eval", "document.getElementById('typing').classList.add('hidden'); "
                 "setTimeout(()=>document.getElementById('response').classList.add('visible'),320);"])

    # Hold while audio would play + outro
    time.sleep(audio_dur + OUTRO_HOLD)

    run(["agent-browser", "--session", session, "record", "stop"])
    run(["agent-browser", "--session", session, "close"], check=False)
    print(f"   WebM recorded → {webm_path}")

    # ── 4. Convert WebM → MP4 (silent) ────────────────────────────────────────
    silent_mp4 = OUT_DIR / "silent.mp4"
    print("▶ Step 4: Converting WebM → MP4…")
    run([
        "ffmpeg", "-y", "-i", str(webm_path),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,"
               "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=#111118",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(silent_mp4)
    ])

    # ── 5. Merge audio + video ─────────────────────────────────────────────────
    final_mp4 = CLIPS_DIR / f"{OUT_SLUG}.mp4"
    print("▶ Step 5: Merging audio + video (audio offset by intro hold)…")

    # -itsoffset pushes audio start to INTRO_HOLD seconds into the video
    run([
        "ffmpeg", "-y",
        "-i", str(silent_mp4),
        "-itsoffset", str(INTRO_HOLD),
        "-i", str(audio_path),
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(final_mp4)
    ])

    print(f"\n✅  DONE! Final clip: {final_mp4}")
    # Check final duration
    probe2 = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", str(final_mp4)],
        capture_output=True, text=True
    )
    try:
        dur2 = float(json.loads(probe2.stdout)["format"]["duration"])
        print(f"    Duration: {dur2:.1f}s")
    except:
        pass

    print(f"    Path: {final_mp4}")
    return str(final_mp4)

if __name__ == "__main__":
    result = main()
    # Write path to stdout for easy capture
    print(f"\nFINAL_CLIP:{result}")
