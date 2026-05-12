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
    for index in range(10, 0, -1):
      frac = index / 10
      r = radius * frac
      a = int(alpha * frac * frac * 0.8)
      draw.ellipse((x - r, y - r, x + r, y + r), fill=color + (a,))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius * 0.08)))


def node_fill(hue: float, alpha: int) -> tuple[int, int, int, int]:
    if hue < 0.33:
        return (240, 120, 186, alpha)
    if hue < 0.66:
        return (110, 220, 228, alpha)
    return (245, 223, 202, alpha)


def draw_node(draw: ImageDraw.ImageDraw, image: Image.Image, x: float, y: float, radius: float, petals: int, phase: float, hue: float) -> None:
    add_glow(image, (x, y), radius * 2.1, (143, 131, 255), 30)
    add_glow(image, (x, y), radius * 1.45, (240, 120, 186), 34)

    stem_bottom = y + radius * random.uniform(1.6, 2.4)
    draw.line((x, y + radius * 0.2, x + math.sin(phase) * radius * 0.24, stem_bottom), fill=(245, 223, 202, 48), width=max(1, int(radius * 0.08)))

    for petal in range(petals):
        angle = (petal / petals) * math.tau + phase * 0.36
        spread = radius * 0.96
        ax = math.cos(angle) * spread
        ay = math.sin(angle) * spread * 0.82
        tip_x = x + ax
        tip_y = y + ay
        side = radius * 0.28
        side_angle = angle + math.pi / 2
        draw.polygon(
            [
                (x, y),
                (x + ax * 0.3 + math.cos(side_angle) * side, y + ay * 0.3 + math.sin(side_angle) * side),
                (tip_x, tip_y),
                (x + ax * 0.52 - math.cos(side_angle) * side * 1.1, y + ay * 0.52 - math.sin(side_angle) * side * 1.1),
            ],
            fill=node_fill((hue + petal * 0.18) % 1, 34),
            outline=(244, 236, 228, 28),
        )

    for vein in range(3):
        angle = phase + vein * (math.tau / 3)
        draw.line(
            (
                x,
                y,
                x + math.cos(angle) * radius * 0.64,
                y + math.sin(angle) * radius * 0.46,
            ),
            fill=(245, 223, 202, 62),
            width=1,
        )

    draw.ellipse((x - radius * 0.17, y - radius * 0.17, x + radius * 0.17, y + radius * 0.17), fill=(245, 223, 202, 64))


def render(output: Path, width: int, height: int) -> None:
    random.seed(13)
    image = Image.new("RGBA", (width, height), (4, 5, 8, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    for y in range(height):
        t = y / max(height - 1, 1)
        shade = int(4 + t * 2)
        draw.line((0, y, width, y), fill=(shade, shade, 8 + int(t * 3), 255))

    add_glow(image, (width * 0.5, height * 0.12), width * 0.24, (143, 131, 255), 48)
    add_glow(image, (width * 0.24, height * 0.68), width * 0.18, (240, 120, 186), 28)
    add_glow(image, (width * 0.8, height * 0.58), width * 0.16, (110, 220, 228), 28)

    draw = ImageDraw.Draw(image, "RGBA")
    for index in range(16):
        y = height * (0.15 + index * 0.048)
        points = []
        for step in range(28):
            t = step / 27
            x = t * width
            wave = math.sin(t * 5.6 + index * 0.4) * width * 0.03 + math.sin(t * 12.4 + index * 0.2) * width * 0.009
            points.append((x, y + wave))
        draw.line(points, fill=(242, 231, 220, random.randint(10, 22)), width=1)

    for x in [width * 0.12, width * 0.25, width * 0.38, width * 0.51, width * 0.64, width * 0.77]:
        draw.line((x, height * 0.08, x, height * 0.92), fill=(244, 236, 228, 10), width=1)

    nodes = [
        (0.22, 0.22, 0.094, 5, 0.2, 0.1),
        (0.53, 0.2, 0.088, 6, 1.0, 0.7),
        (0.8, 0.25, 0.082, 5, 1.7, 0.4),
        (0.3, 0.48, 0.1, 6, 2.1, 0.9),
        (0.62, 0.52, 0.11, 5, 1.4, 0.2),
        (0.8, 0.56, 0.09, 4, 0.8, 0.58),
        (0.22, 0.76, 0.084, 5, 2.8, 0.42),
        (0.52, 0.78, 0.1, 6, 1.8, 0.05),
        (0.78, 0.78, 0.09, 5, 0.4, 0.76),
    ]

    rib_points = []
    for x_norm, y_norm, *_rest in nodes:
        rib_points.append((width * x_norm, height * y_norm))
    for index in range(len(rib_points) - 1):
        x1, y1 = rib_points[index]
        x2, y2 = rib_points[index + 1]
        mid_x = (x1 + x2) * 0.5 + random.uniform(-width * 0.03, width * 0.03)
        mid_y = (y1 + y2) * 0.5 + random.uniform(-height * 0.04, height * 0.04)
        draw.line((x1, y1, mid_x, mid_y, x2, y2), fill=(110, 220, 228, 18 if index % 2 else 14), width=2)

    for spec in nodes:
        x_norm, y_norm, r_norm, petals, phase, hue = spec
        draw_node(draw, image, width * x_norm, height * y_norm, width * r_norm, petals, phase, hue)

    draw = ImageDraw.Draw(image, "RGBA")
    probe_x = width * 0.63
    probe_y = height * 0.46
    draw.ellipse((probe_x - 54, probe_y - 54, probe_x + 54, probe_y + 54), outline=(242, 231, 220, 44), width=2)
    draw.ellipse((probe_x - 30, probe_y - 30, probe_x + 30, probe_y + 30), outline=(110, 220, 228, 38), width=2)
    draw.line((probe_x - 12, probe_y, probe_x + 12, probe_y), fill=(245, 223, 202, 42), width=2)
    draw.line((probe_x, probe_y - 12, probe_x, probe_y + 12), fill=(245, 223, 202, 42), width=2)

    for _ in range(180):
        x = random.uniform(width * 0.06, width * 0.94)
        y = random.uniform(height * 0.08, height * 0.92)
        size = random.uniform(0.8, 2.4)
        draw.ellipse((x - size, y - size, x + size, y + size), fill=node_fill(random.random(), random.randint(18, 42)))

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
