#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw


TAU = math.pi * 2.0


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def hash2(x: float, y: float) -> float:
    value = math.sin(x * 127.1 + y * 311.7) * 43758.5453123
    return value - math.floor(value)


def noise(x: float, y: float) -> float:
    ix = math.floor(x)
    iy = math.floor(y)
    fx = x - ix
    fy = y - iy
    a = hash2(ix, iy)
    b = hash2(ix + 1, iy)
    c = hash2(ix, iy + 1)
    d = hash2(ix + 1, iy + 1)
    ux = fx * fx * (3.0 - 2.0 * fx)
    uy = fy * fy * (3.0 - 2.0 * fy)
    return (
        a * (1.0 - ux) * (1.0 - uy)
        + b * ux * (1.0 - uy)
        + c * (1.0 - ux) * uy
        + d * ux * uy
    )


def fbm(x: float, y: float) -> float:
    value = 0.0
    amplitude = 0.5
    frequency = 1.0
    for _ in range(4):
        value += noise(x * frequency, y * frequency) * amplitude
        frequency *= 2.02
        amplitude *= 0.5
    return value


def field_at(nx: float, ny: float, t: float) -> tuple[float, float]:
    base = (ny - 0.5) - (nx - 0.5) * 0.92
    curve = (
        math.sin(nx * 6.8 + t * 0.22) * 0.08
        + math.sin(ny * 5.4 - t * 0.18) * 0.07
        + (fbm(nx * 2.4 + t * 0.035, ny * 2.6 - t * 0.03) - 0.5) * 0.22
    )
    center = base + curve
    density = math.exp(-((center / 0.125) ** 2))
    return center, density


def blend(base: tuple[int, int, int], top: tuple[int, int, int], alpha: float) -> tuple[int, int, int]:
    return tuple(
        int(round(base[i] * (1.0 - alpha) + top[i] * alpha))
        for i in range(3)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    width = args.width
    height = args.height
    image = Image.new("RGB", (width, height), (2, 2, 2))
    pixels = image.load()
    draw = ImageDraw.Draw(image, "RGBA")

    for y in range(height):
      v = y / max(height - 1, 1)
      stripe = int(2 + v * 6)
      for x in range(width):
          pixels[x, y] = (stripe, stripe, stripe)

    glow_centers = [
        (0.74, 0.24, 0.22, (82, 8, 18)),
        (0.24, 0.78, 0.28, (56, 6, 14)),
        (0.56, 0.52, 0.72, (44, 4, 10)),
    ]
    for gy in range(height):
        ny = gy / max(height - 1, 1)
        for gx in range(width):
            base = pixels[gx, gy]
            nx = gx / max(width - 1, 1)
            color = base
            for cx, cy, radius, target in glow_centers:
                dist = math.hypot((nx - cx) / radius, (ny - cy) / radius)
                if dist < 1.0:
                    alpha = (1.0 - dist) ** 2 * (0.18 if target[0] > 60 else 0.08)
                    color = blend(color, target, alpha)
            pixels[gx, gy] = color

    texture_count = clamp((width * height) / 1800.0, 280, 860)
    for i in range(int(texture_count)):
        x = int(hash2(i, 1) * width)
        y = int(hash2(i, 2) * height)
        alpha = 12 + int(hash2(i, 3) * 10)
        draw.point((x, y), fill=(255, 244, 228, alpha))

    t = 3.8
    step = 9 if width < 720 else 8
    dot_size = 2 if width < 720 else 2

    for y in range(0, height, step):
        for x in range(0, width, step):
            nx = x / width
            ny = y / height
            _, density = field_at(nx, ny, t)
            if density < 0.05:
                continue
            advect = fbm(nx * 8 + t * 0.24, ny * 8 - t * 0.18)
            grit = fbm(nx * 16 - t * 0.12, ny * 16 + t * 0.1)
            pulse = 0.55 + math.sin(t * 2.1 + nx * 9 + ny * 7) * 0.45
            active = density * (0.55 + advect * 0.8) * pulse
            if active < 0.12 or grit < 0.3:
                continue

            dx = int(round((advect - 0.5) * step * 1.4))
            dy = int(round((grit - 0.5) * step * 1.2))
            size = dot_size + int(round(density * 2 + (1 if grit > 0.84 else 0)))
            px = x + dx
            py = y + dy

            if grit > 0.965 or (density > 0.62 and advect > 0.9):
                fill = (255, 246, 236, int(70 + density * 150))
            else:
                fill = (
                    186 + int(grit * 60),
                    18 + int(advect * 34),
                    26 + int(density * 24),
                    int(36 + active * 128),
                )
            draw.rectangle((px, py, px + size, py + size), fill=fill)

    for i in range(11):
        offset = hash2(i, 11) * 0.44 - 0.22
        bend = hash2(i, 12) * 0.36 - 0.18
        phase = hash2(i, 13) * TAU
        alpha = int(20 + hash2(i, 14) * 48)
        points: list[tuple[float, float]] = []
        for j in range(73):
            p = j / 72.0
            x = width * (0.06 + p * 0.88)
            base = 0.86 - p * 0.72
            y = height * (
                base
                + offset
                + math.sin(p * 6 + t * 0.24 + phase) * 0.04
                + math.sin(p * 3.2 + phase) * bend
            )
            points.append((x, y))
        draw.line(points, fill=(255, 56, 72, alpha), width=1)

    void_count = 7 if width < 720 else 10
    for i in range(void_count):
        p = (i + 0.8) / (void_count + 0.8)
        x = width * (0.15 + p * 0.7) + (hash2(i, 21) * 140 - 70)
        y = height * (0.82 - p * 0.62) + (hash2(i, 22) * 180 - 90)
        size = (40 + hash2(i, 23) * 70) if width >= 720 else (28 + hash2(i, 23) * 52)
        draw.rectangle((x - size / 2, y - size / 2, x + size / 2, y + size / 2), fill=(4, 4, 4, 240))
        draw.rectangle((x - size / 2, y - size / 2, x + size / 2, y + size / 2), outline=(255, 240, 230, 26), width=1)

    for i in range(28):
        x = width * (0.04 + hash2(i, 31) * 0.92)
        y = height * (0.04 + hash2(i, 32) * 0.92)
        scale = 0.5 + hash2(i, 33) * 0.8
        if hash2(i, 34) > 0.58:
            s = 8 * scale
            draw.line((x - s, y, x + s, y), fill=(255, 184, 96, 180), width=1)
            draw.line((x, y - s, x, y + s), fill=(255, 184, 96, 180), width=1)
            if scale > 1.1:
                draw.rectangle((x - 1, y - 1, x + 1, y + 1), fill=(255, 246, 234, 200))
        else:
            count = 7 + int(scale * 4)
            for j in range(count):
                draw.rectangle((x, y + j * 6, x + 10 * scale, y + j * 6 + 1), fill=(255, 106, 124, 160))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    print(f"rendered {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
