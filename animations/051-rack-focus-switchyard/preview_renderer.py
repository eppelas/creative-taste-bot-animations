#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


BG = (6, 8, 11)
TEXT = (216, 222, 227)
MUTED = (129, 144, 154)
CYAN = (130, 215, 234)
MAGENTA = (255, 110, 157)
AMBER = (239, 191, 126)
ACID = (215, 239, 109)


def rgba(color: tuple[int, int, int], alpha: int) -> tuple[int, int, int, int]:
    return color[0], color[1], color[2], alpha


def font(size: int):
    for path in (
        "/System/Library/Fonts/Supplemental/Arial Narrow.ttf",
        "/System/Library/Fonts/Supplemental/Trebuchet MS.ttf",
        "/System/Library/Fonts/SFNS.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def mono(size: int):
    for path in (
        "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def gradient(size: tuple[int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size, BG + (255,))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / max(height - 1, 1)
        color = (int(12 - 10 * t), int(16 - 13 * t), int(20 - 15 * t), 255)
        draw.line((0, y, width, y), fill=color)
    return image


def radial(size: tuple[int, int], center: tuple[float, float], radius: float, color: tuple[int, int, int], alpha: int) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for step in range(16, 0, -1):
        t = step / 16
        r = radius * t
        draw.ellipse(
            (center[0] - r, center[1] - r, center[0] + r, center[1] + r),
            fill=rgba(color, int(alpha * 0.32 * (t**2))),
        )
    return layer.filter(ImageFilter.GaussianBlur(radius * 0.08))


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_pane(draw: ImageDraw.ImageDraw, box, tilt: float, title_glow: tuple[int, int, int], line_colors: list[tuple[int, int, int]], seed: int) -> None:
    rng = random.Random(seed)
    layer = Image.new("RGBA", draw._image.size, (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(layer, "RGBA")
    x0, y0, x1, y1 = box
    rounded(ldraw, box, 30, (11, 17, 23, 150), (124, 170, 184, 54), 2)
    rounded(ldraw, (x0 + 22, y0 + 24, x1 - 22, y0 + 62), 18, (255, 255, 255, 12), (255, 255, 255, 18), 1)

    for idx in range(3):
        pts = []
        line_y = y0 + 74 + idx * 46
        for step in range(7):
            px = x0 + 30 + step * ((x1 - x0 - 60) / 6)
            py = line_y + math.sin(step * 0.9 + idx * 1.2 + tilt) * (18 + idx * 6) + rng.uniform(-4, 4)
            pts.append((px, py))
        ldraw.line(pts, fill=rgba(line_colors[idx], 164 if idx == 1 else 110), width=3 if idx == 1 else 2)

    for idx in range(3):
        px = x0 + 48 + idx * ((x1 - x0 - 96) / 2)
        py = y0 + 84 + idx * 32
        r = 6 if idx == 1 else 5
        ldraw.ellipse((px - r, py - r, px + r, py + r), fill=rgba(line_colors[idx], 240))

    glow = Image.new("RGBA", draw._image.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow, "RGBA")
    gdraw.ellipse((x0 + 42, y0 + 32, x1 - 42, y0 + 118), fill=rgba(title_glow, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(22))
    draw._image.alpha_composite(glow)
    draw._image.alpha_composite(layer)


def render(output: Path, width: int, height: int) -> None:
    image = gradient((width, height))
    for center, radius, color, alpha in (
        ((width * 0.28, height * 0.16), width * 0.24, (42, 66, 76), 130),
        ((width * 0.74, height * 0.3), width * 0.2, (127, 36, 53), 96),
        ((width * 0.42, height * 0.84), width * 0.22, (28, 78, 91), 88),
    ):
        image = Image.alpha_composite(image, radial((width, height), center, radius, color, alpha))

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    step = max(34, width // 28)
    for x in range(0, width, step):
        draw.line((x, 0, x, height), fill=(124, 160, 171, 18), width=1)
    for y in range(0, height, step):
        draw.line((0, y, width, y), fill=(124, 160, 171, 18), width=1)

    draw.text((24, 14), "#051 generated animation", font=mono(12), fill=rgba(MUTED, 214))
    draw.text((width - 350, 14), "browser-native split-focus interface study", font=mono(12), fill=rgba(MUTED, 214))

    margin = 18
    top = 58
    left_w = int((width - margin * 2 - 16) * 0.63)
    right_x = margin + left_w + 16
    hero = (margin, top, margin + left_w, height - 218)
    stack = (right_x, top, width - margin, height - 218)

    for rect in (hero, stack):
        rounded(draw, rect, 28, (8, 11, 15, 228), (123, 174, 188, 44), 2)
        rounded(draw, (rect[0] + 12, rect[1] + 12, rect[2] - 12, rect[3] - 12), 22, None, (115, 157, 170, 28), 1)

    draw.text((hero[0] + 20, hero[1] + 18), "RACK FOCUS SWITCHYARD", font=mono(12), fill=rgba(MUTED, 220))
    draw.multiline_text((hero[0] + 20, hero[1] + 42), "Distributed panes,\nno mascot center.", font=font(42), fill=rgba(TEXT, 240), spacing=4)
    draw.multiline_text(
        (hero[2] - 270, hero[1] + 20),
        "Pointer-repelled branch growth,\nreflected relay traffic,\nand a living page instead of a single specimen.",
        font=font(18),
        fill=rgba(TEXT, 184),
        spacing=4,
        align="right",
    )

    draw.line((hero[0] + 82, hero[1] + 162, hero[2] - 86, hero[1] + 162), fill=(123, 174, 188, 40), width=1)
    draw.line((hero[0] + 82, hero[1] + 340, hero[2] - 86, hero[1] + 340), fill=(123, 174, 188, 36), width=1)
    draw.line((hero[0] + 82, hero[1] + 544, hero[2] - 86, hero[1] + 544), fill=(123, 174, 188, 36), width=1)

    pane_layer = ImageDraw.Draw(image, "RGBA")
    draw_pane(pane_layer, (hero[0] + 76, hero[1] + 96, hero[0] + 390, hero[1] + 308), -0.4, CYAN, [CYAN, MAGENTA, AMBER], 1)
    draw_pane(pane_layer, (hero[0] + 338, hero[1] + 74, hero[0] + 648, hero[1] + 322), 0.7, MAGENTA, [MAGENTA, CYAN, AMBER], 2)
    draw_pane(pane_layer, (hero[0] + 170, hero[1] + 360, hero[0] + 578, hero[1] + 602), 0.2, AMBER, [AMBER, CYAN, MAGENTA], 3)

    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow, "RGBA")
    for x, y, rx, ry, col in (
        (hero[0] + 208, hero[1] + 162, 94, 50, CYAN),
        (hero[0] + 492, hero[1] + 182, 112, 56, MAGENTA),
        (hero[0] + 372, hero[1] + 480, 136, 62, AMBER),
    ):
        gdraw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=rgba(col, 50))
    glow = glow.filter(ImageFilter.GaussianBlur(26))
    image.alpha_composite(glow)

    draw = ImageDraw.Draw(image, "RGBA")
    card_x = stack[0] + 16
    card_w = stack[2] - stack[0] - 32
    card_y = stack[1] + 16
    heights = [176, 168, 180]
    titles = ["MODE DRIVER", "RELAY BALANCE", "FIELD LEGEND"]
    for idx, height_box in enumerate(heights):
        box = (card_x, card_y, card_x + card_w, card_y + height_box)
        rounded(draw, box, 22, (10, 15, 20, 204), (115, 157, 170, 38), 1)
        draw.text((card_x + 16, card_y + 16), titles[idx], font=mono(12), fill=rgba(MUTED, 214))
        card_y += height_box + 16

    chip_y = stack[1] + 54
    chip_x = card_x + 16
    for idx, label in enumerate(("RACK", "DRIFT", "BRAID")):
        active = idx == 0
        width_chip = 88
        rounded(
            draw,
            (chip_x, chip_y, chip_x + width_chip, chip_y + 30),
            999,
            rgba(CYAN, 32) if active else (255, 255, 255, 10),
            rgba(CYAN, 80) if active else (255, 255, 255, 20),
            1,
        )
        draw.text((chip_x + 18, chip_y + 8), label, font=mono(12), fill=rgba(TEXT, 220))
        chip_x += width_chip + 8

    badge_y = stack[1] + 100
    for idx, (label, value) in enumerate((("ACTIVE PANE", "A1"), ("POINTER BIAS", "0.42"), ("ANCHORS", "3"))):
        x = card_x + 16 + idx * ((card_w - 32) / 3)
        rounded(draw, (x, badge_y, x + 94, badge_y + 56), 18, (255, 255, 255, 8), (115, 157, 170, 24), 1)
        draw.text((x + 10, badge_y + 8), label, font=mono(10), fill=rgba(MUTED, 214))
        draw.text((x + 10, badge_y + 28), value, font=font(22), fill=rgba(TEXT, 228))

    meter_y = stack[1] + 230
    for idx, (label, value, tint) in enumerate((("PANE A1", 46, CYAN), ("PANE B4", 58, MAGENTA), ("PANE C2", 62, AMBER))):
        y = meter_y + idx * 40
        draw.text((card_x + 16, y), label, font=mono(12), fill=rgba(MUTED, 214))
        rounded(draw, (card_x + 116, y + 6, card_x + card_w - 56, y + 16), 999, (255, 255, 255, 16), None, 1)
        fill_w = (card_w - 172) * value / 100
        rounded(draw, (card_x + 116, y + 6, card_x + 116 + fill_w, y + 16), 999, rgba(tint, 180), None, 1)
        draw.text((card_x + card_w - 40, y - 2), f"{value}", font=mono(12), fill=rgba(TEXT, 214))

    legend_y = stack[1] + 420
    for idx, (tint, copy) in enumerate((
        (CYAN, "stable pane ownership"),
        (MAGENTA, "double-exposure drift"),
        (AMBER, "late traffic catchup"),
        (ACID, "cursor repulsion seeds"),
    )):
        y = legend_y + idx * 28
        draw.rounded_rectangle((card_x + 16, y + 8, card_x + 58, y + 16), radius=999, fill=rgba(tint, 180))
        draw.text((card_x + 72, y), copy, font=font(16), fill=rgba(TEXT, 188))

    footer_y = height - 188
    gap = 16
    footer_w = (width - 36 - gap * 2) / 3
    footer_titles = ["IDEA", "INTERACTION", "NEXT"]
    footer_copy = [
        "Multi-pane cinematic control surface",
        "Repel, retune, plant anchors",
        "Human trace or live input next",
    ]
    for idx in range(3):
        x = 18 + idx * (footer_w + gap)
        rounded(draw, (x, footer_y, x + footer_w, footer_y + 168), 24, (9, 13, 18, 206), (118, 161, 175, 46), 2)
        draw.text((x + 18, footer_y + 16), footer_titles[idx], font=mono(12), fill=rgba(TEXT, 200))
        draw.multiline_text((x + 18, footer_y + 52), footer_copy[idx], font=font(18), fill=rgba(TEXT, 184), spacing=4)

    noise = ImageDraw.Draw(image, "RGBA")
    rng = random.Random(51)
    for _ in range(2800):
        noise.point((rng.randrange(width), rng.randrange(height)), fill=(255, 255, 255, rng.randrange(8, 22)))

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
