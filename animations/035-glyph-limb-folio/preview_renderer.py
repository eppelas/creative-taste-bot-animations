#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


BG_TOP = (246, 239, 228)
BG_BOTTOM = (215, 204, 187)
INK = (29, 34, 39)
CYAN = (106, 170, 196)
CLAY = (197, 110, 79)
GOLD = (208, 161, 63)


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


def add_glow(base: Image.Image, cx: float, cy: float, radius: float, color: tuple[int, int, int], alpha: int) -> Image.Image:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color + (alpha,))
    return Image.alpha_composite(base, layer.filter(ImageFilter.GaussianBlur(radius=radius * 0.32)))


def draw_path(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill: tuple[int, int, int, int], width: int) -> None:
    draw.line(points, fill=fill, width=width, joint="curve")


def curve_point(points: list[tuple[float, float]], t: float) -> tuple[float, float]:
    scaled = t * (len(points) - 1)
    index = min(len(points) - 2, int(scaled))
    local = scaled - index
    ax, ay = points[index]
    bx, by = points[index + 1]
    return (lerp(ax, bx, local), lerp(ay, by, local))


def draw_scene(width: int, height: int) -> Image.Image:
    image = gradient(width, height)
    image = add_glow(image, width * 0.18, height * 0.14, min(width, height) * 0.2, CYAN, 26)
    image = add_glow(image, width * 0.79, height * 0.18, min(width, height) * 0.22, CLAY, 20)
    image = add_glow(image, width * 0.52, height * 0.84, min(width, height) * 0.18, GOLD, 18)
    draw = ImageDraw.Draw(image, "RGBA")

    poster = (
        width * 0.13,
        height * 0.09,
        width * 0.87,
        height * 0.91,
    )
    x0, y0, x1, y1 = poster
    pw = x1 - x0
    ph = y1 - y0

    draw.rounded_rectangle(poster, radius=34, fill=(255, 247, 236, 182), outline=(29, 34, 39, 26), width=1)
    draw.rounded_rectangle((x0 + 14, y0 + 14, x1 - 14, y1 - 14), radius=26, fill=(255, 255, 255, 34))

    for i in range(19):
        gx = x0 + pw / 18 * i
        color = (29, 34, 39, 23) if i % 3 == 0 else (29, 34, 39, 11)
        draw.line((gx, y0 + 18, gx, y1 - 18), fill=color, width=1)

    for i in range(25):
        gy = y0 + ph / 24 * i
        color = (29, 34, 39, 20) if i % 4 == 0 else (29, 34, 39, 9)
        draw.line((x0 + 18, gy, x1 - 18, gy), fill=color, width=1)

    for i in range(-4, 6):
        sx = x0 + pw * 0.2 + i * 52
        draw.line((sx, y0 + 18, sx + 160, y1 - 18), fill=(29, 34, 39, 20), width=1)

    cx = x0 + pw * 0.5 + 26
    head_y = y0 + ph * 0.22
    shoulder_y = y0 + ph * 0.35
    pelvis_y = y0 + ph * 0.6
    ground_y = y0 + ph * 0.88

    spine = [
        (cx, pelvis_y + 16),
        (cx + 4, y0 + ph * 0.53),
        (cx + 10, shoulder_y + 42),
        (cx + 16, head_y + 38),
    ]
    draw_path(draw, spine, (29, 34, 39, 34), 6)
    draw_path(draw, spine, (29, 34, 39, 220), 2)

    torso = [
        (cx - pw * 0.082, shoulder_y - 8),
        (cx - pw * 0.13, y0 + ph * 0.47),
        (cx - pw * 0.1, pelvis_y + 28),
        (cx - pw * 0.042, pelvis_y + 48),
        (cx + pw * 0.042, pelvis_y + 48),
        (cx + pw * 0.1, pelvis_y + 28),
        (cx + pw * 0.13, y0 + ph * 0.47),
        (cx + pw * 0.082, shoulder_y - 8),
        (cx + pw * 0.045, head_y + 28),
        (cx, head_y + 6),
        (cx - pw * 0.045, head_y + 28),
    ]
    draw.polygon(torso, fill=(255, 251, 245, 170), outline=(29, 34, 39, 224))
    draw.ellipse((cx - pw * 0.045, head_y - ph * 0.046, cx + pw * 0.045, head_y + ph * 0.046), fill=(255, 250, 242, 188), outline=(29, 34, 39, 225), width=1)

    for i in range(8):
        t = i / 7
        y = lerp(shoulder_y + 10, pelvis_y + 16, t)
        draw.arc((cx - 24, y - 12, cx + 24, y + 12), 14, 166, fill=(29, 34, 39, 82), width=1)

    face_nodes = [
        (cx - pw * 0.018, head_y - ph * 0.004, 4.2, CYAN),
        (cx, head_y - ph * 0.013, 5.4, GOLD),
        (cx + pw * 0.018, head_y - ph * 0.002, 4.2, CLAY),
    ]
    for fx, fy, radius, color in face_nodes:
        image = add_glow(image, fx, fy, 16, color, 30)
        draw = ImageDraw.Draw(image, "RGBA")
        draw.ellipse((fx - radius, fy - radius, fx + radius, fy + radius), fill=color + (225,), outline=(29, 34, 39, 42))

    draw.arc((cx - 18, head_y + 10, cx + 18, head_y + 24), 14, 166, fill=(29, 34, 39, 138), width=1)

    for side, color in ((-1, CYAN), (1, CLAY)):
        tip_x = cx + side * pw * 0.14
        tip_y = head_y - ph * 0.12
        thread = [
            (cx + side * pw * 0.016, head_y - 6),
            (cx + side * pw * 0.03, head_y - ph * 0.03),
            (cx + side * pw * 0.07, head_y - ph * 0.066),
            (tip_x, tip_y),
        ]
        draw_path(draw, thread, (29, 34, 39, 220), 2)
        for i in range(1, 6):
            bx, by = curve_point(thread, i / 6)
            radius = 2.4 + i * 0.5
            bead_color = CLAY if i % 2 == 0 else CYAN
            draw.ellipse((bx - radius, by - radius, bx + radius, by + radius), fill=bead_color + (196,), outline=(29, 34, 39, 36))
        draw.ellipse((tip_x - 7, tip_y - 7, tip_x + 7, tip_y + 7), fill=color + (214,), outline=(29, 34, 39, 42))

    for side, hand_x, hand_y, color in (
        (-1, x0 + pw * 0.28, y0 + ph * 0.58, CYAN),
        (1, x0 + pw * 0.72, y0 + ph * 0.59, CLAY),
    ):
        arm = [
            (cx + side * pw * 0.055, shoulder_y + 4),
            (cx + side * pw * 0.11, y0 + ph * 0.47),
            (hand_x, hand_y),
        ]
        draw_path(draw, arm, (29, 34, 39, 30), 5)
        draw_path(draw, arm, (29, 34, 39, 225), 2)
        draw.ellipse((hand_x - 5, hand_y - 5, hand_x + 5, hand_y + 5), fill=color + (206,), outline=(29, 34, 39, 48))

    for index, offset in enumerate((-1.15, -0.38, 0.38, 1.15)):
        side_spread = pw * 0.12 * offset
        hip_x = cx + side_spread * 0.36
        hip_y = pelvis_y + 6
        knee_x = cx + side_spread * 0.76
        knee_y = pelvis_y + ph * 0.12 + (-1 if index % 2 == 0 else 1) * 6
        foot_x = cx + side_spread * 2.05 + offset * pw * 0.055
        foot_y = ground_y
        limb = [(hip_x, hip_y), (knee_x, knee_y), (foot_x, foot_y)]
        draw_path(draw, limb, (29, 34, 39, 28), 6)
        draw_path(draw, limb, (29, 34, 39, 225), 2)
        pad_w = pw * (0.032 + abs(offset) * 0.004)
        pad_h = ph * 0.013
        fill = (106, 170, 196, 40) if index % 2 == 0 else (197, 110, 79, 36)
        draw.ellipse((foot_x - pad_w, foot_y + 5 - pad_h, foot_x + pad_w, foot_y + 5 + pad_h), fill=fill, outline=(29, 34, 39, 40))
        draw.line((foot_x - pad_w * 1.1, foot_y + 16, foot_x + pad_w * 1.1, foot_y + 16), fill=(29, 34, 39, 84), width=1)

    for i in range(5):
        lane_y = y0 + ph * (0.28 + i * 0.11)
        points = []
        for step in range(15):
            t = step / 14
            points.append((x0 + pw * (0.08 + t * 0.84), lane_y + math.sin(t * math.tau * 1.1 + i * 0.7) * (8 + i * 1.2)))
        color = (106, 170, 196, 120) if i % 2 == 0 else (197, 110, 79, 102)
        draw_path(draw, points, color, 1)

    labels = [
        ("bead thread", cx - pw * 0.22, head_y - ph * 0.09, cx - pw * 0.075, head_y - ph * 0.05),
        ("spine register", cx + pw * 0.1, y0 + ph * 0.42, cx + 4, y0 + ph * 0.47),
        ("root brace", cx + pw * 0.16, ground_y - ph * 0.03, cx + pw * 0.11, ground_y - 10),
    ]
    for text, lx, ly, tx, ty in labels:
        draw.line((lx, ly, tx, ty), fill=(29, 34, 39, 64), width=1)
        draw.text((lx, ly - 4), text, fill=(29, 34, 39, 146))

    panel = (38, 34, min(width - 38, 522), 300)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay, "RGBA")
    odraw.rounded_rectangle(panel, radius=24, fill=(255, 250, 242, 148), outline=(29, 34, 39, 24), width=1)
    image = Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(radius=0.5)))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.text((62, 58), "CODE ANIMATION STUDY #035", fill=INK + (132,))
    draw.text((62, 94), "Glyph Limb Folio", fill=INK + (235,))
    draw.text((62, 138), "Editorial poster specimen with a rooted full-body", fill=INK + (172,))
    draw.text((62, 160), "alien rendered as crisp stencil drafting.", fill=INK + (172,))
    draw.text((62, 198), "LAW", fill=INK + (132,))
    draw.text((62, 216), "anchor", fill=INK + (228,))
    draw.text((176, 198), "ROOT SPAN", fill=INK + (132,))
    draw.text((176, 216), "0.54", fill=INK + (228,))
    draw.text((292, 198), "HALO LOAD", fill=INK + (132,))
    draw.text((292, 216), "48%", fill=INK + (228,))

    chips = [
        ((x0 + pw * 0.16) - 56, (y0 + ph * 0.3) - 22, (x0 + pw * 0.16) + 56, (y0 + ph * 0.3) + 22, "Anchor", "firm stance", False),
        ((x0 + pw * 0.84) - 56, (y0 + ph * 0.24) - 22, (x0 + pw * 0.84) + 56, (y0 + ph * 0.24) + 22, "Survey", "head scans", False),
        ((x0 + pw * 0.78) - 56, (y0 + ph * 0.78) - 22, (x0 + pw * 0.78) + 56, (y0 + ph * 0.78) + 22, "Flare", "wide display", True),
    ]
    for left, top, right, bottom, title, subtitle, active in chips:
        outline = (208, 161, 63, 88) if active else (29, 34, 39, 24)
        draw.rounded_rectangle((left, top, right, bottom), radius=16, fill=(255, 250, 242, 154), outline=outline, width=1)
        draw.text((left + 12, top + 8), title.upper(), fill=INK + (210,))
        draw.text((left + 12, top + 24), subtitle, fill=INK + (132,))

    draw.text((x0 + 24, y1 - 26), "FOLIO 035 / GLYPH LIMB SPECIMEN", fill=INK + (120,))
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
