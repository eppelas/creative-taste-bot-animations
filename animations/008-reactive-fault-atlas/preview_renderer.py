#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw


TAU = math.pi * 2.0


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


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
        frequency *= 2.03
        amplitude *= 0.5
    return value


def fault_info(nx: float, ny: float, t: float, px: float, py: float, strength: float) -> tuple[float, float, float, float, float, float, float]:
    base = (ny - 0.82) + nx * 0.72
    wave = (
        math.sin(nx * 7.2 + t * 0.26) * 0.06
        + math.cos(ny * 6.4 - t * 0.22) * 0.05
        + (fbm(nx * 2.4 + t * 0.03, ny * 2.7 - t * 0.04) - 0.5) * 0.22
    )
    dx = nx - px
    dy = ny - py
    dist = math.hypot(dx * 1.05, dy * 0.9)
    pull = strength * math.exp(-((dist / 0.18) ** 2))
    side = 1.0 if (base + wave) >= 0.0 else -1.0
    shear = pull * side * 0.11
    center = base + wave + shear
    width_bias = 0.108 + pull * 0.12
    density = math.exp(-((center / width_bias) ** 2))
    grain = fbm(nx * 11.0 + t * 0.18, ny * 11.0 - t * 0.16)
    spark = fbm(nx * 26.0 - t * 0.35, ny * 26.0 + t * 0.32)
    angle = (
        -0.88
        + math.sin((nx + ny) * 8.0 + t * 0.3) * 0.22
        + (fbm(nx * 5.0 - t * 0.08, ny * 5.0 + t * 0.07) - 0.5) * 1.2
        + shear * 5.0
    )
    return center, density, pull, grain, spark, math.cos(angle), math.sin(angle)


def blend(base: tuple[int, int, int], top: tuple[int, int, int], alpha: float) -> tuple[int, int, int]:
    return tuple(int(round(base[i] * (1.0 - alpha) + top[i] * alpha)) for i in range(3))


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
        stripe = int(2 + v * 5)
        for x in range(width):
            pixels[x, y] = (stripe, stripe, stripe)

    glow_centers = [
        (0.70, 0.26, 0.24, (82, 8, 18), 0.16),
        (0.24, 0.80, 0.30, (56, 6, 14), 0.12),
        (0.54, 0.48, 0.72, (38, 4, 10), 0.10),
    ]
    for gy in range(height):
        ny = gy / max(height - 1, 1)
        for gx in range(width):
            base = pixels[gx, gy]
            nx = gx / max(width - 1, 1)
            color = base
            for cx, cy, radius, target, peak in glow_centers:
                dist = math.hypot((nx - cx) / radius, (ny - cy) / radius)
                if dist < 1.0:
                    alpha = (1.0 - dist) ** 2 * peak
                    color = blend(color, target, alpha)
            pixels[gx, gy] = color

    texture_count = int(clamp((width * height) / 2200.0, 260, 860))
    for i in range(texture_count):
        x = int(hash2(i, 1) * width)
        y = int(hash2(i, 2) * height)
        alpha = 10 + int(hash2(i, 3) * 10)
        draw.point((x, y), fill=(255, 244, 228, alpha))

    t = 4.6
    px = 0.62
    py = 0.46
    strength = 1.0
    step = 7 if width < 720 else 6

    for y in range(0, height, step):
        for x in range(0, width, step):
            nx = x / width
            ny = y / height
            _, density, pull, grain, spark, vx, vy = fault_info(nx, ny, t, px, py, strength)
            if density < 0.06:
                continue

            threshold = 0.22 + (1.0 - density) * 0.34
            if grain < threshold and spark < 0.74:
                continue

            warp = pull * 28.0
            px2 = x + vx * warp + (grain - 0.5) * step * 1.8
            py2 = y + vy * warp + (spark - 0.5) * step * 1.8
            hot = clamp(density * 1.15 + pull * 0.9, 0.0, 1.8)
            alpha = int(clamp(0.1 + hot * 0.54 + (spark - 0.5) * 0.2, 0.08, 0.9) * 255)
            size = step * (0.94 if spark > 0.94 else 0.8 if spark > 0.82 else 0.52)

            if spark > 0.94:
                fill = (255, 244, 230, int((0.28 + pull * 0.5) * 255))
            elif spark > 0.88:
                fill = (255, 170, 154, int((0.34 + pull * 0.32) * 255))
            else:
                fill = (
                    255,
                    int(34 + hot * 40),
                    int(32 + hot * 26),
                    alpha,
                )
            draw.rectangle((px2, py2, px2 + size, py2 + size), fill=fill)

    for i in range(10):
        offset = hash2(i, 11) * 0.48 - 0.24
        bend = hash2(i, 12) * 0.40 - 0.20
        phase = hash2(i, 13) * TAU
        alpha = int(18 + hash2(i, 14) * 44)
        points: list[tuple[float, float]] = []
        pointer_bend = math.sin(t * 1.2 + phase) * 80.0
        for j in range(49):
            p = j / 48.0
            x = width * (0.06 + p * 0.9)
            y = height * (
                0.92
                - p * 0.78
                + math.sin(p * 8 + t * 0.32 + phase) * 0.02
                + offset * 0.24
                + bend * math.sin(p * TAU) * 0.12
            ) + pointer_bend * math.exp(-(((p - 0.52) / 0.24) ** 2))
            points.append((x, y))
        draw.line(points, fill=(255, 62, 74, alpha), width=1)

    void_count = 8 if width < 720 else 11
    for i in range(void_count):
        p = (i + 0.9) / (void_count + 0.9)
        x = width * (0.1 + p * 0.78) + (hash2(i, 21) * 160 - 80)
        y = height * (0.9 - p * 0.76) + (hash2(i, 22) * 180 - 90)
        base_size = (28 + hash2(i, 23) * 80) if width >= 720 else (22 + hash2(i, 23) * 52)
        dx = width * px - x
        dy = height * py - y
        dist = math.hypot(dx, dy)
        react = strength * math.exp(-((dist / 180.0) ** 2))
        drift_x = math.sin(t * 0.7 + hash2(i, 24) * TAU) * 22 + dx * react * 0.08
        drift_y = math.cos(t * 0.6 + hash2(i, 25) * TAU) * 18 + dy * react * 0.08
        size = base_size * (1.0 + react * 0.42)

        left = x - size / 2 + drift_x
        top = y - size / 2 + drift_y
        right = left + size
        bottom = top + size
        draw.rectangle((left, top, right, bottom), fill=(2, 2, 2, 240))
        draw.rectangle((left - 2, top - 2, right + 2, bottom + 2), outline=(255, 86, 96, int((0.15 + react * 0.3) * 255)), width=1)
        if react > 0.08:
            cx = (left + right) / 2
            cy = (top + bottom) / 2
            glow = int(react * 0.3 * 255)
            draw.line((cx - size * 0.62, cy, cx + size * 0.62, cy), fill=(255, 244, 232, glow), width=1)
            draw.line((cx, cy - size * 0.62, cx, cy + size * 0.62), fill=(255, 244, 232, glow), width=1)

    for i in range(34):
        x = width * (0.04 + hash2(i, 31) * 0.92)
        y = height * (0.04 + hash2(i, 32) * 0.92)
        scale = 0.45 + hash2(i, 33) * 0.8
        dist = math.hypot(width * px - x, height * py - y)
        react = strength * math.exp(-((dist / 160.0) ** 2))
        alpha = int((0.10 + react * 0.45) * 255)
        size = (5 + scale * 12) * (1 + react * 0.3)
        color = (255, 242, 228, alpha) if react > 0.22 else (255, 110, 112, alpha)

        if hash2(i, 34) > 0.55:
          draw.line((x - size, y, x + size, y), fill=color, width=1)
          draw.line((x, y - size, x, y + size), fill=color, width=1)
        else:
          draw.line((x - size, y - size, x - size * 0.2, y - size), fill=color, width=1)
          draw.line((x - size, y - size, x - size, y - size * 0.2), fill=color, width=1)
          draw.line((x + size, y + size, x + size * 0.2, y + size), fill=color, width=1)
          draw.line((x + size, y + size, x + size, y + size * 0.2), fill=color, width=1)

    ring_radius = 84 + strength * 120
    draw.ellipse(
        (
            width * px - ring_radius,
            height * py - ring_radius,
            width * px + ring_radius,
            height * py + ring_radius,
        ),
        outline=(255, 74, 88, int((0.08 + strength * 0.12) * 255)),
        width=1,
    )
    draw.ellipse(
        (
            width * px - ring_radius * 0.62,
            height * py - ring_radius * 0.62,
            width * px + ring_radius * 0.62,
            height * py + ring_radius * 0.62,
        ),
        outline=(255, 244, 230, int(strength * 0.16 * 255)),
        width=1,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    print(f"rendered {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
