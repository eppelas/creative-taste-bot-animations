#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


TEXT = [
    "Low signal under the leaves",
    "The relay remembers a warm mistake",
    "A shy red weather opens and closes",
    "Several small witnesses lean toward the noise",
    "Another thought arrives late and grows sideways",
]

PALETTES = [
    ((240, 76, 82), (111, 16, 29), (244, 229, 202)),
    ((255, 122, 82), (143, 35, 24), (246, 220, 168)),
    ((217, 74, 101), (86, 14, 27), (246, 233, 214)),
    ((230, 128, 77), (116, 38, 23), (243, 210, 166)),
]


def draw_gradient_background(image: Image.Image) -> None:
    width, height = image.size
    px = image.load()
    for y in range(height):
        t = y / max(height - 1, 1)
        r = int(7 + t * 8)
        g = int(5 + t * 4)
        b = int(4 + t * 3)
        for x in range(width):
            px[x, y] = (r, g, b, 255)


def add_radial_glow(base: Image.Image, center: tuple[float, float], radius: float, color: tuple[int, int, int], alpha: int) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, alpha))
    blurred = layer.filter(ImageFilter.GaussianBlur(radius * 0.18))
    base.alpha_composite(blurred)


def build_clusters(width: int, height: int) -> list[dict]:
    clusters = []
    count = len(TEXT)
    for index, line in enumerate(TEXT):
        palette = PALETTES[index % len(PALETTES)]
        group = index % 4
        x = width * (0.12 + (index + 0.5) / count * 0.76)
        y = height * (0.28 + group * 0.14 + (index % 2) * 0.05)
        clusters.append(
            {
                "x": x,
                "y": y,
                "rx": 84 + index * 12,
                "ry": 54 + (index % 3) * 16,
                "palette": palette,
                "line": line,
            }
        )
    return clusters


def render(output: Path, width: int, height: int) -> None:
    image = Image.new("RGBA", (width, height), (7, 5, 4, 255))
    draw_gradient_background(image)
    add_radial_glow(image, (width * 0.5, height * 0.44), max(width, height) * 0.42, (113, 15, 29), 82)
    add_radial_glow(image, (width * 0.22, height * 0.22), max(width, height) * 0.16, (241, 215, 170), 24)

    draw = ImageDraw.Draw(image, "RGBA")

    grid_x = 74 if width > 720 else 52
    grid_y = 52 if width > 720 else 38
    for x in range(0, width + 1, grid_x):
        draw.line((x, 0, x, height), fill=(247, 239, 226, 10), width=1)
    for y in range(0, height + 1, grid_y):
        draw.line((0, y, width, y), fill=(247, 239, 226, 10), width=1)

    for y in range(0, height, 3):
        alpha = int((0.008 + (y / max(height, 1)) * 0.007) * 255)
        draw.line((0, y, width, y), fill=(247, 239, 226, alpha), width=1)

    clusters = build_clusters(width, height)
    for idx, cluster in enumerate(clusters):
        cx = cluster["x"]
        cy = cluster["y"]
        rx = cluster["rx"]
        ry = cluster["ry"]
        c0, c1, c2 = cluster["palette"]

        add_radial_glow(image, (cx, cy), rx * 0.95, c0, 86)
        add_radial_glow(image, (cx, cy), rx * 0.55, c1, 70)

        draw = ImageDraw.Draw(image, "RGBA")
        draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=(245, 233, 214, 28), width=2)

        for j in range(12):
            angle = (j / 12) * math.tau + idx * 0.34
            orbit = rx * (0.35 + (j % 5) * 0.09)
            bx = cx + math.cos(angle) * orbit
            by = cy + math.sin(angle) * orbit * 0.55
            sx = 8 + (j % 4) * 4
            sy = 4 + (j % 3) * 3
            draw.ellipse((bx - sx, by - sy, bx + sx, by + sy), fill=(*c0, 92))
            draw.ellipse((bx - sx * 0.32, by - sy * 0.32, bx + sx * 0.32, by + sy * 0.32), fill=(*c2, 112))

        for j in range(6):
            sx = cx - rx * 0.2 + j * (rx * 0.12)
            sy = cy + ry * 0.2 + (j % 2) * 6
            top_x = sx + 14 + j * 2
            top_y = sy - 90 - j * 8
            draw.line((sx, sy, sx + 6, sy - 44, top_x, top_y), fill=(245, 224, 194, 44), width=2)

        label_x = cx - rx * 0.34
        label_y = cy - ry - 20
        line_end_x = cx - rx * 0.08
        line_end_y = cy - ry * 0.18
        draw.line((label_x - 8, label_y, label_x - 2, label_y, line_end_x, line_end_y), fill=(245, 236, 225, 54), width=1)
        draw.text((label_x, label_y - 7), cluster["line"][:26], fill=(245, 236, 225, 122))

    for i in range(140):
        x = (i * 67) % width
        y = (i * 131) % height
        size = 1 + (i % 3)
        draw.rectangle((x, y, x + size, y + size), fill=(241, 215, 170, 36 + (i % 5) * 8))

    image.convert("RGB").save(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    render(args.output, args.width, args.height)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
