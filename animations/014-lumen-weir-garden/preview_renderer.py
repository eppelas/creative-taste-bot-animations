#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def add_glow(image: Image.Image, center: tuple[float, float], radius: float, color: tuple[int, int, int], alpha: int) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    for index in range(12, 0, -1):
        frac = index / 12
        r = radius * frac
        a = int(alpha * frac * frac * 0.85)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color + (a,))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius * 0.07)))


def rgba(draw: ImageDraw.ImageDraw, points, fill, outline=None, width=1) -> None:
    draw.polygon(points, fill=fill, outline=outline)
    if outline and width > 1:
        for offset in range(1, width):
            shifted = [(x + offset * 0.1, y) for x, y in points]
            draw.line(shifted + [shifted[0]], fill=outline, width=1)


def draw_valve(draw: ImageDraw.ImageDraw, image: Image.Image, x: float, y: float, rx: float, ry: float, tint: int, phase: float) -> None:
    glow = [
        (247, 223, 203),
        (244, 126, 182),
        (114, 221, 230),
        (194, 241, 191),
    ][tint % 4]
    add_glow(image, (x, y), ry * 1.45, glow, 36)

    draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=glow + (28,), outline=(243, 234, 224, 38), width=2)
    slit = ry * (0.3 + math.sin(phase) * 0.06)
    draw.line((x, y - slit, x, y + slit), fill=(243, 234, 224, 68), width=2)
    draw.arc((x - rx * 0.22, y - ry * 0.36, x + rx * 0.22, y + ry * 0.36), start=90, end=270, fill=(243, 234, 224, 42), width=1)
    draw.arc((x - rx * 0.22, y - ry * 0.36, x + rx * 0.22, y + ry * 0.36), start=-90, end=90, fill=(243, 234, 224, 42), width=1)


def render(output: Path, width: int, height: int) -> None:
    random.seed(14)
    image = Image.new("RGBA", (width, height), (5, 6, 10, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    for y in range(height):
        t = y / max(height - 1, 1)
        r = int(5 + t * 2)
        g = int(6 + t * 3)
        b = int(10 + t * 5)
        draw.line((0, y, width, y), fill=(r, g, b, 255))

    add_glow(image, (width * 0.5, height * 0.12), width * 0.26, (142, 132, 255), 58)
    add_glow(image, (width * 0.22, height * 0.74), width * 0.18, (244, 126, 182), 28)
    add_glow(image, (width * 0.82, height * 0.62), width * 0.18, (114, 221, 230), 28)

    draw = ImageDraw.Draw(image, "RGBA")
    for index in range(18):
        y = height * (0.11 + index * 0.05)
        pts = []
        for step in range(26):
            t = step / 25
            x = t * width
            wave = math.sin(t * 6 + index * 0.42) * width * 0.025 + math.sin(t * 13 + index * 0.3) * width * 0.006
            pts.append((x, y + wave))
        draw.line(pts, fill=(243, 234, 224, random.randint(9, 18)), width=1)

    column_specs = [
        (0.12, 0.1, 0.92, 0.09),
        (0.28, 0.14, 0.9, 0.1),
        (0.45, 0.08, 0.95, 0.12),
        (0.62, 0.16, 0.88, 0.1),
        (0.78, 0.11, 0.9, 0.09),
    ]

    for x_norm, top_norm, bottom_norm, width_norm in column_specs:
        x = width * x_norm
        top = height * top_norm
        bottom = height * bottom_norm
        half = width * width_norm * 0.5
        points = [
            (x, top),
            (x + half, top + height * 0.1),
            (x + half * 0.88, bottom - height * 0.12),
            (x, bottom),
            (x - half * 0.8, bottom - height * 0.08),
            (x - half, top + height * 0.14),
        ]
        rgba(draw, points, (114, 221, 230, 12), (243, 234, 224, 20))
        for offset in (-0.22, 0, 0.22):
            line = []
            for step in range(22):
                t = step / 21
                yy = top + (bottom - top) * t
                bend = math.sin(t * 7 + offset * 7) * half * 0.16 + math.sin(t * 12 + x_norm * 4) * half * 0.05
                line.append((x + bend + half * offset, yy))
            draw.line(line, fill=(247, 223, 203, 26 if offset == 0 else 20), width=2 if offset == 0 else 1)

    connector_rows = [0.3, 0.46, 0.64]
    for row in connector_rows:
        y = height * row
        points = [
            (width * 0.16, y),
            (width * 0.32, y - 26),
            (width * 0.5, y + 22),
            (width * 0.68, y - 18),
            (width * 0.84, y + 10),
        ]
        draw.line(points, fill=(247, 223, 203, 26), width=2)

    valves = [
        (0.13, 0.26, 34, 72, 1, 0.2),
        (0.28, 0.36, 40, 82, 0, 1.0),
        (0.42, 0.22, 44, 96, 2, 0.6),
        (0.47, 0.56, 48, 104, 3, 1.4),
        (0.62, 0.33, 40, 86, 1, 2.1),
        (0.78, 0.24, 36, 78, 0, 1.8),
        (0.8, 0.58, 42, 94, 2, 2.7),
        (0.27, 0.7, 38, 82, 3, 1.1),
        (0.6, 0.76, 46, 98, 0, 0.7),
    ]

    for x_norm, y_norm, rx, ry, tint, phase in valves:
        draw_valve(draw, image, width * x_norm, height * y_norm, rx, ry, tint, phase)

    draw = ImageDraw.Draw(image, "RGBA")
    for index in range(14):
        x = width * (0.1 + index * 0.06)
        y = height * (0.18 + (index % 5) * 0.12)
        h = random.uniform(height * 0.08, height * 0.18)
        draw.line((x - 8, y, x - 8, y + h), fill=(243, 234, 224, 24), width=1)
        draw.line((x + 8, y, x + 8, y + h), fill=(243, 234, 224, 24), width=1)
        for rung in range(7):
            yy = y + h * (rung / 6)
            draw.line((x - 8, yy, x + 8, yy + math.sin(index + rung) * 2), fill=(243, 234, 224, 20), width=1)

    for index in range(24):
        x = width * random.uniform(0.08, 0.92)
        y = height * random.uniform(0.14, 0.78)
        length = random.uniform(height * 0.07, height * 0.15)
        points = []
        for step in range(18):
            t = step / 17
            sway = math.sin(index * 0.5 + t * 4) * random.uniform(8, 18)
            points.append((x + sway, y + length * t))
        draw.line(points, fill=(194, 241, 191, 24), width=1)

    px = width * 0.63
    py = height * 0.46
    add_glow(image, (px, py), 120, (247, 223, 203), 36)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((px - 58, py - 58, px + 58, py + 58), outline=(243, 234, 224, 42), width=2)
    draw.ellipse((px - 30, py - 30, px + 30, py + 30), outline=(114, 221, 230, 38), width=2)
    draw.line((px - 12, py, px + 12, py), fill=(247, 223, 203, 42), width=2)
    draw.line((px, py - 12, px, py + 12), fill=(247, 223, 203, 42), width=2)

    for _ in range(220):
        x = random.uniform(width * 0.06, width * 0.94)
        y = random.uniform(height * 0.08, height * 0.94)
        size = random.uniform(0.8, 2.7)
        palette = random.choice(
            [
                (247, 223, 203),
                (244, 126, 182),
                (114, 221, 230),
                (194, 241, 191),
            ]
        )
        draw.ellipse((x - size, y - size, x + size, y + size), fill=palette + (random.randint(18, 40),))

    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output)


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
