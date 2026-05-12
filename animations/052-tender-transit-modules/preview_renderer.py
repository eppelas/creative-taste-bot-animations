#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


PAPER_TOP = (247, 239, 229)
PAPER_MID = (238, 227, 211)
PAPER_BOTTOM = (222, 204, 184)
INK = (43, 55, 65)
MUTED = (108, 105, 101)
CYAN = (128, 191, 212)
ROSE = (215, 142, 139)
MOSS = (146, 166, 128)
AMBER = (214, 164, 109)


def rgba(color: tuple[int, int, int], alpha: int) -> tuple[int, int, int, int]:
    return color[0], color[1], color[2], alpha


def load_font(size: int):
    for path in (
        "/System/Library/Fonts/Supplemental/Palatino.ttc",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def load_mono(size: int):
    for path in (
        "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def gradient(width: int, height: int) -> Image.Image:
    image = Image.new("RGBA", (width, height), PAPER_BOTTOM + (255,))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / max(height - 1, 1)
        color = tuple(
            round(PAPER_TOP[i] + (PAPER_BOTTOM[i] - PAPER_TOP[i]) * t) for i in range(3)
        ) + (255,)
        draw.line((0, y, width, y), fill=color)
    return image


def add_halo(base: Image.Image, cx: float, cy: float, radius: float, color: tuple[int, int, int], alpha: int) -> Image.Image:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=rgba(color, alpha))
    return Image.alpha_composite(base, layer.filter(ImageFilter.GaussianBlur(radius=max(8, int(radius * 0.28)))))


def draw_grid(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    for x in range(0, width + 96, 96):
        draw.line((x, 0, x, height), fill=rgba(INK, 20), width=1)
    for y in range(0, height + 96, 96):
        draw.line((0, y, width, y), fill=rgba(INK, 20), width=1)


def draw_figure(draw: ImageDraw.ImageDraw, cx: float, floor_y: float, scale: float, accent: tuple[int, int, int]) -> None:
    head_y = floor_y - 64 * scale
    shoulder_y = floor_y - 42 * scale
    hip_y = floor_y - 14 * scale
    arm_reach = 14 * scale
    leg_spread = 10 * scale

    draw.ellipse((cx - 10 * scale, head_y - 10 * scale, cx + 10 * scale, head_y + 10 * scale), outline=rgba(INK, 220), width=max(1, int(2 * scale)))
    draw.line((cx, head_y + 10 * scale, cx, hip_y), fill=rgba(INK, 220), width=max(1, int(2 * scale)))
    draw.line((cx, shoulder_y, cx - arm_reach, shoulder_y + 15 * scale), fill=rgba(accent, 210), width=max(1, int(2 * scale)))
    draw.line((cx, shoulder_y, cx + arm_reach, shoulder_y + 13 * scale), fill=rgba(INK, 210), width=max(1, int(2 * scale)))
    draw.line((cx, hip_y, cx - leg_spread, floor_y), fill=rgba(INK, 220), width=max(1, int(2 * scale)))
    draw.line((cx, hip_y, cx + leg_spread, floor_y + 2 * scale), fill=rgba(INK, 220), width=max(1, int(2 * scale)))
    draw.line((cx - 6 * scale, head_y - 2 * scale, cx - 2 * scale, head_y - 2 * scale), fill=rgba(INK, 200), width=1)
    draw.line((cx + 2 * scale, head_y - 2 * scale, cx + 6 * scale, head_y - 2 * scale), fill=rgba(INK, 200), width=1)

    reflection = Image.new("RGBA", draw._image.size, (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(reflection, "RGBA")
    rdraw.polygon(
        [
            (cx - 18 * scale, floor_y + 3 * scale),
            (cx + 18 * scale, floor_y + 3 * scale),
            (cx + 6 * scale, floor_y + 46 * scale),
            (cx - 10 * scale, floor_y + 46 * scale),
        ],
        fill=rgba(accent, 62),
    )
    reflection = reflection.filter(ImageFilter.GaussianBlur(radius=max(2, int(6 * scale))))
    draw._image.alpha_composite(reflection)


def draw_module(draw: ImageDraw.ImageDraw, box, label: str, accents: tuple[int, int, int], people: int) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=30, fill=(255, 250, 242, 148), outline=rgba(INK, 34), width=1)
    draw.rounded_rectangle((x0 + 2, y0 + 2, x1 - 2, y1 - 2), radius=28, outline=rgba((255, 255, 255), 90), width=1)

    for idx in range(5):
        rain_x = x0 + 34 + idx * 34
        draw.line((rain_x, y0 + 18 + idx * 8, rain_x + 16, y0 + (y1 - y0) * 0.46), fill=rgba((255, 255, 255), 80), width=1)

    draw.line((x0 + 18, y0 + (y1 - y0) * 0.24, x1 - 18, y0 + (y1 - y0) * 0.68), fill=rgba(accents, 120), width=2)
    floor_y = y0 + (y1 - y0) * 0.72
    positions = [0.5] if people == 1 else [0.38, 0.64]
    for idx, pos in enumerate(positions):
        figure_x = x0 + (x1 - x0) * pos
        draw_figure(draw, figure_x, floor_y, min(x1 - x0, y1 - y0) / 180, accents if idx % 2 == 0 else INK)

    draw.text((x0 + 18, y0 + 14), label.upper(), font=load_mono(12), fill=rgba(MUTED, 220))
    draw.line((x0 + 18, y1 - 16, min(x1 - 18, x0 + 120), y1 - 16), fill=rgba(accents, 150), width=2)


def render(output: Path, width: int, height: int) -> None:
    image = gradient(width, height)
    for cx, cy, radius, color, alpha in (
        (width * 0.18, height * 0.14, width * 0.18, CYAN, 34),
        (width * 0.82, height * 0.18, width * 0.16, ROSE, 30),
        (width * 0.22, height * 0.82, width * 0.15, MOSS, 24),
        (width * 0.7, height * 0.78, width * 0.14, AMBER, 22),
    ):
        image = add_halo(image, cx, cy, radius, color, alpha)

    draw = ImageDraw.Draw(image, "RGBA")
    draw_grid(draw, width, height)

    panel = (34, 34, 480, 312)
    draw.rounded_rectangle(panel, radius=28, fill=(255, 250, 243, 176), outline=rgba(INK, 28), width=1)
    draw.text((58, 58), "CODE ANIMATION STUDY #052", font=load_mono(12), fill=rgba(MUTED, 210))
    draw.text((58, 98), "Tender Transit\nModules", font=load_font(52), fill=rgba(INK, 235), spacing=0)
    draw.text((58, 214), "Human editorial sheet instead of another", font=load_font(20), fill=rgba(INK, 190))
    draw.text((58, 240), "creature page or dashboard dossier.", font=load_font(20), fill=rgba(INK, 190))
    draw.text((58, 276), "Rain-focus interaction + note drift", font=load_font(18), fill=rgba(MUTED, 210))

    modules = [
        ((120, 344, 402, 632), "Platform wait", CYAN, 2),
        ((462, 316, 826, 646), "Window fog", ROSE, 1),
        ((844, 360, 1018, 624), "Hand note", MOSS, 1),
        ((170, 760, 468, 1074), "Shared umbrella", AMBER, 2),
        ((532, 752, 800, 1046), "Bench drift", CYAN, 2),
        ((844, 838, 1014, 1082), "Margin witness", ROSE, 1),
    ]
    for box, label, accent, people in modules:
        draw_module(draw, box, label, accent, people)

    connector_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(connector_layer, "RGBA")
    points = [
        (261, 488),
        (644, 480),
        (931, 492),
        (318, 920),
        (666, 900),
        (928, 960),
    ]
    colors = [CYAN, ROSE, MOSS, AMBER]
    for idx in range(len(points) - 1):
        ax, ay = points[idx]
        bx, by = points[idx + 1]
        midx = (ax + bx) * 0.5
        sway = -38 if idx % 2 == 0 else 46
        cdraw.line((ax, ay, midx, ay + sway, bx, by), fill=rgba(colors[idx % len(colors)], 110), width=2, joint="curve")
    connector_layer = connector_layer.filter(ImageFilter.GaussianBlur(radius=0.6))
    image.alpha_composite(connector_layer)

    footer_y = 1136
    footer_w = (width - 68 - 24 * 2) // 3
    cards = [
        ("IDEA", "Design-usable human fragments,\nnot another organism lane."),
        ("INTERACTION", "Pointer acts like focus glass\nand drags reflections sideways."),
        ("NEXT", "Expand into stranger editorial\nstreet scenes or portrait modules."),
    ]
    for idx, (title, copy) in enumerate(cards):
        x = 34 + idx * (footer_w + 24)
        draw.rounded_rectangle((x, footer_y, x + footer_w, 1310), radius=24, fill=(255, 250, 243, 170), outline=rgba(INK, 26), width=1)
        draw.text((x + 18, footer_y + 18), title, font=load_mono(12), fill=rgba(MUTED, 210))
        draw.text((x + 18, footer_y + 58), copy, font=load_font(22), fill=rgba(INK, 190), spacing=5)

    noise = ImageDraw.Draw(image, "RGBA")
    for x in range(0, width, 4):
        for y in range(0, height, 4):
            alpha = 8 if (x + y) % 16 == 0 else 0
            if alpha:
                noise.point((x, y), fill=(255, 255, 255, alpha))

    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output, "PNG")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()
    render(args.output, args.width, args.height)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
