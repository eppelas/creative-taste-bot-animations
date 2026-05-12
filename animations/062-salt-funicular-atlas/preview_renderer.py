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
    for step in range(14, 0, -1):
        t = step / 14
        r = radius * t
        draw.ellipse(
            (center[0] - r, center[1] - r, center[0] + r, center[1] + r),
            fill=hex_rgba(color, int(alpha * (t**2) * 0.42)),
        )
    return layer.filter(ImageFilter.GaussianBlur(radius * 0.08))


def add_text(draw: ImageDraw.ImageDraw, pos: tuple[float, float], text: str, size: int, fill: tuple[int, int, int, int]) -> None:
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Times New Roman.ttf", size)
    except OSError:
        font = ImageFont.load_default()
    draw.text(pos, text, font=font, fill=fill)


def panel(draw: ImageDraw.ImageDraw, rect: tuple[float, float, float, float], radius: int = 24) -> None:
    draw.rounded_rectangle(rect, radius=radius, fill=hex_rgba("#fff9f1", 120), outline=hex_rgba("#645545", 44), width=1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    size = (args.width, args.height)
    rng = random.Random(62)

    image = vertical_gradient(size, "#faf4ea", "#d6c0a5")
    for center, radius, color, alpha in [
        ((size[0] * 0.14, size[1] * 0.12), size[0] * 0.18, "#ffffff", 116),
        ((size[0] * 0.82, size[1] * 0.18), size[0] * 0.16, "#83bdc9", 54),
        ((size[0] * 0.2, size[1] * 0.78), size[0] * 0.18, "#d99b87", 44),
    ]:
        image = Image.alpha_composite(image, radial_glow(size, center, radius, color, alpha))

    grid = Image.new("RGBA", size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grid)
    for x in range(0, size[0], 90):
        gdraw.line((x, 0, x, size[1]), fill=(80, 70, 56, 14), width=1)
    for y in range(0, size[1], 90):
        gdraw.line((0, y, size[0], y), fill=(80, 70, 56, 14), width=1)
    image = Image.alpha_composite(image, grid)

    ui = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(ui)

    margin = 18
    shell = (margin, margin, size[0] - margin, size[1] - margin)
    draw.rounded_rectangle(shell, radius=30, fill=hex_rgba("#fff8ef", 138), outline=hex_rgba("#645545", 52), width=2)

    left = (32, 32, 286, 1010)
    stage = (300, 32, 800, 1010)
    right = (814, 32, 1048, 1010)
    notes = (32, 1024, 1048, 1318)

    for rect in (left, stage, right, notes):
        panel(draw, rect, radius=28 if rect == notes else 30)

    add_text(draw, (left[0] + 18, left[1] + 18), "Animation #062", 16, hex_rgba("#645545", 160))
    add_text(draw, (left[0] + 18, left[1] + 44), "Salt Funicular", 38, hex_rgba("#31404b", 236))
    add_text(draw, (left[0] + 18, left[1] + 82), "Atlas", 38, hex_rgba("#31404b", 236))
    add_text(draw, (left[0] + 18, left[1] + 132), "Daylight cliff cutaway with terraces, brine", 18, hex_rgba("#31404b", 176))
    add_text(draw, (left[0] + 18, left[1] + 156), "reservoirs, and a route car sharing one slope.", 18, hex_rgba("#31404b", 176))

    chips = [("Daylight world", "#83bdc9"), ("Cutaway systems", "#97baa8"), ("Pointer climate", "#d1a35f")]
    for i, (label, color) in enumerate(chips):
        y = left[1] + 210 + i * 40
        draw.rounded_rectangle((left[0] + 18, y, left[0] + 182, y + 28), radius=999, fill=hex_rgba("#ffffff", 90), outline=hex_rgba(color, 90), width=1)
        add_text(draw, (left[0] + 30, y + 6), label, 14, hex_rgba("#31404b", 188))

    meter_specs = [("Salt lift", 0.64), ("Greenhouse hush", 0.56), ("Wind shear", 0.38)]
    for i, (label, value) in enumerate(meter_specs):
        y = left[1] + 360 + i * 78
        panel(draw, (left[0] + 18, y, left[2] - 18, y + 58), radius=18)
        add_text(draw, (left[0] + 30, y + 12), label, 16, hex_rgba("#645545", 164))
        add_text(draw, (left[2] - 74, y + 12), f"{int(value * 100)}%", 16, hex_rgba("#31404b", 210))
        draw.rounded_rectangle((left[0] + 30, y + 34, left[2] - 30, y + 44), radius=999, fill=hex_rgba("#645545", 26))
        draw.rounded_rectangle((left[0] + 30, y + 34, left[0] + 30 + (left[2] - left[0] - 60) * value, y + 44), radius=999, fill=hex_rgba("#83bdc9" if i != 1 else "#97baa8", 190))

    add_text(draw, (left[0] + 18, left[1] + 642), "Move the pointer across the cliff to warm a local", 17, hex_rgba("#31404b", 172))
    add_text(draw, (left[0] + 18, left[1] + 664), "terrace. Click cycles calm, descent, and bloom.", 17, hex_rgba("#31404b", 172))

    panel(draw, (stage[0] + 14, stage[1] + 14, stage[2] - 14, stage[1] + 110), radius=24)
    add_text(draw, (stage[0] + 30, stage[1] + 32), "Coastal section", 16, hex_rgba("#645545", 160))
    add_text(draw, (stage[0] + 30, stage[1] + 58), "Descending route through salt terraces", 22, hex_rgba("#31404b", 220))
    for i, label in enumerate(("Calm spill", "Cabin north", "Terrace 03")):
        x0 = stage[2] - 318 + i * 98
        draw.rounded_rectangle((x0, stage[1] + 28, x0 + 86, stage[1] + 56), radius=999, fill=hex_rgba("#ffffff", 86), outline=hex_rgba("#645545", 44), width=1)
        add_text(draw, (x0 + 10, stage[1] + 35), label, 12, hex_rgba("#31404b", 188))

    cutaway = (stage[0] + 14, stage[1] + 124, stage[2] - 14, stage[2] - 14)
    panel(draw, (stage[0] + 14, stage[1] + 124, stage[2] - 14, stage[2] - 154), radius=24)
    add_text(draw, (stage[0] + 30, stage[1] + 142), "Station register", 16, hex_rgba("#645545", 160))

    cliff = Image.new("RGBA", size, (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(cliff)
    cliff_poly = [
        (stage[0] + 66, stage[1] + 206),
        (stage[0] + 286, stage[1] + 206),
        (stage[0] + 420, stage[1] + 690),
        (stage[0] + 22, stage[1] + 690),
    ]
    cdraw.polygon(cliff_poly, fill=hex_rgba("#7c6550", 210), outline=hex_rgba("#645545", 90))
    for i in range(20):
        y = stage[1] + 226 + i * 24
        cdraw.line((stage[0] + 44, y, stage[0] + 322, y + 24), fill=hex_rgba("#f9f3eb", 20 + i), width=1)

    terrace_data = []
    for i in range(6):
        t = i / 5
        x = stage[0] + 136 + t * 180
        y = stage[1] + 248 + t * 74
        w = 168 - i * 12
        h = 56 + i * 4
        terrace_data.append((x, y, w, h))
        cdraw.polygon(
            [
                (x - w * 0.5, y),
                (x + w * 0.38, y - h * 0.14),
                (x + w * 0.48, y + h * 0.18),
                (x - w * 0.42, y + h * 0.28),
            ],
            fill=hex_rgba("#fff8ef", 98),
            outline=hex_rgba("#31404b", 78),
        )
        for j in range(4):
            yy = y + h * (0.02 + j * 0.05)
            cdraw.line((x - w * 0.32, yy, x + w * 0.08, yy), fill=hex_rgba("#83bdc9", 64), width=1)

    route_start = (terrace_data[0][0] + 106, terrace_data[0][1] - 80)
    route_end = (terrace_data[-1][0] + 44, terrace_data[-1][1] - 28)
    cdraw.line((*route_start, *route_end), fill=hex_rgba("#31404b", 120), width=2)
    cdraw.line((route_start[0] + 10, route_start[1] + 6, route_end[0] + 10, route_end[1] + 6), fill=hex_rgba("#ffffff", 80), width=1)
    cabin_x = lerp(route_start[0], route_end[0], 0.42)
    cabin_y = lerp(route_start[1], route_end[1], 0.42)
    cdraw.rounded_rectangle((cabin_x - 18, cabin_y - 12, cabin_x + 18, cabin_y + 12), radius=10, fill=hex_rgba("#fff8ef", 230), outline=hex_rgba("#31404b", 82), width=1)
    cdraw.rectangle((cabin_x - 8, cabin_y - 4, cabin_x + 8, cabin_y + 4), fill=hex_rgba("#d99b87", 170))

    for i in range(3):
        x = stage[0] + 310 + i * 52
        y = stage[1] + 520 + i * 54
        cdraw.rectangle((x, y, x + 72, y + 44), outline=hex_rgba("#31404b", 62), width=1)
        cdraw.rectangle((x + 4, y + 18, x + 68, y + 34), fill=hex_rgba("#83bdc9", 110))

    for i in range(30):
        x = stage[0] + 84 + rng.random() * 320
        y = stage[1] + 160 + rng.random() * 320
        r = 4 + rng.random() * 8
        cdraw.ellipse((x - r, y - r, x + r, y + r), fill=hex_rgba("#ffffff", rng.randint(34, 76)))

    image = Image.alpha_composite(image, cliff.filter(ImageFilter.GaussianBlur(0.3)))

    station_boxes = [
        (stage[0] + 26, stage[1] + 720, stage[0] + 160, stage[1] + 856, "T1", "Upper mist intake"),
        (stage[0] + 174, stage[1] + 720, stage[0] + 308, stage[1] + 856, "T2", "Funicular seed dock"),
        (stage[0] + 322, stage[1] + 720, stage[0] + 456, stage[1] + 856, "T3", "Brine commons"),
    ]
    for i, (x0, y0, x1, y1, sid, title) in enumerate(station_boxes):
        panel(draw, (x0, y0, x1, y1), radius=22)
        add_text(draw, (x0 + 12, y0 + 12), sid, 16, hex_rgba("#645545", 160))
        add_text(draw, (x1 - 52, y0 + 12), f"{61 - i * 8}%", 16, hex_rgba("#31404b", 205))
        add_text(draw, (x0 + 12, y0 + 42), title, 18, hex_rgba("#31404b", 220))
        draw.rounded_rectangle((x0 + 12, y1 - 20, x1 - 12, y1 - 12), radius=999, fill=hex_rgba("#645545", 24))
        draw.rounded_rectangle((x0 + 12, y1 - 20, x0 + 12 + (x1 - x0 - 24) * (0.61 - i * 0.08), y1 - 12), radius=999, fill=hex_rgba("#83bdc9" if i != 2 else "#d99b87", 180))

    add_text(draw, (right[0] + 18, right[1] + 18), "Atlas notes", 16, hex_rgba("#645545", 160))
    add_text(draw, (right[0] + 18, right[1] + 48), "Architectural and inhabited,", 18, hex_rgba("#31404b", 180))
    add_text(draw, (right[0] + 18, right[1] + 72), "not another idol or mascot.", 18, hex_rgba("#31404b", 180))
    card_a = (right[0] + 18, right[1] + 120, right[2] - 18, right[1] + 232)
    card_b = (right[0] + 18, right[1] + 246, right[2] - 18, right[1] + 358)
    for rect, label, title in [
        (card_a, "Humidity jars", "Condensation stores"),
        (card_b, "Terrace law", "Shared descent"),
    ]:
        panel(draw, rect, radius=20)
        add_text(draw, (rect[0] + 12, rect[1] + 12), label, 15, hex_rgba("#645545", 160))
        add_text(draw, (rect[0] + 12, rect[1] + 40), title, 18, hex_rgba("#31404b", 220))

    for i, (label, value) in enumerate((("Route drift", 0.41), ("Reservoir glow", 0.58))):
        y = right[1] + 394 + i * 72
        panel(draw, (right[0] + 18, y, right[2] - 18, y + 56), radius=18)
        add_text(draw, (right[0] + 30, y + 12), label, 16, hex_rgba("#645545", 160))
        add_text(draw, (right[2] - 72, y + 12), f"{int(value * 100)}%", 16, hex_rgba("#31404b", 205))
        draw.rounded_rectangle((right[0] + 30, y + 34, right[2] - 30, y + 44), radius=999, fill=hex_rgba("#645545", 24))
        draw.rounded_rectangle((right[0] + 30, y + 34, right[0] + 30 + (right[2] - right[0] - 60) * value, y + 44), radius=999, fill=hex_rgba("#97baa8" if i == 0 else "#d1a35f", 180))

    footer_cards = [
        ("Idea", "Inhabited daylight infrastructure"),
        ("Interaction", "Pointer as local weather"),
        ("Next", "Extend into more rooms"),
    ]
    for i, (label, title) in enumerate(footer_cards):
        x0 = notes[0] + 18 + i * 330
        rect = (x0, notes[1] + 16, x0 + 304, notes[3] - 16)
        panel(draw, rect, radius=22)
        add_text(draw, (rect[0] + 14, rect[1] + 14), label, 16, hex_rgba("#645545", 160))
        add_text(draw, (rect[0] + 14, rect[1] + 42), title, 20, hex_rgba("#31404b", 220))

    dust = Image.new("RGBA", size, (0, 0, 0, 0))
    ddraw = ImageDraw.Draw(dust)
    for _ in range(260):
        x = rng.uniform(0, size[0])
        y = rng.uniform(0, size[1])
        r = rng.uniform(0.7, 2.0)
        ddraw.ellipse((x - r, y - r, x + r, y + r), fill=(100, 84, 66, rng.randint(10, 26)))
    dust = dust.filter(ImageFilter.GaussianBlur(0.4))

    image = Image.alpha_composite(image, ui)
    image = Image.alpha_composite(image, dust)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(args.output, quality=95)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
