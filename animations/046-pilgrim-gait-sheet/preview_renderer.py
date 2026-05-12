#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


PAPER_TOP = (248, 240, 229)
PAPER_BOTTOM = (220, 197, 168)
INK = (33, 48, 58)
CYAN = (115, 191, 208)
CORAL = (219, 127, 105)
ACID = (199, 212, 87)
NAVY = (43, 83, 105)


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
    blur = max(2, int(radius * 0.34))
    return Image.alpha_composite(base, layer.filter(ImageFilter.GaussianBlur(radius=blur)))


def draw_path(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill: tuple[int, int, int, int], width: int) -> None:
    draw.line(points, fill=fill, width=width, joint="curve")


def draw_poster(draw: ImageDraw.ImageDraw, width: int, height: int) -> tuple[float, float, float, float]:
    box = (width * 0.11, height * 0.16, width * 0.89, height * 0.9)
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=40, fill=(250, 245, 238, 184), outline=INK + (24,), width=1)
    draw.rounded_rectangle((x0 + 18, y0 + 18, x1 - 18, y1 - 18), radius=30, fill=(255, 255, 255, 38))

    for i in range(5):
        y = y0 + (i + 1) * (y1 - y0) / 6
        draw.line((x0 + 30, y, x1 - 30, y), fill=INK + (14,), width=1)
    for i in range(3):
        x = x0 + (i + 1) * (x1 - x0) / 4
        draw.line((x, y0 + 28, x, y1 - 28), fill=INK + (12,), width=1)
    return box


def draw_guide_marks(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    paths = [
        [(width * 0.15, height * 0.34), (width * 0.44, height * 0.29), (width * 0.78, height * 0.33)],
        [(width * 0.22, height * 0.56), (width * 0.52, height * 0.48), (width * 0.82, height * 0.56)],
        [(width * 0.17, height * 0.8), (width * 0.48, height * 0.72), (width * 0.84, height * 0.78)],
    ]
    for points in paths:
        draw_path(draw, points, INK + (24,), 2)
    for i in range(18):
        x = width * (0.12 + i * 0.042)
        y = height * (0.92 - (i % 4) * 0.018)
        draw.line((x, y, x, y + 10 + (i % 3) * 3), fill=INK + (34,), width=1)


def draw_walker(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float, stance: float, accent: tuple[int, int, int]) -> None:
    body_w = 62 * scale
    body_h = 98 * scale
    root_span = 92 * scale

    leg_data = [
      (-0.42, -0.12),
      (0.0, 0.04),
      (0.4, 0.16),
    ]
    for idx, (offset, bend) in enumerate(leg_data):
        foot_x = cx + root_span * offset
        knee_x = cx + root_span * offset * 0.34 + stance * 16 * scale
        knee_y = cy + body_h * (0.26 + idx * 0.04)
        top_x = cx + root_span * offset * 0.1 + stance * 10 * scale
        top_y = cy + body_h * 0.06
        draw_path(draw, [(top_x, top_y), (knee_x, knee_y), (foot_x, cy + body_h * 0.92)], INK + (120,), max(2, int(4 * scale)))
        draw_path(
            draw,
            [(foot_x, cy + body_h * 0.92), (foot_x - 12 * scale, cy + body_h * (1.02 + bend)), (foot_x + 10 * scale, cy + body_h * (1.0 - bend * 0.3))],
            ACID + (90,),
            2,
        )

    draw.rounded_rectangle(
        (cx - body_w * 0.7, cy - body_h * 0.64, cx + body_w * 0.62, cy + body_h * 0.56),
        radius=28,
        fill=(252, 246, 238, 228),
        outline=INK + (82,),
        width=2,
    )
    draw.ellipse((cx - body_w * 0.34, cy - body_h * 0.2, cx + body_w * 0.3, cy + body_h * 0.16), fill=CYAN + (24,))
    draw.ellipse((cx - body_w * 0.48, cy + body_h * 0.04, cx - body_w * 0.18, cy + body_h * 0.2), fill=CORAL + (40,))
    draw.ellipse((cx + body_w * 0.14, cy + body_h * 0.02, cx + body_w * 0.44, cy + body_h * 0.18), fill=CORAL + (40,))

    for i in range(4):
        y = cy - body_h * 0.1 + i * body_h * 0.16
        draw_path(draw, [(cx - body_w * 0.34, y), (cx, y + math.sin(i * 0.9) * 3), (cx + body_w * 0.28, y - 2)], NAVY + (74,), 1)

    dots = [
        (cx - body_w * 0.14 + stance * 5 * scale, cy - body_h * 0.38, 8 * scale, NAVY),
        (cx + body_w * 0.1 + stance * 4 * scale, cy - body_h * 0.36, 8 * scale, NAVY),
        (cx - body_w * 0.02 + stance * 3 * scale, cy - body_h * 0.24, 7 * scale, CORAL),
    ]
    for x, y, r, color in dots:
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color + (210,))

    for idx in range(6):
        spread = (idx - 2.5) * 16 * scale
        x0 = cx + stance * 5 * scale
        y0 = cy - body_h * 0.54
        x1 = x0 + spread
        y1 = y0 - 34 * scale - abs(spread) * 0.14
        draw_path(draw, [(x0, y0), (x0 + spread * 0.36, y0 - 12 * scale), (x1, y1)], NAVY + (88,), 2)
        bead = accent if idx % 2 == 0 else CORAL
        draw.ellipse((x1 - 4 * scale, y1 - 4 * scale, x1 + 4 * scale, y1 + 4 * scale), fill=bead + (188,))

    draw_path(draw, [(cx - body_w * 1.02, cy - body_h * 0.58), (cx - body_w * 0.46, cy - body_h * 0.58), (cx - body_w * 0.46, cy - body_h * 0.16)], INK + (44,), 1)
    draw_path(draw, [(cx + body_w * 0.74, cy + body_h * 0.08), (cx + body_w * 1.18, cy + body_h * 0.08), (cx + body_w * 1.18, cy + body_h * 0.42)], INK + (44,), 1)


def draw_hud(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    note = (36, 34, 494, 292)
    meter = (width - 330, 44, width - 34, 248)
    for box in (note, meter):
        draw.rounded_rectangle(box, radius=28, fill=(255, 250, 242, 178), outline=INK + (24,), width=1)

    draw.text((58, 54), "CODE ANIMATION STUDY #046", fill=INK + (122,))
    draw.text((58, 92), "Pilgrim Gait Sheet", fill=INK + (234,))
    draw.text((58, 138), "Illustrated gait poster for a grounded three-dot", fill=INK + (176,))
    draw.text((58, 162), "species, built as reusable anatomy instead of", fill=INK + (176,))
    draw.text((58, 186), "another detached manual or console page.", fill=INK + (176,))
    draw.text((58, 228), "ACTIVE", fill=INK + (124,))
    draw.text((58, 248), "brace", fill=INK + (224,))
    draw.text((168, 228), "ROOT SPAN", fill=INK + (124,))
    draw.text((168, 248), "0.52", fill=INK + (224,))
    draw.text((280, 228), "HALO SWAY", fill=INK + (124,))
    draw.text((280, 248), "18%", fill=INK + (224,))

    draw.text((width - 306, 64), "GAIT LAWS", fill=INK + (126,))
    chips = [
        ("brace / stable load", CYAN, 96),
        ("survey / forward search", CORAL, 140),
        ("thread / soft tether", ACID, 184),
    ]
    for label, color, y in chips:
        draw.rounded_rectangle((width - 306, y, width - 74, y + 30), radius=16, fill=(255, 255, 255, 56), outline=INK + (18,), width=1)
        draw.ellipse((width - 294, y + 8, width - 280, y + 22), fill=color + (180,))
        draw.text((width - 270, y + 8), label.upper(), fill=INK + (186,))


def draw_scene(width: int, height: int) -> Image.Image:
    image = gradient(width, height)
    image = add_glow(image, width * 0.2, height * 0.16, min(width, height) * 0.18, CYAN, 28)
    image = add_glow(image, width * 0.8, height * 0.18, min(width, height) * 0.2, CORAL, 24)
    image = add_glow(image, width * 0.56, height * 0.84, min(width, height) * 0.16, ACID, 18)
    draw = ImageDraw.Draw(image, "RGBA")

    draw_guide_marks(draw, width, height)
    x0, y0, x1, y1 = draw_poster(draw, width, height)

    walkers = [
        (x0 + (x1 - x0) * 0.23, y0 + (y1 - y0) * 0.58, 0.9, -0.36, CYAN),
        (x0 + (x1 - x0) * 0.54, y0 + (y1 - y0) * 0.36, 1.06, 0.1, NAVY),
        (x0 + (x1 - x0) * 0.76, y0 + (y1 - y0) * 0.7, 0.94, 0.28, ACID),
    ]

    for cx, cy, scale, stance, accent in walkers:
        draw_walker(draw, cx, cy, scale, stance, accent)

    draw.text((x0 + 42, y0 + 30), "gait notes", fill=INK + (116,))
    draw.text((x1 - 194, y0 + 30), "rooted balance", fill=INK + (116,))
    draw.text((x0 + 48, y1 - 50), "bead-thread crown", fill=INK + (116,))
    draw.text((x1 - 168, y1 - 50), "three-dot face", fill=INK + (116,))

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
