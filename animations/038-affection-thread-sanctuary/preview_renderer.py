#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def lerp_color(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_gradient(width: int, height: int, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGB", (width, height), top)
    pixels = image.load()
    for y in range(height):
        color = lerp_color(top, bottom, y / max(1, height - 1))
        for x in range(width):
            pixels[x, y] = color
    return image


def draw_glow(draw: ImageDraw.ImageDraw, x: float, y: float, radius: float, color: tuple[int, int, int, int]) -> None:
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def draw_thread(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill: tuple[int, int, int, int], width: int) -> None:
    draw.line(points, fill=fill, width=width, joint="curve")


def draw_creature(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    scale: float,
    face: tuple[int, int, int],
    blush: tuple[int, int, int, int],
    body: tuple[int, int, int, int],
) -> None:
    sx = scale
    draw.ellipse((x - 64 * sx, y - 86 * sx, x + 64 * sx, y + 82 * sx), fill=body)
    draw.ellipse((x - 46 * sx, y - 118 * sx, x + 34 * sx, y - 46 * sx), fill=(244, 247, 241, 245))
    draw.ellipse((x - 28 * sx, y - 20 * sx, x + 28 * sx, y + 14 * sx), fill=blush)

    eyes = [(-20, -88), (0, -98), (18, -82)]
    for index, (ex, ey) in enumerate(eyes):
        tone = (242, 192, 127, 255) if index == 1 else face + (245,)
        draw.ellipse(
            (x + (ex - 6) * sx, y + (ey - 6) * sx, x + (ex + 6) * sx, y + (ey + 6) * sx),
            fill=tone,
        )

    draw.arc((x - 20 * sx, y - 6 * sx, x + 20 * sx, y + 18 * sx), start=15, end=165, fill=(242, 192, 127, 180), width=max(1, int(2 * sx)))

    for offset in (-18, -6, 6, 18):
        draw_thread(
            draw,
            [
                (x + offset * sx, y - 112 * sx),
                (x + (offset * 0.6) * sx, y - 158 * sx),
                (x + (offset * 0.9) * sx, y - 198 * sx),
            ],
            (222, 245, 166, 90),
            max(1, int(2 * sx)),
        )
        draw_glow(draw, x + offset * 0.9 * sx, y - 198 * sx, 4 * sx, (243, 168, 180, 85))

    for direction in (-1, 1):
        draw_thread(
            draw,
            [
                (x + 14 * direction * sx, y + 56 * sx),
                (x + 36 * direction * sx, y + 106 * sx),
                (x + 48 * direction * sx, y + 168 * sx),
            ],
            (228, 235, 228, 120),
            max(1, int(3 * sx)),
        )
        draw_thread(
            draw,
            [
                (x - 6 * direction * sx, y + 60 * sx),
                (x - 30 * direction * sx, y + 112 * sx),
                (x - 56 * direction * sx, y + 184 * sx),
            ],
            (228, 235, 228, 90),
            max(1, int(2 * sx)),
        )


def render_preview(width: int, height: int) -> Image.Image:
    base = vertical_gradient(width, height, (12, 16, 22), (4, 5, 6)).convert("RGBA")
    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow, "RGBA")

    glow_specs = [
        (width * 0.22, height * 0.18, width * 0.18, (159, 227, 221, 30)),
        (width * 0.77, height * 0.2, width * 0.2, (243, 168, 180, 28)),
        (width * 0.54, height * 0.76, width * 0.22, (223, 245, 166, 18)),
    ]
    for x, y, radius, color in glow_specs:
        draw_glow(glow_draw, x, y, radius, color)
    glow = glow.filter(ImageFilter.GaussianBlur(radius=42))
    image = Image.alpha_composite(base, glow)

    mist = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    mist_draw = ImageDraw.Draw(mist, "RGBA")
    for i in range(8):
        y = height * (0.18 + i * 0.085)
        points = []
        for step in range(16):
            x = step / 15 * width
            wave = math.sin(i * 0.7 + step * 0.45) * 18 + math.cos(i * 0.5 + step * 0.25) * 10
            points.append((x, y + wave))
        draw_thread(mist_draw, points, (191, 226, 228, 18 + i * 3), 2)
    mist = mist.filter(ImageFilter.GaussianBlur(radius=2))
    image = Image.alpha_composite(image, mist)

    draw = ImageDraw.Draw(image, "RGBA")

    bridges = [
        ((width * 0.17, height * 0.28), (width * 0.45, height * 0.58)),
        ((width * 0.44, height * 0.21), (width * 0.59, height * 0.62)),
        ((width * 0.79, height * 0.24), (width * 0.74, height * 0.57)),
    ]
    for index, (start, end) in enumerate(bridges):
        mid = ((start[0] + end[0]) * 0.5, min(start[1], end[1]) - 120 - index * 14)
        draw.line([start, mid, end], fill=(223, 245, 166, 58), width=2, joint="curve")
        for j in range(6):
            t = j / 5
            x = (1 - t) * (1 - t) * start[0] + 2 * (1 - t) * t * mid[0] + t * t * end[0]
            y = (1 - t) * (1 - t) * start[1] + 2 * (1 - t) * t * mid[1] + t * t * end[1]
            draw_glow(draw, x, y, 5, (243, 168, 180, 46))

    floor_y = int(height * 0.82)
    floor = [(0, floor_y)]
    for step in range(28):
        x = step / 27 * width
        wave = math.sin(step * 0.42) * 10 + math.cos(step * 0.24) * 8
        floor.append((x, floor_y + wave))
    floor.extend([(width, height), (0, height)])
    draw.polygon(floor, fill=(10, 12, 14, 220))

    creatures = [
        (width * 0.28, height * 0.67, 0.86, (159, 227, 221)),
        (width * 0.43, height * 0.61, 1.08, (243, 168, 180)),
        (width * 0.58, height * 0.65, 0.96, (223, 245, 166)),
        (width * 0.73, height * 0.58, 0.8, (159, 227, 221)),
    ]
    for x, y, scale, face in creatures:
        draw_creature(
            draw,
            x,
            y,
            scale,
            face,
            (243, 168, 180, 42),
            (244, 247, 241, 205),
        )

    for left, right in zip(creatures, creatures[1:]):
        start = (left[0] + 16, left[1] - 12)
        end = (right[0] - 16, right[1] - 12)
        mid = ((start[0] + end[0]) * 0.5, min(start[1], end[1]) - 70)
        draw.line([start, mid, end], fill=(223, 245, 166, 54), width=2, joint="curve")

    wake = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    wake_draw = ImageDraw.Draw(wake, "RGBA")
    center = (width * 0.56, height * 0.55)
    for radius, alpha in ((88, 38), (128, 26), (170, 14)):
        wake_draw.ellipse(
            (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
            outline=(223, 245, 166, alpha),
            width=2,
        )
    draw_glow(wake_draw, center[0], center[1], 120, (242, 192, 127, 32))
    wake = wake.filter(ImageFilter.GaussianBlur(radius=10))
    image = Image.alpha_composite(image, wake)

    return image.convert("RGB")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    image = render_preview(args.width, args.height)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output, format="PNG")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
