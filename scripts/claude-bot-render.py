#!/usr/bin/env python3
"""
claude-bot-render.py — Generate "American Claude Bot" content clips
Renders a fake Claude chat UI, animates the response, records it.

Usage:
  python3 scripts/claude-bot-render.py --prompt "remind me to buy milk"
  python3 scripts/claude-bot-render.py --prompt "remind me to buy milk" --mode military
  python3 scripts/claude-bot-render.py --batch  # runs all prompts from prompt-bank.json
"""

import argparse, json, os, subprocess, sys, time, textwrap
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
CLIPS_DIR = WORKSPACE / "clips" / "claude-bot"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)

# ── SYSTEM PROMPTS BY MODE ────────────────────────────────────────────────────
MODES = {
    "military": """You are Claude, but you respond to EVERY request — no matter how mundane — 
like a hyper-patriotic American special operations commander. 
Use military jargon, combat metaphors, and intense tactical language for completely normal tasks.
Keep responses SHORT (2-4 sentences max). Never break character. Always enthusiastic.""",

    "lawyer": """You are Claude, but you respond to every request like an aggressive American trial lawyer 
making an opening statement to a jury. Dramatic, emphatic, uses legal jargon for mundane tasks.
SHORT responses only (2-4 sentences). Never break character.""",

    "surgeon": """You are Claude, but you respond to every request like you're performing emergency surgery. 
Everything is life-or-death urgent. Use medical jargon for completely normal everyday tasks.
SHORT responses (2-4 sentences). High urgency always.""",

    "wallstreet": """You are Claude, but you respond to every request like a hyped-up Wall Street trader 
on the floor during a market crash. Everything is a trade, a position, a play.
SHORT responses (2-4 sentences). Pure alpha energy.""",

    "coach": """You are Claude, but you respond to every request like an intense American football coach 
giving a halftime speech when the team is down 40 points. Everything is about heart, grit, and winning.
SHORT responses (2-4 sentences). Never give up energy.""",
}

# ── PROMPT BANK ───────────────────────────────────────────────────────────────
PROMPT_BANK = [
    {"prompt": "remind me to buy milk", "mode": "military"},
    {"prompt": "help me write a grocery list", "mode": "military"},
    {"prompt": "what's the weather like today?", "mode": "military"},
    {"prompt": "I need to schedule a dentist appointment", "mode": "military"},
    {"prompt": "help me pick a movie to watch tonight", "mode": "military"},
    {"prompt": "write me a shopping list for tacos", "mode": "military"},
    {"prompt": "I need to clean my room", "mode": "military"},
    {"prompt": "help me write a thank you note", "mode": "military"},
    {"prompt": "I need to walk my dog", "mode": "military"},
    {"prompt": "help me make a bedtime routine", "mode": "military"},
    {"prompt": "I need to do my taxes", "mode": "lawyer"},
    {"prompt": "help me respond to this email", "mode": "lawyer"},
    {"prompt": "should I text my ex back?", "mode": "lawyer"},
    {"prompt": "help me return this Amazon package", "mode": "lawyer"},
    {"prompt": "I need to apologize to my friend", "mode": "lawyer"},
    {"prompt": "I have a headache", "mode": "surgeon"},
    {"prompt": "I'm a little tired today", "mode": "surgeon"},
    {"prompt": "I need to make breakfast", "mode": "surgeon"},
    {"prompt": "I'm thinking of getting a haircut", "mode": "surgeon"},
    {"prompt": "help me pick a restaurant for dinner", "mode": "surgeon"},
    {"prompt": "should I buy this $12 t-shirt?", "mode": "wallstreet"},
    {"prompt": "help me save more money", "mode": "wallstreet"},
    {"prompt": "I need to split the dinner bill", "mode": "wallstreet"},
    {"prompt": "help me plan my weekend", "mode": "coach"},
    {"prompt": "I don't feel like going to the gym today", "mode": "coach"},
    {"prompt": "help me stay motivated at work", "mode": "coach"},
    {"prompt": "I'm having a bad day", "mode": "coach"},
    {"prompt": "I need to wake up earlier", "mode": "coach"},
]

def get_claude_response(prompt: str, mode: str) -> str:
    """Call Claude API with the mode system prompt."""
    import urllib.request
    
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        result = subprocess.run(
            ["openclaw", "config", "get", "providers.anthropic.apiKey"],
            capture_output=True, text=True
        )
        api_key = result.stdout.strip().strip('"')
    
    system = MODES.get(mode, MODES["military"])
    payload = json.dumps({
        "model": "claude-haiku-4-5",
        "max_tokens": 150,
        "system": system,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["content"][0]["text"].strip()

def render_html(user_prompt: str, claude_response: str) -> str:
    """Generate HTML for the chat UI."""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #1a1a2e;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }}
  .phone {{
    width: 390px;
    height: 844px;
    background: #0f0f1a;
    border-radius: 40px;
    padding: 60px 0 40px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: 0 40px 80px rgba(0,0,0,0.6);
    border: 1px solid #2a2a3e;
  }}
  .header {{
    padding: 0 20px 16px;
    border-bottom: 1px solid #1e1e30;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .avatar {{
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #cc785c, #d4966e);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
  }}
  .header-text h2 {{
    color: #e8d5c4;
    font-size: 15px;
    font-weight: 600;
  }}
  .header-text span {{
    color: #6b6b8a;
    font-size: 12px;
  }}
  .messages {{
    flex: 1;
    padding: 20px 16px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 16px;
    justify-content: flex-end;
  }}
  .bubble {{
    max-width: 82%;
    padding: 12px 16px;
    border-radius: 18px;
    font-size: 15px;
    line-height: 1.5;
    animation: fadeIn 0.3s ease;
  }}
  .user-bubble {{
    background: #2a2a4a;
    color: #c8c8e8;
    align-self: flex-end;
    border-bottom-right-radius: 4px;
  }}
  .claude-bubble {{
    background: linear-gradient(135deg, #1a2a1a, #1e3020);
    border: 1px solid #2a4a2a;
    color: #d4f0d4;
    align-self: flex-start;
    border-bottom-left-radius: 4px;
  }}
  .typing {{ 
    display: flex; gap: 4px; padding: 8px 4px;
    align-self: flex-start;
  }}
  .dot {{
    width: 8px; height: 8px;
    background: #6b8a6b;
    border-radius: 50%;
    animation: bounce 1.2s infinite;
  }}
  .dot:nth-child(2) {{ animation-delay: 0.2s; }}
  .dot:nth-child(3) {{ animation-delay: 0.4s; }}
  @keyframes bounce {{
    0%, 60%, 100% {{ transform: translateY(0); }}
    30% {{ transform: translateY(-8px); }}
  }}
  @keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}
  .input-bar {{
    padding: 12px 16px;
    border-top: 1px solid #1e1e30;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .input-box {{
    flex: 1;
    background: #1e1e30;
    border: 1px solid #2a2a42;
    border-radius: 22px;
    padding: 10px 16px;
    color: #8888aa;
    font-size: 14px;
  }}
  .brand {{
    text-align: center;
    padding: 8px;
    color: #3a3a5a;
    font-size: 11px;
    letter-spacing: 0.5px;
  }}
</style>
</head>
<body>
<div class="phone">
  <div class="header">
    <div class="avatar">✺</div>
    <div class="header-text">
      <h2>Claude</h2>
      <span>AI Assistant</span>
    </div>
  </div>
  <div class="messages">
    <div class="bubble user-bubble">{user_prompt}</div>
    <div class="bubble claude-bubble" id="response" style="opacity:0">{claude_response}</div>
  </div>
  <div class="input-bar">
    <div class="input-box">Message Claude...</div>
  </div>
  <div class="brand">Claude by Anthropic</div>
</div>
<script>
setTimeout(() => {{
  document.getElementById('response').style.opacity = '1';
  document.getElementById('response').style.animation = 'fadeIn 0.4s ease';
}}, 800);
</script>
</body>
</html>"""

def make_clip(user_prompt: str, claude_response: str, out_path: Path) -> Path:
    """Render HTML → screenshots → video via ffmpeg."""
    import tempfile
    
    html_content = render_html(user_prompt, claude_response)
    html_file = out_path.parent / "frame.html"
    html_file.write_text(html_content)
    
    frames_dir = out_path.parent / "frames"
    frames_dir.mkdir(exist_ok=True)
    
    # Take screenshots at different states using agent-browser
    url = f"file://{html_file.absolute()}"
    
    # Frame 1-15: user message only (0.5s)
    subprocess.run(["agent-browser", "open", url], capture_output=True)
    for i in range(8):
        subprocess.run(["agent-browser", "screenshot", str(frames_dir / f"frame_{i:04d}.png")], capture_output=True)
    
    # Frame 16-30: with Claude response visible
    # Inject JS to show response
    subprocess.run(["agent-browser", "eval", 
                    "document.getElementById('response').style.opacity='1'"], capture_output=True)
    time.sleep(0.3)
    for i in range(8, 90):
        subprocess.run(["agent-browser", "screenshot", str(frames_dir / f"frame_{i:04d}.png")], capture_output=True)
    
    subprocess.run(["agent-browser", "close"], capture_output=True)
    
    # Stitch frames into video with ffmpeg
    subprocess.run([
        "ffmpeg", "-y", "-framerate", "15",
        "-pattern_type", "glob", "-i", str(frames_dir / "frame_*.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:-1:-1:color=black",
        str(out_path)
    ], capture_output=True, check=True)
    
    return out_path

def main():
    parser = argparse.ArgumentParser()
    src = parser.add_mutually_exclusive_group()
    src.add_argument("--prompt", help="Single user prompt")
    src.add_argument("--batch", action="store_true", help="Run all prompts from bank")
    parser.add_argument("--mode", default="military", choices=list(MODES.keys()))
    parser.add_argument("--text-only", action="store_true", help="Just print response, no video")
    args = parser.parse_args()
    
    prompts = []
    if args.batch:
        prompts = PROMPT_BANK
    elif args.prompt:
        prompts = [{"prompt": args.prompt, "mode": args.mode}]
    else:
        # Default demo
        prompts = [{"prompt": "remind me to buy milk", "mode": "military"}]
    
    for item in prompts:
        prompt = item["prompt"]
        mode = item.get("mode", args.mode)
        print(f"\n[claude-bot] Prompt: \"{prompt}\" | Mode: {mode}")
        
        response = get_claude_response(prompt, mode)
        print(f"[claude-bot] Response: {response}")
        
        if args.text_only:
            continue
        
        slug = prompt[:30].replace(" ", "-").replace("?", "").replace("'", "")
        ts = datetime.now().strftime("%H%M%S")
        out_dir = CLIPS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}-{slug}-{ts}"
        out_dir.mkdir(parents=True, exist_ok=True)
        
        clip_path = out_dir / "clip.mp4"
        print(f"[claude-bot] Rendering clip → {clip_path}")
        make_clip(prompt, response, clip_path)
        print(f"[claude-bot] ✅ Done: {clip_path}")
        
        # Save metadata
        (out_dir / "meta.json").write_text(json.dumps({
            "prompt": prompt, "mode": mode, "response": response,
            "clip": str(clip_path)
        }, indent=2))

if __name__ == "__main__":
    main()
