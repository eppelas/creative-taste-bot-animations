#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


BG_TOP = (9, 11, 16)
BG_BOTTOM = (2, 3, 5)
TEXT = (217, 221, 228)
MUTED = (136, 146, 156)
LINE = (116, 154, 170)
CRIMSON = (215, 38, 72)
EMBER = (255, 108, 102)
ROSE = (255, 159, 152)
CYAN = (129, 218, 243)
ACID = (208, 235, 99)
SAND = (233, 200, 164)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def vertical_gradient(width: int, height: int) -> Image.Image:
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
    return Image.alpha_composite(base, layer.filter(ImageFilter.GaussianBlur(radius=max(2, radius * 0.34))))


def draw_grid(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    step = max(28, int(min(width, height) * 0.033))
    for x in range(0, width, step):
        draw.line((x, 0, x, height), fill=LINE + (12,), width=1)
    for y in range(0, height, step):
        draw.line((0, y, width, y), fill=LINE + (12,), width=1)


def draw_lane(draw: ImageDraw.ImageDraw, width: int, y: float, seed: float, depth: float) -> None:
    points: list[tuple[float, float]] = []
    highlights: list[tuple[float, float]] = []
    strands: list[tuple[float, float]] = []
    for step in range(45):
        u = step / 44
        x = width * 0.08 + u * width * 0.84
        center_bias = math.sin(u * math.pi)
        sag = 30 * depth * center_bias
        wave = math.sin(u * math.tau * 1.4 + seed) * 8
        wave2 = math.sin(u * math.tau * 3.2 - seed * 1.4) * 4
        points.append((x, y + sag + wave + wave2))
        highlights.append((x, y + sag * 0.8 + wave * 0.6 - 4))
        strands.append((x, y + sag * 1.1 - wave2 * 0.8 + 10))

    draw.line(points, fill=CRIMSON + (90,), width=max(2, int(2 + depth * 2)), joint="curve")
    draw.line(highlights, fill=ROSE + (56,), width=1, joint="curve")
    draw.line(strands, fill=(118, 90, 82, 44), width=1, joint="curve")


def draw_ticks(draw: ImageDraw.ImageDraw, width: int, y: float, seed: float, alpha: int) -> None:
    for tick in range(9):
        u = (tick + 0.5) / 9
        x = width * 0.12 + u * width * 0.76 + math.sin(seed + tick * 1.7) * 12
        y0 = y - 18 + math.sin(seed + tick) * 4
        y1 = y + 18 + math.sin(seed * 0.8 + tick * 1.2) * 4
        draw.line((x, y0, x, y1), fill=CYAN + (alpha,), width=1)


def draw_particles(base: Image.Image, width: int, height: int) -> Image.Image:
    image = base
    for idx in range(70):
        x = width * (0.05 + (idx % 10) * 0.09) + math.sin(idx * 2.7) * 18
        y = height * (0.06 + (idx // 10) * 0.085) + math.cos(idx * 1.3) * 22
        radius = 14 + (idx % 4) * 3
        image = add_glow(image, x, y, radius, CYAN, 110)
    for idx in range(50):
        x = width * (0.1 + (idx % 8) * 0.11) + math.cos(idx * 1.1) * 12
        y = height * (0.25 + (idx // 8) * 0.09) + math.sin(idx * 1.8) * 14
        image = add_glow(image, x, y, 5, ROSE, 70)
    return image


def draw_mode(draw: ImageDraw.ImageDraw, x: float, y: float, label: str, hint: str, active: bool = False) -> None:
    box = (x - 76, y - 28, x + 76, y + 28)
    outline = ACID + (90,) if active else LINE + (42,)
    fill = (11, 13, 18, 220)
    draw.rounded_rectangle(box, radius=18, fill=fill, outline=outline, width=1)
    draw.text((x - 18, y - 15), label, fill=TEXT + (230,))
    draw.text((x - 52, y + 4), hint, fill=MUTED + (180,))


def draw_panel(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    left = (24, 24, min(width * 0.42, 458), 360)
    right = (width - min(width * 0.33, 370) - 24, 24, width - 24, 420)
    for box in (left, right):
        draw.rounded_rectangle(box, radius=26, fill=(10, 11, 16, 208), outline=LINE + (34,), width=1)

    x0, y0, _, _ = left
    draw.text((x0 + 16, y0 + 16), "CODE ANIMATION STUDY #045", fill=MUTED + (210,))
    draw.text((x0 + 16, y0 + 52), "Crimson Sag", fill=TEXT + (242,))
    draw.text((x0 + 16, y0 + 96), "Weather", fill=TEXT + (242,))
    lines = [
        "A governed dark-red poster field of sagging lanes,",
        "calibration marks, and ember particles where the",
        "motion lives in distributed pressure behavior instead",
        "of another single organism or dashboard page.",
    ]
    for idx, line in enumerate(lines):
        draw.text((x0 + 16, y0 + 154 + idx * 22), line, fill=TEXT + (208,))

    lines2 = [
        "Move through the field to shear the nearest lanes and",
        "thicken the hanging weight. Click one of the floating",
        "anchors to retune the whole weather law between sag,",
        "braid, and flare.",
    ]
    for idx, line in enumerate(lines2):
        draw.text((x0 + 16, y0 + 252 + idx * 20), line, fill=MUTED + (220,))

    draw.text((x0 + 16, y0 + 322), "FIELD MODE", fill=MUTED + (188,))
    draw.text((x0 + 126, y0 + 322), "DROP WEIGHT", fill=MUTED + (188,))
    draw.text((x0 + 252, y0 + 322), "PARTICLE LIFT", fill=MUTED + (188,))
    draw.text((x0 + 16, y0 + 342), "SAG", fill=TEXT + (236,))
    draw.text((x0 + 126, y0 + 342), "0.42", fill=TEXT + (236,))
    draw.text((x0 + 252, y0 + 342), "28", fill=TEXT + (236,))

    xr, yr, _, _ = right
    draw.text((xr + 18, yr + 18), "REVIEW NOTES", fill=MUTED + (200,))
    draw.text((xr + 18, yr + 56), "Idea, interaction, and what could grow", fill=TEXT + (232,))
    draw.text((xr + 18, yr + 86), "next", fill=TEXT + (232,))
    draw.text((xr + 18, yr + 124), "IDEA", fill=MUTED + (190,))
    idea_lines = [
        "A darker generative poster-field built from sagging",
        "crimson lanes, calibration ticks, and ember particles,",
        "keeping the motion distributed across the whole",
        "weather surface instead of another rooted manual page.",
    ]
    for idx, line in enumerate(idea_lines):
        draw.text((xr + 18, yr + 148 + idx * 20), line, fill=TEXT + (194,))

    draw.text((xr + 18, yr + 244), "INTERACTION", fill=MUTED + (190,))
    interaction_lines = [
        "Pointer movement shears the nearest lanes and",
        "thickens the hanging pressure. Click the floating",
        "anchors to switch the field law between weighted",
        "drop, cross-current braid, and rising flare.",
    ]
    for idx, line in enumerate(interaction_lines):
        draw.text((xr + 18, yr + 268 + idx * 20), line, fill=TEXT + (194,))

    draw.text((xr + 18, yr + 344), "NEXT", fill=MUTED + (190,))
    next_lines = [
        "Push this branch toward a broader graphic language:",
        "denser mark families, print-usable layout variants,",
        "and a few weather presets that keep it feeling",
        "governed rather than like a generic HUD.",
    ]
    for idx, line in enumerate(next_lines):
        draw.text((xr + 18, yr + 368 + idx * 20), line, fill=TEXT + (194,))


def draw_scene(width: int, height: int) -> Image.Image:
    image = vertical_gradient(width, height)
    image = add_glow(image, width * 0.5, height * 0.5, height * 0.28, CRIMSON, 56)
    image = add_glow(image, width * 0.18, height * 0.18, height * 0.12, CYAN, 24)
    image = add_glow(image, width * 0.84, height * 0.82, height * 0.12, EMBER, 20)
    image = draw_particles(image, width, height)

    draw = ImageDraw.Draw(image, "RGBA")
    draw_grid(draw, width, height)

    for idx in range(13):
        y = height * (0.14 + idx * 0.065)
        draw_lane(draw, width, y, idx * 0.9 + 0.4, 0.45 + idx * 0.045)
        draw_ticks(draw, width, y, idx * 0.8 + 0.3, 50 + idx * 6)

    for idx in range(-6, 7):
        x = width * 0.5 + idx * 34
        path = [
            (x, height * 0.28),
            (x + math.sin(idx * 0.6) * 24, height * 0.44),
            (x - math.cos(idx * 0.5) * 16, height * 0.61),
            (x + math.sin(idx * 0.4) * 18, height * 0.76),
        ]
        draw.line(path, fill=ROSE + (28,), width=1, joint="curve")

    draw_mode(draw, width * 0.17, height * 0.78, "SAG", "weighted lanes", active=True)
    draw_mode(draw, width * 0.78, height * 0.23, "BRAID", "cross-current weave")
    draw_mode(draw, width * 0.76, height * 0.81, "FLARE", "rising embers")

    back = (width - 146, height - 56, width - 18, height - 20)
    draw.rounded_rectangle(back, radius=18, fill=(11, 13, 18, 204), outline=LINE + (36,), width=1)
    draw.text((width - 122, height - 47), "BACK TO INDEX", fill=TEXT + (214,))

    draw_panel(draw, width, height)
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
