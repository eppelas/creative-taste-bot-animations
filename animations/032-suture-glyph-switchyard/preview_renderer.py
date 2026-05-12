#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


BG = "#f3f0ea"
INK = "#223847"
CYAN = "#73c8f1"
CORAL = "#ffb499"
ACID = "#d6f55f"
DUST = "#9fb3c1"
LINE = (42, 61, 76, 36)
MUTED = (34, 56, 71, 176)
PAPER = (255, 255, 255, 166)


def hex_rgba(value: str, alpha: int) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def vertical_gradient(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size)
    draw = ImageDraw.Draw(image)
    top_rgb = hex_rgba(top, 255)
    bottom_rgb = hex_rgba(bottom, 255)
    for y in range(height):
        t = y / max(height - 1, 1)
        color = tuple(int(lerp(top_rgb[i], bottom_rgb[i], t)) for i in range(3)) + (255,)
        draw.line((0, y, width, y), fill=color)
    return image


def radial_glow(size: tuple[int, int], center: tuple[float, float], radius: float, color: str, alpha: int) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for step in range(18, 0, -1):
        t = step / 18
        current_radius = radius * t
        current_alpha = int(alpha * (t**2) * 0.42)
        draw.ellipse(
            (
                center[0] - current_radius,
                center[1] - current_radius,
                center[0] + current_radius,
                center[1] + current_radius,
            ),
            fill=hex_rgba(color, current_alpha),
        )
    return layer.filter(ImageFilter.GaussianBlur(radius * 0.08))


def draw_panel(base: Image.Image, width: int, height: int) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    box = (34, 34, min(width - 34, 760), 300)
    draw.rounded_rectangle(box, radius=28, fill=PAPER, outline=LINE, width=2)
    draw.text((58, 58), "CODE ANIMATION STUDY #032", fill=MUTED)
    draw.text((58, 94), "SUTURE GLYPH SWITCHYARD", fill=hex_rgba(INK, 255))
    draw.multiline_text(
        (58, 142),
        "A flatter editorial control surface: stitched current lanes,\n"
        "bead relays, and small grammar cards on one pale board so the\n"
        "motion feels usable for design, not another soft specimen.",
        fill=hex_rgba(INK, 230),
        spacing=8,
    )
    draw.multiline_text(
        (58, 230),
        "Pointer shear tugs the nearest seams. Grammar cards switch the\n"
        "board logic between stitch, bead, and wake.",
        fill=MUTED,
        spacing=8,
    )
    draw.text((58, 278), "GRAMMAR", fill=MUTED)
    draw.text((152, 278), "stitch", fill=hex_rgba(INK, 255))
    draw.text((242, 278), "SHEAR", fill=MUTED)
    draw.text((312, 278), "0.33", fill=hex_rgba(INK, 255))
    draw.text((392, 278), "RELAY COUNT", fill=MUTED)
    draw.text((532, 278), "42", fill=hex_rgba(INK, 255))
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.2)))


def draw_chip(draw: ImageDraw.ImageDraw, x: float, y: float, title: str, subtitle: str, outline: str) -> None:
    box = (x - 84, y - 32, x + 84, y + 32)
    draw.rounded_rectangle(box, radius=18, fill=PAPER, outline=hex_rgba(outline, 120), width=2)
    draw.text((x - 64, y - 18), title, fill=hex_rgba(INK, 255))
    draw.text((x - 64, y + 2), subtitle, fill=MUTED)


def draw_modules(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    modules = [
        (0.1, 0.14, 0.14, 0.12),
        (0.28, 0.12, 0.18, 0.14),
        (0.54, 0.14, 0.12, 0.1),
        (0.76, 0.12, 0.16, 0.15),
        (0.12, 0.62, 0.16, 0.14),
        (0.34, 0.66, 0.2, 0.12),
        (0.58, 0.64, 0.14, 0.14),
        (0.76, 0.68, 0.16, 0.12),
    ]
    for index, (x, y, w, h) in enumerate(modules):
        x0 = width * x
        y0 = height * y
        x1 = x0 + width * w
        y1 = y0 + height * h
        draw.rounded_rectangle((x0, y0, x1, y1), radius=24, fill=(255, 255, 255, 48), outline=LINE, width=2)
        for row in range(5):
            yy = y0 + 20 + row * ((y1 - y0 - 40) / 4)
            draw.line((x0 + 16, yy, x1 - 16, yy + math.sin(row + index) * 3), fill=hex_rgba(CYAN, 44), width=2)
        if index % 2 == 0:
            cx = (x0 + x1) / 2
            cy = (y0 + y1) / 2
            r = min(x1 - x0, y1 - y0) * 0.18
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=hex_rgba(CORAL, 64), width=2)
        if index % 3 != 1:
            for gx in range(int(x0 + 18), int(x1 - 18), 9):
                for gy in range(int(y0 + 18), int(y1 - 18), 9):
                    draw.rectangle((gx, gy, gx + 1, gy + 1), fill=hex_rgba(ACID, 60))


def draw_lanes(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    base_rows = [0.2, 0.31, 0.43, 0.56, 0.7, 0.82]
    for row_index, row in enumerate(base_rows):
        points = []
        highlight = []
        for step in range(82):
            t = step / 81
            x = t * width
            y = height * row + math.sin(t * 6.8 + row_index * 0.8) * (16 + row_index * 2) + math.cos(t * 3.1 - row_index * 0.6) * 7
            points.append((x, y))
            highlight.append((x, y - 2))
        draw.line(points, fill=hex_rgba(INK, 86), width=1)
        draw.line(highlight, fill=hex_rgba(CYAN, 72), width=1)


def draw_spines(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    center_x = width * 0.5
    top = height * 0.24
    bottom = height * 0.86
    for index in range(7):
        side = index / 6 - 0.5
        points = []
        for step in range(33):
            p = step / 32
            x = center_x + side * 180 + math.sin(p * 5 + index) * 20
            y = lerp(top, bottom, p)
            points.append((x, y))
        color = CYAN if index % 2 == 0 else CORAL
        draw.line(points, fill=hex_rgba(color, 110), width=3)

    draw.ellipse(
        (center_x - width * 0.16, height * 0.42, center_x + width * 0.16, height * 0.58),
        fill=(255, 255, 255, 66),
        outline=hex_rgba(CYAN, 140),
        width=2,
    )
    draw.ellipse(
        (center_x - width * 0.08, height * 0.47, center_x + width * 0.08, height * 0.53),
        fill=hex_rgba(CORAL, 92),
    )


def draw_relays(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    random.seed(32)
    base_rows = [0.2, 0.31, 0.43, 0.56, 0.7, 0.82]
    for index in range(42):
        t = (index + 1) / 43
        row_index = index % len(base_rows)
        x = t * width
        y = height * base_rows[row_index] + math.sin(t * 6.8 + row_index * 0.8) * (16 + row_index * 2) + math.cos(t * 3.1 - row_index * 0.6) * 7
        bar_w = 8 + (index % 4) * 3
        draw.rectangle((x - bar_w, y - 2, x + bar_w, y + 2), fill=hex_rgba(CYAN, 68))
        radius = 3 + (index % 3)
        fill = CORAL if index % 2 else ACID
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=hex_rgba(fill, 170))
        if index % 2 == 0:
            draw.line((x, y, x + 14, y - 12), fill=hex_rgba(INK, 80), width=1)


def draw_labels(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    labels = [
        ("GLYPH RELAY", 0.12, 0.58),
        ("STITCH FIELD", 0.42, 0.74),
        ("WAKE SAMPLES", 0.76, 0.66),
        ("BOARD NOISE", 0.28, 0.18),
        ("SOFT PANEL", 0.75, 0.16),
    ]
    for text, nx, ny in labels:
        draw.text((nx * width, ny * height), text, fill=MUTED)


def render(output: Path, width: int, height: int) -> None:
    image = vertical_gradient((width, height), "#ffffff", BG)
    for center, radius, color, alpha in [
        ((width * 0.18, height * 0.2), width * 0.23, CYAN, 86),
        ((width * 0.78, height * 0.22), width * 0.22, CORAL, 74),
        ((width * 0.58, height * 0.82), width * 0.2, ACID, 54),
    ]:
        image = Image.alpha_composite(image, radial_glow((width, height), center, radius, color, alpha))

    draw = ImageDraw.Draw(image)

    random.seed(8)
    for _ in range(160):
        x = random.uniform(0, width)
        y = random.uniform(0, height)
        r = random.uniform(0.8, 2.0)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=hex_rgba(DUST, random.randint(28, 76)))

    for x in range(0, width, 72):
        draw.line((x, 0, x, height), fill=(42, 61, 76, 14), width=1)

    draw_modules(draw, width, height)
    draw_lanes(draw, width, height)
    draw_spines(draw, width, height)
    draw_relays(draw, width, height)
    draw_labels(draw, width, height)

    chips = [
        (width * 0.2, height * 0.28, "STITCH", "taut seams", CYAN),
        (width * 0.76, height * 0.48, "BEAD", "node chains", CORAL),
        (width * 0.34, height * 0.78, "WAKE", "soft drag", ACID),
    ]
    for x, y, title, subtitle, outline in chips:
        draw_chip(draw, x, y, title, subtitle, outline)

    draw_panel(image, width, height)

    image = image.convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


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
