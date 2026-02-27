#!/usr/bin/env python3
"""Hailuo AI video generation via MiniMax API.
Usage: python3 hailuo-video.py "prompt text" [--image URL] [--duration 6] [--resolution 1080P]
"""
import os, sys, time, requests, argparse

API_KEY = os.environ.get("MINIMAX_API_KEY", "")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media")

def create_task(prompt, image_url=None, duration=6, resolution="1080P"):
    url = "https://api.minimax.io/v1/video_generation"
    payload = {
        "prompt": prompt,
        "model": "MiniMax-Hailuo-2.3",
        "duration": duration,
        "resolution": resolution,
    }
    if image_url:
        payload["first_frame_image"] = image_url
    
    resp = requests.post(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    data = resp.json()
    if "task_id" not in data:
        print(f"Error: {data}")
        sys.exit(1)
    return data["task_id"]

def poll_task(task_id, timeout=600):
    url = f"https://api.minimax.io/v1/query/video_generation?task_id={task_id}"
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status", "Unknown")
        print(f"  Status: {status}")
        
        if status == "Success":
            return data.get("file_id")
        elif status in ("Failed", "Error"):
            print(f"Task failed: {data}")
            sys.exit(1)
        
        time.sleep(10)
    
    print("Timeout waiting for video generation")
    sys.exit(1)

def download_video(file_id, prompt):
    url = f"https://api.minimax.io/v1/files/retrieve?file_id={file_id}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    
    download_url = data.get("file", {}).get("download_url")
    if not download_url:
        print(f"No download URL: {data}")
        sys.exit(1)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Sanitize filename from prompt
    safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in prompt[:50]).strip().replace(" ", "-")
    filename = f"hailuo-{safe_name}-{int(time.time())}.mp4"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    print(f"Downloading to {filepath}...")
    video = requests.get(download_url)
    with open(filepath, "wb") as f:
        f.write(video.content)
    
    print(f"Done! Saved: {filepath}")
    return filepath

def main():
    parser = argparse.ArgumentParser(description="Generate video with Hailuo AI")
    parser.add_argument("prompt", help="Text description of the video")
    parser.add_argument("--image", help="First frame image URL (image-to-video mode)")
    parser.add_argument("--duration", type=int, default=6, help="Duration in seconds (default: 6)")
    parser.add_argument("--resolution", default="1080P", help="Resolution (default: 1080P)")
    args = parser.parse_args()
    
    if not API_KEY:
        print("Error: MINIMAX_API_KEY not set. Get one at https://platform.minimax.io")
        sys.exit(1)
    
    print(f"Generating video: {args.prompt}")
    task_id = create_task(args.prompt, args.image, args.duration, args.resolution)
    print(f"Task ID: {task_id}")
    
    file_id = poll_task(task_id)
    filepath = download_video(file_id, args.prompt)
    return filepath

if __name__ == "__main__":
    main()
