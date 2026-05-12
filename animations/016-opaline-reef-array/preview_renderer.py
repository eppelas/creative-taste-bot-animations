#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def add_glow(
    image: Image.Image,
    center: tuple[float, float],
    radius: float,
    color: tuple[int, int, int],
    alpha: int,
) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    for index in range(12, 0, -1):
        frac = index / 12
        r = radius * frac
        a = int(alpha * frac * frac * 0.84)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color + (a,))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius * 0.08)))


def rgba_tuple(color: tuple[int, int, int], alpha: int) -> tuple[int, int, int, int]:
    return color + (alpha,)


def mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def render_reef(
    draw: ImageDraw.ImageDraw,
    image: Image.Image,
    x: float,
    base_y: float,
    stem_height: float,
    stem_width: float,
    tint: tuple[int, int, int],
    tint2: tuple[int, int, int],
    phase: float,
) -> None:
    left = []
    right = []
    spine = []
    steps = 24

    for step in range(steps + 1):
      t = step / steps
      y = base_y - stem_height * t
      bend = math.sin(phase + t * 4.5) * stem_width * 0.7 + math.cos(phase * 0.7 + t * 8) * stem_width * 0.26
      px = x + bend
      width_local = stem_width * (1.08 - t * 0.34)
      left.append((px - width_local, y))
      right.insert(0, (px + width_local, y))
      spine.append((px, y, width_local))

    stem_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    stem_draw = ImageDraw.Draw(stem_layer, "RGBA")
    stem_draw.polygon(left + right, fill=rgba_tuple(mix(tint, tint2, 0.3), 52), outline=(246, 239, 230, 40))
    image.alpha_composite(stem_layer.filter(ImageFilter.GaussianBlur(stem_width * 0.05)))
    draw.polygon(left + right, outline=(246, 239, 230, 34))

    for rung in range(7):
        t = 0.14 + rung * 0.11
        node = spine[min(int(t * steps), steps)]
        px, py, width_local = node
        draw.line((px - width_local * 1.1, py, px + width_local * 1.1, py), fill=(246, 239, 230, 34), width=1)

    for idx in range(5):
        t = 0.12 + idx * 0.2
        node = spine[min(int(t * steps), steps)]
        px, py, width_local = node
        rx = stem_width * (1.7 - idx * 0.08)
        ry = stem_width * 2.2
        cx = px + math.sin(phase + idx * 0.9) * stem_width * 0.35
        cy = py + math.cos(phase + idx * 0.8) * 5
        color = mix(tint, tint2, 0.2 + idx * 0.16)

        add_glow(image, (cx, cy), rx * 1.8, color, 32)
        capsule = Image.new("RGBA", image.size, (0, 0, 0, 0))
        capsule_draw = ImageDraw.Draw(capsule, "RGBA")
        capsule_draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=rgba_tuple(color, 42), outline=(246, 239, 230, 34), width=1)
        capsule_draw.ellipse((cx - rx * 0.16, cy - ry * 0.24, cx + rx * 0.22, cy + ry * 0.24), fill=(38, 20, 48, 78))
        image.alpha_composite(capsule.filter(ImageFilter.GaussianBlur(rx * 0.04)))
        draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=(246, 239, 230, 30), width=1)

        for vein in (-1, 0, 1):
            pts = []
            for step in range(14):
                vt = step / 13
                vx = cx + vein * rx * 0.23 + math.sin(vt * math.tau + phase + idx) * rx * 0.09
                vy = cy - ry * 0.68 + vt * ry * 1.36 + math.cos(vt * math.tau * 1.24 + phase) * ry * 0.06
                pts.append((vx, vy))
            draw.line(pts, fill=(122, 224, 222, 48), width=1)


def render(output: Path, width: int, height: int) -> None:
    random.seed(16)
    image = Image.new("RGBA", (width, height), (4, 6, 11, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    for y in range(height):
        t = y / max(height - 1, 1)
        draw.line((0, y, width, y), fill=(4, 6 + int(t * 5), 11 + int(t * 10), 255))

    add_glow(image, (width * 0.48, height * 0.12), width * 0.32, (156, 144, 255), 58)
    add_glow(image, (width * 0.24, height * 0.62), width * 0.18, (245, 182, 210), 24)
    add_glow(image, (width * 0.76, height * 0.58), width * 0.2, (122, 224, 222), 24)

    draw = ImageDraw.Draw(image, "RGBA")
    for index in range(24):
        y = height * (0.12 + index * 0.034)
        points = []
        for step in range(30):
            t = step / 29
            x = t * width
            wave = math.sin(t * 6 + index * 0.4) * width * 0.014
            wave += math.cos(t * 13 + index * 0.2) * width * 0.004
            points.append((x, y + wave))
        draw.line(points, fill=(246, 239, 230, random.randint(8, 16)), width=1)

    palette = [
        (245, 182, 210),
        (122, 224, 222),
        (156, 144, 255),
        (205, 242, 197),
        (246, 225, 203),
    ]
    reef_specs = [
        (0.1, 0.86, 0.28, 0.026, 0, 2),
        (0.23, 0.8, 0.36, 0.03, 1, 3),
        (0.35, 0.84, 0.32, 0.028, 2, 4),
        (0.48, 0.78, 0.4, 0.034, 3, 0),
        (0.61, 0.85, 0.31, 0.027, 4, 1),
        (0.73, 0.79, 0.37, 0.031, 0, 2),
        (0.85, 0.83, 0.3, 0.026, 1, 3),
    ]

    for idx, (x_n, base_n, h_n, w_n, a_i, b_i) in enumerate(reef_specs):
        render_reef(
            draw,
            image,
            width * x_n,
            height * base_n,
            height * h_n,
            width * w_n,
            palette[a_i],
            palette[b_i],
            0.4 + idx * 0.7,
        )

    draw = ImageDraw.Draw(image, "RGBA")
    focus_x = width * 0.58
    focus_y = height * 0.54
    add_glow(image, (focus_x, focus_y), 140, (246, 225, 203), 30)
    for ring in range(4):
        rx = 34 + ring * 34
        ry = 22 + ring * 18
        draw.ellipse((focus_x - rx, focus_y - ry, focus_x + rx, focus_y + ry), outline=(246, 239, 230, 42 - ring * 8), width=2 if ring == 0 else 1)

    for _ in range(220):
        x = random.uniform(width * 0.04, width * 0.96)
        y = random.uniform(height * 0.04, height * 0.96)
        size = random.uniform(0.8, 2.6)
        color = random.choice(palette[:3] + [(246, 225, 203)])
        draw.ellipse((x - size, y - size, x + size, y + size), fill=rgba_tuple(color, random.randint(18, 42)))

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
