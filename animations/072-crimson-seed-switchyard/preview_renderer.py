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


def arch_point(start_x: float, end_x: float, base_y: float, arc: float, t: float) -> tuple[float, float]:
    x = lerp(start_x, end_x, t)
    y = base_y - math.sin(t * math.pi) * arc
    return x, y


def draw_worker(draw: ImageDraw.ImageDraw, x: float, y: float, size: float, body: tuple[int, int, int], glow: tuple[int, int, int]) -> None:
    draw.ellipse((x - size * 0.52, y - size * 1.12, x + size * 0.52, y - size * 0.12), fill=body)
    draw.ellipse((x - size * 0.18, y - size * 0.92, x - size * 0.02, y - size * 0.76), fill=(248, 244, 236))
    draw.ellipse((x + size * 0.02, y - size * 0.88, x + size * 0.18, y - size * 0.72), fill=(248, 244, 236))
    draw.ellipse((x - size * 0.13, y - size * 0.86, x - size * 0.07, y - size * 0.8), fill=(24, 19, 22))
    draw.ellipse((x + size * 0.07, y - size * 0.84, x + size * 0.13, y - size * 0.78), fill=(24, 19, 22))
    draw.arc((x - size * 0.16, y - size * 0.62, x + size * 0.16, y - size * 0.36), 14, 170, fill=(72, 42, 46), width=max(1, int(size * 0.05)))
    draw.line((x + size * 0.48, y - size * 0.7, x + size * 0.9, y - size * 1.22), fill=(238, 226, 214), width=max(1, int(size * 0.04)))
    draw.ellipse((x + size * 0.84, y - size * 1.28, x + size * 1.02, y - size * 1.1), fill=glow)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    w, h = args.width, args.height
    image = vertical_gradient((w, h), (24, 11, 18), (8, 6, 11)).convert("RGBA")
    draw = ImageDraw.Draw(image)

    add_glow(image, (w * 0.18, h * 0.2), w * 0.18, (136, 187, 199, 34), w * 0.06)
    add_glow(image, (w * 0.77, h * 0.19), w * 0.18, (239, 74, 88, 54), w * 0.05)
    add_glow(image, (w * 0.52, h * 0.74), w * 0.26, (255, 136, 104, 28), w * 0.08)

    for i in range(8):
        y = h * (0.14 + i * 0.1)
        draw.line((w * 0.06, y, w * 0.94, y - 8 + (i % 2) * 16), fill=(255, 255, 255, 8), width=1)

    arches = []
    for i in range(5):
        start_x = w * (0.06 + i * 0.16)
        end_x = start_x + w * (0.2 + (i % 2) * 0.03)
        arches.append((start_x, end_x, h * (0.42 + (i % 3) * 0.08), h * (0.08 + (i % 2) * 0.05), w * (0.038 + (i % 2) * 0.008)))

    for index, (start_x, end_x, base_y, arc, thickness) in enumerate(arches):
        points = [arch_point(start_x, end_x, base_y, arc, i / 80) for i in range(81)]
        draw.line(points, fill=(128, 55, 74, 70), width=max(1, int(thickness + 10)))
        draw.line(points, fill=(239, 74, 88, 118), width=max(1, int(thickness)))
        draw.line(points, fill=(246, 198, 162, 54), width=2)

        seed_count = 7 + (index % 3)
        for s in range(seed_count):
            t = (s + 1) / (seed_count + 1)
            x, y = arch_point(start_x, end_x, base_y, arc, t)
            radius = 8 + (s % 3)
            add_glow(image, (x, y), 34, (255, 136, 104, 88), 16)
            draw.ellipse((x - radius, y - radius * 1.1, x + radius, y + radius * 1.1), fill=(239, 74, 88, 220))
            draw.line((x, y + radius + 3, x, y + radius + 18), fill=(246, 198, 162, 70), width=2)

    draw = ImageDraw.Draw(image)
    for index, (start_x, end_x, base_y, arc, thickness) in enumerate(arches):
        a = arch_point(start_x, end_x, base_y, arc, 0.18)
        b = arch_point(start_x, end_x, base_y, arc, 0.82)
        draw.line((a[0], a[1] + thickness * 0.44, b[0], b[1] + thickness * 0.44), fill=(246, 198, 162, 70), width=3)
        if index < len(arches) - 1:
            c = arch_point(start_x, end_x, base_y, arc, 0.88)
            next_arch = arches[index + 1]
            d = arch_point(next_arch[0], next_arch[1], next_arch[2], next_arch[3], 0.12)
            draw.line((c[0], c[1] + thickness * 0.3, d[0], d[1] + next_arch[4] * 0.3), fill=(246, 198, 162, 54), width=2)

    floor = Image.new("RGBA", image.size, (0, 0, 0, 0))
    floor_draw = ImageDraw.Draw(floor)
    for y in range(int(h * 0.64), h):
        t = (y - h * 0.64) / max(1, h * 0.36)
        color = tuple(int(lerp(a, b, t)) for a, b in zip((54, 15, 25), (8, 8, 11)))
        floor_draw.line((0, y, w, y), fill=color + (220,))
    floor = floor.filter(ImageFilter.GaussianBlur(radius=1.5))
    image.alpha_composite(floor)

    draw = ImageDraw.Draw(image)
    worker_specs = [
        (0, 0.16, 18, (243, 231, 218), (255, 136, 104)),
        (1, 0.34, 20, (246, 198, 162), (255, 136, 104)),
        (2, 0.55, 18, (243, 231, 218), (246, 198, 162)),
        (3, 0.42, 21, (246, 198, 162), (239, 74, 88)),
        (4, 0.72, 17, (243, 231, 218), (255, 136, 104)),
    ]
    for lane, along, size, body, glow in worker_specs:
        arch = arches[lane]
        x, y = arch_point(arch[0], arch[1], arch[2], arch[3], along)
        add_glow(image, (x, y - size * 0.6), 26, glow + (60,), 13)
        draw_worker(draw, x, y + arch[4] * 0.42, size, body, glow)

    spark_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    spark_draw = ImageDraw.Draw(spark_layer)
    for i in range(72):
        x = w * (0.08 + ((i * 0.061) % 0.84))
        y = h * (0.1 + ((i * 0.043) % 0.7))
        r = 1 + (i % 3)
        spark_draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 160, 118, 100))
    spark_layer = spark_layer.filter(ImageFilter.GaussianBlur(radius=1.4))
    image.alpha_composite(spark_layer)

    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((38, 38, 382, 402), radius=30, fill=(12, 11, 17, 214), outline=(255, 255, 255, 24), width=1)
    draw.text((62, 68), "#072 Crimson Seed", fill=(243, 231, 218))
    draw.text((62, 108), "semi-transparent inhabited switchyard", fill=(243, 231, 218, 208))
    draw.text((62, 146), "tiny caretakers + world-bound controls", fill=(243, 231, 218, 208))
    draw.rounded_rectangle((62, 208, 182, 242), radius=16, fill=(255, 255, 255, 18), outline=(255, 255, 255, 28))
    draw.text((78, 218), "EMBER FIELD", fill=(243, 231, 218))
    draw.rounded_rectangle((194, 208, 316, 242), radius=16, fill=(255, 255, 255, 18), outline=(255, 255, 255, 28))
    draw.text((210, 218), "LIVE CONTROLS", fill=(243, 231, 218))
    draw.multiline_text(
        (62, 272),
        "Move pointer to open nearby pods.\nClick to send one pulse convoy.\nButtons recolor the whole body.",
        fill=(243, 231, 218, 214),
        spacing=8,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
