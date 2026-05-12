#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


def hex_rgba(value: str, alpha: int) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def add_glow(base: Image.Image, shape: Image.Image, blur: int) -> Image.Image:
    return Image.alpha_composite(base, shape.filter(ImageFilter.GaussianBlur(blur)))


def draw_grid(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    for x in range(int(width * 0.16), int(width * 0.85), int(width * 0.085)):
        draw.line((x, int(height * 0.08), x, int(height * 0.94)), fill=(90, 116, 150, 20), width=1)
    for y in range(int(height * 0.12), int(height * 0.9), int(height * 0.11)):
        draw.line((int(width * 0.12), y, int(width * 0.88), y), fill=(90, 116, 150, 18), width=1)


def draw_spine(base: Image.Image, width: int, height: int) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    x = width * 0.5
    top = height * 0.08
    bottom = height * 0.94
    colors = [
        hex_rgba("#8f83ff", 120),
        hex_rgba("#ef78bb", 128),
        hex_rgba("#f6dfca", 136),
        hex_rgba("#72dde4", 128),
        hex_rgba("#f0ab63", 120),
    ]
    points = []
    for i in range(13):
        t = i / 12
        y = bottom + (top - bottom) * t
        sway = math.sin(t * 7.1) * width * 0.005
        points.append((x + sway, y))
    for idx, color in enumerate(colors):
        glow_draw.line(points, fill=color, width=int(width * (0.018 - idx * 0.0023)), joint="curve")
    draw = ImageDraw.Draw(base)
    draw.line(points, fill=(250, 241, 232, 165), width=max(2, int(width * 0.0035)), joint="curve")


def membrane_points(cx: float, cy: float, rx: float, ry: float, side: int, openness: float) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for i in range(28):
        t = i / 27
        angle = math.pi * (0.15 + t * 0.7)
        flare = 1.0 + math.sin(t * math.pi) * openness * 0.54
        x = cx + math.cos(angle * side) * rx * flare
        y = cy - math.sin(angle) * ry * (0.74 + t * 0.4)
        points.append((x, y))
    points.extend(
        [
            (cx + side * rx * 0.48, cy + ry * 0.22),
            (cx + side * rx * 0.14, cy + ry * 0.58),
            (cx, cy + ry * 0.9),
        ]
    )
    return points


def draw_organ(base: Image.Image, width: int, height: int, cx: float, cy: float, rx: float, ry: float, openness: float) -> None:
    organ = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(organ)
    left = membrane_points(cx, cy, rx, ry, -1, openness)
    right = membrane_points(cx, cy, rx, ry, 1, openness)
    fill_a = hex_rgba("#f6dfca", 28)
    fill_b = hex_rgba("#ef78bb", 30)
    outline = (252, 244, 236, 90)
    draw.polygon(left, fill=fill_a, outline=outline)
    draw.polygon(right, fill=fill_b, outline=outline)
    for rib in range(10):
        t = rib / 9
        x = cx + (t - 0.5) * rx * 1.6
        y = cy - ry * 0.06 + math.sin(t * math.pi * 2) * ry * 0.05
        draw.line((cx, cy + ry * 0.58, x, y), fill=(248, 240, 232, 48), width=1)
    draw.ellipse((cx - rx * 0.12, cy + ry * 0.02, cx + rx * 0.12, cy + ry * 0.44), fill=(248, 240, 232, 70))
    base.alpha_composite(organ.filter(ImageFilter.GaussianBlur(8)))
    base.alpha_composite(organ)


def draw_pods(base: Image.Image, width: int, height: int, anchors: list[tuple[float, float]]) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for index, (ax, ay) in enumerate(anchors):
        side = -1 if index % 2 == 0 else 1
        x = ax + side * width * (0.18 + 0.025 * (index % 3))
        y = ay + height * (-0.03 + 0.025 * (index % 4))
        r = width * (0.015 + 0.003 * (index % 3))
        draw.line((ax + side * width * 0.03, ay + height * 0.02, x, y), fill=(240, 171, 99, 84) if side < 0 else (114, 221, 228, 84), width=2)
        draw.ellipse((x - r * 2.2, y - r * 2.2, x + r * 2.2, y + r * 2.2), fill=(246, 223, 202, 22))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(26, 26, 36, 180), outline=(248, 240, 232, 112))
        draw.ellipse((x - r * 0.42, y - r * 0.42, x + r * 0.42, y + r * 0.42), outline=(248, 240, 232, 88))
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(4)))
    base.alpha_composite(layer)


def draw_diagnostics(base: Image.Image, width: int, height: int) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for i in range(22):
        side = -1 if i % 2 == 0 else 1
        x = width * 0.5 + side * width * (0.18 + 0.012 * (i % 6))
        y = height * (0.11 + 0.036 * i)
        draw.line((x - side * width * 0.018, y - height * 0.032, x + side * width * 0.01, y + height * 0.032), fill=(114, 221, 228, 44) if side > 0 else (240, 171, 99, 44), width=1)
        draw.rectangle((x - 2, y - 2, x + 2, y + 2), fill=(239, 120, 187, 120) if i % 3 == 0 else (114, 221, 228, 112))
    for i in range(6):
        y = height * (0.13 + i * 0.14)
        x = width * (0.2 if i % 2 == 0 else 0.8)
        r = width * (0.015 + 0.004 * (i % 3))
        draw.ellipse((x - r, y - r, x + r, y + r), outline=(239, 120, 187, 80) if i % 2 == 0 else (114, 221, 228, 80), width=2)
        draw.ellipse((x - r * 0.45, y - r * 0.45, x + r * 0.45, y + r * 0.45), outline=(240, 171, 99, 70), width=1)
    base.alpha_composite(layer)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    width = args.width
    height = args.height

    base = Image.new("RGBA", (width, height), "#06070c")
    background_glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(background_glow)
    glow_draw.ellipse((width * 0.36, height * 0.02, width * 0.64, height * 0.23), fill=hex_rgba("#8f83ff", 32))
    glow_draw.ellipse((width * 0.18, height * 0.18, width * 0.46, height * 0.44), fill=hex_rgba("#72dde4", 18))
    glow_draw.ellipse((width * 0.54, height * 0.45, width * 0.84, height * 0.72), fill=hex_rgba("#ef78bb", 20))
    base = add_glow(base, background_glow, 70)

    draw = ImageDraw.Draw(base)
    draw_grid(draw, width, height)
    draw_spine(base, width, height)

    organ_specs = [
      (0.5, 0.18, 0.17, 0.095, 0.70),
      (0.5, 0.31, 0.23, 0.11, 0.76),
      (0.5, 0.49, 0.18, 0.095, 0.62),
      (0.5, 0.66, 0.12, 0.09, 0.48),
      (0.5, 0.81, 0.09, 0.12, 0.56),
    ]
    anchors: list[tuple[float, float]] = []
    for x_norm, y_norm, rx_norm, ry_norm, openness in organ_specs:
        cx = width * x_norm
        cy = height * y_norm
        draw_organ(base, width, height, cx, cy, width * rx_norm, height * ry_norm, openness)
        anchors.append((cx, cy))

    draw_pods(base, width, height, anchors)
    draw_diagnostics(base, width, height)

    root = Image.new("RGBA", base.size, (0, 0, 0, 0))
    root_draw = ImageDraw.Draw(root)
    cx = width * 0.5
    cy = height * 0.9
    root_draw.ellipse((cx - width * 0.12, cy - width * 0.12, cx + width * 0.12, cy + width * 0.12), fill=hex_rgba("#8f83ff", 18))
    for i in range(16):
        angle = math.pi * (1.15 + i / 15 * 0.7)
        length = width * (0.05 + (i % 5) * 0.013)
        root_draw.line((cx, cy, cx + math.cos(angle) * length, cy + math.sin(angle) * height * 0.09), fill=(114, 221, 228, 64), width=2)
    base = add_glow(base, root, 28)
    base.alpha_composite(root)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
