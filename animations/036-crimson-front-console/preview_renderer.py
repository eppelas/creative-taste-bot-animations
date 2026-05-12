#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


BG_TOP = (9, 11, 18)
BG_BOTTOM = (5, 6, 10)
TEXT = (247, 239, 231)
MUTED = (188, 179, 170)
CRIMSON = (255, 81, 103)
EMBER = (255, 155, 109)
CYAN = (125, 218, 244)
ACID = (221, 255, 101)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def add_glow(base: Image.Image, cx: float, cy: float, radius: float, color: tuple[int, int, int], alpha: int) -> Image.Image:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color + (alpha,))
    return Image.alpha_composite(base, overlay.filter(ImageFilter.GaussianBlur(radius=radius * 0.34)))


def rounded(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], radius: float, fill: tuple[int, int, int, int], outline: tuple[int, int, int, int], width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_scene(width: int, height: int) -> Image.Image:
    image = Image.new("RGBA", (width, height), BG_BOTTOM + (255,))
    draw = ImageDraw.Draw(image, "RGBA")

    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(round(lerp(BG_TOP[i], BG_BOTTOM[i], t)) for i in range(3)) + (255,)
        draw.line((0, y, width, y), fill=color)

    image = add_glow(image, width * 0.18, height * 0.14, min(width, height) * 0.22, CRIMSON, 32)
    image = add_glow(image, width * 0.82, height * 0.16, min(width, height) * 0.24, CYAN, 24)
    image = add_glow(image, width * 0.56, height * 0.86, min(width, height) * 0.18, EMBER, 18)
    draw = ImageDraw.Draw(image, "RGBA")

    shell = (24, 24, width - 24, height - 24)
    rounded(draw, shell, 30, (6, 8, 12, 212), (255, 226, 204, 34))
    rounded(draw, (36, 36, width - 36, height - 36), 24, (255, 255, 255, 5), (255, 255, 255, 12))

    for step in range(0, width, 80):
        draw.line((step, 24, step, height - 24), fill=(255, 255, 255, 7), width=1)
    for step in range(0, height, 80):
        draw.line((24, step, width - 24, step), fill=(255, 255, 255, 7), width=1)

    top_left = (52, 50, width * 0.68, 208)
    top_right = (width * 0.71, 50, width - 52, 208)
    left_col = (52, 224, 250, height * 0.72)
    main_panel = (266, 224, width - 266, height * 0.72)
    right_col = (width - 250, 224, width - 52, height * 0.72)
    bottom = (52, height * 0.75, width - 52, height - 66)

    panel_fill = (12, 15, 22, 196)
    panel_outline = (255, 226, 204, 24)
    soft_fill = (255, 255, 255, 8)

    for box, radius in (
        (top_left, 24),
        (top_right, 24),
        (left_col, 24),
        (main_panel, 24),
        (right_col, 24),
        (bottom, 24),
    ):
        rounded(draw, box, radius, panel_fill, panel_outline)

    # Title panel
    draw.text((76, 74), "CODE ANIMATION STUDY #036", fill=MUTED + (180,))
    draw.text((76, 104), "Crimson Front Console", fill=TEXT + (240,))
    draw.text((76, 146), "A real crimson forecast interface with structural storm weather,", fill=TEXT + (172,))
    draw.text((76, 168), "live panes, relay strips, and browser-native pressure logic.", fill=TEXT + (172,))
    for i, label in enumerate(("pointer shear", "mode retune", "live console")):
        x0 = 76 + i * 154
        rounded(draw, (x0, 186, x0 + 132, 214), 14, soft_fill, (255, 255, 255, 14))
        draw.text((x0 + 12, 194), label, fill=TEXT + (170,))

    # Top-right mode panel
    draw.text((top_right[0] + 24, 74), "FRONT MODE", fill=MUTED + (180,))
    modes = [("Survey", True), ("Shear", False), ("Bloom", False)]
    for i, (label, active) in enumerate(modes):
        x0 = top_right[0] + 22 + i * 86
        fill = (255, 255, 255, 16) if active else (255, 255, 255, 7)
        outline = (221, 255, 101, 86) if active else (255, 226, 204, 26)
        rounded(draw, (x0, 104, x0 + 72, 136), 16, fill, outline)
        draw.text((x0 + 14, 114), label, fill=TEXT + (220,))
    draw.text((top_right[0] + 24, 156), "Survey keeps the weather wide and legible.", fill=TEXT + (160,))
    draw.text((top_right[0] + 24, 176), "A design board under calm diagnostic pressure.", fill=TEXT + (160,))

    # Left column cards
    left_cards = [
        (70, 244, 232, 354, "PRESSURE WINDOWS"),
        (70, 372, 232, 504, "RELAY CHANNELS"),
        (70, 522, 232, 700, "CELL SAMPLERS"),
    ]
    for x0, y0, x1, y1, label in left_cards:
        rounded(draw, (x0, y0, x1, y1), 18, (255, 255, 255, 6), (255, 226, 204, 18))
        draw.text((x0 + 16, y0 + 16), label, fill=MUTED + (180,))

    draw.text((86, 278), "0.46", fill=TEXT + (235,))
    draw.text((86, 300), "front spread", fill=TEXT + (152,))
    draw.text((86, 328), "0.31", fill=TEXT + (235,))
    draw.text((86, 350), "lateral drift", fill=TEXT + (152,))
    rounded(draw, (86, 356, 214, 366), 8, (255, 255, 255, 12), (255, 255, 255, 0))
    rounded(draw, (86, 356, 168, 366), 8, CRIMSON + (220,), (255, 255, 255, 0))

    for idx, pct in enumerate((56, 38, 24)):
        y = 406 + idx * 30
        dot_color = CYAN if idx == 0 else EMBER if idx == 1 else ACID
        draw.ellipse((86, y + 6, 96, y + 16), fill=dot_color + (230,))
        rounded(draw, (104, y + 8, 184, y + 12), 3, (255, 255, 255, 12), (255, 255, 255, 0))
        rounded(draw, (104, y + 8, 104 + 0.8 * pct, y + 12), 3, dot_color + (210,), (255, 255, 255, 0))
        draw.text((192, y), f"{pct}%", fill=TEXT + (205,))

    for row in range(2):
        for col in range(3):
            x = 86 + col * 42
            y = 562 + row * 42
            rounded(draw, (x, y, x + 28, y + 28), 10, (255, 255, 255, 7), (255, 255, 255, 12))
            image = add_glow(image, x + 14, y + 14, 12, CRIMSON if (row + col) % 2 == 0 else CYAN, 26)
    draw = ImageDraw.Draw(image, "RGBA")

    # Main panel
    draw.text((286, 246), "STORM FRONT", fill=MUTED + (180,))
    draw.text((286, 274), "Distributed pressure map", fill=TEXT + (238,))
    draw.text((286, 306), "Pointer shear bends the basins and the console retunes", fill=TEXT + (156,))
    draw.text((286, 328), "how the field pools, rebounds, and glows.", fill=TEXT + (156,))
    draw.text((width - 432, 248), "TARGET OFFSET", fill=MUTED + (180,))
    draw.text((width - 432, 274), "12.4°", fill=TEXT + (238,))

    stage = (286, 360, width - 286, height * 0.66)
    rounded(draw, stage, 24, (8, 11, 18, 228), (255, 226, 204, 24))
    sx0, sy0, sx1, sy1 = stage
    sw = sx1 - sx0
    sh = sy1 - sy0

    for x in range(int(sx0), int(sx1), 40):
        draw.line((x, sy0, x, sy1), fill=(255, 255, 255, 8), width=1)
    for y in range(int(sy0), int(sy1), 40):
        draw.line((sx0, y, sx1, y), fill=(255, 255, 255, 8), width=1)

    center_x = sx0 + sw * 0.48
    center_y = sy0 + sh * 0.52

    seam = []
    for i in range(19):
        t = i / 18
        x = sx0 + sw * (0.08 + t * 0.84)
        y = center_y + math.sin(t * math.tau * 1.25) * sh * 0.12 + math.sin(t * 12.8) * sh * 0.02
        seam.append((x, y))

    for cx, cy, radius, color, alpha in (
        (sx0 + sw * 0.22, sy0 + sh * 0.32, 78, CRIMSON, 28),
        (sx0 + sw * 0.42, sy0 + sh * 0.55, 96, CRIMSON, 34),
        (sx0 + sw * 0.68, sy0 + sh * 0.42, 88, EMBER, 22),
        (sx0 + sw * 0.72, sy0 + sh * 0.72, 72, CYAN, 20),
    ):
        image = add_glow(image, cx, cy, radius, color, alpha)
    draw = ImageDraw.Draw(image, "RGBA")

    for lane in range(7):
        points = []
        y_base = sy0 + sh * (0.16 + lane * 0.11)
        for step in range(22):
            t = step / 21
            x = sx0 + sw * t
            y = y_base + math.sin(t * math.tau * 1.1 + lane * 0.6) * (10 + lane * 1.3)
            points.append((x, y))
        line = CRIMSON + (78,) if lane % 2 == 0 else CYAN + (46,)
        draw.line(points, fill=line, width=1)

    for blur in range(34, 2, -6):
        temp = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        tdraw = ImageDraw.Draw(temp, "RGBA")
        tdraw.line(seam, fill=CRIMSON + (18,), width=blur)
        image = Image.alpha_composite(image, temp.filter(ImageFilter.GaussianBlur(radius=blur * 0.45)))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.line(seam, fill=EMBER + (210,), width=18)
    draw.line(seam, fill=(255, 236, 214, 230), width=2)

    for i in range(len(seam) - 1):
        ax, ay = seam[i]
        bx, by = seam[i + 1]
        mx = (ax + bx) * 0.5
        my = (ay + by) * 0.5
        dx = bx - ax
        dy = by - ay
        length = math.hypot(dx, dy) or 1.0
        nx = -dy / length
        ny = dx / length
        open_amount = 10 + math.sin(i * 0.8) * 4
        color = ACID + (64,) if i % 3 == 0 else CRIMSON + (52,)
        draw.line((mx - nx * open_amount, my - ny * open_amount, mx + nx * open_amount, my + ny * open_amount), fill=color, width=1)

    for i in range(42):
        x = sx0 + ((i * 41) % int(sw))
        y = sy0 + ((i * 67 + (i % 7) * 23) % int(sh))
        size = 2 if i % 5 else 4
        color = CYAN + (190,) if i % 4 == 0 else EMBER + (180,) if i % 3 == 0 else (255, 226, 204, 40)
        draw.rounded_rectangle((x - size * 2, y - size / 2, x + size * 2, y + size / 2), radius=2, fill=color)

    rounded(draw, (sx1 - 154, sy0 + 34, sx1 - 38, sy0 + 150), 26, (8, 11, 18, 110), (255, 226, 204, 20))
    for ring in range(3):
        r = 40 - ring * 10
        draw.ellipse((sx1 - 96 - r, sy0 + 92 - r, sx1 - 96 + r, sy0 + 92 + r), outline=(255, 255, 255, 18), width=1)

    rounded(draw, (sx0 + 26, sy0 + 24, sx0 + 160, sy0 + 84), 14, (8, 11, 18, 120), (255, 226, 204, 20))
    draw.text((sx0 + 40, sy0 + 38), "18 cells", fill=TEXT + (225,))
    draw.text((sx0 + 40, sy0 + 58), "active storm pockets", fill=TEXT + (142,))
    rounded(draw, (sx0 + 36, sy1 - 86, sx0 + 176, sy1 - 28), 14, (8, 11, 18, 120), (255, 226, 204, 20))
    draw.text((sx0 + 48, sy1 - 72), "0.52", fill=TEXT + (225,))
    draw.text((sx0 + 48, sy1 - 52), "current swell", fill=TEXT + (142,))

    legend = (sx0 + 130, sy1 - 64, sx1 - 130, sy1 - 20)
    rounded(draw, legend, 14, (8, 11, 18, 120), (255, 226, 204, 20))
    draw.text((legend[0] + 16, legend[1] + 12), "cyan: cooler relay      crimson: pressure seam      amber: warm uplift", fill=TEXT + (152,))

    # Sliders under stage
    slider_y0 = sy1 + 18
    slider_w = (main_panel[2] - main_panel[0] - 48) / 3
    slider_labels = [("Cell density", "0.62", CRIMSON), ("Shear drift", "0.31", CYAN), ("Ember lift", "0.42", EMBER)]
    for i, (label, value, color) in enumerate(slider_labels):
        x0 = 286 + i * slider_w
        x1 = x0 + slider_w - 10
        rounded(draw, (x0, slider_y0, x1, slider_y0 + 76), 18, (255, 255, 255, 6), (255, 226, 204, 18))
        draw.text((x0 + 14, slider_y0 + 12), label, fill=TEXT + (160,))
        draw.text((x1 - 56, slider_y0 + 12), value, fill=TEXT + (220,))
        rounded(draw, (x0 + 14, slider_y0 + 42, x1 - 14, slider_y0 + 50), 4, (255, 255, 255, 14), (255, 255, 255, 0))
        rounded(draw, (x0 + 14, slider_y0 + 42, x0 + 14 + (x1 - x0 - 28) * 0.58, slider_y0 + 50), 4, color + (210,), (255, 255, 255, 0))

    # Right column cards
    right_cards = [
        (width - 232, 244, width - 70, 330, "FORECAST NOTES"),
        (width - 232, 348, width - 70, 470, "SIGNAL STRIPS"),
        (width - 232, 488, width - 70, 700, "USAGE NOTE"),
    ]
    for x0, y0, x1, y1, label in right_cards:
        rounded(draw, (x0, y0, x1, y1), 18, (255, 255, 255, 6), (255, 226, 204, 18))
        draw.text((x0 + 16, y0 + 16), label, fill=MUTED + (180,))

    draw.text((width - 214, 280), "relay calm", fill=TEXT + (220,))
    draw.text((width - 214, 302), "Active grammar", fill=TEXT + (142,))
    draw.text((width - 214, 328), "centered", fill=TEXT + (220,))
    draw.text((width - 214, 350), "Pointer zone", fill=TEXT + (142,))

    labels = [("north seam", "stable", CYAN), ("ember lane", "rising", EMBER), ("field strain", "0.28", ACID)]
    for i, (name, value, color) in enumerate(labels):
        y = 388 + i * 26
        draw.ellipse((width - 212, y + 2, width - 202, y + 12), fill=color + (220,))
        draw.text((width - 194, y), name, fill=TEXT + (170,))
        draw.text((width - 118, y), value, fill=TEXT + (220,))

    note_x = width - 214
    for idx, line in enumerate(
        (
            "Closer to a design surface",
            "than the recent creature plates.",
            "Real panes, live readouts, and",
            "a weather grammar that could",
            "feed a visual system directly.",
        )
    ):
        draw.text((note_x, 534 + idx * 22), line, fill=TEXT + (156,))

    # Bottom timeline
    draw.text((76, bottom[1] + 18), "PROPAGATION STRIP", fill=MUTED + (180,))
    draw.text((76, bottom[1] + 44), "Front history", fill=TEXT + (235,))
    track = (76, bottom[1] + 82, width - 76, bottom[3] - 44)
    rounded(draw, track, 18, (255, 255, 255, 6), (255, 226, 204, 18))

    tx0, ty0, tx1, ty1 = track
    points_a = []
    points_b = []
    for i in range(46):
        t = i / 45
        x = tx0 + (tx1 - tx0) * t
        y1 = ty0 + (ty1 - ty0) * (0.58 - math.sin(t * math.tau * 1.2) * 0.18 - t * 0.06)
        y2 = ty0 + (ty1 - ty0) * (0.42 - math.cos(t * math.tau * 1.35 + 0.7) * 0.11)
        points_a.append((x, y1))
        points_b.append((x, y2))
        image = add_glow(image, x, y1, 12, EMBER, 18)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.line(points_a, fill=CYAN + (190,), width=3)
    draw.line(points_b, fill=CRIMSON + (110,), width=2)

    for i, label in enumerate(("west ingress", "relay braid", "pressure basin", "heat rise", "quiet edge")):
        draw.text((76 + i * ((width - 152) / 4), bottom[3] - 24), label, fill=TEXT + (132,))

    return image.convert("RGB")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    image = draw_scene(args.width, args.height)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
