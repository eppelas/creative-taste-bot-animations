#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


BG_TOP = (246, 241, 234)
BG_BOTTOM = (238, 229, 218)
TEXT = (36, 50, 48)
MUTED = (93, 111, 107)
LINE = (94, 122, 118, 42)
PAPER = (255, 252, 247, 214)
MINT = (130, 203, 189)
TEAL = (74, 140, 137)
CYAN = (176, 235, 225)
AMBER = (240, 191, 134)
ROSE = (219, 156, 165)
LEAF = (201, 224, 177)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def rounded(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], radius: float, fill, outline, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def add_glow(base: Image.Image, cx: float, cy: float, radius: float, color: tuple[int, int, int], alpha: int) -> Image.Image:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color + (alpha,))
    return Image.alpha_composite(base, overlay.filter(ImageFilter.GaussianBlur(radius=radius * 0.34)))


def draw_gradient_background(width: int, height: int) -> Image.Image:
    image = Image.new("RGBA", (width, height), BG_BOTTOM + (255,))
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(round(lerp(BG_TOP[i], BG_BOTTOM[i], t)) for i in range(3)) + (255,)
        draw.line((0, y, width, y), fill=color)
    image = add_glow(image, width * 0.16, height * 0.1, min(width, height) * 0.22, CYAN, 36)
    image = add_glow(image, width * 0.82, height * 0.16, min(width, height) * 0.18, AMBER, 28)
    image = add_glow(image, width * 0.58, height * 0.86, min(width, height) * 0.16, ROSE, 24)
    return image


def draw_grid(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    for x in range(0, width, 88):
        draw.line((x, 0, x, height), fill=(94, 122, 118, 10), width=1)
    for y in range(0, height, 88):
        draw.line((0, y, width, y), fill=(94, 122, 118, 10), width=1)


def draw_header(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float]) -> None:
    rounded(draw, box, 30, PAPER, LINE, 2)
    x0, y0, x1, y1 = box
    draw.text((x0 + 24, y0 + 20), "CREATIVE TASTE BOT MOTION STUDY 041", fill=MUTED)
    draw.text((x0 + 24, y0 + 54), "Opaline Pressure Greenhouse", fill=TEXT)
    draw.multiline_text(
        (x0 + 24, y0 + 104),
        "A pale living control surface where one rooted greenhouse body,\n"
        "opaline side chambers, and tactile sliders inhabit the same\n"
        "folio-like page instead of a detached dashboard.",
        fill=(36, 50, 48, 214),
        spacing=9,
    )
    pills = ["mode: pulse", "humidity: 64%", "permeability: 48%"]
    for index, pill in enumerate(pills):
        px = x0 + 24 + index * 146
        rounded(draw, (px, y1 - 42, px + 128, y1 - 12), 15, (255, 255, 255, 132), (94, 122, 118, 26))
        draw.text((px + 14, y1 - 33), pill, fill=(36, 50, 48, 208))


def draw_overview(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float]) -> None:
    rounded(draw, box, 30, PAPER, LINE, 2)
    x0, y0, x1, y1 = box
    draw.text((x0 + 22, y0 + 20), "SYSTEM NOTES", fill=MUTED)
    draw.multiline_text(
        (x0 + 22, y0 + 52),
        "Recent notes favored a lighter HTML/control-surface lane:\n"
        "shared field motion, opaline compartments, and tactile\n"
        "biology instead of fake software chrome.",
        fill=(36, 50, 48, 206),
        spacing=8,
    )
    labels = [("root ribs", MINT), ("opaline chambers", CYAN), ("pulse pollen", AMBER), ("blush weather", ROSE)]
    for idx, (label, color) in enumerate(labels):
        py = y0 + 150 + idx * 26
        draw.ellipse((x0 + 24, py, x0 + 34, py + 10), fill=color + (255,))
        draw.text((x0 + 44, py - 2), label, fill=(36, 50, 48, 194))


def draw_left_cards(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float]) -> None:
    rounded(draw, box, 28, PAPER, LINE, 2)
    x0, y0, x1, _ = box
    draw.text((x0 + 18, y0 + 18), "CLIMATE CARDS", fill=MUTED)
    cards = [
        ("Lower Support", "Four basin roots hold the organism so the page stays believable."),
        ("Face Logic", "Light wells and membranes replace a human face."),
        ("Design Use", "The layout aims for a strange folio instead of a creature portrait alone."),
    ]
    top = y0 + 48
    for title, copy in cards:
        rounded(draw, (x0 + 16, top, x1 - 16, top + 104), 18, (255, 255, 255, 118), (94, 122, 118, 20))
        draw.text((x0 + 28, top + 16), title, fill=(36, 50, 48, 220))
        draw.multiline_text((x0 + 28, top + 42), copy, fill=(36, 50, 48, 176), spacing=7)
        top += 118


def draw_right_cards(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float]) -> None:
    rounded(draw, box, 28, PAPER, LINE, 2)
    x0, y0, x1, _ = box
    draw.text((x0 + 18, y0 + 18), "SIGNAL READOUTS", fill=MUTED)
    rounded(draw, (x0 + 16, y0 + 48, x1 - 16, y0 + 198), 18, (255, 255, 255, 118), (94, 122, 118, 20))
    bars = [("Dew wells", 0.58, CYAN), ("Root lift", 0.44, LEAF), ("Blush tide", 0.31, ROSE)]
    for idx, (label, value, color) in enumerate(bars):
        py = y0 + 74 + idx * 36
        draw.text((x0 + 28, py), label, fill=(36, 50, 48, 210))
        draw.text((x1 - 74, py), f"{value:.2f}", fill=(36, 50, 48, 200))
        rounded(draw, (x0 + 28, py + 18, x1 - 28, py + 28), 6, (94, 122, 118, 18), None)
        rounded(draw, (x0 + 28, py + 18, x0 + 28 + (x1 - x0 - 56) * value, py + 28), 6, color + (210,), None)
    rounded(draw, (x0 + 16, y0 + 214, x1 - 16, y0 + 320), 18, (255, 255, 255, 118), (94, 122, 118, 20))
    draw.text((x0 + 28, y0 + 230), "Pointer Rule", fill=(36, 50, 48, 220))
    draw.multiline_text(
        (x0 + 28, y0 + 258),
        "Drag local focus,\n"
        "wake pollen arcs,\n"
        "and part nearby\n"
        "membranes.",
        fill=(36, 50, 48, 176),
        spacing=7,
    )


def draw_chamber(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], color: tuple[int, int, int]) -> None:
    rounded(draw, box, 26, color + (72,), (94, 122, 118, 18), 1)
    x0, y0, x1, y1 = box
    for band in range(4):
        yy = y0 + (band + 1) * ((y1 - y0) / 5)
        points = []
        for step in range(18):
            t = step / 17
            px = x0 + t * (x1 - x0)
            py = yy + math.sin(t * math.tau * 1.2 + band * 0.8) * ((y1 - y0) * 0.06)
            points.append((px, py))
        draw.line(points, fill=color + (96,), width=3)


def draw_stage(base: Image.Image, box: tuple[float, float, float, float]) -> None:
    draw = ImageDraw.Draw(base, "RGBA")
    rounded(draw, box, 30, (255, 250, 244, 206), LINE, 2)
    x0, y0, x1, y1 = box
    inner = (x0 + 16, y0 + 16, x1 - 16, y1 - 16)
    rounded(draw, inner, 24, (255, 250, 244, 148), (255, 255, 255, 118), 1)
    ix0, iy0, ix1, iy1 = inner
    iw = ix1 - ix0
    ih = iy1 - iy0

    for row in range(7):
        yy = iy0 + ih * (0.12 + row * 0.12)
        points = []
        for step in range(24):
            t = step / 23
            px = ix0 + iw * t
            py = yy + math.sin(t * math.tau * 1.1 + row * 0.6) * (5 + row * 0.8)
            points.append((px, py))
        draw.line(points, fill=(94, 122, 118, 20), width=1)

    chambers = [
        (ix0 + iw * 0.08, iy0 + ih * 0.1, ix0 + iw * 0.28, iy0 + ih * 0.26, CYAN),
        (ix0 + iw * 0.72, iy0 + ih * 0.08, ix0 + iw * 0.9, iy0 + ih * 0.22, AMBER),
        (ix0 + iw * 0.1, iy0 + ih * 0.56, ix0 + iw * 0.32, iy0 + ih * 0.72, LEAF),
        (ix0 + iw * 0.74, iy0 + ih * 0.54, ix0 + iw * 0.92, iy0 + ih * 0.74, ROSE),
    ]
    for chamber in chambers:
        draw_chamber(draw, chamber[:4], chamber[4])

    cx = ix0 + iw * 0.52
    cy = iy0 + ih * 0.52
    body_w = iw * 0.24
    body_h = ih * 0.36
    base = add_glow(base, cx, cy, body_w * 1.1, CYAN, 42)
    base = add_glow(base, cx, cy + body_h * 0.1, body_w * 0.8, ROSE, 24)
    draw = ImageDraw.Draw(base, "RGBA")

    for scale, alpha in ((1.18, 116), (0.92, 100), (0.66, 86)):
        bbox = (cx - body_w * scale, cy - body_h * scale, cx + body_w * scale, cy + body_h * scale)
        draw.ellipse(bbox, fill=(255, 255, 255, alpha), outline=(74, 140, 137, 40), width=2)

    for i in range(4):
        offset = (i - 1.5) * body_w * 0.42
        draw.line(
            (
                cx + offset * 0.4,
                cy + body_h * 0.8,
                cx + offset,
                cy + body_h * 1.2,
                cx + offset * 1.42,
                iy1 - 28,
            ),
            fill=(74, 140, 137, 110),
            width=5,
            joint="curve",
        )
        draw.line(
            (
                cx + offset * 0.42,
                cy + body_h * 0.88,
                cx + offset * 1.1,
                cy + body_h * 1.28,
                cx + offset * 1.7,
                iy1 - 18,
            ),
            fill=(74, 140, 137, 76),
            width=3,
            joint="curve",
        )

    for idx in range(-2, 3):
        rx = cx + idx * 24
        draw.ellipse((rx - 7, cy - 20, rx + 7, cy + 20), fill=(255, 255, 255, 220 if idx else 255))

    for index in range(54):
        angle = index * 0.31
        radius_x = body_w * (1.5 + (index % 6) * 0.06)
        radius_y = body_h * (1.12 + (index % 4) * 0.08)
        px = cx + math.cos(angle) * radius_x
        py = cy + math.sin(angle * 1.28) * radius_y
        size = 2 if index % 5 else 4
        color = AMBER if index % 3 else ROSE
        draw.ellipse((px - size, py - size, px + size, py + size), fill=color + (146,))

    control_y = iy1 - 104
    modes = [("Pulse", True), ("Drift", False), ("Bloom", False)]
    for index, (label, active) in enumerate(modes):
        px = ix0 + 30 + index * 104
        rounded(draw, (px, control_y, px + 88, control_y + 34), 16, (255, 255, 255, 138 if active else 104), (94, 122, 118, 26))
        draw.text((px + 18, control_y + 10), label, fill=(36, 50, 48, 220))

    sliders = [("Humidity", 0.64), ("Permeability", 0.48)]
    for index, (label, value) in enumerate(sliders):
        sx0 = ix0 + 30 + index * 196
        sx1 = sx0 + 182
        sy0 = iy1 - 56
        rounded(draw, (sx0, sy0, sx1, sy0 + 38), 18, (255, 255, 255, 120), (94, 122, 118, 18))
        draw.text((sx0 + 14, sy0 + 9), label, fill=(36, 50, 48, 206))
        draw.text((sx1 - 54, sy0 + 9), f"{round(value * 100)}%", fill=(36, 50, 48, 206))
        rounded(draw, (sx0 + 14, sy0 + 24, sx1 - 14, sy0 + 30), 4, (94, 122, 118, 18), None)
        rounded(draw, (sx0 + 14, sy0 + 24, sx0 + 14 + (sx1 - sx0 - 28) * value, sy0 + 30), 4, (74, 140, 137, 186), None)


def draw_footer(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float]) -> None:
    rounded(draw, box, 30, PAPER, LINE, 2)
    x0, y0, x1, _ = box
    draw.text((x0 + 20, y0 + 18), "REVIEW NOTES", fill=MUTED)
    cards = [
        ("Idea", "Translate the pale greenhouse control-surface image lane into one living browser page with believable rooted support."),
        ("Interaction", "Pointer drift parts nearby membranes while the sliders retune humidity thickness and chamber opening."),
        ("Next", "A later variant could retile these modules into a flatter editorial layout without losing the tactile biology."),
    ]
    card_w = (x1 - x0 - 52) / 3
    for idx, (title, copy) in enumerate(cards):
        left = x0 + 16 + idx * (card_w + 10)
        rounded(draw, (left, y0 + 46, left + card_w, y0 + 144), 18, (255, 255, 255, 118), (94, 122, 118, 20))
        draw.text((left + 14, y0 + 60), title, fill=(36, 50, 48, 220))
        draw.multiline_text((left + 14, y0 + 88), copy, fill=(36, 50, 48, 176), spacing=7)


def render(width: int, height: int) -> Image.Image:
    image = draw_gradient_background(width, height)
    draw = ImageDraw.Draw(image, "RGBA")
    draw_grid(draw, width, height)

    shell = (22, 22, width - 22, height - 22)
    rounded(draw, shell, 34, (255, 252, 247, 44), (255, 255, 255, 86), 1)

    header = (34, 34, width - 328, 248)
    overview = (width - 310, 34, width - 34, 248)
    left = (34, 266, 288, 856)
    stage = (306, 266, width - 326, 856)
    right = (width - 308, 266, width - 34, 856)
    footer = (34, 874, width - 34, height - 34)

    draw_header(draw, header)
    draw_overview(draw, overview)
    draw_left_cards(draw, left)
    draw_stage(image, stage)
    draw = ImageDraw.Draw(image, "RGBA")
    draw_right_cards(draw, right)
    draw_footer(draw, footer)
    return image


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    image = render(args.width, args.height)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(args.output, "PNG")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
