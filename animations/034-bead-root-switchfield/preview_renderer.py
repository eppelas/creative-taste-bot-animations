#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


BG_TOP = (16, 34, 51)
BG_BOTTOM = (5, 10, 17)
INK = (239, 244, 237)
MUTED = (239, 244, 237, 156)
CYAN = (115, 216, 255)
ACID = (214, 245, 95)
CORAL = (255, 144, 120)
PANEL = (7, 13, 20, 198)
LINE = (208, 229, 241, 34)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def gradient(width: int, height: int) -> Image.Image:
    image = Image.new("RGBA", (width, height), BG_BOTTOM + (255,))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(round(lerp(BG_TOP[i], BG_BOTTOM[i], t)) for i in range(3)) + (255,)
        draw.line((0, y, width, y), fill=color)
    return image


def add_glow(base: Image.Image, cx: float, cy: float, radius: float, color: tuple[int, int, int], alpha: int) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color + (alpha,))
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius=48)))


def draw_path(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill: tuple[int, int, int, int], width: int) -> None:
    draw.line(points, fill=fill, width=width, joint="curve")


def draw_scene(width: int, height: int) -> Image.Image:
    image = gradient(width, height)
    add_glow(image, width * 0.16, height * 0.17, min(width, height) * 0.22, CYAN, 28)
    add_glow(image, width * 0.76, height * 0.16, min(width, height) * 0.2, CORAL, 24)
    add_glow(image, width * 0.55, height * 0.84, min(width, height) * 0.2, ACID, 18)
    draw = ImageDraw.Draw(image, "RGBA")

    sway = 18
    shear = 0.22
    for i in range(-10, 42):
        ratio = i / 42
        x = ratio * width + sway
        tilt = 90 + math.sin(i * 0.4) * 12 + shear * 38
        color = (115, 216, 255, 46) if i % 3 == 0 else (239, 244, 237, 20)
        draw.line((x, -40, x + tilt, height + 40), fill=color, width=1)

    for i in range(7):
        y = height * (0.18 + i * 0.11)
        points = []
        for step in range(18):
            t = step / 17
            x = width * (0.12 + t * 0.76)
            points.append((x, y + math.sin(t * math.pi * 2 + i) * 6))
        draw_path(draw, points, (214, 245, 95, 16), 1)

    cx = width * 0.49
    cy = height * 0.56
    pelvis_y = cy + 96
    shoulder_y = cy - 52
    head_y = cy - 118
    ground_y = height * 0.84
    root_spread = 0.66
    charge = 0.68

    add_glow(image, cx, cy - 12, min(width, height) * 0.18, (16, 37, 54), 28)
    draw = ImageDraw.Draw(image, "RGBA")

    root_offsets = [-1.2, -0.45, 0.45, 1.2]
    for index, offset in enumerate(root_offsets):
        spread = 120 + abs(offset) * 44
        anchor_x = cx + offset * spread * root_spread + 12
        knee_x = cx + offset * 46 + sway * 0.18
        knee_y = pelvis_y + 70 + math.sin(index) * 14
        points = [
            (cx + offset * 16, pelvis_y - 10),
            (cx + offset * 24, pelvis_y + 26),
            (knee_x, knee_y),
            (anchor_x, ground_y),
        ]
        color = (115, 216, 255, 132) if index % 2 == 0 else (255, 144, 120, 118)
        draw_path(draw, points, color, max(2, round(3.4 - abs(offset) * 0.3)))
        draw.ellipse(
            (anchor_x - 18, ground_y - 4, anchor_x + 18, ground_y + 10),
            fill=(214, 245, 95, 30) if index % 2 == 0 else (115, 216, 255, 24),
        )

    draw_path(
        draw,
        [
            (cx, pelvis_y),
            (cx + 4, cy + 48),
            (cx + sway * 0.16, shoulder_y + 40),
            (cx + 6, head_y + 40),
        ],
        (239, 244, 237, 82),
        5,
    )

    torso = [
        (cx - 52, shoulder_y - 8),
        (cx - 98, cy - 4),
        (cx - 62, cy + 88),
        (cx - 18, pelvis_y + 16),
        (cx + 18, pelvis_y + 16),
        (cx + 66, cy + 88),
        (cx + 100, cy - 4),
        (cx + 52, shoulder_y - 8),
        (cx + 30, head_y + 26),
        (cx, head_y + 4),
        (cx - 30, head_y + 26),
    ]
    draw.polygon(torso, fill=(10, 24, 35, 184), outline=(239, 244, 237, 36))
    draw.ellipse((cx - 34, cy - 68, cx + 34, cy + 84), outline=(115, 216, 255, 56), width=1)

    for i in range(8):
        ratio = i / 7
        y = lerp(shoulder_y + 12, pelvis_y + 10, ratio)
        bow = math.sin(i * 0.7) * 8
        color = (214, 245, 95, 46) if i % 2 == 0 else (255, 144, 120, 38)
        draw.arc((cx - 44, y - 12, cx + 44 + bow, y + 12), 200, 340, fill=color, width=1)

    draw.ellipse((cx - 42, head_y - 34, cx + 42, head_y + 34), outline=(239, 244, 237, 54), width=1)
    lights = [
        (cx - 18, head_y - 2, 5),
        (cx, head_y - 12, 6),
        (cx + 18, head_y - 1, 5),
    ]
    for index, (lx, ly, r) in enumerate(lights):
        color = ACID if index == 1 else CYAN
        add_glow(image, lx, ly, 18 + charge * 10, color, 42)
        draw = ImageDraw.Draw(image, "RGBA")
        draw.ellipse((lx - r, ly - r, lx + r, ly + r), fill=color + (220,))

    draw.arc((cx - 16, head_y + 10, cx + 16, head_y + 24), 200, 340, fill=(255, 144, 120, 82), width=1)

    tendril_offsets = [-1.2, -0.45, 0.45, 1.2]
    for index, offset in enumerate(tendril_offsets):
        arc = offset * 60
        end_x = cx + arc + sway * 0.18
        end_y = head_y - 110 - abs(offset) * 10
        points = [
            (cx + offset * 10, head_y - 8),
            (cx + offset * 18, head_y - 26),
            (cx + arc * 0.62, head_y - 66),
            (end_x, end_y),
        ]
        draw_path(draw, points, (239, 244, 237, 66) if index % 2 == 0 else (115, 216, 255, 82), 2)
        for i in range(3):
            t = (i + 1) / 4
            bx = lerp(points[0][0], end_x, t)
            by = lerp(points[0][1], end_y, t)
            size = 3 + i * 1.4
            color = CORAL if i % 2 == 0 else ACID
            draw.ellipse((bx - size, by - size, bx + size, by + size), fill=color + (180,), outline=(239, 244, 237, 40))

    for i in range(4):
        py = cy - 90 + i * 72
        draw_path(
            draw,
            [
                (width * 0.1, py),
                (cx - 90 + i * 8, py + sway * 0.12),
                (cx + 96 - i * 6, py - sway * 0.1),
                (width * 0.9, py + math.sin(i) * 8),
            ],
            (115, 216, 255, 62),
            1,
        )

    for i in range(max(120, int(width * 0.11))):
        x = (i * 73) % width
        y = (i * 29 + (i % 7) * 41) % height
        size = 1 + ((i * 17) % 13) / 7
        color = (255, 144, 120, 84) if i % 5 == 0 else (239, 244, 237, 42)
        draw.ellipse((x - size, y - size, x + size, y + size), fill=color)

    draw.text((cx + 72, head_y - 28), "face cluster", fill=ACID + (190,))
    draw.text((cx + 94, pelvis_y + 52), "root load", fill=CYAN + (184,))
    draw.text((cx - 148, head_y - 74), "bead thread", fill=CORAL + (182,))

    panel_box = (38, 34, min(width - 38, 654), 330)
    panel_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(panel_layer, "RGBA")
    pdraw.rounded_rectangle(panel_box, radius=24, fill=PANEL, outline=LINE, width=1)
    image.alpha_composite(panel_layer.filter(ImageFilter.GaussianBlur(radius=0.5)))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.text((62, 58), "CODE ANIMATION STUDY #034", fill=MUTED)
    draw.text((62, 94), "Bead Root Switchfield", fill=INK + (236,))
    draw.text((62, 138), "A darker design-illustration plate where one rooted", fill=INK + (178,))
    draw.text((62, 160), "creature stands inside diagonal switch lanes.", fill=INK + (178,))
    draw.text((62, 196), "STANCE", fill=MUTED)
    draw.text((62, 214), "brace", fill=INK + (225,))
    draw.text((192, 196), "ROOT SPREAD", fill=MUTED)
    draw.text((192, 214), "0.66", fill=INK + (225,))
    draw.text((316, 196), "FACE CHARGE", fill=MUTED)
    draw.text((316, 214), "68%", fill=INK + (225,))

    chips = [
        ((width * 0.22) - 64, (height * 0.33) - 26, (width * 0.22) + 64, (height * 0.33) + 26, "Brace", "stable legs", False),
        ((width * 0.79) - 64, (height * 0.29) - 26, (width * 0.79) + 64, (height * 0.29) + 26, "Bloom", "open tendrils", False),
        ((width * 0.73) - 64, (height * 0.72) - 26, (width * 0.73) + 64, (height * 0.73) + 26, "Signal", "active rails", True),
    ]
    for x0, y0, x1, y1, title, subtitle, active in chips:
        draw.rounded_rectangle(
            (x0, y0, x1, y1),
            radius=16,
            fill=(7, 13, 20, 188),
            outline=(214, 245, 95, 84) if active else LINE,
            width=1,
        )
        draw.text((x0 + 14, y0 + 10), title.upper(), fill=INK + (218,))
        draw.text((x0 + 14, y0 + 26), subtitle, fill=MUTED)

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
