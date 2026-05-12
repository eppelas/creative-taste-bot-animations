#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def hex_rgba(value: str, alpha: int) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a,)[0] * t


def vertical_gradient(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size)
    draw = ImageDraw.Draw(image)
    a = hex_rgba(top, 255)
    b = hex_rgba(bottom, 255)
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(int(lerp(a[i], b[i], t)) for i in range(3)) + (255,)
        draw.line((0, y, width, y), fill=color)
    return image


def radial_glow(size: tuple[int, int], center: tuple[float, float], radius: float, color: str, alpha: int) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for step in range(18, 0, -1):
        t = step / 18
        r = radius * t
        draw.ellipse(
            (center[0] - r, center[1] - r, center[0] + r, center[1] + r),
            fill=hex_rgba(color, int(alpha * (t**2) * 0.34)),
        )
    return layer.filter(ImageFilter.GaussianBlur(radius * 0.08))


def serif(size: int):
    for path in (
        "/System/Library/Fonts/Supplemental/Palatino.ttc",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
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


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def sample_box(draw: ImageDraw.ImageDraw, box, tone: str, tag: str, title: str, metric: str) -> None:
    tones = {
        "blue": "#eff6f8",
        "green": "#edf5e8",
        "amber": "#f7eee5",
        "rose": "#f8eceb",
    }
    rounded(draw, box, 20, hex_rgba(tones[tone], 240), hex_rgba("#60533a", 28), 1)
    draw.text((box[0] + 12, box[1] + 10), tag, font=mono(11), fill=hex_rgba("#60533a", 150))
    draw.text((box[0] + 12, box[1] + 32), title, font=serif(23), fill=hex_rgba("#413729", 238))
    draw.text((box[0] + 12, box[1] + 74), metric, font=mono(12), fill=hex_rgba("#413729", 160))


def render(output: Path, width: int, height: int) -> None:
    rng = random.Random(50)
    size = (width, height)
    image = vertical_gradient(size, "#f4ede2", "#e7dbc9")

    for center, radius, color, alpha in (
        ((width * 0.12, height * 0.1), width * 0.18, "#ffffff", 120),
        ((width * 0.84, height * 0.18), width * 0.16, "#7ca7bc", 54),
        ((width * 0.18, height * 0.86), width * 0.18, "#93b087", 58),
        ((width * 0.78, height * 0.84), width * 0.16, "#cc8f88", 54),
    ):
        image = Image.alpha_composite(image, radial_glow(size, center, radius, color, alpha))

    ui = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(ui, "RGBA")

    for x in range(0, width, 88):
        draw.line((x, 0, x, height), fill=(96, 83, 58, 18), width=1)
    for y in range(0, height, 88):
        draw.line((0, y, width, y), fill=(96, 83, 58, 18), width=1)

    margin = 18
    header_h = 168
    left_w = 286
    right_w = 298
    footer_h = 182
    gap = 14

    header_left = (margin, margin, width - 390, margin + header_h)
    header_right = (header_left[2] + gap, margin, width - margin, margin + header_h)
    left_col = (margin, header_left[3] + gap, margin + left_w, height - footer_h - margin - gap)
    stage = (left_col[2] + gap, left_col[1], width - right_w - margin - gap, left_col[3])
    right_col = (stage[2] + gap, left_col[1], width - margin, left_col[3])
    footer = (margin, stage[3] + gap, width - margin, height - margin)

    for rect in (header_left, header_right, left_col, stage, right_col, footer):
      rounded(draw, rect, 28, hex_rgba("#fffaf2", 170), hex_rgba("#60533a", 54), 1)

    draw.text((header_left[0] + 16, header_left[1] + 16), "GENERATED ANIMATION 050", font=mono(12), fill=hex_rgba("#60533a", 170))
    draw.text((header_left[0] + 16, header_left[1] + 42), "Route Sample", font=serif(52), fill=hex_rgba("#413729", 240))
    draw.text((header_left[0] + 16, header_left[1] + 94), "Workbench", font=serif(52), fill=hex_rgba("#413729", 240))
    draw.text((header_left[0] + 18, header_left[1] + 134), "Draggable specimen slips retune one organic route board.", font=serif(20), fill=hex_rgba("#413729", 180))

    readout_x = header_left[0] + 16
    for i, (label, value) in enumerate((("ACTIVE SLIPS", "4"), ("ROUTE TENSION", "63%"), ("GARDEN DENSITY", "48%"))):
        x = readout_x + i * 146
        rounded(draw, (x, header_left[1] + 174, x + 132, header_left[1] + 226), 18, hex_rgba("#ffffff", 108), hex_rgba("#60533a", 26), 1)
        draw.text((x + 12, header_left[1] + 184), label, font=mono(10), fill=hex_rgba("#60533a", 150))
        draw.text((x + 12, header_left[1] + 201), value, font=serif(22), fill=hex_rgba("#413729", 230))

    draw.text((header_right[0] + 16, header_right[1] + 16), "WHY THIS BRANCH", font=mono(12), fill=hex_rgba("#60533a", 170))
    right_copy = [
        "A pale operable tool, not another atlas,",
        "manual, or dark dashboard. The board breaks",
        "the recent loop by making the main gesture",
        "physical: move the work samples and the page",
        "retunes around them."
    ]
    for i, line in enumerate(right_copy):
        draw.text((header_right[0] + 16, header_right[1] + 48 + i * 22), line, font=serif(18), fill=hex_rgba("#413729", 176))

    draw.text((left_col[0] + 16, left_col[1] + 16), "TRAY LOGIC", font=mono(12), fill=hex_rgba("#60533a", 170))
    tray_copy = [
        ("BLUE SAMPLE", "Cold route memory"),
        ("GREEN SAMPLE", "Lower-field creeper logic"),
        ("AMBER SAMPLE", "Dry support pressure"),
        ("ROSE SAMPLE", "Signal bloom and side loops"),
    ]
    for i, (head, line) in enumerate(tray_copy):
        y = left_col[1] + 48 + i * 74
        rounded(draw, (left_col[0] + 14, y, left_col[2] - 14, y + 60), 18, hex_rgba("#ffffff", 96), hex_rgba("#60533a", 22), 1)
        draw.text((left_col[0] + 26, y + 12), head, font=mono(10), fill=hex_rgba("#60533a", 150))
        draw.text((left_col[0] + 26, y + 30), line, font=serif(18), fill=hex_rgba("#413729", 180))

    feed_y = left_col[1] + 352
    draw.text((left_col[0] + 16, feed_y), "ROUTE FEED", font=mono(12), fill=hex_rgba("#60533a", 170))
    for i, (tag, color, value) in enumerate((("A1", "#7ca7bc", "62%"), ("B3", "#93b087", "71%"), ("C2", "#d5a46f", "58%"), ("D4", "#cc8f88", "66%"))):
        y = feed_y + 28 + i * 26
        draw.ellipse((left_col[0] + 18, y + 4, left_col[0] + 28, y + 14), fill=hex_rgba(color, 220))
        draw.text((left_col[0] + 38, y), tag, font=mono(12), fill=hex_rgba("#413729", 210))
        draw.text((left_col[2] - 62, y), value, font=mono(12), fill=hex_rgba("#413729", 170))

    rounded(draw, stage, 26, hex_rgba("#fffaf2", 124), hex_rgba("#60533a", 26), 1)
    draw.text((stage[0] + 18, stage[1] + 16), "WORKBENCH FIELD", font=mono(12), fill=hex_rgba("#60533a", 170))
    draw.text((stage[2] - 270, stage[1] + 16), "DRAG SAMPLES TO RETUNE THE BOARD", font=mono(11), fill=hex_rgba("#60533a", 150))

    sx0, sy0, sx1, sy1 = stage
    for x in range(sx0 + 30, sx1 - 20, 92):
        draw.line((x, sy0 + 40, x, sy1 - 18), fill=(96, 83, 58, 12), width=1)
    for y in range(sy0 + 40, sy1 - 18, 92):
        draw.line((sx0 + 20, y, sx1 - 20, y), fill=(96, 83, 58, 12), width=1)

    sample_specs = [
        ((sx0 + 48, sy0 + 84, sx0 + 204, sy0 + 192), "blue", "A1 COLD BRAID", "Sky rinse vial", "Lift 0.62"),
        ((sx0 + 360, sy0 + 102, sx0 + 516, sy0 + 210), "green", "B3 MOSS VALVE", "Creeper splice", "Humid 0.71"),
        ((sx0 + 126, sy0 + 360, sx0 + 282, sy0 + 468), "amber", "C2 ROOT BRACE", "Dry hinge chip", "Brace 0.58"),
        ((sx0 + 408, sy0 + 404, sx0 + 564, sy0 + 512), "rose", "D4 BLOOM SEAM", "Signal blush tile", "Bloom 0.66"),
    ]
    centers = []
    for box, tone, tag, title, metric in sample_specs:
        sample_box(draw, box, tone, tag, title, metric)
        centers.append(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2, tone))

    route_colors = {
        "blue": "#7ca7bc",
        "green": "#93b087",
        "amber": "#d5a46f",
        "rose": "#cc8f88",
    }
    for i in range(len(centers) - 1):
        ax, ay, atone = centers[i]
        bx, by, btone = centers[i + 1]
        mid_x = (ax + bx) / 2 + math.sin(i * 1.2) * 34
        mid_y = (ay + by) / 2 - math.cos(i * 0.9) * 58
        draw.line((ax, ay, mid_x, mid_y, bx, by), fill=hex_rgba(route_colors[atone], 48), width=16)
        draw.line((ax, ay, mid_x, mid_y, bx, by), fill=hex_rgba(route_colors[btone], 148), width=3)
        for t in range(7):
            u = t / 6
            x = ax * (1 - u) + bx * u + math.sin(u * math.pi * 2 + i) * 10
            y = ay * (1 - u) + by * u + math.cos(u * math.pi * 2 + i) * 8
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=hex_rgba(route_colors[atone if t < 3 else btone], 180))

    for idx in range(54):
        x = sx0 + 26 + (idx % 13) * 48 + math.sin(idx * 0.7) * 8
        y = sy0 + 462 + (idx // 13) * 52 + math.cos(idx * 0.9) * 10
        r = 2 + (idx % 3)
        fill = "#93b087" if idx % 3 == 0 else "#7ca7bc" if idx % 3 == 1 else "#cc8f88"
        draw.ellipse((x - r, y - r, x + r, y + r), fill=hex_rgba(fill, 92))
        if idx % 2 == 0:
            draw.line((x, y, x + math.sin(idx) * 12, y - 26 - (idx % 4) * 6), fill=hex_rgba("#7c8262", 46), width=1)

    dock_y = sy1 - 128
    rounded(draw, (sx0 + 18, dock_y, sx0 + 310, sy1 - 18), 20, hex_rgba("#ffffff", 114), hex_rgba("#60533a", 24), 1)
    rounded(draw, (sx0 + 324, dock_y, sx1 - 18, sy1 - 18), 20, hex_rgba("#ffffff", 114), hex_rgba("#60533a", 24), 1)
    draw.text((sx0 + 32, dock_y + 14), "CALIBRATION", font=mono(11), fill=hex_rgba("#60533a", 150))
    for i, (label, value, color) in enumerate((("CURRENT PULL", 0.63, "#7ca7bc"), ("ROOT SPREAD", 0.48, "#93b087"))):
        y = dock_y + 40 + i * 30
        draw.text((sx0 + 32, y), label, font=mono(11), fill=hex_rgba("#413729", 170))
        rounded(draw, (sx0 + 152, y + 4, sx0 + 276, y + 12), 999, hex_rgba("#60533a", 16))
        rounded(draw, (sx0 + 152, y + 4, sx0 + 152 + 124 * value, y + 12), 999, hex_rgba(color, 180))
        draw.text((sx0 + 242, y - 2), f"{value:.2f}", font=mono(11), fill=hex_rgba("#413729", 170))

    draw.text((sx0 + 338, dock_y + 14), "PULSE LOG", font=mono(11), fill=hex_rgba("#60533a", 150))
    for i, label in enumerate(("pulse 3 / R3", "pulse 2 / R2", "pulse 1 / R1")):
        y = dock_y + 40 + i * 22
        draw.text((sx0 + 338, y), label, font=mono(11), fill=hex_rgba("#413729", 165))

    draw.text((right_col[0] + 16, right_col[1] + 16), "LIVE TASKS", font=mono(12), fill=hex_rgba("#60533a", 170))
    tasks = [
        ("Rebalance top lane", "Lift one cool or amber slip higher.", "open"),
        ("Wake route knots", "Click the board to plant a moving pulse.", "live"),
        ("Feed lower garden", "Drop the green slip deeper for density.", "lush"),
    ]
    for i, (head, line, badge) in enumerate(tasks):
        y = right_col[1] + 44 + i * 92
        rounded(draw, (right_col[0] + 14, y, right_col[2] - 14, y + 76), 18, hex_rgba("#ffffff", 94), hex_rgba("#60533a", 24), 1)
        draw.text((right_col[0] + 26, y + 12), head, font=serif(19), fill=hex_rgba("#413729", 220))
        draw.text((right_col[0] + 26, y + 38), line, font=serif(16), fill=hex_rgba("#413729", 170))
        draw.text((right_col[2] - 70, y + 12), badge, font=mono(11), fill=hex_rgba("#413729", 160))

    note_y = right_col[1] + 334
    rounded(draw, (right_col[0] + 14, note_y, right_col[2] - 14, note_y + 144), 18, hex_rgba("#ffffff", 94), hex_rgba("#60533a", 24), 1)
    draw.text((right_col[0] + 26, note_y + 12), "BOARD NOTES", font=mono(11), fill=hex_rgba("#60533a", 150))
    notes = [
        "One embodied field drives every readout.",
        "No detached HUD chrome.",
        "No centered mascot object.",
        "The lower band keeps the denser garden law."
    ]
    for i, line in enumerate(notes):
        draw.text((right_col[0] + 26, note_y + 34 + i * 22), line, font=serif(16), fill=hex_rgba("#413729", 168))

    for i, title in enumerate(("IDEA", "INTERACTION", "NEXT")):
        fx0 = footer[0] + 14 + i * ((footer[2] - footer[0] - 42) / 3)
        fx1 = fx0 + ((footer[2] - footer[0] - 42) / 3) - 14
        rounded(draw, (fx0, footer[1] + 14, fx1, footer[3] - 14), 22, hex_rgba("#ffffff", 92), hex_rgba("#60533a", 24), 1)
        draw.text((fx0 + 14, footer[1] + 28), title, font=mono(11), fill=hex_rgba("#60533a", 150))
    draw.text((footer[0] + 28, footer[1] + 56), "A tactile pale workbench of slips, currents,", font=serif(16), fill=hex_rgba("#413729", 168))
    draw.text((footer[0] + 28, footer[1] + 78), "and lower garden density in one board.", font=serif(16), fill=hex_rgba("#413729", 168))
    draw.text((footer[0] + 373, footer[1] + 56), "Drag slips to retune routes. Click to plant", font=serif(16), fill=hex_rgba("#413729", 168))
    draw.text((footer[0] + 373, footer[1] + 78), "pulses that wake side loops and spores.", font=serif(16), fill=hex_rgba("#413729", 168))
    draw.text((footer[0] + 718, footer[1] + 56), "Future versions could ingest live text or", font=serif(16), fill=hex_rgba("#413729", 168))
    draw.text((footer[0] + 718, footer[1] + 78), "Telegram tasks as new sample slips.", font=serif(16), fill=hex_rgba("#413729", 168))

    dust = Image.new("RGBA", size, (0, 0, 0, 0))
    ddraw = ImageDraw.Draw(dust)
    for _ in range(240):
        x = rng.uniform(0, width)
        y = rng.uniform(0, height)
        r = rng.uniform(0.8, 2.0)
        ddraw.ellipse((x - r, y - r, x + r, y + r), fill=(96, 83, 58, rng.randint(10, 30)))
    dust = dust.filter(ImageFilter.GaussianBlur(0.5))

    image = Image.alpha_composite(image, ui)
    image = Image.alpha_composite(image, dust)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()
    render(args.output, args.width, args.height)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
