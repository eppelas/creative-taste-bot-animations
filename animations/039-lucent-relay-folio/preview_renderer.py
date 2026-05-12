#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def lerp_color(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(image)
    for y in range(height):
      t = y / max(1, height - 1)
      draw.line([(0, y), (width, y)], fill=lerp_color(top, bottom, t))
    return image


def soft_ellipse(layer: Image.Image, bbox: tuple[float, float, float, float], color: tuple[int, int, int, int], blur: int) -> None:
    temp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(temp)
    draw.ellipse(bbox, fill=color)
    layer.alpha_composite(temp.filter(ImageFilter.GaussianBlur(blur)))


def draw_valve(layer: Image.Image, center: tuple[float, float], scale: float, angle: float, open_amount: float) -> None:
    cx, cy = center
    temp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(temp)

    stem_top = (cx, cy - 180 * scale)
    stem_bottom = (cx, cy - 16 * scale)
    draw.line([stem_top, stem_bottom], fill=(58, 67, 77, 48), width=max(1, int(2 * scale)))

    left = [
        (cx, cy - 6 * scale),
        (cx - 46 * scale, cy - (20 + open_amount * 36) * scale),
        (cx - 78 * scale, cy + (18 + open_amount * 24) * scale),
        (cx - 20 * scale, cy + 92 * scale),
    ]
    right = [
        (cx, cy - 6 * scale),
        (cx + 46 * scale, cy - (20 + open_amount * 36) * scale),
        (cx + 78 * scale, cy + (18 + open_amount * 24) * scale),
        (cx + 20 * scale, cy + 92 * scale),
    ]

    membrane = left + right[::-1]
    draw.polygon(membrane, fill=(245, 251, 253, 118))
    draw.line(left, fill=(124, 197, 219, 92), width=max(1, int(2 * scale)))
    draw.line(right, fill=(216, 145, 116, 84), width=max(1, int(2 * scale)))
    draw.arc(
        [cx - 34 * scale, cy + 16 * scale, cx + 34 * scale, cy + 96 * scale],
        195,
        -15,
        fill=(168, 221, 194, 96),
        width=max(1, int(2 * scale)),
    )

    glow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse(
        [cx - 48 * scale, cy + 10 * scale, cx + 48 * scale, cy + 92 * scale],
        fill=(255, 255, 255, 55),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(int(10 * scale)))
    temp.alpha_composite(glow)

    temp = temp.rotate(angle, center=center, resample=Image.Resampling.BICUBIC)
    layer.alpha_composite(temp)


def draw_panel(draw: ImageDraw.ImageDraw, bbox: tuple[int, int, int, int]) -> None:
    draw.rounded_rectangle(bbox, radius=26, outline=(68, 77, 87, 42), fill=(255, 251, 245, 102), width=1)


def render(output: Path, width: int, height: int) -> None:
    image = vertical_gradient((width, height), (250, 246, 240), (221, 209, 195)).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))

    soft_ellipse(overlay, (70, 40, 340, 290), (123, 203, 223, 56), 26)
    soft_ellipse(overlay, (760, 80, 1030, 320), (214, 145, 116, 36), 26)
    soft_ellipse(overlay, (420, 930, 760, 1270), (171, 222, 195, 42), 34)

    grid = ImageDraw.Draw(overlay)
    for i in range(5):
        x = int(width * (0.18 + i * 0.16))
        grid.line([(x, int(height * 0.12)), (x, int(height * 0.92))], fill=(36, 44, 54, 22), width=1)
    for i in range(7):
        y = int(height * (0.14 + i * 0.11))
        grid.arc([90, y - 24, width - 90, y + 30], 180, 360, fill=(36, 44, 54, 18), width=1)

    for i in range(4):
        x = width * (0.22 + i * 0.17)
        temp = Image.new("RGBA", image.size, (0, 0, 0, 0))
        td = ImageDraw.Draw(temp)
        alpha = 28 + i * 12
        td.rectangle(
            [x - (65 + i * 12), height * 0.08, x + (65 + i * 12), height * 0.92],
            fill=(255, 255, 255, alpha if i % 2 else alpha - 6),
        )
        temp = temp.rotate(-7 + i * 2, center=(x, height / 2), resample=Image.Resampling.BICUBIC)
        overlay.alpha_composite(temp.filter(ImageFilter.GaussianBlur(2)))

    columns = [0.28, 0.42, 0.58, 0.72]
    for ci, column in enumerate(columns):
        for i in range(4):
            y = 0.2 + i * 0.16 + (ci % 2) * 0.03
            scale = 0.76 + ((ci + i) % 3) * 0.12
            angle = (-7 + ci * 4 + i) * math.pi / 180
            open_amount = 0.28 + 0.16 * math.sin(ci * 0.8 + i * 0.5)
            draw_valve(overlay, (width * column, height * y), scale, angle, open_amount)

    dots = ImageDraw.Draw(overlay)
    for i in range(150):
        px = (i * 73) % width
        py = (i * 131) % height
        radius = 1 + (i % 4)
        color = (
            (123, 203, 223, 96)
            if i % 3 == 0
            else (214, 145, 116, 72)
            if i % 3 == 1
            else (255, 255, 255, 88)
        )
        dots.ellipse([px, py, px + radius, py + radius], fill=color)

    image.alpha_composite(overlay)
    draw = ImageDraw.Draw(image, "RGBA")

    draw_panel(draw, (18, 18, 466, 282))
    draw_panel(draw, (884, 18, 1062, 286))
    draw_panel(draw, (18, 1128, 690, 1332))

    draw.text((38, 40), "ANIMATION 039 / OPTICAL TRANSLUCENT HABITAT", fill=(70, 79, 88, 200))
    draw.text((38, 78), "Lucent Relay Folio", fill=(22, 30, 38, 235))
    draw.text(
        (38, 124),
        "A vertical reflective valve conservatory where focus shifts between",
        fill=(42, 50, 58, 196),
    )
    draw.text(
        (38, 146),
        "near glass echoes and far membranes while current wakes open the",
        fill=(42, 50, 58, 196),
    )
    draw.text((38, 168), "nearest valves.", fill=(42, 50, 58, 196))

    draw.text((902, 40), "FOCUS PLANES", fill=(70, 79, 88, 200))
    draw.text((902, 74), "Reflective slices", fill=(22, 30, 38, 220))
    labels = [
        "Near plane: wet glass glare.",
        "Middle plane: hanging valves.",
        "Far plane: pale pollen weather.",
    ]
    for idx, label in enumerate(labels):
        top = 118 + idx * 52
        draw.rounded_rectangle((900, top, 1046, top + 42), radius=16, outline=(68, 77, 87, 34), fill=(255, 255, 255, 70))
        draw.text((912, top + 12), label, fill=(52, 60, 68, 180))

    draw.text((38, 1150), "FIELD NOTES", fill=(70, 79, 88, 200))
    footer_cards = [
        ("Focus Split", "63%"),
        ("Valve Lift", "46%"),
        ("Weather Calm", "78%"),
    ]
    for idx, (title, value) in enumerate(footer_cards):
        x0 = 38 + idx * 214
        draw.rounded_rectangle((x0, 1180, x0 + 194, 1300), radius=18, outline=(68, 77, 87, 34), fill=(255, 255, 255, 72))
        draw.text((x0 + 14, 1192), title.upper(), fill=(70, 79, 88, 180))
        draw.rounded_rectangle((x0 + 14, 1220, x0 + 180, 1232), radius=6, fill=(225, 232, 232, 220))
        draw.rounded_rectangle((x0 + 14, 1220, x0 + 14 + int((166 * (0.63, 0.46, 0.78)[idx])), 1232), radius=6, fill=(123, 203, 223, 210))
        draw.text((x0 + 14, 1248), value, fill=(22, 30, 38, 232))

    image = image.filter(ImageFilter.GaussianBlur(0.2))
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()
    render(args.output, args.width, args.height)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
