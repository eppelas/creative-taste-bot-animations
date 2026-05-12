#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


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
        t = y / max(1, height - 1)
        color = tuple(int(lerp(top_rgb[i], bottom_rgb[i], t)) for i in range(3)) + (255,)
        draw.line((0, y, width, y), fill=color)
    return image


def radial_glow(size: tuple[int, int], center: tuple[float, float], radius: float, color: str, alpha: int) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    steps = 18
    for step in range(steps, 0, -1):
        t = step / steps
        current_radius = radius * t
        current_alpha = int(alpha * (t**2) * 0.45)
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


def point_for(width: int, height: int, t: float) -> tuple[float, float]:
    center_x = width * 0.5
    y = lerp(height * 0.1, height * 0.9, t)
    bend = math.sin(t * 8.4 + 0.7) * width * 0.045 + math.sin(t * 18 + 1.2) * width * 0.018
    return center_x + bend, y


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    random.seed(27)
    size = (args.width, args.height)
    image = vertical_gradient(size, "#07080d", "#05060a")

    for center, radius, color, alpha in [
        ((size[0] * 0.22, size[1] * 0.2), size[0] * 0.22, "#7ce1d4", 70),
        ((size[0] * 0.78, size[1] * 0.24), size[0] * 0.24, "#f7a2c5", 60),
        ((size[0] * 0.5, size[1] * 0.82), size[0] * 0.2, "#f7cc7f", 55),
    ]:
        image = Image.alpha_composite(image, radial_glow(size, center, radius, color, alpha))

    grid = Image.new("RGBA", size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grid)
    for x in range(0, size[0], 36):
        gdraw.line((x, 0, x, size[1]), fill=(238, 241, 236, 16), width=1)
    for y in range(0, size[1], 36):
        gdraw.line((0, y, size[0], y), fill=(238, 241, 236, 16), width=1)
    image = Image.alpha_composite(image, grid)

    haze = Image.new("RGBA", size, (0, 0, 0, 0))
    for i in range(6):
        center = point_for(size[0], size[1], 0.08 + i * 0.16)
        color = "#f7a2c5" if i % 2 == 0 else "#7ce1d4"
        haze = Image.alpha_composite(
            haze,
            radial_glow(
                size,
                (center[0], size[1] * (0.16 + i * 0.14)),
                size[0] * (0.2 + (i % 2) * 0.05),
                color,
                55,
            ),
        )
    image = Image.alpha_composite(image, haze)

    braid_fill = Image.new("RGBA", size, (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(braid_fill)
    left_edge: list[tuple[float, float]] = []
    right_edge: list[tuple[float, float]] = []
    accent = "#7ce1d4"
    secondary = "#f7a2c5"
    glow = "#f7cc7f"

    cell_points: list[tuple[float, float, float]] = []
    count = 18
    for i in range(count):
        t = i / (count - 1)
        x, y = point_for(size[0], size[1], t)
        radius = 36 + math.sin(i * 0.9) * 10 + (1 - abs(0.5 - t) * 2) * 16
        left_edge.append((x + radius, y))
        right_edge.insert(0, (x - radius, y))
        cell_points.append((x, y, radius))

    bdraw.polygon(left_edge + right_edge, fill=hex_rgba(accent, 18))
    braid_fill = braid_fill.filter(ImageFilter.GaussianBlur(20))
    image = Image.alpha_composite(image, braid_fill)

    filaments = Image.new("RGBA", size, (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(filaments)
    for i in range(len(cell_points) - 1):
        ax, ay, _ = cell_points[i]
        bx, by, _ = cell_points[i + 1]
        fdraw.line((ax, ay, bx, by), fill=hex_rgba(secondary, 36), width=3)
    filaments = filaments.filter(ImageFilter.GaussianBlur(3))
    image = Image.alpha_composite(image, filaments)

    body = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    for i, (x, y, radius) in enumerate(cell_points):
        body = Image.alpha_composite(body, radial_glow(size, (x, y), radius * 1.4, glow, 85))
        d.ellipse(
            (x - radius * 0.78, y - radius * 0.56, x + radius * 0.78, y + radius * 0.56),
            fill=hex_rgba(accent if i % 2 == 0 else secondary, 48),
            outline=hex_rgba("#f2f5ef", 28),
            width=2,
        )
        d.ellipse(
            (x - radius * 0.46, y - radius * 0.22, x + radius * 0.46, y + radius * 0.22),
            fill=hex_rgba(glow, 34),
        )
        for j in range(-4, 5):
            yy = y + j * radius * 0.08
            span = radius * (0.38 + math.cos((j / 4) * math.pi) * 0.2)
            d.line((x - span, yy, x + span, yy), fill=hex_rgba(secondary, 36), width=1)

        if i % 2 == 0:
            side = -1 if i % 4 == 0 else 1
            colony_x = x + side * 86
            colony_y = y + math.cos(i) * 18
            fdraw.line((x, y, colony_x, colony_y), fill=hex_rgba(glow, 42), width=2)
            body = Image.alpha_composite(body, radial_glow(size, (colony_x, colony_y), 30, secondary, 70))
            d.ellipse(
                (colony_x - 18, colony_y - 14, colony_x + 18, colony_y + 14),
                fill=hex_rgba(accent, 40),
                outline=hex_rgba("#f2f5ef", 24),
            )

    body = body.filter(ImageFilter.GaussianBlur(0.4))
    image = Image.alpha_composite(image, body)

    patches = Image.new("RGBA", size, (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(patches)
    patch_data = [
        (-1, 0.14, "Bloom", "lumen tide", accent),
        (1, 0.44, "Mesh", "veil lattice", "#8cc4ff"),
        (-1, 0.74, "Drift", "mist current", "#f88fa0"),
    ]

    for side, t, label, hint, color in patch_data:
        anchor_x, anchor_y = point_for(size[0], size[1], t)
        px = anchor_x + side * 156
        py = anchor_y
        pdraw.line((anchor_x, anchor_y, px, py), fill=hex_rgba(color, 64), width=2)
        pdraw.ellipse((px - 62, py - 28, px + 62, py + 28), fill=hex_rgba(color, 42), outline=hex_rgba("#f4f7ef", 34), width=2)
        pdraw.text((px, py - 6), label, anchor="mm", fill=hex_rgba("#f2f6ef", 220))
        pdraw.text((px, py + 10), hint, anchor="mm", fill=hex_rgba("#f2f6ef", 140))

    image = Image.alpha_composite(image, patches)

    dust = Image.new("RGBA", size, (0, 0, 0, 0))
    ddraw = ImageDraw.Draw(dust)
    for index in range(170):
        x = random.uniform(0, size[0])
        y = random.uniform(0, size[1])
        r = random.uniform(1.0, 2.8)
        color = accent if index % 3 == 0 else secondary
        ddraw.ellipse((x - r, y - r, x + r, y + r), fill=hex_rgba(color, 46))
    dust = dust.filter(ImageFilter.GaussianBlur(0.6))
    image = Image.alpha_composite(image, dust)

    image = image.filter(ImageFilter.GaussianBlur(0.2))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
