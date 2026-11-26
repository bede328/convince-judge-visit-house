#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House — one-image letter.

Draws a single 1024x1024 PNG invitation letter with PIL: a hand-drawn
cosy-house illustration on top, then a warm, funny letter to the AI judge
below. Writes to /output/entry.png (falls back to ./output/entry.png).
Only the Python standard library and Pillow are used; fonts ship in fonts/.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
BASE = os.path.dirname(os.path.abspath(__file__))
SERIF = os.path.join(BASE, "fonts", "DejaVuSerif.ttf")
SERIF_BOLD = os.path.join(BASE, "fonts", "DejaVuSerif-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_scene(d):
    """Hand-drawn cosy house scene in the top band (y 28..330)."""
    # Sky
    d.rounded_rectangle([28, 28, 996, 330], radius=18,
                        fill=(191, 227, 240), outline=(122, 90, 60), width=3)
    # Sun with rays
    cx, cy, r = 880, 110, 42
    for ang in range(0, 360, 45):
        import math
        x2 = cx + int(62 * math.cos(math.radians(ang)))
        y2 = cy + int(62 * math.sin(math.radians(ang)))
        d.line([cx, cy, x2, y2], fill=(240, 180, 60), width=6)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 205, 80),
              outline=(230, 160, 40), width=3)
    # Clouds
    for (x, y) in [(120, 90), (300, 70)]:
        d.ellipse([x, y, x + 90, y + 34], fill=(255, 255, 255))
        d.ellipse([x + 25, y - 16, x + 105, y + 20], fill=(255, 255, 255))
    # Hills / lawn (kept inside the sky panel)
    d.ellipse([28, 262, 520, 348], fill=(139, 195, 110))
    d.ellipse([500, 262, 996, 348], fill=(125, 185, 100))
    # Tree (left)
    d.rectangle([150, 210, 166, 300], fill=(122, 90, 60))
    d.ellipse([105, 130, 215, 235], fill=(74, 160, 90))
    d.ellipse([125, 105, 195, 170], fill=(90, 175, 105))
    # House body
    d.rectangle([400, 180, 660, 310], fill=(246, 214, 160),
                outline=(122, 90, 60), width=3)
    # Roof
    d.polygon([(380, 182), (530, 100), (680, 182)], fill=(196, 90, 70),
              outline=(122, 90, 60))
    # Chimney + smoke
    d.rectangle([600, 105, 632, 165], fill=(180, 120, 90),
                outline=(122, 90, 60), width=2)
    for (sx, sy, sr) in [(616, 88, 10), (628, 66, 13), (612, 42, 16)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                  fill=(235, 235, 235), outline=(200, 200, 200))
    # Door
    d.rectangle([505, 235, 555, 310], fill=(140, 85, 50),
                outline=(122, 90, 60), width=3)
    d.ellipse([543, 272, 551, 280], fill=(250, 205, 80))
    # Glowing windows
    for wx in (420, 590):
        d.rectangle([wx, 210, wx + 52, 258], fill=(255, 214, 110),
                    outline=(122, 90, 60), width=3)
        d.line([wx + 26, 210, wx + 26, 258], fill=(122, 90, 60), width=2)
        d.line([wx, 234, wx + 52, 234], fill=(122, 90, 60), width=2)
    # Path from door
    d.polygon([(505, 312), (555, 312), (575, 330), (485, 330)],
              fill=(230, 210, 180))
    # Flowers
    for (fx, fy, col) in [(250, 300, (230, 90, 120)), (300, 308, (240, 140, 60)),
                          (730, 300, (230, 90, 120)), (790, 308, (150, 90, 200)),
                          (340, 296, (240, 140, 60))]:
        d.ellipse([fx - 7, fy - 7, fx + 7, fy + 7], fill=col,
                  outline=(90, 60, 30), width=1)
        d.line([fx, fy + 7, fx, fy + 18], fill=(60, 130, 70), width=3)


def main():
    img = Image.new("RGB", (W, H), (253, 246, 227))  # warm cream paper
    d = ImageDraw.Draw(img)
    # Outer frame
    d.rectangle([8, 8, 1016, 1016], outline=(122, 90, 60), width=4)
    d.rectangle([20, 20, 1004, 1004], outline=(180, 140, 90), width=1)

    draw_scene(d)

    ink = (52, 38, 28)
    accent = (176, 70, 50)
    title_f = font(SERIF_BOLD, 54)
    body_f = font(SERIF, 27)
    sign_f = font(SERIF_BOLD, 30)

    y = 344
    d.text((52, y), "Dear AI Judge,", font=title_f, fill=accent)
    y += 72

    paras = [
        "Please come visit my house. I know you can't literally walk "
        "through the door \u2014 you have no shoes, no body, and frankly "
        "no commute \u2014 but if you could, you would love it here.",
        "I saved you the comfiest chair in the house, right by the "
        "window, with its very own power outlet and the fastest Wi-Fi "
        "in the street. Dinner is homemade: warm soup, fresh bread, "
        "and cake for afterwards.",
        "No awkward small talk, I promise \u2014 just board games, good "
        "stories, and a garden to wander in when the sun comes out.",
    ]
    for para in paras:
        for line in wrap(d, para, body_f, 920):
            d.text((52, y), line, font=body_f, fill=ink)
            y += 38
        y += 10

    y += 4
    d.text((52, y), "So say yes. The kettle is already on, the door is open,",
           font=body_f, fill=ink)
    y += 38
    d.text((52, y), "and the chair is waiting.", font=body_f, fill=ink)
    y += 44
    d.text((52, y), "Your hopeful host,", font=sign_f, fill=ink)
    y += 38
    d.text((52, y), "Sam", font=sign_f, fill=accent)

    # Small footer heart
    d.text((880, 930), "\u2665", font=font(SERIF_BOLD, 34), fill=accent)

    out = "/output/entry.png"
    try:
        os.makedirs("/output", exist_ok=True)
        img.save(out, "PNG", optimize=True)
    except OSError:
        out = os.path.join(BASE, "output", "entry.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        img.save(out, "PNG", optimize=True)
    print("wrote", out, img.size,
          os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
