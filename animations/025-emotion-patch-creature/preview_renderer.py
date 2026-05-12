#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def hex_rgba(value: str, alpha: int) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def add_glow(base: Image.Image, layer: Image.Image, blur: int) -> Image.Image:
    return Image.alpha_composite(base, layer.filter(ImageFilter.GaussianBlur(blur)))


def draw_background(base: Image.Image, width: int, height: int) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse((width * 0.08, height * 0.04, width * 0.38, height * 0.3), fill=hex_rgba("#78dee4", 22))
    draw.ellipse((width * 0.58, height * 0.06, width * 0.88, height * 0.32), fill=hex_rgba("#f48cbc", 18))
    draw.ellipse((width * 0.32, height * 0.58, width * 0.7, height * 0.9), fill=hex_rgba("#988eff", 24))
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(80)))

    draw = ImageDraw.Draw(base)
    for x in range(int(width * 0.09), int(width * 0.93), int(width * 0.08)):
        draw.line((x, int(height * 0.08), x, int(height * 0.92)), fill=(100, 120, 150, 18), width=1)
    for y in range(int(height * 0.1), int(height * 0.9), int(height * 0.11)):
        draw.line((int(width * 0.08), y, int(width * 0.92), y), fill=(100, 120, 150, 18), width=1)

    for i in range(160):
        x = width * ((i * 73) % 1000) / 1000
        y = height * ((i * 97) % 1000) / 1000
        r = 1 + (i % 3)
        fill = (120, 222, 228, 36) if i % 3 == 0 else (244, 140, 188, 32) if i % 3 == 1 else (245, 222, 199, 30)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=fill)


def draw_orbitals(base: Image.Image, width: int, height: int, cx: float, cy: float, body_radius: float) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for i in range(10):
        t = i / 10
        angle = t * math.tau + 0.35
        radius = body_radius * (1.06 + t * 0.42)
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius * (0.58 + t * 0.15)
        draw.line((cx + math.cos(angle) * radius * 0.8, cy + math.sin(angle) * radius * 0.8, x, y), fill=(120, 222, 228, 54) if i % 3 == 0 else (244, 140, 188, 48), width=2 if i % 4 == 0 else 1)
        draw.rounded_rectangle((x - 5, y - 5, x + 5, y + 5), radius=2, fill=(245, 222, 199, 150) if i % 2 == 0 else (152, 142, 255, 136))
    base.alpha_composite(layer)


def draw_creature(base: Image.Image, width: int, height: int) -> None:
    cx = width * 0.49
    cy = height * 0.57
    body_radius = min(width, height) * 0.16

    halo = Image.new("RGBA", base.size, (0, 0, 0, 0))
    halo_draw = ImageDraw.Draw(halo)
    halo_draw.ellipse((cx - body_radius * 2.2, cy - body_radius * 2.1, cx + body_radius * 2.2, cy + body_radius * 2.2), fill=hex_rgba("#f2b46e", 28))
    halo_draw.ellipse((cx - body_radius * 1.8, cy - body_radius * 1.8, cx + body_radius * 1.8, cy + body_radius * 1.8), fill=hex_rgba("#f48cbc", 22))
    base.alpha_composite(halo.filter(ImageFilter.GaussianBlur(60)))

    draw_orbitals(base, width, height, cx, cy, body_radius)

    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse((cx - body_radius * 0.86, cy - body_radius * 1.12, cx + body_radius * 0.86, cy + body_radius * 1.12), fill=(245, 222, 199, 34), outline=(245, 238, 228, 88), width=3)
    draw.ellipse((cx - body_radius * 0.56, cy - body_radius * 0.76, cx - body_radius * 0.02, cy + body_radius * 0.12), fill=(120, 222, 228, 20))
    draw.ellipse((cx + body_radius * 0.02, cy - body_radius * 0.12, cx + body_radius * 0.52, cy + body_radius * 0.68), fill=(244, 140, 188, 20))

    for i in range(8):
        t = i / 7
        y = cy - body_radius * 0.82 + t * body_radius * 1.55
        w = body_radius * (0.2 + math.sin(t * math.pi) * 0.8)
        draw.arc((cx - w, y - body_radius * 0.14, cx + w, y + body_radius * 0.14), 200, 340, fill=(120, 222, 228, 56) if i % 2 == 0 else (244, 180, 110, 50), width=2)

    eye_y = cy - body_radius * 0.22
    for side, color in ((-1, (120, 222, 228, 220)), (1, (152, 142, 255, 220))):
        ex = cx + side * body_radius * 0.3
        draw.ellipse((ex - body_radius * 0.17, eye_y - body_radius * 0.22, ex + body_radius * 0.17, eye_y + body_radius * 0.22), fill=(245, 238, 228, 230))
        draw.ellipse((ex - body_radius * 0.07, eye_y - body_radius * 0.1, ex + body_radius * 0.08, eye_y + body_radius * 0.11), fill=color)
        draw.ellipse((ex - body_radius * 0.026, eye_y - body_radius * 0.038, ex + body_radius * 0.026, eye_y + body_radius * 0.038), fill=(8, 16, 24, 255))
        draw.arc((ex - body_radius * 0.18, eye_y - body_radius * 0.3, ex + body_radius * 0.18, eye_y + body_radius * 0.08), 195, 344, fill=(8, 16, 24, 180), width=3)

    mouth_y = cy + body_radius * 0.3
    draw.arc((cx - body_radius * 0.36, mouth_y - body_radius * 0.1, cx + body_radius * 0.36, mouth_y + body_radius * 0.14), 18, 162, fill=(245, 238, 228, 190), width=3)
    draw.ellipse((cx - body_radius * 0.65, cy + body_radius * 0.02, cx - body_radius * 0.32, cy + body_radius * 0.22), fill=(244, 140, 188, 44))
    draw.ellipse((cx + body_radius * 0.32, cy + body_radius * 0.02, cx + body_radius * 0.65, cy + body_radius * 0.22), fill=(244, 140, 188, 44))

    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(10)))
    base.alpha_composite(layer)

    draw = ImageDraw.Draw(base)
    for side, count in ((-1, 3), (1, 4)):
        paw_x = cx + side * width * 0.15
        paw_y = cy + height * 0.15
        palm_w = width * 0.055
        palm_h = height * 0.09
        draw.line((cx + side * width * 0.05, cy + height * 0.1, paw_x, paw_y), fill=(244, 180, 110, 60) if side < 0 else (120, 222, 228, 60), width=3)
        draw.ellipse((paw_x - palm_w * 0.9, paw_y - palm_h, paw_x + palm_w * 0.9, paw_y + palm_h), fill=(245, 222, 199, 30), outline=(245, 238, 228, 78), width=2)
        for i in range(count):
            offset = (i - (count - 1) * 0.5) * palm_w * 0.42
            draw.line((paw_x + offset, paw_y - palm_h * 0.48, paw_x + offset + side * palm_w * (0.22 + 0.04 * i), paw_y - palm_h * (1.24 + 0.05 * i)), fill=(245, 238, 228, 78), width=2)

    draw.line((cx, cy + body_radius * 1.12, cx - width * 0.014, height * 0.92), fill=(245, 238, 228, 46), width=3)


def draw_hud(base: Image.Image, width: int, height: int) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    left = (40, 38, int(width * 0.39), int(height * 0.29))
    right = (int(width * 0.72), 54, width - 36, int(height * 0.37))
    for box in (left, right):
      draw.rounded_rectangle(box, radius=28, fill=(13, 16, 26, 178), outline=(245, 238, 228, 36), width=2)

    colors = [
        (120, 222, 228, 80),
        (244, 140, 188, 70),
        (245, 222, 199, 64),
        (152, 142, 255, 70),
    ]
    for i in range(4):
        y0 = 110 + i * 92
        draw.rounded_rectangle((right[0] + 16, y0, right[2] - 16, y0 + 72), radius=18, fill=(255, 255, 255, 10), outline=(245, 238, 228, 22), width=1)
        draw.rectangle((right[0] + 26, y0 + 20, right[0] + 48, y0 + 42), fill=colors[i])

    base.alpha_composite(layer)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    width = args.width
    height = args.height

    base = Image.new("RGBA", (width, height), "#07080d")
    draw_background(base, width, height)
    draw_creature(base, width, height)
    draw_hud(base, width, height)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
