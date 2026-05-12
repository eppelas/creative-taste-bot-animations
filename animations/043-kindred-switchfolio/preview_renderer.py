#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def rounded(draw: ImageDraw.ImageDraw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def load_font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Avenir Next.ttc" if not bold else "/System/Library/Fonts/Supplemental/Avenir Next.ttc",
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Supplemental/Menlo.ttc",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_body(draw: ImageDraw.ImageDraw, cx: float, cy: float):
    ink = (35, 69, 87, 180)
    shell = (244, 237, 226, 245)
    pale = (255, 248, 238, 230)

    outer = [
        (cx, cy - 190),
        (cx + 86, cy - 170),
        (cx + 98, cy - 52),
        (cx + 74, cy + 38),
        (cx + 56, cy + 146),
        (cx, cy + 188),
        (cx - 56, cy + 146),
        (cx - 74, cy + 38),
        (cx - 98, cy - 52),
        (cx - 86, cy - 170),
    ]
    draw.polygon(outer, fill=shell, outline=ink)
    for top, width in [(-110, 118), (-8, 102), (100, 88)]:
        draw.ellipse((cx - width / 2, cy + top - 28, cx + width / 2, cy + top + 28), fill=pale, outline=(35, 69, 87, 80))

    blush = (240, 140, 117, 78)
    draw.ellipse((cx - 58, cy - 58, cx - 16, cy - 34), fill=blush)
    draw.ellipse((cx + 16, cy - 58, cx + 58, cy - 34), fill=blush)

    supports = [
        [(cx - 44, cy + 150), (cx - 112, cy + 244), (cx - 148, cy + 316)],
        [(cx + 44, cy + 150), (cx + 112, cy + 244), (cx + 148, cy + 316)],
        [(cx - 14, cy + 168), (cx - 44, cy + 254), (cx - 74, cy + 332)],
        [(cx + 14, cy + 168), (cx + 44, cy + 254), (cx + 74, cy + 332)],
    ]
    for points in supports:
        draw.line(points, fill=(35, 69, 87, 180), width=7)

    for dx, dy, radius, fill in [(-18, -108, 12, (35, 69, 87, 255)), (18, -108, 12, (35, 69, 87, 255)), (0, -72, 8, (240, 140, 117, 255))]:
        draw.ellipse((cx + dx - radius, cy + dy - radius, cx + dx + radius, cy + dy + radius), fill=fill)

    draw.arc((cx - 28, cy - 18, cx + 28, cy + 22), start=10, end=170, fill=(35, 69, 87, 215), width=4)
    for index in range(5):
        x = cx - 42 + index * 21
        draw.line((x, cy - 152, x + (index - 2) * 3, cy + 138), fill=(35, 69, 87, 70), width=2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    width = args.width
    height = args.height
    image = Image.new("RGBA", (width, height), (248, 241, 231, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    for y in range(height):
      t = y / max(1, height - 1)
      r = int(248 * (1 - t) + 235 * t)
      g = int(241 * (1 - t) + 223 * t)
      b = int(231 * (1 - t) + 204 * t)
      draw.line((0, y, width, y), fill=(r, g, b, 255))

    for cx, cy, color, radius in [
        (190, 170, (103, 198, 218, 28), 170),
        (860, 190, (240, 140, 117, 28), 180),
        (580, 1160, (213, 218, 87, 24), 210),
    ]:
        glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow, "RGBA")
        gdraw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color)
        glow = glow.filter(ImageFilter.GaussianBlur(40))
        image.alpha_composite(glow)

    noise = ImageDraw.Draw(image, "RGBA")
    for index in range(1200):
        x = (index * 137) % width
        y = (index * 79) % height
        alpha = 8 + (index % 6) * 3
        noise.point((x, y), fill=(22, 32, 42, alpha))

    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow, "RGBA")
    board = (120, 220, width - 120, height - 180)
    rounded(sdraw, board, 40, fill=(112, 90, 57, 40))
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    image.alpha_composite(shadow, (0, 18))

    draw = ImageDraw.Draw(image, "RGBA")
    rounded(draw, board, 40, fill=(245, 237, 224, 255), outline=(35, 69, 87, 26), width=2)
    rounded(draw, (board[0] + 16, board[1] + 16, board[2] - 16, board[3] - 16), 28, outline=(35, 69, 87, 22), width=2)
    draw.line((board[0] + 30, board[1] + 70, board[2] - 30, board[1] + 70), fill=(35, 69, 87, 22), width=2)
    draw.line((board[0] + 30, board[1] + 108, board[2] - 30, board[1] + 108), fill=(35, 69, 87, 22), width=2)

    tabs = [
        ((board[0] + 36, board[1] + 24, board[0] + 198, board[1] + 56), (223, 238, 237, 255)),
        ((board[2] - 214, board[1] + 24, board[2] - 124, board[1] + 56), (244, 215, 202, 255)),
        ((board[2] - 114, board[1] + 24, board[2] - 26, board[1] + 56), (233, 237, 178, 255)),
    ]
    for box, fill in tabs:
        rounded(draw, box, 14, fill=fill, outline=(35, 69, 87, 28), width=2)

    mono = load_font(16)
    mono_small = load_font(13)
    title_font = load_font(44, bold=True)
    body_font = load_font(20)
    body_small = load_font(18)

    draw.text((board[0] + 52, board[1] + 33), "KINDRED SWITCHFOLIO", fill=(35, 69, 87, 180), font=mono)
    draw.text((board[2] - 194, board[1] + 33), "BODY LAW", fill=(35, 69, 87, 180), font=mono)
    draw.text((board[2] - 102, board[1] + 33), "BRACE", fill=(35, 69, 87, 220), font=mono)

    chamber_w = 178
    chamber_h = 128
    chamber_gap = 20
    left_x = board[0] + 38
    right_x = board[2] - chamber_w - 38
    top_y = board[1] + 156

    for idx in range(8):
        side_x = left_x if idx < 4 else right_x
        band = idx % 4
        cy = top_y + band * (chamber_h + chamber_gap)
        rounded(draw, (side_x, cy, side_x + chamber_w, cy + chamber_h), 24, fill=(251, 247, 240, 235), outline=(35, 69, 87, 26), width=2)
        accent = (103, 198, 218, 56) if idx < 4 else (240, 140, 117, 52)
        rounded(draw, (side_x + 14, cy + 14, side_x + chamber_w - 14, cy + 40), 12, fill=accent)
        points = []
        for step in range(5):
            px = side_x + 18 + step * ((chamber_w - 36) / 4)
            py = cy + chamber_h * 0.7 + math.sin(step * 0.8 + idx) * 8
            points.append((px, py))
        draw.line(points, fill=(35, 69, 87, 110), width=3)
        draw.text((side_x + 16, cy + chamber_h - 20), f"CHAMBER 0{idx + 1}", fill=(35, 69, 87, 150), font=mono_small)

    center_x = width / 2
    center_y = 715
    for lane in range(6):
        color = (35, 69, 87, 66) if lane % 3 == 0 else (103, 198, 218, 110) if lane % 3 == 1 else (240, 140, 117, 102)
        width_line = 4 if lane in (2, 3) else 2
        points = []
        for step in range(24):
            t = step / 23
            x = board[0] + 212 + t * (board[2] - board[0] - 424)
            sway = math.sin(t * math.pi * 2 + lane * 0.6) * (32 + lane * 4)
            y = center_y + math.sin(t * math.pi + lane * 0.5) * 118 - 220 + t * 440 + sway * 0.18
            points.append((x, y))
        draw.line(points, fill=color, width=width_line)

    for idx in range(4):
        y = board[1] + 170 + idx * ((board[3] - board[1] - 320) / 3)
        for step in range(24):
            x0 = board[0] + 182 + step * 22
            draw.line((x0, y, x0 + 8, y), fill=(35, 69, 87, 38), width=1)

    for index in range(34):
        lane = index % 6
        side = -1 if index % 2 else 1
        ring = 78 + lane * 28
        angle = 0.5 + index * 0.48
        x = center_x + math.cos(angle) * ring + side * (30 + lane * 16)
        y = center_y + math.sin(angle * 1.6) * (40 + lane * 16)
        radius = 3 + (index % 3)
        fill = (103, 198, 218, 215) if index % 4 == 0 else (240, 140, 117, 195) if index % 4 == 1 else (213, 218, 87, 185) if index % 4 == 2 else (35, 69, 87, 110)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill)

    draw_body(draw, center_x, center_y)

    for copy, x, y in [
        ("bilateral support", board[0] + 256, board[3] - 130),
        ("bead routes", board[0] + 596, board[1] + 252),
        ("care seam", board[0] + 160, board[1] + 528),
        ("face tile", board[0] + 458, board[1] + 380),
    ]:
        draw.text((x, y), copy, fill=(35, 69, 87, 132), font=mono_small)
        draw.line((x - 8, y + 18, x + 52, y + 18), fill=(35, 69, 87, 54), width=2)

    note_box = (38, 34, 556, 304)
    rounded(draw, note_box, 28, fill=(255, 251, 246, 214), outline=(35, 69, 87, 24), width=2)
    draw.text((58, 56), "Code Animation Study #043", fill=(35, 69, 87, 128), font=mono_small)
    draw.text((58, 82), "Kindred\nSwitchfolio", fill=(23, 38, 48, 255), font=title_font, spacing=2)
    draw.text((58, 178), "A pale moving field manual where one rooted\nnonhuman body, side chambers, and specimen-style\nannotations share the same illustrated interface page.", fill=(23, 38, 48, 190), font=body_font, spacing=6)
    draw.text((58, 258), "Move across the folio to bend seams and retune\nthe same body law.", fill=(23, 38, 48, 160), font=body_small, spacing=5)

    control_box = (700, 34, 1042, 232)
    rounded(draw, control_box, 28, fill=(255, 251, 246, 214), outline=(35, 69, 87, 24), width=2)
    draw.text((752, 56), "SWITCHFOLIO CONTROLS", fill=(35, 69, 87, 128), font=mono_small)
    pills = [
        ((752, 92, 846, 128), (205, 235, 239, 255), "BRACE"),
        ((856, 92, 948, 128), (246, 220, 214, 255), "WEAVE"),
        ((956, 92, 1020, 128), (233, 237, 178, 255), "CHORUS"),
    ]
    for box, fill, label in pills:
        rounded(draw, box, 18, fill=fill, outline=(35, 69, 87, 28), width=2)
        draw.text((box[0] + 18, box[1] + 10), label, fill=(23, 38, 48, 230), font=mono_small)
    draw.text((724, 148), "The controls only retune visible body stance,\nbead routes, chamber openness, and annotation\nrhythm.", fill=(23, 38, 48, 164), font=body_small, spacing=5)

    image = image.convert("RGB")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output, quality=95)
    print(f"preview_renderer {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
