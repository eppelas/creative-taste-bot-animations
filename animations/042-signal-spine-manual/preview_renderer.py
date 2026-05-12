#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


BG = (5, 7, 11)
CYAN = (122, 214, 239)
MAGENTA = (255, 90, 135)
AMBER = (244, 194, 134)
ACID = (216, 241, 95)
TEXT = (213, 219, 223)
MUTED = (124, 138, 145)


def hex_alpha(color: tuple[int, int, int], alpha: int) -> tuple[int, int, int, int]:
    return color[0], color[1], color[2], alpha


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], radius: int, fill, outline, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def make_gradient(width: int, height: int) -> Image.Image:
    image = Image.new("RGBA", (width, height), BG + (255,))
    px = image.load()
    for y in range(height):
        t = y / max(1, height - 1)
        r = int(10 - 8 * t)
        g = int(14 - 10 * t)
        b = int(18 - 13 * t)
        for x in range(width):
            px[x, y] = (max(2, r), max(3, g), max(5, b), 255)
    return image


def draw_grid(draw: ImageDraw.ImageDraw, width: int, height: int, step: int) -> None:
    color = (90, 118, 127, 24)
    for x in range(0, width, step):
      draw.line((x, 0, x, height), fill=color, width=1)
    for y in range(0, height, step):
      draw.line((0, y, width, y), fill=color, width=1)


def draw_noise(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    rng = random.Random(42)
    width, height = image.size
    for _ in range(3000):
        x = rng.randrange(width)
        y = rng.randrange(height)
        alpha = rng.randrange(10, 26)
        draw.point((x, y), fill=(255, 255, 255, alpha))


def draw_spine(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    cx = int(width * 0.38)
    top = int(height * 0.17)
    bottom = int(height * 0.74)
    panel_h = [54, 62, 52, 58, 56, 64, 56]
    panel_w = [190, 236, 170, 248, 188, 262, 198]
    colors = [CYAN, AMBER, MAGENTA, CYAN, ACID, AMBER, CYAN]

    axis_points = []
    for idx in range(8):
        t = idx / 7
        y = top + (bottom - top) * t
        x = cx + int(math.sin(t * math.pi * 3.1) * 20)
        axis_points.append((x, y))
    draw.line(axis_points, fill=(160, 206, 220, 72), width=4, joint="curve")
    draw.line(axis_points, fill=hex_alpha(CYAN, 185), width=9, joint="curve")

    for idx, (pw, ph, tint) in enumerate(zip(panel_w, panel_h, colors)):
        y = top + idx * 96
        x = cx - pw // 2 + int(math.sin(idx * 0.9) * 10)
        rounded_panel(
            draw,
            (x, y, x + pw, y + ph),
            radius=min(22, ph // 2),
            fill=(8, 12, 16, 220),
            outline=(132, 173, 187, 68),
            width=2,
        )
        rounded_panel(
            draw,
            (x + 14, y + 12, x + pw - 14, y + ph - 12),
            radius=min(18, max(10, (ph - 24) // 2)),
            fill=(255, 255, 255, 4),
            outline=hex_alpha(tint, 84),
            width=2,
        )
        draw.line((x + 24, y + ph / 2, x + pw - 24, y + ph / 2), fill=hex_alpha(tint, 188), width=3)
        draw.line((x - 118, y + ph / 2, x, y + ph / 2), fill=hex_alpha(tint, 88), width=2)
        draw.line((x + pw, y + ph / 2, x + pw + 118, y + ph / 2), fill=hex_alpha(tint, 88), width=2)

    bead_y = top - 26
    draw.ellipse((cx - 22, bead_y - 10, cx - 12, bead_y), fill=CYAN)
    draw.ellipse((cx - 5, bead_y - 24, cx + 7, bead_y - 12), fill=MAGENTA)
    draw.ellipse((cx + 14, bead_y - 10, cx + 24, bead_y), fill=AMBER)


def draw_side_panels(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    left_specs = [(58, 170, 184, 118, CYAN), (32, 372, 220, 134, AMBER), (74, 620, 196, 126, MAGENTA)]
    right_specs = [(width - 286, 170, 184, 118, CYAN), (width - 266, 372, 220, 134, AMBER), (width - 298, 620, 196, 126, MAGENTA)]
    for x, y, w, h, tint in left_specs + right_specs:
        rounded_panel(draw, (x, y, x + w, y + h), radius=18, fill=(7, 10, 13, 196), outline=(130, 171, 183, 50), width=2)
        rounded_panel(draw, (x + 12, y + 12, x + w - 12, y + h - 12), radius=12, fill=(255, 255, 255, 4), outline=hex_alpha(tint, 78), width=1)
        draw.line((x + 18, y + 40, x + w - 18, y + 40), fill=hex_alpha(tint, 160), width=2)
        for idx in range(4):
            yy = y + 62 + idx * 15
            points = []
            for step in range(7):
                px = x + 18 + step * ((w - 36) / 6)
                py = yy + math.sin(step * 0.85 + idx * 0.6) * (7 + idx * 2)
                points.append((px, py))
            color = tint if idx % 2 == 0 else ACID
            draw.line(points, fill=hex_alpha(color, 140 if idx == 1 else 88), width=2)


def draw_crosshair(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    cx = int(width * 0.38)
    cy = int(height * 0.5)
    r = 76
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(216, 241, 95, 86), width=2)
    draw.line((cx - r - 22, cy, cx + r + 22, cy), fill=(122, 214, 239, 64), width=2)
    draw.line((cx, cy - r - 22, cx, cy + r + 22), fill=(255, 90, 135, 64), width=2)


def draw_metrics(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    stack_x = int(width * 0.65)
    card_w = int(width * 0.28)
    cards = [
        (stack_x, 110, card_w, 114, "ALIGNMENT LOG"),
        (stack_x, 246, card_w, 224, "LIVE READOUTS"),
        (stack_x, 492, card_w, 186, "LEGEND"),
    ]
    for x, y, w, h, title in cards:
        rounded_panel(draw, (x, y, x + w, y + h), radius=24, fill=(9, 13, 18, 206), outline=(118, 161, 175, 46), width=2)
        draw.text((x + 18, y + 16), title, fill=(213, 219, 223, 196))
    for idx, (label, tint, value) in enumerate((("SHEAR", CYAN, 41), ("PULSE", MAGENTA, 58), ("BIAS", AMBER, 33), ("GATE", ACID, 72))):
        y = 290 + idx * 38
        draw.text((stack_x + 20, y), label, fill=(124, 138, 145, 220))
        track = (stack_x + 95, y + 8, stack_x + 260, y + 18)
        rounded_panel(draw, track, 999, (107, 126, 136, 44), None, 1)
        fill_w = (track[2] - track[0]) * value / 100
        rounded_panel(draw, (track[0], track[1], track[0] + fill_w, track[3]), 999, hex_alpha(tint, 180), None, 1)
        draw.text((stack_x + 275, y), f"{value:02d}", fill=(213, 219, 223, 200))


def draw_review(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    y = height - 212
    gap = 16
    total_w = width - 60
    card_w = (total_w - gap * 2) / 3
    titles = ["IDEA", "INTERACTION", "NEXT"]
    for idx, title in enumerate(titles):
        x = 20 + idx * (card_w + gap)
        rounded_panel(draw, (x, y, x + card_w, y + 172), radius=24, fill=(9, 13, 18, 206), outline=(118, 161, 175, 46), width=2)
        draw.text((x + 18, y + 16), title, fill=(213, 219, 223, 196))
        draw.text((x + 18, y + 54), "review note embedded on page", fill=(183, 192, 197, 168))


def render(output: Path, width: int, height: int) -> None:
    image = make_gradient(width, height)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    draw_grid(draw, width, height, max(30, width // 28))
    draw_spine(draw, width, height)
    draw_side_panels(draw, width, height)
    draw_crosshair(draw, width, height)
    draw_metrics(draw, width, height)
    draw_review(draw, width, height)

    glow = overlay.filter(ImageFilter.GaussianBlur(radius=12))
    image.alpha_composite(glow)
    image.alpha_composite(overlay)
    draw_noise(image)

    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output, "PNG")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()
    render(args.output, args.width, args.height)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
