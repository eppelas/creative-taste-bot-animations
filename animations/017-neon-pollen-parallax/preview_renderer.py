#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def blend(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def add_glow(layer: Image.Image, center: tuple[float, float], radius: float, color: tuple[int, int, int], alpha: int) -> None:
    glow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.42))
    layer.alpha_composite(glow)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    width = args.width
    height = args.height
    rng = random.Random(17)

    image = Image.new("RGBA", (width, height), (4, 5, 11, 255))
    pixels = image.load()

    top = (8, 12, 26)
    middle = (5, 7, 16)
    bottom = (2, 3, 7)
    for y in range(height):
      t = y / max(height - 1, 1)
      base = blend(top, middle if t < 0.55 else bottom, t / 0.55 if t < 0.55 else (t - 0.55) / 0.45)
      for x in range(width):
        pixels[x, y] = (*base, 255)

    glow_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    add_glow(glow_layer, (width * 0.5, height * 0.12), height * 0.34, (110, 88, 255), 92)
    add_glow(glow_layer, (width * 0.26, height * 0.58), height * 0.16, (255, 94, 168), 82)
    add_glow(glow_layer, (width * 0.76, height * 0.42), height * 0.15, (98, 217, 255), 72)
    add_glow(glow_layer, (width * 0.58, height * 0.72), height * 0.22, (255, 211, 123), 30)
    image.alpha_composite(glow_layer)

    rail_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    rail_draw = ImageDraw.Draw(rail_layer)
    for i in range(9):
        py = height * (0.2 + i * 0.08) + math.sin(i * 0.6) * 18
        start = width * (0.16 + (i % 3) * 0.03)
        end = width * (0.84 + (i % 2) * 0.03)
        bend = (i - 4) * 0.01 * height
        points = []
        steps = 32
        for step in range(steps + 1):
            p = step / steps
            x = start + (end - start) * p
            y = py + math.sin(p * math.pi) * bend + math.sin(p * 7 + i) * 10
            points.append((x, y))
        color = (255, 94, 168, 62) if i % 4 == 0 else (98, 217, 255, 56)
        rail_draw.line(points, fill=color, width=4)
        reflection = [(x + 18, y + 7) for x, y in points]
        rail_draw.line(reflection, fill=(255, 211, 123, 38), width=2)
    rail_layer = rail_layer.filter(ImageFilter.GaussianBlur(0.8))
    image.alpha_composite(rail_layer)

    pane_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pane_draw = ImageDraw.Draw(pane_layer)
    pane_specs = [
        (0.21, 0.11, -30),
        (0.38, 0.08, 20),
        (0.56, 0.13, -16),
        (0.78, 0.1, 24),
    ]
    for x_ratio, width_ratio, lean in pane_specs:
        x = width * x_ratio
        w = width * width_ratio
        polygon = [
            (x - w * 0.5, 0),
            (x + w * 0.5, 0),
            (x + w * 0.5 + lean, height),
            (x - w * 0.5 + lean, height),
        ]
        pane_draw.polygon(polygon, fill=(255, 255, 255, 32))
        pane_draw.line((x - w * 0.16, 0, x - w * 0.16 + lean, height), fill=(98, 217, 255, 64), width=2)
        pane_draw.line((x + w * 0.18, 0, x + w * 0.18 + lean, height), fill=(255, 255, 255, 26), width=1)
    pane_layer = pane_layer.filter(ImageFilter.GaussianBlur(0.8))
    image.alpha_composite(pane_layer)

    pollen_glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pollen_core = Image.new("RGBA", image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(pollen_glow)
    core_draw = ImageDraw.Draw(pollen_core)
    palette = [(255, 94, 168), (98, 217, 255), (255, 211, 123), (139, 115, 255)]
    for _ in range(240):
        depth = rng.random() ** 1.4
        x = rng.uniform(0, width)
        y = rng.uniform(0, height)
        size = 1.5 + depth * 8.5
        blur = 1.0 - clamp(abs(depth - 0.56) / 0.45, 0, 1)
        color = palette[int(rng.random() * len(palette)) % len(palette)]
        glow_radius = size * (2.2 + (1.0 - blur) * 2.8)
        glow_alpha = int(34 + blur * 88)
        glow_draw.ellipse(
            (x - glow_radius, y - glow_radius, x + glow_radius, y + glow_radius),
            fill=(*color, glow_alpha),
        )
        if blur > 0.45:
            core_draw.rectangle(
                (x - size * 0.45, y - size * 0.45, x + size * 0.45, y + size * 0.45),
                fill=(*color, int(176 + blur * 70)),
            )
        else:
            core_draw.ellipse(
                (x - size, y - size * 0.7, x + size * 1.8, y + size * 0.7),
                fill=(*color, 84),
            )
    pollen_glow = pollen_glow.filter(ImageFilter.GaussianBlur(8))
    pollen_core = pollen_core.filter(ImageFilter.GaussianBlur(0.6))
    image.alpha_composite(pollen_glow)
    image.alpha_composite(pollen_core)

    grain = Image.new("L", image.size)
    grain_pixels = grain.load()
    for y in range(height):
        for x in range(width):
            grain_pixels[x, y] = 118 + rng.randint(-18, 18)
    grain = grain.filter(ImageFilter.GaussianBlur(0.2))
    grain_rgba = Image.new("RGBA", image.size, (255, 255, 255, 0))
    grain_rgba.putalpha(grain)
    grain_rgba = ImageChops.multiply(grain_rgba, Image.new("RGBA", image.size, (18, 20, 28, 255)))
    image.alpha_composite(grain_rgba)

    image.convert("RGB").save(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
