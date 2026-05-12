#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


BG = "#07121f"
CYAN = "#6dd7ff"
ACID = "#d9ff54"
PEACH = "#ffb59b"
RED = "#f5576d"
INK = "#d4f2ff"
MUTED = (212, 242, 255, 172)
PANEL = (6, 12, 22, 196)
LINE = (167, 224, 255, 46)


def hex_rgba(value: str, alpha: int) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4)) + (alpha,)


def diagonal_point(t: float, width: int, height: int, offset: float, travel: float, lane_width: float, phase: float) -> tuple[float, float]:
    x = t * (width + 240) - 120
    base_y = height * 0.12 + t * height * 0.76 + offset
    drift = math.sin(t * 8 + phase) * travel * 0.78
    wave = math.cos(t * 13 + phase) * lane_width * 0.18
    return x, base_y + drift + wave


def draw_lane(draw: ImageDraw.ImageDraw, width: int, height: int, index: int, color: str, offset: float) -> None:
    lane_width = 32 + (index % 5) * 11
    travel = 28 + (index % 6) * 9
    phase = index * 0.53
    points = [diagonal_point(step / 28, width, height, offset, travel, lane_width, phase) for step in range(29)]
    fill_color = hex_rgba(color, 44)
    stroke_color = hex_rgba(color, 214)
    draw.line(points, fill=fill_color, width=int(lane_width), joint="curve")
    draw.line(points, fill=stroke_color, width=2, joint="curve")

    for cut_index, cut in enumerate((0.18, 0.39, 0.58, 0.79)):
        x, y = diagonal_point(cut, width, height, offset, travel, lane_width, phase)
        rw = 16 + ((cut_index + index) % 3) * 10
        rh = 9 + ((cut_index + index) % 2) * 5
        draw.rectangle((x - rw / 2, y - rh / 2, x + rw / 2, y + rh / 2), fill=BG, outline=stroke_color, width=1)

    for step in range(2, 26, 3):
        x1, y1 = points[step]
        x2, y2 = points[step + 1]
        angle = math.atan2(y2 - y1, x2 - x1)
        spread = 8
        left = (x1 - math.cos(angle) * spread - math.sin(angle) * 5, y1 - math.sin(angle) * spread + math.cos(angle) * 5)
        right = (x1 + math.cos(angle) * spread - math.sin(angle) * 5, y1 + math.sin(angle) * spread + math.cos(angle) * 5)
        draw.line((left, (x1, y1), right), fill=stroke_color, width=1)


def draw_tags(base: Image.Image, width: int, height: int) -> None:
    tag_specs = [
        (0.21, 0.27, CYAN, "DRIFT", "long lanes"),
        (0.77, 0.48, PEACH, "KNOT", "tight braids"),
        (0.35, 0.77, ACID, "FLARE", "acid sparks"),
    ]
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x_ratio, y_ratio, accent, title, subtitle in tag_specs:
        x = int(width * x_ratio)
        y = int(height * y_ratio)
        box = (x - 92, y - 34, x + 92, y + 34)
        draw.rounded_rectangle(box, radius=18, fill=(5, 10, 18, 200), outline=hex_rgba(accent, 120), width=2)
        draw.text((x - 74, y - 18), title, fill=hex_rgba(accent, 255))
        draw.text((x - 74, y + 2), subtitle, fill=MUTED)
    base.alpha_composite(overlay)


def draw_panel(base: Image.Image, width: int, height: int) -> None:
    panel = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(panel)
    box = (40, 34, min(width - 40, 720), 292)
    draw.rounded_rectangle(box, radius=28, fill=PANEL, outline=LINE, width=2)
    draw.text((64, 58), "CODE ANIMATION STUDY #029", fill=MUTED)
    draw.text((64, 96), "DIAGONAL GLYPH WEATHER", fill=INK)
    hint = (
        "A print-system storm of diagonal contours, stencil blocks, and moving\n"
        "connector marks where the motion lives in the field itself."
    )
    draw.multiline_text((64, 144), hint, fill=INK, spacing=8)
    meta = (
        "Move through the weather to drag the nearest currents off-axis.\n"
        "Floating field tags switch the grammar: drift, knot, or flare."
    )
    draw.multiline_text((64, 204), meta, fill=MUTED, spacing=8)
    draw.text((64, 258), "FIELD MODE", fill=MUTED)
    draw.text((168, 258), "drift", fill=INK)
    draw.text((256, 258), "SHEAR", fill=MUTED)
    draw.text((324, 258), "0.34", fill=INK)
    draw.text((394, 258), "DENSITY", fill=MUTED)
    draw.text((484, 258), "52", fill=INK)
    base.alpha_composite(panel.filter(ImageFilter.GaussianBlur(0.2)))


def render(output: Path, width: int, height: int) -> None:
    image = Image.new("RGBA", (width, height), BG)
    draw = ImageDraw.Draw(image)

    for y in range(height):
      ratio = y / max(height - 1, 1)
      color = (
        int(8 - ratio * 5),
        int(17 + ratio * 7),
        int(28 + ratio * 6),
        255,
      )
      draw.line((0, y, width, y), fill=color)

    for x in range(-height, width + height, 52):
        draw.line((x, 0, x + height, height), fill=(182, 230, 255, 18), width=1)

    accent_cycle = [CYAN, ACID, PEACH, RED]
    offsets = [-220, -150, -70, -18, 46, 112, 188, 264, 332, 410, 488, 566]
    for index, offset in enumerate(offsets):
        draw_lane(draw, width, height, index, accent_cycle[index % len(accent_cycle)], offset)

    for index in range(80):
        x = (index * 137) % width
        y = (index * 211) % height
        size = 2 + (index % 3)
        tone = accent_cycle[index % len(accent_cycle)]
        draw.rectangle((x, y, x + size, y + size), fill=hex_rgba(tone, 200))

    for radius, alpha in ((120, 18), (220, 12), (320, 8)):
        glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.ellipse(
            (width * 0.5 - radius, height * 0.56 - radius, width * 0.5 + radius, height * 0.56 + radius),
            outline=(109, 215, 255, alpha),
            width=2,
        )
        image.alpha_composite(glow)

    draw_tags(image, width, height)
    draw_panel(image, width, height)

    image = image.convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


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
