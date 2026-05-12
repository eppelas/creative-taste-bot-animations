#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


PALETTE = {
    "top": (11, 14, 22),
    "mid": (8, 10, 17),
    "bottom": (4, 5, 10),
    "panel": (18, 21, 30),
    "ink": (241, 243, 251),
    "muted": (170, 177, 201),
    "blue": (132, 182, 223),
    "amber": (241, 187, 131),
    "red": (221, 89, 86),
    "violet": (89, 104, 170),
    "white": (255, 255, 255),
}


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def blend(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(lerp(a[i], b[i], t)) for i in range(3))


def add_gradient(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    for y in range(height):
        t = y / max(1, height - 1)
        if t < 0.45:
            color = blend(PALETTE["top"], PALETTE["mid"], t / 0.45)
        else:
            color = blend(PALETTE["mid"], PALETTE["bottom"], (t - 0.45) / 0.55)
        draw.line((0, y, width, y), fill=color)


def glow(base: Image.Image, center: tuple[float, float], radius: float, color: tuple[int, int, int, int], blur: float) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=blur))
    base.alpha_composite(layer)


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], alpha: int = 190) -> None:
    draw.rounded_rectangle(
        box,
        radius=28,
        fill=PALETTE["panel"] + (alpha,),
        outline=(255, 255, 255, 42),
        width=2,
    )


def draw_city(base: Image.Image, width: int, height: int) -> None:
    draw = ImageDraw.Draw(base, "RGBA")
    horizon = int(height * 0.62)
    for idx in range(28):
        x = int(width * (idx / 27) - 24)
        tower_w = 34 + (idx % 5) * 12
        tower_h = int(height * (0.18 + (idx % 7) * 0.04))
        draw.rectangle((x, horizon - tower_h, x + tower_w, height), fill=(10, 12, 20, 220))

    for idx in range(180):
        x = (idx * 73) % width
        y = int(height * (0.24 + ((idx * 19) % 100) / 220))
        size = 2 + idx % 3
        if idx % 9 == 0:
            color = PALETTE["amber"] + (180,)
        elif idx % 7 == 0:
            color = PALETTE["red"] + (120,)
        else:
            color = PALETTE["blue"] + (150,)
        draw.rectangle((x, y, x + size * 2, y + size), fill=color)

    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(layer)
    for band in range(6):
        y = int(height * (0.48 + band * 0.065))
        ldraw.line((0, y, width, y + 18), fill=PALETTE["blue"] + (26,), width=4)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=4))
    base.alpha_composite(layer)


def draw_figure(base: Image.Image, width: int, height: int) -> None:
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    x = width * 0.68
    y = height * 0.9

    coat = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(coat, "RGBA")
    cdraw.polygon(
        [
            (x - 128, y + 10),
            (x - 138, y - 146),
            (x - 74, y - 318),
            (x + 12, y - 420),
            (x + 108, y - 366),
            (x + 124, y - 118),
            (x + 72, y + 40),
        ],
        fill=(18, 21, 31, 240),
        outline=PALETTE["blue"] + (44,),
    )
    cdraw.ellipse((x - 18, y - 414, x + 102, y - 248), fill=(17, 20, 28, 245))
    cdraw.ellipse((x - 2, y - 398, x + 84, y - 288), fill=PALETTE["amber"] + (28,))
    cdraw.rectangle((x + 32, y - 342, x + 50, y - 286), fill=PALETTE["red"] + (54,))
    coat = coat.filter(ImageFilter.GaussianBlur(radius=1.4))
    base.alpha_composite(coat)

    draw.line((x + 44, y - 288, x + 90, y - 172, x + 112, y - 78), fill=PALETTE["blue"] + (58,), width=3)


def draw_glass(base: Image.Image, width: int, height: int) -> None:
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")

    for idx in range(8):
        y = int(height * (0.12 + idx * 0.11))
        draw.line((width * 0.04, y, width * 0.95, y - 20), fill=(255, 255, 255, 26), width=2)

    for idx in range(110):
        x = (idx * 97) % width
        y = (idx * 61) % height
        length = 18 + (idx % 5) * 10
        color = PALETTE["amber"] + (26,) if idx % 10 == 0 else (255, 255, 255, 32)
        draw.line((x, y, x - length * 0.24, y + length), fill=color, width=1)

    for idx in range(9):
        x = int(width * (0.08 + (idx % 3) * 0.2))
        y = int(height * (0.12 + (idx // 3) * 0.16))
        w = int(width * (0.12 + (idx % 2) * 0.02))
        h = int(height * 0.026)
        draw.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=(255, 255, 255, 22))
        draw.rectangle((x + 8, y + h + 5, x + int(w * 0.7), y + h + 8), fill=PALETTE["blue"] + (38,))

    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.8))
    base.alpha_composite(layer)


def draw_shutter(base: Image.Image, width: int, height: int) -> None:
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    x = width * 0.48
    y = height * 0.62
    points = [
        (x - 240, y - 24),
        (x + 210, y - 108),
        (x + 246, y - 60),
        (x - 200, y + 24),
    ]
    draw.polygon(points, fill=PALETTE["blue"] + (66,))
    draw.line((x - 240, y, x + 238, y - 86), fill=PALETTE["white"] + (90,), width=4)
    draw.line((x - 238, y + 10, x + 240, y - 76), fill=PALETTE["red"] + (64,), width=3)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=6))
    base.alpha_composite(layer)


def add_ui(base: Image.Image, width: int, height: int) -> None:
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")

    rounded_panel(draw, (40, 42, 384, 430))
    rounded_panel(draw, (406, 42, width - 40, height - 286))
    rounded_panel(draw, (40, height - 242, width - 40, height - 40), 178)

    draw.text((70, 72), "#074 / dark human editorial night scene", fill=PALETTE["muted"])
    draw.text((70, 112), "OBSIDIAN", fill=PALETTE["ink"])
    draw.text((70, 146), "GLASS RELAY", fill=PALETTE["blue"])
    draw.multiline_text(
        (70, 198),
        "Hover shifts focus between\nwet glass, figure silhouette,\nand distant city bands.\nClick sends a shutter sweep.",
        fill=PALETTE["muted"],
        spacing=8,
    )

    chip_y = 310
    chips = [
        ("reflection hold", PALETTE["blue"]),
        ("figure focus", PALETTE["amber"]),
        ("shutter drag", PALETTE["red"]),
    ]
    for idx, (label, color) in enumerate(chips):
        x0 = 70 + idx * 92
        draw.rounded_rectangle((x0, chip_y, x0 + 84, chip_y + 28), radius=14, fill=(255, 255, 255, 16), outline=color + (96,), width=2)
        draw.text((x0 + 9, chip_y + 8), label, fill=PALETTE["ink"])

    notes = [
        ("Idea", "A cropped interior figure, wet glass, and reflected city light share one editorial night frame."),
        ("Interaction", "Focus bias changes by hover; one click leaves a short long-exposure shutter streak."),
        ("Next", "Could later add a second reflection inset or scooter-light pass without becoming a storyboard."),
    ]
    card_w = (width - 112) / 3
    for idx, (title, body) in enumerate(notes):
        x0 = 56 + idx * (card_w + 14)
        x1 = x0 + card_w
        draw.rounded_rectangle((x0, height - 222, x1, height - 58), radius=22, fill=(255, 255, 255, 14), outline=(255, 255, 255, 36), width=2)
        draw.text((x0 + 18, height - 198), title.upper(), fill=PALETTE["ink"])
        draw.multiline_text((x0 + 18, height - 164), body, fill=PALETTE["muted"], spacing=7)

    base.alpha_composite(layer)


def render(output: Path, width: int, height: int) -> None:
    image = Image.new("RGBA", (width, height), PALETTE["top"] + (255,))
    draw = ImageDraw.Draw(image, "RGBA")
    add_gradient(draw, width, height)

    glow(image, (width * 0.18, height * 0.16), width * 0.16, PALETTE["violet"] + (44,), width * 0.06)
    glow(image, (width * 0.82, height * 0.18), width * 0.18, PALETTE["blue"] + (34,), width * 0.06)
    glow(image, (width * 0.26, height * 0.72), width * 0.18, PALETTE["amber"] + (28,), width * 0.05)

    draw_city(image, width, height)
    draw_figure(image, width, height)
    draw_glass(image, width, height)
    draw_shutter(image, width, height)
    add_ui(image, width, height)

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
