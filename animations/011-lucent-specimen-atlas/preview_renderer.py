#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


def rgba(hex_color: str, alpha: int) -> tuple[int, int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def bezier_points(p0, p1, p2, p3, steps=80):
    points = []
    for i in range(steps + 1):
        t = i / steps
        mt = 1 - t
        x = (
            mt**3 * p0[0]
            + 3 * mt**2 * t * p1[0]
            + 3 * mt * t**2 * p2[0]
            + t**3 * p3[0]
        )
        y = (
            mt**3 * p0[1]
            + 3 * mt**2 * t * p1[1]
            + 3 * mt * t**2 * p2[1]
            + t**3 * p3[1]
        )
        points.append((x, y))
    return points


def draw_radial(image: Image.Image, center_x: float, center_y: float, radius: float, color: tuple[int, int, int], alpha: int):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    steps = 9
    for i in range(steps, 0, -1):
        frac = i / steps
        r = radius * frac
        a = int(alpha * frac * frac * 0.6)
        draw.ellipse((center_x - r, center_y - r, center_x + r, center_y + r), fill=color + (a,))
    image.alpha_composite(overlay)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    width = args.width
    height = args.height
    cx = width * 0.5

    random.seed(11)

    base = Image.new("RGBA", (width, height), (5, 5, 6, 255))
    draw_radial(base, cx, height * 0.18, width * 0.18, (162, 118, 255), 52)
    draw_radial(base, cx, height * 0.5, width * 0.22, (240, 107, 164), 64)
    draw_radial(base, width * 0.72, height * 0.66, width * 0.12, (120, 216, 216), 38)

    grid = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    g = ImageDraw.Draw(grid)
    for x in range(int(width * 0.1), int(width * 0.91), int(width * 0.09)):
        g.line((x, height * 0.05, x, height * 0.95), fill=(110, 150, 185, 18), width=1)
    for y in range(int(height * 0.08), int(height * 0.93), int(height * 0.11)):
        g.line((width * 0.1, y, width * 0.9, y), fill=(110, 150, 185, 18), width=1)
    base.alpha_composite(grid)

    arcs = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    a = ImageDraw.Draw(arcs)
    for i in range(8):
        bbox = (
            cx - width * (0.12 + i * 0.04),
            height * (0.06 + i * 0.08),
            cx + width * (0.12 + i * 0.04),
            height * (0.24 + i * 0.08),
        )
        a.arc(bbox, start=195, end=345, fill=(226, 170, 100, 38), width=1)
    base.alpha_composite(arcs)

    stem = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    s = ImageDraw.Draw(stem)
    stem_points = []
    for i in range(180):
        t = i / 179
        y = lerp(height * 0.12, height * 0.9, t)
        offset = math.sin(t * 8.2) * width * 0.01 + math.sin(t * 17.0) * width * 0.003
        stem_points.append((cx + offset, y))
    s.line(stem_points, fill=(245, 205, 188, 120), width=int(width * 0.025))
    s.line(stem_points, fill=(255, 242, 236, 130), width=int(width * 0.007))
    for i in range(22):
        y = lerp(height * 0.16, height * 0.86, i / 21)
        span = width * random.uniform(0.03, 0.09)
        wave = math.sin(i * 0.4) * width * 0.03
        color = (226, 170, 100, 84) if i % 3 == 0 else (120, 216, 216, 52)
        s.arc((cx - span, y - 10, cx + span, y + 10), 190, 350, fill=color, width=1)
        s.line((cx - span, y, cx + wave, y + 3, cx + span, y), fill=color, width=1)
    stem = stem.filter(ImageFilter.GaussianBlur(1.2))
    base.alpha_composite(stem)

    petals = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(petals)
    seeds = [
        (0.18, 0.32, 0.17, -0.14),
        (0.28, 0.2, 0.18, -0.08),
        (0.4, 0.28, 0.22, 0.04),
        (0.52, 0.18, 0.15, 0.06),
        (0.74, 0.12, 0.12, 0.12),
    ]
    fills = [
        ((255, 225, 208, 32), (240, 107, 164, 42), (120, 216, 216, 28)),
        ((255, 225, 208, 28), (226, 170, 100, 38), (120, 216, 216, 26)),
    ]
    for idx, seed in enumerate(seeds):
        base_y = height * (0.12 + 0.78 * seed[0])
        petal_w = width * seed[1]
        petal_h = height * seed[2]
        lift = height * seed[3]
        for side in (-1, 1):
            tip = (cx + side * petal_w, base_y + lift)
            upper = bezier_points(
                (cx, base_y),
                (cx + side * petal_w * 0.34, base_y - petal_h * 0.18),
                (cx + side * petal_w * 0.74, base_y - petal_h * 0.6),
                tip,
            )
            lower = bezier_points(
                tip,
                (tip[0] - side * petal_w * 0.14, tip[1] + petal_h * 0.28),
                (cx + side * petal_w * 0.18, base_y + petal_h * 0.2),
                (cx, base_y),
            )
            shape = upper + lower
            choice = fills[idx % len(fills)]
            pdraw.polygon(shape, fill=choice[1])
            pdraw.line(shape, fill=(255, 241, 229, 74), width=2)
            for vein_index in range(1, 5):
                t = vein_index / 5
                end = upper[min(int(t * (len(upper) - 1)), len(upper) - 1)]
                ctrl = (cx + side * petal_w * (0.28 + t * 0.2), base_y - petal_h * (0.12 + t * 0.08))
                points = bezier_points((cx + side * petal_w * 0.03, base_y), ctrl, ctrl, end, steps=36)
                pdraw.line(points, fill=choice[2], width=1)
    petals = petals.filter(ImageFilter.GaussianBlur(2.0))
    base.alpha_composite(petals)

    crown = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(crown)
    top = height * 0.1
    for i in range(11):
        spread = (i - 5) * width * 0.01
        points = bezier_points(
            (cx + spread * 0.3, top + height * 0.1),
            (cx + spread, top + height * 0.05 + i * 2),
            (cx + spread * 0.9, top + height * 0.015),
            (cx + spread * 0.7, top),
            steps=50,
        )
        color = (240, 107, 164, 92) if i % 2 == 0 else (161, 117, 255, 88)
        cdraw.line(points, fill=color, width=2)
    crown = crown.filter(ImageFilter.GaussianBlur(1))
    base.alpha_composite(crown)

    pods = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(pods)
    pod_specs = [
        (0.62, 0.22, 26),
        (0.56, 0.27, 18),
        (0.72, 0.25, 22),
        (0.79, 0.14, 34),
        (0.82, -0.16, 18),
    ]
    for idx, (yy, side_offset, radius) in enumerate(pod_specs):
        x = cx + width * side_offset
        y = height * yy
        odraw.line(
            [(cx + width * 0.05 * (1 if side_offset > 0 else -1), y + 18), (x, y)],
            fill=(226, 170, 100, 72),
            width=2,
        )
        color = (255, 242, 232, 84) if idx % 2 == 0 else (120, 216, 216, 58)
        odraw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(40, 28, 38, 80), outline=color, width=2)
        odraw.ellipse((x - radius * 0.4, y - radius * 0.5, x - radius * 0.05, y - radius * 0.1), fill=(255, 240, 232, 66))
    pods = pods.filter(ImageFilter.GaussianBlur(0.6))
    base.alpha_composite(pods)

    root = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(root)
    for i in range(28):
        side = -1 if i % 2 == 0 else 1
        length = width * (0.12 + (i % 6) * 0.02)
        y = height * 0.9
        points = bezier_points(
            (cx, y),
            (cx + side * length * 0.15, y + 10),
            (cx + side * length * 0.7, y + 26 + i * 1.3),
            (cx + side * length, y + 40 + i * 2),
            steps=42,
        )
        color = (120, 216, 216, 48) if i % 3 == 0 else (240, 107, 164, 42)
        rdraw.line(points, fill=color, width=1)
    root = root.filter(ImageFilter.GaussianBlur(0.8))
    base.alpha_composite(root)

    specks = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    q = ImageDraw.Draw(specks)
    palette = [(246, 212, 170), (239, 105, 171), (122, 214, 215)]
    for _ in range(220):
        x = random.uniform(width * 0.18, width * 0.82)
        y = random.uniform(height * 0.08, height * 0.94)
        r = random.uniform(0.8, 2.2)
        color = random.choice(palette)
        q.ellipse((x - r, y - r, x + r, y + r), fill=color + (random.randint(44, 92),))
    specks = specks.filter(ImageFilter.GaussianBlur(0.3))
    base.alpha_composite(specks)

    marks = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    m = ImageDraw.Draw(marks)
    accent = ["#f06ba4", "#78d8d8", "#e2aa64"]
    for i in range(34):
        side = 1 if i % 2 == 0 else -1
        x = cx + side * width * random.uniform(0.29, 0.46)
        y = height * random.uniform(0.04, 0.96)
        length = random.uniform(10, 32)
        color = rgba(accent[i % 3], random.randint(60, 108))
        m.line((x, y - length * 0.5, x, y + length * 0.5), fill=color, width=1)
        m.line((x - 4, y, x + 4, y), fill=color, width=1)
    base.alpha_composite(marks)

    probe = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_radial(probe, cx, height * 0.42, width * 0.12, (255, 245, 236), 34)
    draw_radial(probe, cx, height * 0.42, width * 0.18, (241, 120, 171), 28)
    draw_radial(probe, cx, height * 0.42, width * 0.22, (120, 216, 216), 16)
    base = ImageChops.screen(base, probe)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
