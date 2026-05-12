#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def vertical_gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(image)
    for y in range(height):
      t = y / max(1, height - 1)
      color = tuple(int(lerp(top[i], bottom[i], t)) for i in range(3))
      draw.line((0, y, width, y), fill=color)
    return image


def add_glow(base: Image.Image, center: tuple[float, float], radius: float, color: tuple[int, int, int, int], blur: float) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=blur))
    base.alpha_composite(layer)


def draw_creature(draw: ImageDraw.ImageDraw, x: float, y: float, size: float, color: tuple[int, int, int], prop: str) -> None:
    body_w = size * 0.72
    body_h = size * 1.02
    draw.ellipse((x - body_w * 0.55, y - body_h * 0.86, x + body_w * 0.55, y + body_h * 0.2), fill=color)
    draw.ellipse((x - body_w * 0.26, y - body_h * 0.24, x - body_w * 0.02, y + body_h * 0.02), fill=(248, 245, 237))
    draw.ellipse((x + body_w * 0.02, y - body_h * 0.28, x + body_w * 0.26, y - body_h * 0.02), fill=(248, 245, 237))
    draw.ellipse((x - body_w * 0.18, y - body_h * 0.16, x - body_w * 0.08, y - body_h * 0.06), fill=(26, 34, 44))
    draw.ellipse((x + body_w * 0.1, y - body_h * 0.2, x + body_w * 0.2, y - body_h * 0.1), fill=(26, 34, 44))
    draw.arc((x - body_w * 0.16, y - body_h * 0.02, x + body_w * 0.16, y + body_h * 0.18), 12, 170, fill=(55, 42, 38), width=max(1, int(size * 0.03)))
    draw.line((x - body_w * 0.18, y + body_h * 0.18, x - body_w * 0.26, y + body_h * 0.56), fill=(26, 34, 44), width=max(1, int(size * 0.05)))
    draw.line((x + body_w * 0.18, y + body_h * 0.18, x + body_w * 0.26, y + body_h * 0.56), fill=(26, 34, 44), width=max(1, int(size * 0.05)))

    if prop in {"flag", "banner"}:
        draw.line((x + body_w * 0.54, y - body_h * 0.22, x + body_w * 0.82, y - body_h * 0.82), fill=(239, 232, 221), width=max(1, int(size * 0.04)))
        fill = (241, 194, 110) if prop == "flag" else (231, 163, 128)
        draw.polygon(
            [
                (x + body_w * 0.82, y - body_h * 0.82),
                (x + body_w * 1.12, y - body_h * 0.74),
                (x + body_w * 0.94, y - body_h * 0.48),
                (x + body_w * 0.82, y - body_h * 0.52),
            ],
            fill=fill,
        )
    elif prop == "lantern":
        draw.line((x + body_w * 0.52, y - body_h * 0.12, x + body_w * 0.82, y - body_h * 0.44), fill=(239, 232, 221), width=max(1, int(size * 0.04)))
        draw.rounded_rectangle(
            (x + body_w * 0.72, y - body_h * 0.58, x + body_w * 0.94, y - body_h * 0.36),
            radius=size * 0.08,
            fill=(241, 194, 110),
        )
    elif prop == "pole":
        draw.line((x - body_w * 0.52, y - body_h * 0.08, x - body_w * 0.76, y - body_h * 0.84), fill=(239, 232, 221), width=max(1, int(size * 0.04)))
    elif prop == "drum":
        draw.ellipse((x + body_w * 0.5, y - body_h * 0.04, x + body_w * 0.88, y + body_h * 0.2), fill=(241, 226, 173))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    w, h = args.width, args.height
    image = vertical_gradient((w, h), (23, 49, 81), (7, 17, 29)).convert("RGBA")
    draw = ImageDraw.Draw(image)

    add_glow(image, (w * 0.78, h * 0.16), w * 0.03, (255, 229, 173, 220), w * 0.01)
    add_glow(image, (w * 0.78, h * 0.16), w * 0.12, (255, 196, 126, 90), w * 0.04)

    draw.ellipse((w * 0.75, h * 0.13, w * 0.81, h * 0.19), fill=(255, 234, 188))

    for i in range(6):
        x = w * (0.18 + i * 0.11)
        y = h * (0.2 + (i % 2) * 0.03)
        draw.ellipse((x - w * 0.12, y - h * 0.02, x + w * 0.12, y + h * 0.02), fill=(255, 255, 255, 22 + i * 10))

    ridge = [
        (0, h * 0.59),
        (w * 0.11, h * 0.5),
        (w * 0.23, h * 0.57),
        (w * 0.36, h * 0.48),
        (w * 0.52, h * 0.56),
        (w * 0.7, h * 0.5),
        (w * 0.85, h * 0.58),
        (w, h * 0.52),
        (w, h),
        (0, h),
    ]
    draw.polygon(ridge, fill=(9, 20, 33))

    buildings = [
        (0.08, 0.14, 0.18, (33, 56, 79)),
        (0.24, 0.1, 0.14, (39, 71, 97)),
        (0.38, 0.13, 0.2, (35, 58, 80)),
        (0.58, 0.12, 0.15, (39, 68, 90)),
        (0.73, 0.14, 0.19, (34, 54, 77)),
    ]
    base_y = h * 0.69
    for idx, (x_rel, w_rel, h_rel, color) in enumerate(buildings):
        x = w * x_rel
        bw = w * w_rel
        bh = h * h_rel
        y = base_y - bh
        draw.rounded_rectangle((x, y, x + bw, y + bh), radius=24, fill=color)
        draw.rounded_rectangle((x + 4, y + 4, x + bw - 4, y + bh - 4), radius=20, outline=(255, 255, 255, 12))
        for row in range(3):
            for col in range(2):
                wx = x + bw * (0.22 + col * 0.32)
                wy = y + bh * (0.22 + row * 0.22)
                draw.rounded_rectangle(
                    (wx, wy, wx + bw * 0.16, wy + bh * 0.12),
                    radius=8,
                    fill=(241, 194, 110, 36 + row * 12),
                )

    arch = [
        (w * 0.12, h * 0.67),
        (w * 0.22, h * 0.45),
        (w * 0.36, h * 0.55),
        (w * 0.49, h * 0.62),
        (w * 0.61, h * 0.53),
        (w * 0.73, h * 0.43),
        (w * 0.88, h * 0.59),
    ]
    draw.line(arch, fill=(240, 232, 221, 54), width=4)

    lantern_points = []
    for i in range(11):
        x = w * (0.12 + i * 0.075 + ((i % 2) * 0.01))
        y = h * (0.22 + (i % 3) * 0.018) + math.sin(i * 0.7) * 6
        lantern_points.append((x, y))
    draw.line(lantern_points, fill=(240, 232, 221, 80), width=3)
    for i, (x, y) in enumerate(lantern_points):
        body_y = y + 18
        draw.line((x, y, x, body_y - 7), fill=(240, 232, 221, 100), width=2)
        add_glow(image, (x, body_y), 16, (241, 194, 110, 210), 12)
        add_glow(image, (x, body_y), 44, (241, 194, 110, 55), 26)
        fill = (241, 194, 110) if i % 2 == 0 else (231, 163, 128)
        draw.rounded_rectangle((x - 10, body_y - 8, x + 10, body_y + 10), radius=6, fill=fill, outline=(255, 255, 255, 40))

    banner_colors = [
        (239, 198, 111),
        (140, 184, 210),
        (136, 174, 140),
        (231, 163, 128),
        (124, 107, 148),
    ]
    for i in range(8):
        x = w * (0.12 + i * 0.11)
        y = h * (0.31 + ((i + 1) % 2) * 0.03)
        width = w * (0.08 + (i % 3) * 0.01)
        depth = h * (0.02 + (i % 2) * 0.012)
        draw.line((x - 16, y - 10, x + width + 16, y - 10), fill=(240, 232, 221, 36), width=2)
        draw.polygon(
            [
                (x, y),
                (x + width * 0.52, y + 10 + math.sin(i) * 4),
                (x + width, y + 1),
                (x + width * 0.82, y + depth),
                (x + width * 0.12, y + depth),
            ],
            fill=banner_colors[i % len(banner_colors)] + (208,),
        )

    ground_top = int(h * 0.68)
    for y in range(ground_top, h):
        t = (y - ground_top) / max(1, h - ground_top)
        color = tuple(int(lerp(a, b, t)) for a, b in zip((37, 54, 74), (11, 17, 24)))
        draw.line((0, y, w, y), fill=color)
    draw.ellipse((w * 0.23, h * 0.74, w * 0.77, h * 0.9), outline=(240, 232, 221, 20), width=2)
    draw.ellipse((w * 0.36, h * 0.77, w * 0.72, h * 0.88), outline=(240, 232, 221, 16), width=2)

    for x_rel, y_rel, w_rel, h_rel, color in [
        (0.16, 0.82, 0.06, 0.05, (140, 184, 210)),
        (0.35, 0.84, 0.08, 0.04, (231, 163, 128)),
        (0.63, 0.83, 0.06, 0.05, (136, 174, 140)),
        (0.82, 0.84, 0.07, 0.04, (124, 107, 148)),
    ]:
        draw.rounded_rectangle(
            (w * x_rel, h * y_rel, w * (x_rel + w_rel), h * (y_rel + h_rel)),
            radius=18,
            fill=color + (110,),
            outline=(240, 232, 221, 34),
        )

    creature_specs = [
        (0.2, 0.74, 70, (241, 194, 110), "flag"),
        (0.31, 0.79, 84, (140, 184, 210), "drum"),
        (0.43, 0.7, 76, (231, 163, 128), "lantern"),
        (0.56, 0.77, 82, (136, 174, 140), "banner"),
        (0.67, 0.72, 68, (241, 226, 173), "pole"),
        (0.78, 0.78, 88, (124, 107, 148), "flag"),
        (0.86, 0.68, 66, (231, 163, 128), "lantern"),
    ]
    for x_rel, y_rel, size, color, prop in creature_specs:
        draw_creature(draw, w * x_rel, h * y_rel, size, color, prop)
        draw.ellipse((w * x_rel - size * 0.86, h * y_rel + size * 0.1, w * x_rel + size * 0.86, h * y_rel + size * 0.34), outline=(255, 255, 255, 26), width=1)

    spark_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    spark_draw = ImageDraw.Draw(spark_layer)
    for i in range(42):
        x = w * (0.08 + (i * 0.021 % 0.84))
        y = h * (0.17 + ((i * 0.037) % 0.56))
        r = 2 + (i % 3)
        spark_draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 228, 162, 130))
    spark_layer = spark_layer.filter(ImageFilter.GaussianBlur(radius=1.5))
    image.alpha_composite(spark_layer)

    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((36, 36, 360, 390), radius=28, fill=(10, 19, 31, 210), outline=(255, 255, 255, 22), width=1)
    draw.text((62, 68), "#071 Lantern Yard", fill=(240, 232, 221))
    draw.text((62, 108), "story-first courtyard rehearsal", fill=(240, 232, 221, 200))
    draw.text((62, 146), "awkward creatures + lantern wave", fill=(240, 232, 221, 200))
    draw.rounded_rectangle((62, 206, 180, 240), radius=16, fill=(255, 255, 255, 20), outline=(255, 255, 255, 26))
    draw.text((76, 216), "TWILIGHT YARD", fill=(240, 232, 221))
    draw.rounded_rectangle((194, 206, 308, 240), radius=16, fill=(255, 255, 255, 20), outline=(255, 255, 255, 26))
    draw.text((208, 216), "NAIVE WORLD", fill=(240, 232, 221))
    draw.multiline_text(
        (62, 270),
        "Hover shifts nearby attention.\nClick sends one shared cue\nthrough the whole rope.",
        fill=(240, 232, 221, 212),
        spacing=8,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(args.output, quality=95)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
