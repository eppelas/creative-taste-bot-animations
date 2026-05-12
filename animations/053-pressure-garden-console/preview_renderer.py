#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


BG = (6, 7, 10)
TEXT = (221, 227, 232)
MUTED = (129, 144, 154)
WHITE = (235, 231, 226)
CYAN = (121, 202, 226)
CRIMSON = (182, 44, 72)
ROSE = (240, 139, 140)
AMBER = (213, 179, 109)


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
        t = y / max(1, height - 1)
        color = (
            int(13 - 10 * t),
            int(18 - 14 * t),
            int(24 - 18 * t),
            255,
        )
        draw.line((0, y, width, y), fill=color)
    return image


def radial(size: tuple[int, int], center: tuple[float, float], radius: float, color: tuple[int, int, int], alpha: int) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for step in range(20, 0, -1):
        t = step / 20
        r = radius * t
        draw.ellipse(
            (center[0] - r, center[1] - r, center[0] + r, center[1] + r),
            fill=rgba(color, int(alpha * (t**2) * 0.34)),
        )
    return layer.filter(ImageFilter.GaussianBlur(radius * 0.08))


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def render(output: Path, width: int, height: int) -> None:
    rng = random.Random(53)
    image = gradient((width, height))
    for center, radius, color, alpha in (
        ((width * 0.18, height * 0.2), width * 0.22, CYAN, 100),
        ((width * 0.82, height * 0.78), width * 0.24, CRIMSON, 112),
        ((width * 0.55, height * 0.42), width * 0.28, WHITE, 34),
    ):
        image = Image.alpha_composite(image, radial((width, height), center, radius, color, alpha))

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    step = max(34, width // 28)
    for x in range(0, width, step):
        draw.line((x, 0, x, height), fill=(128, 170, 186, 18), width=1)
    for y in range(0, height, step):
        draw.line((0, y, width, y), fill=(128, 170, 186, 18), width=1)

    draw.text((24, 14), "#053 generated animation", font=mono(12), fill=rgba(MUTED, 214))
    draw.text((width - 348, 14), "browser-native pressure console study", font=mono(12), fill=rgba(MUTED, 214))

    margin = 18
    top = 58
    left_w = int((width - margin * 2 - 16) * 0.66)
    right_x = margin + left_w + 16
    panel = (margin, top, margin + left_w, height - 220)
    stack = (right_x, top, width - margin, height - 220)

    for rect in (panel, stack):
        rounded(draw, rect, 30, (8, 11, 16, 228), (123, 174, 188, 44), 2)
        rounded(draw, (rect[0] + 12, rect[1] + 12, rect[2] - 12, rect[3] - 12), 22, None, (115, 157, 170, 28), 1)

    draw.text((panel[0] + 20, panel[1] + 18), "PRESSURE GARDEN CONSOLE", font=mono(12), fill=rgba(MUTED, 220))
    draw.multiline_text((panel[0] + 20, panel[1] + 42), "Controls that\nactually retune\nthe field.", font=font(42), fill=rgba(TEXT, 240), spacing=4)
    draw.multiline_text(
        (panel[2] - 286, panel[1] + 22),
        "White dots to red pressure,\nrounded seams, rooted density.\nNo detached fake chrome.",
        font=font(18),
        fill=rgba(TEXT, 186),
        spacing=4,
        align="right",
    )

    field_box = (panel[0] + 42, panel[1] + 132, panel[2] - 38, panel[3] - 44)
    rounded(draw, field_box, 26, (10, 14, 19, 150), (129, 187, 202, 28), 1)

    # Membranes
    membrane = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    mdraw = ImageDraw.Draw(membrane, "RGBA")
    for i in range(6):
        left = field_box[0] + 30 + i * 54
        top_y = field_box[1] + 40 + i * 42
        w = 208 + i * 14
        h = 72 + (i % 3) * 18
        wobble = math.sin(i * 0.7) * 22
        points = [
            (left, top_y),
            (left + w * 0.24, top_y - wobble),
            (left + w * 0.76, top_y + h + wobble),
            (left + w, top_y + h * 0.58),
            (left + w * 0.82, top_y + h + wobble),
            (left + w * 0.2, top_y + h),
        ]
        mdraw.polygon(points, fill=rgba(CYAN if i % 2 == 0 else CRIMSON, 18), outline=rgba(CYAN, 70))
    membrane = membrane.filter(ImageFilter.GaussianBlur(6))
    image = Image.alpha_composite(image, membrane)

    draw = ImageDraw.Draw(image, "RGBA")

    # Lanes
    for i in range(7):
        pts = []
        base_y = field_box[1] + 54 + i * ((field_box[3] - field_box[1] - 108) / 6)
        for step_i in range(7):
            x = field_box[0] + 24 + step_i * ((field_box[2] - field_box[0] - 52) / 6)
            y = base_y + math.sin(step_i * 0.9 + i * 0.7) * (16 + i * 1.4)
            pts.append((x, y))
        draw.line(pts, fill=rgba(CYAN if i % 3 == 0 else WHITE, 120 if i % 3 == 0 else 54), width=3 if i % 3 == 0 else 2)

    # Particle field
    for row in range(11):
        for col in range(15):
            x = field_box[0] + 28 + col * ((field_box[2] - field_box[0] - 56) / 14)
            y = field_box[1] + 36 + row * ((field_box[3] - field_box[1] - 74) / 10)
            x += math.cos((row * 0.6) + (col * 0.4)) * 10
            y += math.sin((row * 0.5) + (col * 0.8)) * 8
            r = 3 + ((row + col) % 3)
            glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            gdraw = ImageDraw.Draw(glow, "RGBA")
            tone = CRIMSON if (row + col) % 4 == 0 else WHITE
            gdraw.ellipse((x - r * 3, y - r * 3, x + r * 3, y + r * 3), fill=rgba(tone, 28))
            glow = glow.filter(ImageFilter.GaussianBlur(8))
            image = Image.alpha_composite(image, glow)
            draw = ImageDraw.Draw(image, "RGBA")
            draw.ellipse((x - r, y - r, x + r, y + r), fill=rgba(tone, 212))
            draw.ellipse((x - r * 0.45, y - r * 0.45, x + r * 0.45, y + r * 0.45), fill=rgba(ROSE if tone == CRIMSON else WHITE, 228))

    pill = (panel[0] + 20, panel[3] - 48, panel[0] + 420, panel[3] - 14)
    rounded(draw, pill, 999, (8, 12, 17, 152), (126, 173, 190, 44), 1)
    draw.text((pill[0] + 16, pill[1] + 10), "LIVE PARAMETER ECHO: WHITE DOTS, RED PRESSURE, ROUNDED LANES", font=mono(11), fill=rgba(TEXT, 176))

    card_x = stack[0] + 16
    card_w = stack[2] - stack[0] - 32
    heights = [312, 132, 160]
    titles = ["TUNER RAIL", "LIVE METERS", "LEGEND FRAGMENTS"]
    y = stack[1] + 16
    for idx, h in enumerate(heights):
        box = (card_x, y, card_x + card_w, y + h)
        rounded(draw, box, 22, (10, 14, 19, 206), (115, 157, 170, 38), 1)
        draw.text((card_x + 16, y + 16), titles[idx], font=mono(12), fill=rgba(MUTED, 220))
        y += h + 16

    tuner_y = stack[1] + 48
    tuner_titles = ["PARTICLE POLARITY", "WAVE CURVATURE", "MEMBRANE DENSITY"]
    tuner_values = ["WHITE TO RED", "ROUNDED BRAID", "ROOTED MIDDLE"]
    for idx, title in enumerate(tuner_titles):
        box = (card_x + 14, tuner_y + idx * 88, card_x + card_w - 14, tuner_y + idx * 88 + 74)
        active = idx == 0
        rounded(draw, box, 18, (15, 20, 27, 226), (182, 44, 72, 80) if active else (115, 157, 170, 34), 1)
        draw.text((box[0] + 14, box[1] + 12), title, font=mono(11), fill=rgba(MUTED, 214))
        draw.text((box[2] - 132, box[1] + 12), tuner_values[idx], font=mono(11), fill=rgba(TEXT, 214))
        mini = (box[0] + 14, box[1] + 34, box[2] - 14, box[3] - 12)
        rounded(draw, mini, 14, (255, 255, 255, 10), (115, 157, 170, 20), 1)
        for j in range(3):
            cx = mini[0] + 28 + j * 68
            cy = mini[1] + 12 + (j % 2) * 12
            col = CRIMSON if idx == 0 and j == 2 else WHITE if idx == 0 else CYAN if idx == 1 else ROSE
            draw.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=rgba(col, 220))
        draw.line((mini[0] + 18, mini[3] - 14, mini[0] + 94, mini[1] + 10, mini[0] + 176, mini[3] - 10, mini[2] - 16, mini[1] + 6), fill=rgba(CYAN, 138), width=2)

    meter_top = stack[1] + 344
    meter_specs = [("POLARITY", 0.74, CYAN), ("CURVATURE", 0.64, ROSE), ("DENSITY", 0.58, AMBER)]
    for idx, (label, value, tint) in enumerate(meter_specs):
        row_y = meter_top + 14 + idx * 30
        draw.text((card_x + 16, row_y), label, font=mono(11), fill=rgba(MUTED, 214))
        track = (card_x + 106, row_y + 6, card_x + card_w - 16, row_y + 16)
        rounded(draw, track, 999, (255, 255, 255, 14), None, 1)
        fill_w = (track[2] - track[0]) * value
        rounded(draw, (track[0], track[1], track[0] + fill_w, track[3]), 999, rgba(tint, 192), None, 1)

    swatch_top = stack[1] + 492
    for idx in range(3):
        x0 = card_x + 16 + idx * ((card_w - 48) / 3)
        x1 = x0 + ((card_w - 48) / 3)
        box = (x0, swatch_top, x1, swatch_top + 54)
        rounded(draw, box, 14, (255, 255, 255, 10), (115, 157, 170, 20), 1)
        if idx == 0:
            for j, col in enumerate((WHITE, WHITE, CRIMSON)):
                cx = x0 + 18 + j * 26
                draw.ellipse((cx - 4, swatch_top + 23 - 4, cx + 4, swatch_top + 23 + 4), fill=rgba(col, 220))
        elif idx == 1:
            draw.ellipse((x0 + 16, swatch_top + 12, x0 + 56, swatch_top + 42), fill=rgba(CYAN, 70))
            draw.ellipse((x0 + 38, swatch_top + 8, x0 + 88, swatch_top + 38), fill=rgba(ROSE, 54))
        else:
            for j, col in enumerate((WHITE, CYAN, CRIMSON)):
                draw.line((x0 + 12, swatch_top + 18 + j * 8, x1 - 12, swatch_top + 8 + j * 12), fill=rgba(col, 78), width=3)

    footer_y = height - 188
    footer_w = (width - 36 - 32) / 3
    footer_titles = ["IDEA", "INTERACTION", "NEXT"]
    footer_copy = [
        "Controls visibly retune the same image.",
        "Pointer shear plus click tuning.",
        "Later: combine tuners or attach a body.",
    ]
    for idx in range(3):
        x = 18 + idx * (footer_w + 16)
        rounded(draw, (x, footer_y, x + footer_w, footer_y + 168), 24, (9, 13, 18, 206), (118, 161, 175, 46), 2)
        draw.text((x + 18, footer_y + 16), footer_titles[idx], font=mono(12), fill=rgba(TEXT, 200))
        draw.multiline_text((x + 18, footer_y + 52), footer_copy[idx], font=font(18), fill=rgba(TEXT, 184), spacing=4)

    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output, quality=95)


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
