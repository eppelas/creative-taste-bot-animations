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
    return a + (b - a) * t


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
    for step in range(16, 0, -1):
        t = step / 16
        current_radius = radius * t
        draw.ellipse(
            (
                center[0] - current_radius,
                center[1] - current_radius,
                center[0] + current_radius,
                center[1] + current_radius,
            ),
            fill=hex_rgba(color, int(alpha * (t**2) * 0.42)),
        )
    return layer.filter(ImageFilter.GaussianBlur(radius * 0.08))


def add_text(draw: ImageDraw.ImageDraw, pos: tuple[float, float], text: str, size: int, fill: tuple[int, int, int, int]) -> None:
    try:
      font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Times New Roman.ttf", size)
    except OSError:
      font = ImageFont.load_default()
    draw.text(pos, text, font=font, fill=fill)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    rng = random.Random(48)
    size = (args.width, args.height)
    image = vertical_gradient(size, "#f3ede4", "#e8decd")

    for center, radius, color, alpha in [
        ((size[0] * 0.15, size[1] * 0.1), size[0] * 0.18, "#ffffff", 120),
        ((size[0] * 0.82, size[1] * 0.16), size[0] * 0.16, "#7ca7bc", 50),
        ((size[0] * 0.24, size[1] * 0.82), size[0] * 0.2, "#8baa87", 46),
        ((size[0] * 0.72, size[1] * 0.82), size[0] * 0.18, "#c98d89", 44),
    ]:
        image = Image.alpha_composite(image, radial_glow(size, center, radius, color, alpha))

    grain = Image.new("RGBA", size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grain)
    for x in range(0, size[0], 76):
        gdraw.line((x, 0, x, size[1]), fill=(122, 112, 88, 18), width=1)
    for y in range(0, size[1], 76):
        gdraw.line((0, y, size[0], y), fill=(122, 112, 88, 18), width=1)
    image = Image.alpha_composite(image, grain)

    ui = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(ui)

    margin = 18
    inner = (margin, margin, size[0] - margin, size[1] - margin)
    draw.rounded_rectangle(inner, radius=30, fill=hex_rgba("#fffaf2", 150), outline=hex_rgba("#6b624a", 70), width=2)

    header_h = 170
    left_w = 234
    right_w = 244
    footer_h = 162
    stage_top = margin + header_h + 14
    stage_bottom = size[1] - footer_h - 30

    header_left = (margin + 14, margin + 14, margin + left_w + 274, margin + header_h)
    header_right = (header_left[2] + 14, margin + 14, size[0] - margin - 14, margin + header_h)
    left_col = (margin + 14, stage_top, margin + left_w, stage_bottom)
    stage = (left_col[2] + 14, stage_top, size[0] - margin - right_w - 28, stage_bottom)
    right_col = (stage[2] + 14, stage_top, size[0] - margin - 14, stage_bottom)
    footer = (margin + 14, stage_bottom + 14, size[0] - margin - 14, size[1] - margin - 14)

    panels = [header_left, header_right, left_col, stage, right_col, footer]
    for rect in panels:
        draw.rounded_rectangle(rect, radius=24, fill=hex_rgba("#fffaf2", 110), outline=hex_rgba("#6b624a", 46), width=1)

    add_text(draw, (header_left[0] + 16, header_left[1] + 16), "Code Animation Study #048", 16, hex_rgba("#6b624a", 160))
    add_text(draw, (header_left[0] + 16, header_left[1] + 44), "Greenhouse Route Atlas", 52, hex_rgba("#3b362a", 240))
    add_text(draw, (header_left[0] + 16, header_left[1] + 108), "A pale browser-native service page of membranes, routes, and creeper field.", 20, hex_rgba("#3b362a", 180))

    add_text(draw, (header_right[0] + 16, header_right[1] + 16), "Route legend", 18, hex_rgba("#6b624a", 170))
    legend = [("H1 humid spine", "#7ca7bc"), ("M2 mosswalk", "#8baa87"), ("C3 canopy edge", "#d7a76d"), ("R4 root loop", "#c98d89"), ("S5 sporeway", "#94877a")]
    for i, (label, color) in enumerate(legend):
        y = header_right[1] + 48 + i * 22
        draw.ellipse((header_right[0] + 18, y + 3, header_right[0] + 28, y + 13), fill=hex_rgba(color, 220))
        add_text(draw, (header_right[0] + 36, y), label, 16, hex_rgba("#3b362a", 190))

    stage_fill = Image.new("RGBA", size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(stage_fill)
    sdraw.rounded_rectangle(stage, radius=24, fill=hex_rgba("#fffaf2", 84), outline=hex_rgba("#6b624a", 34), width=1)

    sx0, sy0, sx1, sy1 = stage
    map_h = int((sy1 - sy0) * 0.72)
    lattice_top = sy0 + map_h
    sdraw.line((sx0, lattice_top, sx1, lattice_top), fill=hex_rgba("#6b624a", 40), width=1)

    center_x = (sx0 + sx1) * 0.5
    center_y = sy0 + map_h * 0.48
    radius = min(sx1 - sx0, map_h) * 0.28
    for ring in range(6):
        points = []
        depth = ring / 5
        for step in range(160):
            angle = (step / 160) * math.pi * 2
            wobble = math.sin(angle * 2.4 + ring * 0.5) * 0.09 + math.cos(angle * 3.1 - ring) * 0.05
            r = radius * (0.78 + depth * 0.1 + wobble)
            points.append((center_x + math.cos(angle) * r * (1.08 + depth * 0.05), center_y + math.sin(angle) * r * (0.82 + depth * 0.06)))
        sdraw.polygon(points, outline=hex_rgba("#7d715c" if ring % 2 else "#7ca7bc", 54 - ring * 4), fill=hex_rgba("#ffffff", 10))

    route_points = [
        ("H1", "humid spine", "#7ca7bc", center_x - radius * 1.1, center_y - radius * 0.76),
        ("M2", "mosswalk", "#8baa87", center_x + radius * 0.98, center_y - radius * 0.4),
        ("C3", "canopy edge", "#d7a76d", center_x + radius * 0.64, center_y + radius * 0.38),
        ("R4", "root loop", "#c98d89", center_x - radius * 1.02, center_y + radius * 0.74),
        ("S5", "sporeway", "#94877a", center_x - radius * 0.08, center_y + radius * 1.1),
    ]
    links = [(0, 1), (1, 2), (0, 3), (3, 4), (2, 4), (1, 4)]
    for a_index, b_index in links:
        _, _, color, ax, ay = route_points[a_index]
        _, _, _, bx, by = route_points[b_index]
        mid_x = (ax + bx) / 2 + (by - ay) * 0.12
        mid_y = (ay + by) / 2 - (bx - ax) * 0.12
        sdraw.line((ax, ay, mid_x, mid_y, bx, by), fill=hex_rgba(color, 110), width=4)
        sdraw.line((ax, ay, mid_x, mid_y, bx, by), fill=hex_rgba("#ffffff", 40), width=1)

    for rid, label, color, x, y in route_points:
        image = Image.alpha_composite(image, radial_glow(size, (x, y), 32, color, 90))
        sdraw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=hex_rgba(color, 230))
        sdraw.ellipse((x - 16, y - 16, x + 16, y + 16), outline=hex_rgba("#6b624a", 60), width=1)
        add_text(sdraw, (x - 10, y - 34), rid, 16, hex_rgba("#3b362a", 220))
        add_text(sdraw, (x - 24, y + 18), label, 16, hex_rgba("#3b362a", 170))

    for i in range(8):
        x = sx0 + 42 + i * ((sx1 - sx0 - 84) / 7)
        sway = math.sin(i * 0.7) * 10
        top = lattice_top + 16 + (i % 3) * 12
        sdraw.line((x, sy1 - 22, x + sway * 0.3, sy1 - 120, x + sway, top), fill=hex_rgba("#7d715c", 120), width=3)
        for bead in range(6):
            t = bead / 5
            bx = x + sway * 0.2 + math.sin(bead + i) * 3
            by = sy1 - 22 - t * ((sy1 - 22) - top)
            bead_color = "#d7a76d" if bead % 3 == 0 else "#8baa87" if bead % 2 == 0 else "#94877a"
            sdraw.ellipse((bx - 3, by - 3, bx + 3, by + 3), fill=hex_rgba(bead_color, 180))
    for i in range(7):
        ax = sx0 + 44 + i * ((sx1 - sx0 - 88) / 7)
        bx = sx0 + 44 + (i + 1) * ((sx1 - sx0 - 88) / 7)
        my = sy1 - 86 - math.sin(i * 0.8) * 12
        sdraw.line((ax, sy1 - 52, (ax + bx) / 2, my, bx, sy1 - 48), fill=hex_rgba("#8baa87" if i % 2 else "#7ca7bc", 110), width=3)

    image = Image.alpha_composite(image, stage_fill.filter(ImageFilter.GaussianBlur(0.3)))

    add_text(draw, (left_col[0] + 14, left_col[1] + 16), "Route overview", 18, hex_rgba("#6b624a", 170))
    for i, (label, color) in enumerate([(item[0] + "  " + item[1], item[2]) for item in route_points]):
        y = left_col[1] + 50 + i * 30
        draw.ellipse((left_col[0] + 14, y + 3, left_col[0] + 24, y + 13), fill=hex_rgba(color, 220))
        add_text(draw, (left_col[0] + 32, y), label, 16, hex_rgba("#3b362a", 185))

    chart_y = left_col[1] + 220
    draw.rounded_rectangle((left_col[0] + 14, chart_y, left_col[2] - 14, chart_y + 128), radius=16, fill=hex_rgba("#ffffff", 54), outline=hex_rgba("#6b624a", 34), width=1)
    for offset, color in [(0, "#7ca7bc"), (12, "#8baa87"), (-10, "#d7a76d"), (18, "#c98d89"), (24, "#94877a")]:
        points = []
        for step in range(16):
            t = step / 15
            x = left_col[0] + 22 + t * (left_col[2] - left_col[0] - 44)
            y = chart_y + 72 + math.sin(t * math.pi * 3 + offset) * 22 + offset
            points.append((x, y))
        draw.line(points, fill=hex_rgba(color, 180), width=2)

    dial_y = chart_y + 144
    draw.rounded_rectangle((left_col[0] + 14, dial_y, left_col[2] - 14, dial_y + 152), radius=18, fill=hex_rgba("#ffffff", 52), outline=hex_rgba("#6b624a", 34), width=1)
    cx = (left_col[0] + left_col[2]) / 2
    cy = dial_y + 76
    draw.ellipse((cx - 48, cy - 48, cx + 48, cy + 48), outline=hex_rgba("#6b624a", 90), width=1)
    draw.ellipse((cx - 36, cy - 36, cx + 36, cy + 36), outline=hex_rgba("#6b624a", 34), width=1)
    add_text(draw, (cx - 18, cy - 18), "76", 36, hex_rgba("#3b362a", 240))
    add_text(draw, (cx - 26, cy + 20), "humidity", 14, hex_rgba("#6b624a", 150))

    add_text(draw, (right_col[0] + 14, right_col[1] + 16), "Specimen insets", 18, hex_rgba("#6b624a", 170))
    for i in range(2):
        box = (right_col[0] + 14, right_col[1] + 46 + i * 126, right_col[2] - 14, right_col[1] + 146 + i * 126)
        draw.rounded_rectangle(box, radius=16, fill=hex_rgba("#ffffff", 54), outline=hex_rgba("#6b624a", 34), width=1)
        for j in range(5):
            ax = box[0] + 22 + j * 28
            ay = box[1] + 56 + math.sin(j + i * 0.7) * 10
            bx = ax + 36
            by = ay - 28 + math.cos(j) * 12
            draw.line((ax, ay, bx, by), fill=hex_rgba("#c98d89" if i == 0 else "#8baa87", 120), width=2)
        draw.ellipse((box[0] + 70, box[1] + 26, box[0] + 78, box[1] + 34), fill=hex_rgba("#7ca7bc", 200))
        draw.ellipse((box[0] + 148, box[1] + 60, box[0] + 156, box[1] + 68), fill=hex_rgba("#d7a76d", 200))

    status_y = right_col[1] + 304
    add_text(draw, (right_col[0] + 14, status_y), "Microclimate", 18, hex_rgba("#6b624a", 170))
    bars = [("Humidity", 0.76, "#7ca7bc"), ("Canopy ease", 0.61, "#8baa87"), ("Signal clarity", 0.58, "#d7a76d")]
    for i, (label, value, color) in enumerate(bars):
        y = status_y + 34 + i * 42
        add_text(draw, (right_col[0] + 14, y), label, 16, hex_rgba("#3b362a", 170))
        add_text(draw, (right_col[2] - 66, y), f"{int(value * 100)}%", 16, hex_rgba("#3b362a", 200))
        draw.rounded_rectangle((right_col[0] + 14, y + 20, right_col[2] - 14, y + 28), radius=999, fill=hex_rgba("#6b624a", 32))
        draw.rounded_rectangle((right_col[0] + 14, y + 20, right_col[0] + 14 + (right_col[2] - right_col[0] - 28) * value, y + 28), radius=999, fill=hex_rgba(color, 180))

    signal_y = status_y + 176
    add_text(draw, (right_col[0] + 14, signal_y), "Signal feed", 18, hex_rgba("#6b624a", 170))
    for i, (rid, _, color, _, _) in enumerate(route_points):
        y = signal_y + 30 + i * 24
        add_text(draw, (right_col[0] + 14, y), rid, 16, hex_rgba(color, 220))
        feed = 0.2 + i * 0.11 + rng.random() * 0.09
        add_text(draw, (right_col[0] + 52, y), f"{feed:.2f} kPa", 16, hex_rgba("#3b362a", 170))

    add_text(draw, (footer[0] + 16, footer[1] + 18), "Idea", 18, hex_rgba("#6b624a", 170))
    add_text(draw, (footer[0] + 16, footer[1] + 48), "Interaction", 18, hex_rgba("#6b624a", 170))
    add_text(draw, (footer[0] + 16, footer[1] + 78), "Next", 18, hex_rgba("#6b624a", 170))
    draw.rounded_rectangle((footer[2] - 150, footer[3] - 52, footer[2] - 18, footer[3] - 18), radius=999, fill=hex_rgba("#ffffff", 110), outline=hex_rgba("#6b624a", 50), width=1)
    add_text(draw, (footer[2] - 130, footer[3] - 43), "Back to index", 16, hex_rgba("#3b362a", 220))

    dust = Image.new("RGBA", size, (0, 0, 0, 0))
    ddraw = ImageDraw.Draw(dust)
    for _ in range(260):
        x = rng.uniform(0, size[0])
        y = rng.uniform(0, size[1])
        r = rng.uniform(0.8, 2.2)
        ddraw.ellipse((x - r, y - r, x + r, y + r), fill=(122, 112, 88, rng.randint(16, 34)))
    dust = dust.filter(ImageFilter.GaussianBlur(0.4))
    image = Image.alpha_composite(image, ui)
    image = Image.alpha_composite(image, dust)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
