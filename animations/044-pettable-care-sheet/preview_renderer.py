#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


PAPER_TOP = (246, 237, 223)
PAPER_BOTTOM = (232, 220, 199)
INK = (36, 48, 56)
CYAN = (120, 196, 210)
CORAL = (231, 132, 114)
ACID = (181, 216, 89)
YELLOW = (217, 213, 75)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def gradient(width: int, height: int) -> Image.Image:
    image = Image.new("RGBA", (width, height), PAPER_BOTTOM + (255,))
    draw = ImageDraw.Draw(image)
    for y in range(height):
      t = y / max(1, height - 1)
      color = tuple(round(lerp(PAPER_TOP[i], PAPER_BOTTOM[i], t)) for i in range(3)) + (255,)
      draw.line((0, y, width, y), fill=color)
    return image


def add_glow(base: Image.Image, cx: float, cy: float, radius: float, color: tuple[int, int, int], alpha: int) -> Image.Image:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color + (alpha,))
    return Image.alpha_composite(base, layer.filter(ImageFilter.GaussianBlur(radius=radius * 0.34)))


def draw_path(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill: tuple[int, int, int, int], width: int) -> None:
    draw.line(points, fill=fill, width=width, joint="curve")


def draw_poster(draw: ImageDraw.ImageDraw, width: int, height: int) -> tuple[float, float, float, float]:
    box = (width * 0.08, height * 0.08, width * 0.92, height * 0.92)
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=38, fill=(248, 241, 231, 220), outline=INK + (34,), width=1)
    draw.rounded_rectangle((x0 + 18, y0 + 18, x1 - 18, y1 - 18), radius=28, fill=(255, 255, 255, 34))
    for i in range(4):
        y = y0 + (i + 1) * (y1 - y0) / 5
        draw.line((x0 + 26, y, x1 - 26, y), fill=INK + (18,), width=1)
    for i in range(3):
        x = x0 + (i + 1) * (x1 - x0) / 4
        draw.line((x, y0 + 24, x, y1 - 24), fill=INK + (14,), width=1)
    for i in range(180):
        x = x0 + ((i * 57) % int(x1 - x0))
        y = y0 + ((i * 91) % int(y1 - y0))
        draw.ellipse((x, y, x + 2, y + 2), fill=(120, 196, 210, 18) if i % 3 == 0 else INK + (14,))
    return box


def draw_thread(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]]) -> None:
    draw_path(draw, points, CYAN + (70,), 8)
    draw_path(draw, points, INK + (66,), 2)
    for i in range(18):
        t = i / 17
        ax, ay = points[0]
        bx, by = points[-1]
        x = lerp(ax, bx, t)
        y = lerp(ay, by, t) + math.sin(t * math.tau * 2.1) * 12
        color = YELLOW if i % 2 == 0 else CORAL
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=color + (156,))


def draw_creature(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float, left_bias: float) -> None:
    body_w = 86 * scale
    body_h = 74 * scale

    for idx in range(4):
        root_x = cx + (-34 + idx * 22) * scale
        knee_x = root_x + (-10 + idx * 6) * scale
        knee_y = cy + 64 * scale + (idx % 2) * 8 * scale
        foot_x = root_x + (-22 + idx * 14) * scale
        foot_y = cy + 138 * scale
        draw_path(draw, [(root_x, cy + 26 * scale), (knee_x, knee_y), (foot_x, foot_y)], INK + (86,), 4)
        draw.ellipse((foot_x - 9 * scale, foot_y - 4 * scale, foot_x + 9 * scale, foot_y + 5 * scale), fill=ACID + (42,), outline=INK + (26,))

    draw.ellipse((cx - body_w, cy - body_h, cx + body_w, cy + body_h), fill=(241, 220, 197, 218), outline=INK + (68,), width=2)
    draw.ellipse((cx - body_w * 0.24, cy - body_h * 0.54, cx + body_w * 0.12, cy - body_h * 0.14), fill=(255, 255, 255, 44))

    blush_alpha = 48 + int(scale * 12)
    draw.ellipse((cx - 42 * scale, cy + 4 * scale, cx - 14 * scale, cy + 22 * scale), fill=CORAL + (blush_alpha,))
    draw.ellipse((cx + 14 * scale, cy + 4 * scale, cx + 42 * scale, cy + 22 * scale), fill=CORAL + (blush_alpha,))

    face_y = cy - 10 * scale
    for direction in (-1, 1):
        eye_x = cx + direction * (22 + left_bias * 6) * scale
        draw.ellipse((eye_x - 13 * scale, face_y - 12 * scale, eye_x + 13 * scale, face_y + 12 * scale), fill=INK + (220,))
        draw.ellipse((eye_x - 6 * scale, face_y - 6 * scale, eye_x + 6 * scale, face_y + 6 * scale), fill=YELLOW + (218,))
        draw.ellipse((eye_x - 2 * scale, face_y - 2 * scale, eye_x + 2 * scale, face_y + 2 * scale), fill=(255, 255, 255, 220))

    draw.arc((cx - 14 * scale, cy + 10 * scale, cx + 14 * scale, cy + 28 * scale), 10, 170, fill=INK + (180,), width=2)

    for direction, color in ((-1, CYAN), (1, CORAL)):
        x0 = cx + direction * 24 * scale
        y0 = cy - 56 * scale
        x1 = cx + direction * 36 * scale
        y1 = cy - 92 * scale
        draw_path(draw, [(x0, y0), (x0 + direction * 10 * scale, y0 - 20 * scale), (x1, y1)], INK + (82,), 3)
        draw.ellipse((x1 - 7 * scale, y1 - 7 * scale, x1 + 7 * scale, y1 + 7 * scale), fill=color + (186,))

    for i in range(5):
        angle = i / 5 * math.tau
        x = cx + math.cos(angle) * (90 + i * 9) * scale
        y = cy + math.sin(angle * 1.2) * 26 * scale
        color = CYAN if i % 2 == 0 else ACID
        draw.ellipse((x - 4 * scale, y - 4 * scale, x + 4 * scale, y + 4 * scale), fill=color + (110,))


def draw_hud(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    note = (40, 38, 486, 274)
    meter = (width - 308, 54, width - 36, 246)
    for box in (note, meter):
        draw.rounded_rectangle(box, radius=28, fill=(255, 250, 242, 176), outline=INK + (22,), width=1)

    draw.text((64, 56), "CODE ANIMATION STUDY #044", fill=INK + (128,))
    draw.text((64, 92), "Pettable Care Sheet", fill=INK + (232,))
    draw.text((64, 136), "Flatter creature poster with tactile attention", fill=INK + (176,))
    draw.text((64, 160), "instead of another manual, atlas, or console.", fill=INK + (176,))
    draw.text((64, 204), "ACTIVE", fill=INK + (128,))
    draw.text((64, 224), "moss", fill=INK + (220,))
    draw.text((176, 204), "WARMTH", fill=INK + (128,))
    draw.text((176, 224), "0.76", fill=INK + (220,))
    draw.text((286, 204), "THREAD", fill=INK + (128,))
    draw.text((286, 224), "passing", fill=INK + (220,))

    draw.text((width - 286, 74), "COLONY READOUT", fill=INK + (128,))
    chips = [
        ("brush", CYAN, width - 286, 110),
        ("hold", CORAL, width - 286, 154),
        ("comfort", ACID, width - 286, 198),
    ]
    for label, color, x, y in chips:
        draw.rounded_rectangle((x, y, x + 214, y + 30), radius=14, fill=(255, 255, 255, 54), outline=INK + (18,), width=1)
        draw.ellipse((x + 10, y + 8, x + 24, y + 22), fill=color + (170,))
        draw.text((x + 34, y + 8), label.upper(), fill=INK + (188,))


def draw_scene(width: int, height: int) -> Image.Image:
    image = gradient(width, height)
    image = add_glow(image, width * 0.18, height * 0.16, min(width, height) * 0.18, CYAN, 26)
    image = add_glow(image, width * 0.8, height * 0.16, min(width, height) * 0.2, CORAL, 24)
    image = add_glow(image, width * 0.52, height * 0.82, min(width, height) * 0.18, ACID, 20)
    draw = ImageDraw.Draw(image, "RGBA")

    x0, y0, x1, y1 = draw_poster(draw, width, height)
    centers = [
        (x0 + (x1 - x0) * 0.25, y0 + (y1 - y0) * 0.3, 0.92, -0.3),
        (x0 + (x1 - x0) * 0.72, y0 + (y1 - y0) * 0.3, 0.86, 0.12),
        (x0 + (x1 - x0) * 0.34, y0 + (y1 - y0) * 0.68, 1.04, 0.18),
        (x0 + (x1 - x0) * 0.75, y0 + (y1 - y0) * 0.71, 0.98, -0.14),
    ]

    draw_thread(draw, [(centers[0][0], centers[0][1] + 16), (width * 0.46, height * 0.32), (centers[1][0], centers[1][1] + 18)])
    draw_thread(draw, [(centers[2][0], centers[2][1] + 18), (width * 0.54, height * 0.71), (centers[3][0], centers[3][1] + 12)])

    for cx, cy, scale, bias in centers:
        draw_creature(draw, cx, cy, scale, bias)
        draw.ellipse((cx - 90 * scale, cy - 88 * scale, cx + 90 * scale, cy + 88 * scale), outline=CORAL + (42,), width=2)
        draw.line((cx, cy - 82 * scale, cx + 94, cy - 114 * scale), fill=INK + (54,), width=1)
        draw.ellipse((cx + 98, cy - 124 * scale, cx + 128, cy - 94 * scale), outline=INK + (44,), width=1)

    draw.text((x0 + 48, y0 + 38), "care sheet", fill=INK + (126,))
    draw.text((x1 - 216, y0 + 38), "brush to soothe", fill=INK + (126,))
    draw.text((x0 + 52, y1 - 54), "soft roots", fill=INK + (126,))
    draw.text((x1 - 194, y1 - 54), "colony line", fill=INK + (126,))

    draw_hud(draw, width, height)
    return image.convert("RGB")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    image = draw_scene(args.width, args.height)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
