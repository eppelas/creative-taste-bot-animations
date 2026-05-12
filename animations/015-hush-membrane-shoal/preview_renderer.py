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
        a = int(alpha * frac * frac * 0.82)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color + (a,))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius * 0.08)))


def palette(index: int, alpha: int) -> tuple[int, int, int, int]:
    colors = [
        (244, 138, 194),
        (125, 225, 223),
        (155, 137, 255),
        (245, 228, 208),
    ]
    r, g, b = colors[index % len(colors)]
    return (r, g, b, alpha)


def render_body(
    draw: ImageDraw.ImageDraw,
    image: Image.Image,
    x: float,
    y: float,
    rx: float,
    ry: float,
    hue: int,
    phase: float,
) -> None:
    add_glow(image, (x, y), rx * 1.6, (244, 138, 194), 28)
    add_glow(image, (x, y), rx * 1.2, (125, 225, 223), 24)

    shell_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shell_draw = ImageDraw.Draw(shell_layer, "RGBA")
    bbox = (x - rx, y - ry, x + rx, y + ry)
    shell_draw.ellipse(bbox, fill=palette(hue, 42), outline=(248, 239, 230, 36), width=2)
    shell_draw.ellipse((x - rx * 0.82, y - ry * 0.82, x + rx * 0.82, y + ry * 0.82), fill=palette(hue + 1, 16))
    shell_draw.ellipse((x - rx * 0.26, y - ry * 0.2, x + rx * 0.18, y + ry * 0.14), fill=(255, 245, 236, 68))
    image.alpha_composite(shell_layer.filter(ImageFilter.GaussianBlur(rx * 0.03)))

    draw.ellipse(bbox, outline=(248, 239, 230, 34), width=1)

    for vein in range(5):
        vein_t = vein / 4
        vx = x - rx * 0.56 + vein_t * rx * 1.12
        points = []
        for step in range(16):
            t = step / 15
            px = vx + math.sin(t * math.tau + phase + vein_t * 2.6) * rx * 0.08
            py = y - ry * 0.66 + t * ry * 1.32 + math.cos(t * math.tau * 1.4 + phase) * ry * 0.07
            points.append((px, py))
        draw.line(points, fill=(117, 227, 224, 72), width=1)

    pore_x = x + math.cos(phase) * rx * 0.1
    pore_y = y + math.sin(phase * 1.2) * ry * 0.08
    add_glow(image, (pore_x, pore_y), rx * 0.3, (226, 98, 171), 26)
    draw.ellipse(
        (pore_x - rx * 0.18, pore_y - ry * 0.14, pore_x + rx * 0.18, pore_y + ry * 0.14),
        fill=(37, 18, 46, 92),
        outline=(248, 239, 230, 18),
    )


def render(output: Path, width: int, height: int) -> None:
    random.seed(15)
    image = Image.new("RGBA", (width, height), (5, 6, 11, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    for y in range(height):
        t = y / max(height - 1, 1)
        draw.line((0, y, width, y), fill=(5, 6 + int(t * 3), 11 + int(t * 6), 255))

    add_glow(image, (width * 0.5, height * 0.18), width * 0.34, (155, 137, 255), 48)
    add_glow(image, (width * 0.28, height * 0.54), width * 0.18, (244, 138, 194), 24)
    add_glow(image, (width * 0.74, height * 0.6), width * 0.18, (125, 225, 223), 26)

    draw = ImageDraw.Draw(image, "RGBA")
    for index in range(18):
        y = height * (0.14 + index * 0.045)
        points = []
        for step in range(30):
            t = step / 29
            x = t * width
            wave = math.sin(t * 6 + index * 0.42) * width * 0.024
            wave += math.cos(t * 13 + index * 0.26) * width * 0.008
            points.append((x, y + wave))
        draw.line(points, fill=(245, 236, 228, random.randint(8, 16)), width=1)

    body_specs = [
        (0.24, 0.26, 0.12, 0.085, 0, 0.3),
        (0.52, 0.24, 0.11, 0.078, 2, 1.1),
        (0.78, 0.31, 0.1, 0.074, 1, 1.8),
        (0.18, 0.56, 0.102, 0.076, 3, 2.2),
        (0.45, 0.5, 0.13, 0.09, 0, 0.9),
        (0.72, 0.56, 0.118, 0.084, 1, 2.5),
        (0.34, 0.78, 0.104, 0.076, 2, 1.5),
        (0.64, 0.8, 0.126, 0.09, 3, 0.5),
    ]

    for x_norm, y_norm, rx_norm, ry_norm, hue, phase in body_specs:
        render_body(
            draw,
            image,
            width * x_norm,
            height * y_norm,
            width * rx_norm,
            height * ry_norm,
            hue,
            phase,
        )

    draw = ImageDraw.Draw(image, "RGBA")
    ripple_center = (width * 0.62, height * 0.48)
    for ring in range(4):
        rx = 32 + ring * 34
        ry = 24 + ring * 18
        draw.ellipse(
            (
                ripple_center[0] - rx,
                ripple_center[1] - ry,
                ripple_center[0] + rx,
                ripple_center[1] + ry,
            ),
            outline=(248, 236, 226, 44 - ring * 8),
            width=2 if ring == 0 else 1,
        )

    add_glow(image, ripple_center, 120, (247, 236, 226), 28)

    for _ in range(190):
        x = random.uniform(width * 0.06, width * 0.94)
        y = random.uniform(height * 0.08, height * 0.94)
        size = random.uniform(0.8, 2.5)
        draw.ellipse(
            (x - size, y - size, x + size, y + size),
            fill=palette(random.randint(0, 3), random.randint(18, 42)),
        )

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
