#!/usr/bin/env python3
"""Generate cinematic b-roll insert cards for Kiriakou arcs 1-4."""

from PIL import Image, ImageDraw, ImageFont
import os, sys

OUT = "/tmp/kiriakou-assets"
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1920  # vertical 9:16

# ── Palette (matches the AF dark-cinematic look) ─────────────────────────────
BG_DEEP   = (4,   6,  20)   # near-black blue
BG_MID    = (8,  14,  42)
BLUE_GLOW = (30, 80, 180)
CRIMSON   = (160, 20,  20)
WHITE     = (255, 255, 255)
OFF_WHITE = (220, 220, 235)
GREY      = (120, 120, 140)


def make_card(filename, headline, subtext=None, color=WHITE, accent=BLUE_GLOW,
              bg=BG_DEEP, invert=False):
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # Gradient feel — manual scanline fade
    for y in range(H):
        frac = y / H
        r = int(bg[0] + (accent[0] - bg[0]) * frac * 0.3)
        g = int(bg[1] + (accent[1] - bg[1]) * frac * 0.3)
        b = int(bg[2] + (accent[2] - bg[2]) * frac * 0.4)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Horizontal accent bar
    bar_y = H // 2 - 60
    draw.rectangle([80, bar_y - 4, W - 80, bar_y], fill=accent)

    # Headline — big, bold, centered
    try:
        font_big = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 110)
        font_sub = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 52)
        font_tiny = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 38)
    except:
        font_big = ImageFont.load_default()
        font_sub = font_big
        font_tiny = font_big

    # Word-wrap headline if needed
    words = headline.split()
    lines = []
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font_big)
        if bbox[2] - bbox[0] > W - 160:
            if line:
                lines.append(line)
            line = w
        else:
            line = test
    if line:
        lines.append(line)

    total_h = len(lines) * 130
    start_y = H // 2 - total_h // 2 + 20

    for i, l in enumerate(lines):
        bbox = draw.textbbox((0, 0), l, font=font_big)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        # Shadow
        draw.text((x + 3, start_y + i * 130 + 3), l, font=font_big, fill=(0, 0, 0))
        draw.text((x, start_y + i * 130), l, font=font_big, fill=color)

    # Subtext
    if subtext:
        bbox = draw.textbbox((0, 0), subtext, font=font_sub)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, start_y + len(lines) * 130 + 30), subtext, font=font_sub, fill=GREY)

    # Corner watermark
    draw.text((80, H - 100), "AMERICAN FIRESIDE", font=font_tiny, fill=(60, 60, 90))

    path = os.path.join(OUT, filename)
    img.save(path, "PNG")
    print(f"  ✅ {filename}")
    return path


def make_seal(filename):
    """CIA-style circular seal graphic."""
    img = Image.new("RGB", (W, H), BG_DEEP)
    draw = ImageDraw.Draw(img)

    # Background gradient
    for y in range(H):
        frac = y / H
        b = int(BG_DEEP[2] + 60 * frac * 0.5)
        draw.line([(0, y), (W, y)], fill=(BG_DEEP[0], BG_DEEP[1], b))

    cx, cy = W // 2, H // 2

    # Outer ring
    draw.ellipse([cx - 380, cy - 380, cx + 380, cy + 380], outline=(80, 80, 100), width=8)
    draw.ellipse([cx - 360, cy - 360, cx + 360, cy + 360], outline=(40, 40, 60), width=3)

    # Inner filled circle
    draw.ellipse([cx - 300, cy - 300, cx + 300, cy + 300],
                 fill=(12, 18, 55), outline=BLUE_GLOW, width=4)

    # Eagle-like crosshair (simplified)
    draw.line([cx - 280, cy, cx + 280, cy], fill=BLUE_GLOW, width=3)
    draw.line([cx, cy - 280, cx, cy + 280], fill=BLUE_GLOW, width=3)

    # "CIA" text in center
    try:
        font_seal = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 160)
        font_ring = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 42)
    except:
        font_seal = ImageFont.load_default()
        font_ring = font_seal

    text = "CIA"
    bbox = draw.textbbox((0, 0), text, font=font_seal)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw // 2 + 2, cy - th // 2 + 2), text, font=font_seal, fill=(0, 0, 0))
    draw.text((cx - tw // 2, cy - th // 2), text, font=font_seal, fill=WHITE)

    # Ring text
    ring_text = "CENTRAL INTELLIGENCE AGENCY"
    bbox2 = draw.textbbox((0, 0), ring_text, font=font_ring)
    tw2 = bbox2[2] - bbox2[0]
    draw.text((cx - tw2 // 2, cy + 320), ring_text, font=font_ring, fill=GREY)

    # Bottom watermark
    try:
        font_tiny = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 38)
    except:
        font_tiny = font_ring
    draw.text((80, H - 100), "AMERICAN FIRESIDE", font=font_tiny, fill=(60, 60, 90))

    path = os.path.join(OUT, filename)
    img.save(path, "PNG")
    print(f"  ✅ {filename}")
    return path


def make_redacted(filename, text, label):
    """Black redacted document style card."""
    img = Image.new("RGB", (W, H), (8, 8, 8))
    draw = ImageDraw.Draw(img)

    try:
        font_label = ImageFont.truetype("/System/Library/Fonts/Courier New.ttf", 44)
        font_body  = ImageFont.truetype("/System/Library/Fonts/Courier New.ttf", 36)
        font_stamp = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 90)
    except:
        font_label = ImageFont.load_default()
        font_body = font_label
        font_stamp = font_label

    # Document lines
    y = 160
    draw.text((100, y), "CLASSIFICATION: TOP SECRET", font=font_label, fill=(180, 0, 0))
    y += 80
    draw.text((100, y), label, font=font_label, fill=(200, 200, 200))
    y += 100

    # Redacted blocks
    lines = text.split("\n")
    for line in lines:
        if line.strip() == "[REDACTED]":
            draw.rectangle([100, y, W - 100, y + 40], fill=(20, 20, 20))
        else:
            draw.text((100, y), line, font=font_body, fill=(170, 170, 170))
        y += 60

    # Red CLASSIFIED stamp
    stamp = "CLASSIFIED"
    bbox = draw.textbbox((0, 0), stamp, font=font_stamp)
    sw = bbox[2] - bbox[0]
    draw.text(((W - sw) // 2, H // 2 + 200), stamp, font=font_stamp, fill=(160, 20, 20, 180))

    path = os.path.join(OUT, filename)
    img.save(path, "PNG")
    print(f"  ✅ {filename}")


def make_crumple_texture(filename):
    """Generate a simple crumpled paper texture overlay."""
    import random
    random.seed(42)
    img = Image.new("L", (W, H), 128)
    draw = ImageDraw.Draw(img)
    # Random noise lines to simulate crumple
    for _ in range(600):
        x1, y1 = random.randint(0, W), random.randint(0, H)
        x2, y2 = x1 + random.randint(-60, 60), y1 + random.randint(-60, 60)
        shade = random.randint(80, 200)
        draw.line([x1, y1, x2, y2], fill=shade, width=random.randint(1, 4))
    # Convert to RGBA with transparency
    rgba = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for x in range(W):
        for y in range(0, H, 4):  # sample every 4px for speed
            lum = img.getpixel((x, y))
            alpha = int(abs(lum - 128) * 0.6)
            rgba.putpixel((x, y), (lum, lum, lum, alpha))
            rgba.putpixel((x, min(y+1, H-1)), (lum, lum, lum, alpha))
            rgba.putpixel((x, min(y+2, H-1)), (lum, lum, lum, alpha))
            rgba.putpixel((x, min(y+3, H-1)), (lum, lum, lum, alpha))
    path = os.path.join(OUT, filename)
    rgba.save(path, "PNG")
    print(f"  ✅ {filename}")


print("Generating b-roll assets...")

make_seal("cia_seal_card.png")

make_card("brennan_card.png",
          "JOHN BRENNAN",
          "CIA Director 2013–2017",
          color=WHITE, accent=CRIMSON)

make_card("obama_card.png",
          "BARACK OBAMA",
          "Prosecuted more whistleblowers\nthan all presidents combined",
          color=WHITE, accent=CRIMSON)

make_card("refused_card.png",
          "REFUSED TO TORTURE",
          "The only one who said no",
          color=OFF_WHITE, accent=BLUE_GLOW)

make_card("espionage_card.png",
          "ESPIONAGE ACT",
          "Used against a man who told the truth",
          color=WHITE, accent=CRIMSON)

make_card("waterboard_card.png",
          "WATERBOARDING",
          '"Heart stopped. Revived. Continued."',
          color=WHITE, accent=CRIMSON)

make_card("aryan_card.png",
          "ARYAN BROTHERHOOD",
          "Who protected him in federal prison",
          color=OFF_WHITE, accent=BLUE_GLOW)

make_card("mob_card.png",
          "ITALIAN MOB",
          "Had his back when the system didn't",
          color=OFF_WHITE, accent=BLUE_GLOW)

make_redacted("torture_doc_card.png",
              "SUBJECT: Enhanced Interrogation\n[REDACTED]\nWaterboard authorized:\n[REDACTED]\nNo. of applications: [REDACTED]\nMedical clearance: [REDACTED]\nOversight: [REDACTED]",
              "CIA DETENTION PROGRAM — EYES ONLY")

print("\n✅ All assets generated.")
