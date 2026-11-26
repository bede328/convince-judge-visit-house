#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House — one-image letter.

Draws a single 1024x1024 PNG invitation letter: a hand-drawn cosy-house
illustration on top, then a warm, funny letter to the AI judge below.
Writes to /output/entry.png (falls back to ./output/entry.png).

PURE PYTHON STANDARD LIBRARY ONLY — no Pillow, no third-party imports.
The server sandbox runs `python3 -P -s main.py` in a bare python3.13
image, so this file ships its own tiny PNG encoder (zlib + struct), a
small raster layer (rects, rounded rects, ellipses, polygons, thick
lines) and an embedded 5x7 bitmap font scaled up for legibility.
Output is deterministic: same bytes on every run.
"""
import math
import os
import struct
import zlib

W = H = 1024
BASE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Embedded 5x7 bitmap font.
# Each glyph is 7 rows; '#' is an ink pixel. Most glyphs are 5 columns
# wide; the em-dash is 9 columns wide. Lowercase letters use the full
# 7-row cell (x-height rows 2..6, descenders reach row 6).
# ---------------------------------------------------------------------------
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "a": (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#..#", ".#...", "#####", ".#...", ".#...", ".#..."),
    "g": (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    "j": ("....#", ".....", "..##.", "...#.", "...#.", "#..#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", "####.", "#...#", "#...#", "####.", "#....", "#...."),
    "q": (".....", ".####", "#...#", "#...#", ".####", "....#", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "#####", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", "#...#", "#...#", "#...#", ".####", "....#", ".###."),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", ".##.."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "—": (".........", ".........", ".........", "#########",
          ".........", ".........", "........."),
    "♥": (".#.#.", "#####", "#####", "#####", ".###.", "..#..", "....."),
}


def glyph_width(ch):
    rows = FONT.get(ch)
    return len(rows[0]) if rows else 5


def spacing_px(scale):
    return max(1, scale // 3)


def text_width(text, scale, bold=False):
    w = 0
    for ch in text:
        w += glyph_width(ch) * scale + spacing_px(scale)
    if w:
        w -= spacing_px(scale)
    if bold:
        w += 2
    return w


def wrap(text, scale, max_w, bold=False):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if text_width(trial, scale, bold) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------------------
# Tiny raster canvas (RGB bytearray) + PNG encoder (zlib + struct only).
# Coordinates are inclusive, matching the old Pillow code's boxes.
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.pix = bytearray(bytes(bg) * (w * h))

    def fill_rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w - 1, x1)
        y1 = min(self.h - 1, y1)
        if x1 < x0 or y1 < y0:
            return
        row = bytes(color) * (x1 - x0 + 1)
        for y in range(y0, y1 + 1):
            base = (y * self.w + x0) * 3
            self.pix[base:base + len(row)] = row

    def rect_outline(self, x0, y0, x1, y1, color, width=1):
        self.fill_rect(x0, y0, x1, y0 + width - 1, color)
        self.fill_rect(x0, y1 - width + 1, x1, y1, color)
        self.fill_rect(x0, y0, x0 + width - 1, y1, color)
        self.fill_rect(x1 - width + 1, y0, x1, y1, color)

    def _ellipse_span(self, cx, cy, rx, ry):
        """Yield (y, x_left, x_right) scanlines of a filled ellipse."""
        if rx <= 0 or ry <= 0:
            return
        ry_i = int(round(ry))
        for dy in range(-ry_i, ry_i + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * math.sqrt(t)) if t > 0 else 0
            yield int(round(cy)) + dy, cx - dx, cx + dx

    def ellipse(self, x0, y0, x1, y1, color):
        cx = (x0 + x1) / 2.0
        cy = (y0 + y1) / 2.0
        rx = (x1 - x0) / 2.0
        ry = (y1 - y0) / 2.0
        for y, xl, xr in self._ellipse_span(cx, cy, rx, ry):
            self.fill_rect(int(xl), y, int(xr), y, color)

    def ellipse_outline(self, x0, y0, x1, y1, fill, outline, width=1):
        self.ellipse(x0, y0, x1, y1, outline)
        self.ellipse(x0 + width, y0 + width, x1 - width, y1 - width, fill)

    def circle(self, cx, cy, r, color):
        self.ellipse(cx - r, cy - r, cx + r, cy + r, color)

    def _rounded_spans(self, x0, y0, x1, y1, radius):
        r = max(0, min(radius, (x1 - x0) // 2, (y1 - y0) // 2))
        cx0, cx1 = x0 + r, x1 - r
        cy0, cy1 = y0 + r, y1 - r
        for y in range(y0, y1 + 1):
            if y < cy0:
                dy = cy0 - y
                dx = int(math.sqrt(max(0, r * r - dy * dy))) if r else 0
                yield y, cx0 - dx, cx1 + dx
            elif y > cy1:
                dy = y - cy1
                dx = int(math.sqrt(max(0, r * r - dy * dy))) if r else 0
                yield y, cx0 - dx, cx1 + dx
            else:
                yield y, x0, x1

    def rounded_rect(self, x0, y0, x1, y1, radius, fill, outline=None,
                     width=3):
        if outline is not None:
            for y, xl, xr in self._rounded_spans(x0, y0, x1, y1, radius):
                self.fill_rect(xl, y, xr, y, outline)
            inner = max(0, radius - width)
            for y, xl, xr in self._rounded_spans(
                    x0 + width, y0 + width, x1 - width, y1 - width, inner):
                self.fill_rect(xl, y, xr, y, fill)
        else:
            for y, xl, xr in self._rounded_spans(x0, y0, x1, y1, radius):
                self.fill_rect(xl, y, xr, y, fill)

    def polygon(self, points, color):
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if y0 == y1:
                    continue
                lo, hi = (y0, y1) if y0 < y1 else (y1, y0)
                if lo <= y < hi or (y == max(ys) and y == hi):
                    t = (y + 0.5 - y0) / float(y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill_rect(int(math.ceil(xs[i])), y,
                               int(math.floor(xs[i + 1])), y, color)

    def thick_line(self, x0, y0, x1, y1, color, width=1):
        r = max(0, width // 2)
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            t = i / float(steps)
            x = int(round(x0 + (x1 - x0) * t))
            y = int(round(y0 + (y1 - y0) * t))
            if r:
                self.circle(x, y, r, color)
            else:
                self.fill_rect(x, y, x, y, color)

    def text(self, x, y, s, color, scale, bold=False):
        for dx in ((0, 2) if bold else (0,)):
            cx = x + dx
            for ch in s:
                rows = FONT.get(ch)
                if rows:
                    gw = len(rows[0])
                    for ri, row in enumerate(rows):
                        for ci, bit in enumerate(row):
                            if bit == "#":
                                self.fill_rect(
                                    cx + ci * scale, y + ri * scale,
                                    cx + (ci + 1) * scale - 1,
                                    y + (ri + 1) * scale - 1, color)
                    cx += gw * scale + spacing_px(scale)
                else:
                    cx += 5 * scale + spacing_px(scale)


def _png_chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(path, canvas):
    w, h = canvas.w, canvas.h
    raw = bytearray()
    row_bytes = w * 3
    for y in range(h):
        raw.append(0)  # filter: None
        raw += canvas.pix[y * row_bytes:(y + 1) * row_bytes]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + _png_chunk(b"IHDR", ihdr)
           + _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _png_chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------------------
# Scene + letter (same design, layout and wording as the Pillow version).
# ---------------------------------------------------------------------------
BROWN = (122, 90, 60)
INK = (52, 38, 28)
ACCENT = (176, 70, 50)


def draw_scene(c):
    """Hand-drawn cosy house scene in the top band (y 28..330)."""
    # Sky
    c.rounded_rect(28, 28, 996, 330, 18, (191, 227, 240),
                   outline=BROWN, width=3)
    # Sun with rays
    cx, cy, r = 880, 110, 42
    for ang in range(0, 360, 45):
        x2 = cx + int(62 * math.cos(math.radians(ang)))
        y2 = cy + int(62 * math.sin(math.radians(ang)))
        c.thick_line(cx, cy, x2, y2, (240, 180, 60), width=6)
    c.ellipse_outline(cx - r, cy - r, cx + r, cy + r,
                      (250, 205, 80), (230, 160, 40), width=3)
    # Clouds
    for (x, y) in [(120, 90), (300, 70)]:
        c.ellipse(x, y, x + 90, y + 34, (255, 255, 255))
        c.ellipse(x + 25, y - 16, x + 105, y + 20, (255, 255, 255))
    # Hills / lawn (kept inside the sky panel)
    c.ellipse(28, 262, 520, 348, (139, 195, 110))
    c.ellipse(500, 262, 996, 348, (125, 185, 100))
    # Tree (left)
    c.fill_rect(150, 210, 166, 300, BROWN)
    c.ellipse(105, 130, 215, 235, (74, 160, 90))
    c.ellipse(125, 105, 195, 170, (90, 175, 105))
    # House body
    c.fill_rect(400, 180, 660, 310, (246, 214, 160))
    c.rect_outline(400, 180, 660, 310, BROWN, width=3)
    # Roof
    c.polygon([(380, 182), (530, 100), (680, 182)], (196, 90, 70))
    # Roof outline: two thick edges (base is hidden behind the house body)
    c.thick_line(380, 182, 530, 100, BROWN, width=3)
    c.thick_line(530, 100, 680, 182, BROWN, width=3)
    # Chimney + smoke
    c.fill_rect(600, 105, 632, 165, (180, 120, 90))
    c.rect_outline(600, 105, 632, 165, BROWN, width=2)
    for (sx, sy, sr) in [(616, 88, 10), (628, 66, 13), (612, 42, 16)]:
        c.ellipse_outline(sx - sr, sy - sr, sx + sr, sy + sr,
                          (235, 235, 235), (200, 200, 200), width=1)
    # Door
    c.fill_rect(505, 235, 555, 310, (140, 85, 50))
    c.rect_outline(505, 235, 555, 310, BROWN, width=3)
    c.ellipse(543, 272, 551, 280, (250, 205, 80))
    # Glowing windows
    for wx in (420, 590):
        c.fill_rect(wx, 210, wx + 52, 258, (255, 214, 110))
        c.rect_outline(wx, 210, wx + 52, 258, BROWN, width=3)
        c.thick_line(wx + 26, 210, wx + 26, 258, BROWN, width=2)
        c.thick_line(wx, 234, wx + 52, 234, BROWN, width=2)
    # Path from door
    c.polygon([(505, 312), (555, 312), (575, 330), (485, 330)],
              (230, 210, 180))
    # Flowers
    for (fx, fy, col) in [(250, 300, (230, 90, 120)), (300, 308, (240, 140, 60)),
                          (730, 300, (230, 90, 120)), (790, 308, (150, 90, 200)),
                          (340, 296, (240, 140, 60))]:
        c.ellipse_outline(fx - 7, fy - 7, fx + 7, fy + 7, col, (90, 60, 30),
                          width=1)
        c.thick_line(fx, fy + 7, fx, fy + 18, (60, 130, 70), width=3)


def main():
    c = Canvas(W, H, (253, 246, 227))  # warm cream paper
    # Outer frame
    c.rect_outline(8, 8, 1016, 1016, BROWN, width=4)
    c.rect_outline(20, 20, 1004, 1004, (180, 140, 90), width=1)

    draw_scene(c)

    y = 344
    c.text(52, y, "Dear AI Judge,", ACCENT, scale=6, bold=True)
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
    total_lines = 0
    for para in paras:
        lines = wrap(para, 3, 920)
        total_lines += len(lines)
        for line in lines:
            c.text(52, y, line, INK, scale=3)
            y += 30
        y += 8

    y += 4
    c.text(52, y, "So say yes. The kettle is already on, the door is open,",
           INK, scale=3)
    y += 30
    c.text(52, y, "and the chair is waiting.", INK, scale=3)
    y += 38
    c.text(52, y, "Your hopeful host,", INK, scale=4, bold=True)
    y += 36
    c.text(52, y, "Sam", ACCENT, scale=4, bold=True)
    y += 28

    # Small footer heart
    c.text(880, 930, "\u2665", ACCENT, scale=5)

    out = "/output/entry.png"
    try:
        os.makedirs("/output", exist_ok=True)
        size = write_png(out, c)
    except OSError:
        out = os.path.join(BASE, "output", "entry.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        size = write_png(out, c)
    print("wrote", out, (W, H), size, "bytes;",
          total_lines, "body lines; last text y =", y)


if __name__ == "__main__":
    main()
