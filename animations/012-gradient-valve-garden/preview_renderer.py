#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def rgba(hex_color: str, alpha: int) -> tuple[int, int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def add_glow(image: Image.Image, center: tuple[float, float], radius: float, color: tuple[int, int, int], alpha: int) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y = center
    steps = 9
    for index in range(steps, 0, -1):
        frac = index / steps
        r = radius * frac
        a = int(alpha * frac * frac * 0.8)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color + (a,))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius * 0.08)))


def specimen_center(width: int, y_norm: float) -> float:
    return width * 0.5 + math.sin(y_norm * 7.2) * width * 0.022 + math.sin(y_norm * 15.5) * width * 0.008


def draw_valve(draw: ImageDraw.ImageDraw, width: int, height: int, y_norm: float, radius: float, lift: float) -> None:
    cx = specimen_center(width, y_norm)
    cy = lerp(height * 0.18, height * 0.82, y_norm)

    top = (cx, cy - lift)
    right_mid = (cx + radius * 0.92, cy - lift * 0.18)
    right_low = (cx + radius * 0.8, cy + lift * 0.66)
    bottom = (cx, cy + lift * 1.06)
    left_low = (cx - radius * 0.82, cy + lift * 0.6)
    left_mid = (cx - radius * 0.88, cy - lift * 0.16)

    draw.polygon(
        [top, right_mid, right_low, bottom, left_low, left_mid],
        fill=(245, 121, 185, 44),
        outline=(244, 232, 220, 42),
    )

    for offset, color in (
        (0.0, (246, 220, 198, 78)),
        (radius * 0.1, (140, 124, 255, 44)),
        (-radius * 0.1, (115, 221, 225, 38)),
    ):
        draw.line(
            [
                (cx + offset * 0.12, cy - lift * 0.72),
                (cx + offset * 0.54, cy - lift * 0.1),
                (cx + offset * 0.16, cy + lift * 0.72),
            ],
            fill=color,
            width=2,
        )


def render(output: Path, width: int, height: int) -> None:
    random.seed(12)
    image = Image.new("RGBA", (width, height), (5, 5, 7, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    for y in range(height):
        t = y / max(height - 1, 1)
        shade = int(7 - t * 2)
        draw.line((0, y, width, y), fill=(shade, shade, 10, 255))

    add_glow(image, (width * 0.5, height * 0.18), width * 0.22, (140, 124, 255), 72)
    add_glow(image, (width * 0.52, height * 0.48), width * 0.26, (245, 121, 185), 84)
    add_glow(image, (width * 0.74, height * 0.64), width * 0.16, (115, 221, 225), 58)

    draw = ImageDraw.Draw(image, "RGBA")
    for index in range(36):
        y = lerp(height * 0.13, height * 0.87, index / 35)
        wave = math.sin(index * 0.65) * 12
        alpha = random.randint(14, 28)
        draw.line((width * 0.16, y + wave, width * 0.16 + random.randint(12, 28), y + wave), fill=(241, 231, 220, alpha), width=1)
        draw.line((width * 0.84 - random.randint(12, 28), y - wave, width * 0.84, y - wave), fill=(241, 231, 220, alpha), width=1)

    for index in range(28):
        side = -1 if index % 2 == 0 else 1
        x = width * 0.5 + side * width * random.uniform(0.14, 0.33)
        y = random.uniform(height * 0.12, height * 0.88)
        length = random.uniform(26, 92)
        color = (245, 121, 185, random.randint(20, 44)) if side < 0 else (115, 221, 225, random.randint(18, 40))
        draw.line((x, y - length * 0.5, x + side * random.uniform(-16, 16), y + length * 0.5), fill=color, width=2)

    stem_points = []
    for index in range(90):
        t = index / 89
        y = lerp(height * 0.13, height * 0.87, t)
        x = specimen_center(width, t)
        stem_points.append((x, y))
    draw.line(stem_points, fill=(246, 220, 198, 96), width=max(8, int(width * 0.015)))
    draw.line(stem_points, fill=(244, 236, 228, 104), width=max(3, int(width * 0.004)))

    valve_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    valve_draw = ImageDraw.Draw(valve_layer, "RGBA")
    for index in range(9):
        t = index / 8
        radius = lerp(width * 0.08, width * 0.15, math.sin(t * math.pi))
        lift = lerp(height * 0.05, height * 0.09, math.sin(t * math.pi))
        draw_valve(valve_draw, width, height, t, radius, lift)
        add_glow(valve_layer, (specimen_center(width, t), lerp(height * 0.18, height * 0.82, t)), radius * 1.4, (246, 220, 198), 38)
    image.alpha_composite(valve_layer.filter(ImageFilter.GaussianBlur(2.6)))

    draw = ImageDraw.Draw(image, "RGBA")
    lens_x = width * 0.53
    lens_y = height * 0.44
    draw.ellipse((lens_x - 92, lens_y - 92, lens_x + 92, lens_y + 92), outline=(241, 231, 220, 58), width=2)
    draw.arc((lens_x - 58, lens_y - 58, lens_x + 58, lens_y + 58), -44, 104, fill=(241, 231, 220, 84), width=2)

    rail_x0 = width * 0.78
    rail_x1 = width * 0.94
    rail_y0 = height * 0.2
    rail_y1 = height * 0.78
    draw.rounded_rectangle((rail_x0, rail_y0, rail_x1, rail_y1), radius=26, fill=(12, 12, 17, 164), outline=(241, 231, 220, 28), width=1)
    channel_colors = ["#f579b9", "#73dde1", "#f0b06e"]
    channel_names = ["Bloom", "Curl", "Pressure"]
    for index, (name, hex_color) in enumerate(zip(channel_names, channel_colors)):
        top = rail_y0 + 22 + index * (height * 0.16)
        bottom = top + height * 0.12
        draw.rounded_rectangle((rail_x0 + 12, top, rail_x1 - 12, bottom), radius=18, fill=(255, 255, 255, 10), outline=(241, 231, 220, 20), width=1)
        draw.text((rail_x0 + 24, top + 10), name, fill=(241, 231, 220, 150))
        draw.rounded_rectangle((rail_x0 + 24, bottom - 18, rail_x1 - 24, bottom - 10), radius=6, fill=(255, 255, 255, 16))
        fill_w = (rail_x1 - rail_x0 - 48) * (0.44 + index * 0.12)
        draw.rounded_rectangle((rail_x0 + 24, bottom - 18, rail_x0 + 24 + fill_w, bottom - 10), radius=6, fill=rgba(hex_color, 180))

    for _ in range(140):
        x = random.uniform(0, width)
        y = random.uniform(0, height)
        r = random.uniform(0.8, 2.4)
        tone = random.choice(((246, 220, 198), (245, 121, 185), (115, 221, 225), (184, 240, 153)))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=tone + (random.randint(14, 42),))

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
