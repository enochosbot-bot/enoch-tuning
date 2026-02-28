#!/usr/bin/env python3
"""
Kiriakou Arcs 1-4 — Cinematic Style Pass
Applies: dark blue grade, b-roll card inserts, impactful text overlays
"""

import subprocess, os, tempfile, shutil, sys

FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
CLIPS  = os.path.expanduser("~/Desktop/Kiriakou-Clips/clips")
ASSETS = "/tmp/kiriakou-assets"
OUT    = os.path.expanduser("~/Desktop/Kiriakou-Clips/styled")
TMP    = "/tmp/kiriakou-style-tmp"

os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

# ── Color grade filter chain ──────────────────────────────────────────────────
# Blue push, crush blacks, slight contrast boost, desaturate slightly
GRADE = (
    "curves=r='0/0 0.12/0.01 1/0.86':g='0/0 0.10/0.02 1/0.81':b='0/0 0.08/0.18 1/1.0',"
    "eq=contrast=1.18:brightness=-0.04:saturation=0.88"
)

# ── Drawtext helper ───────────────────────────────────────────────────────────
def dt(text, start, end, y_pos="(h*0.82)", size=68, color="white", stroke=4):
    """Return a drawtext filter segment enabled between start-end seconds."""
    safe = text.replace("'", "\\'").replace(":", "\\:")
    return (
        f"drawtext=text='{safe}'"
        f":fontfile=/System/Library/Fonts/HelveticaNeue.ttc"
        f":fontsize={size}:fontcolor={color}"
        f":borderw={stroke}:bordercolor=black"
        f":x=(w-text_w)/2:y={y_pos}"
        f":enable='between(t\\,{start}\\,{end})'"
    )


def run(cmd, label=""):
    """Run ffmpeg command, print progress label."""
    print(f"  → {label}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ❌ ERROR:\n{result.stderr[-800:]}")
        return False
    return True


def card_to_clip(png, duration=1.5, suffix=""):
    """Convert a PNG card to a short video clip with the same grade + vertical format."""
    out = os.path.join(TMP, f"card_{suffix}.mp4")
    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-i", png,
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=decrease,"
               f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,{GRADE}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duration),
        "-movflags", "+faststart",
        out
    ]
    run(cmd, f"card clip → {os.path.basename(png)}")
    return out


def extract_seg(src, t_start, t_end, suffix, text_filters=None):
    """Extract a segment from src with color grade + optional text overlays."""
    out = os.path.join(TMP, f"seg_{suffix}.mp4")
    duration = t_end - t_start

    vf_chain = GRADE
    if text_filters:
        vf_chain = GRADE + "," + ",".join(text_filters)

    cmd = [
        FFMPEG, "-y",
        "-ss", str(t_start), "-t", str(duration),
        "-i", src,
        "-vf", vf_chain,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        out
    ]
    run(cmd, f"segment {suffix} ({t_start:.0f}s–{t_end:.0f}s)")
    return out


def concat_clips(clips, outfile):
    """Concat a list of clips using ffmpeg concat demuxer."""
    list_path = os.path.join(TMP, "concat_list.txt")
    with open(list_path, "w") as f:
        for c in clips:
            f.write(f"file '{c}'\n")

    cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        "-movflags", "+faststart",
        outfile
    ]
    run(cmd, f"concat → {os.path.basename(outfile)}")


# ─────────────────────────────────────────────────────────────────────────────
# ARC 1 — The Decision (240s)
# Kiriakou is asked to run the torture program, refuses, mentor warns him
# ─────────────────────────────────────────────────────────────────────────────
def process_arc1():
    src = os.path.join(CLIPS, "arc1_the_decision.mp4")
    print("\n━━━ ARC 1 — THE DECISION ━━━")

    segs = [
        # (t_start, t_end, card_after, card_duration, text_overlays_during_seg)
        # Seg 1: 0-50s, then cut to CIA seal
        extract_seg(src, 0, 50, "a1_s1", [
            dt("CENTRAL INTELLIGENCE AGENCY", 5, 20, y_pos="h*0.10", size=54, color="white"),
        ]),
        card_to_clip(f"{ASSETS}/cia_seal_card.png", 1.5, "a1_seal"),

        # Seg 2: 50-120s — the ask/refusal moment, then cut to REFUSED card
        extract_seg(src, 50, 120, "a1_s2"),
        card_to_clip(f"{ASSETS}/refused_card.png", 1.8, "a1_refused"),

        # Seg 3: 120-180s — mentor warning, then cut to torture doc
        extract_seg(src, 120, 180, "a1_s3"),
        card_to_clip(f"{ASSETS}/torture_doc_card.png", 1.5, "a1_torture"),

        # Seg 4: 180-240s — irony/punchline
        extract_seg(src, 180, 240, "a1_s4", [
            dt("THE ONLY ONE WHO SAID NO", 30, 55, y_pos="h*0.10", size=60, color="white"),
        ]),
    ]
    concat_clips(segs, f"{OUT}/arc1_styled.mp4")
    print("  ✅ arc1_styled.mp4")


# ─────────────────────────────────────────────────────────────────────────────
# ARC 2 — The Retaliation (223s)
# ABC interview → espionage charges, Brennan/Obama connection
# ─────────────────────────────────────────────────────────────────────────────
def process_arc2():
    src = os.path.join(CLIPS, "arc2_the_retaliation.mp4")
    print("\n━━━ ARC 2 — THE RETALIATION ━━━")

    segs = [
        # Seg 1: 0-55s — ABC interview setup
        extract_seg(src, 0, 55, "a2_s1", [
            dt("ABC NEWS INTERVIEW", 3, 18, y_pos="h*0.10", size=54),
        ]),
        card_to_clip(f"{ASSETS}/espionage_card.png", 1.8, "a2_esp"),

        # Seg 2: 55-130s — charges dropped, then Brennan card
        extract_seg(src, 55, 130, "a2_s2"),
        card_to_clip(f"{ASSETS}/brennan_card.png", 1.5, "a2_brennan"),

        # Seg 3: 130-180s, then Obama card
        extract_seg(src, 130, 180, "a2_s3"),
        card_to_clip(f"{ASSETS}/obama_card.png", 1.5, "a2_obama"),

        # Seg 4: 180-223s — punchline
        extract_seg(src, 180, 223, "a2_s4", [
            dt("TRUTH IS ESPIONAGE", 15, 38, y_pos="h*0.10", size=60, color="white"),
        ]),
    ]
    concat_clips(segs, f"{OUT}/arc2_styled.mp4")
    print("  ✅ arc2_styled.mp4")


# ─────────────────────────────────────────────────────────────────────────────
# ARC 3 — The Mob (190s)
# Prison, Aryan Brotherhood offers protection, Italian mob backs him instead
# ─────────────────────────────────────────────────────────────────────────────
def process_arc3():
    src = os.path.join(CLIPS, "arc3_the_mob.mp4")
    print("\n━━━ ARC 3 — THE MOB ━━━")

    segs = [
        # Seg 1: 0-40s — prison intro
        extract_seg(src, 0, 40, "a3_s1", [
            dt("FEDERAL PRISON", 3, 18, y_pos="h*0.10", size=54),
        ]),
        card_to_clip(f"{ASSETS}/aryan_card.png", 1.8, "a3_aryan"),

        # Seg 2: 40-100s — Aryan Brotherhood incident
        extract_seg(src, 40, 100, "a3_s2"),
        card_to_clip(f"{ASSETS}/mob_card.png", 1.5, "a3_mob"),

        # Seg 3: 100-190s — Italian mob protection story
        extract_seg(src, 100, 190, "a3_s3", [
            dt("THE MOB HAD HIS BACK", 20, 45, y_pos="h*0.10", size=58, color="white"),
        ]),
    ]
    concat_clips(segs, f"{OUT}/arc3_styled.mp4")
    print("  ✅ arc3_styled.mp4")


# ─────────────────────────────────────────────────────────────────────────────
# ARC 4 — Heart Stopped (70s)
# Cold cells, waterboarding, heart stopped, revived to torture more
# ─────────────────────────────────────────────────────────────────────────────
def process_arc4():
    src = os.path.join(CLIPS, "arc4_heart_stopped.mp4")
    print("\n━━━ ARC 4 — HEART STOPPED ━━━")

    segs = [
        # Seg 1: 0-22s — cold cells / setup
        extract_seg(src, 0, 22, "a4_s1", [
            dt("ENHANCED INTERROGATION", 3, 18, y_pos="h*0.10", size=50),
        ]),
        card_to_clip(f"{ASSETS}/waterboard_card.png", 2.0, "a4_water"),

        # Seg 2: 22-50s — waterboarding, heart stops
        extract_seg(src, 22, 50, "a4_s2"),
        card_to_clip(f"{ASSETS}/torture_doc_card.png", 1.5, "a4_doc"),

        # Seg 3: 50-70s — revived to continue
        extract_seg(src, 50, 70, "a4_s3", [
            dt("REVIVED. CONTINUED.", 5, 18, y_pos="h*0.10", size=64,
               color="white"),
        ]),
    ]
    concat_clips(segs, f"{OUT}/arc4_styled.mp4")
    print("  ✅ arc4_styled.mp4")


# ── Run all ───────────────────────────────────────────────────────────────────
print("╔═══════════════════════════════════════════════════╗")
print("║   Kiriakou Style Pass — Arcs 1-4                 ║")
print("╚═══════════════════════════════════════════════════╝")

process_arc1()
process_arc2()
process_arc3()
process_arc4()

print("\n╔═══════════════════════════════════════════════════╗")
print("║   ALL DONE                                        ║")
print("╚═══════════════════════════════════════════════════╝")
print(f"\nOutput: {OUT}")
import subprocess as sp
sp.run(["ls", "-lh", OUT])
