#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def hex_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), alpha)


def draw_gradient(image: Image.Image, top: str, bottom: str) -> None:
    draw = ImageDraw.Draw(image)
    top_rgba = hex_rgba(top)
    bottom_rgba = hex_rgba(bottom)
    width, height = image.size
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(int(top_rgba[i] * (1 - t) + bottom_rgba[i] * t) for i in range(4))
        draw.line((0, y, width, y), fill=color)


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill, outline, radius: int) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)
    inset = 12
    draw.rounded_rectangle(
        (box[0] + inset, box[1] + inset, box[2] - inset, box[3] - inset),
        radius=max(8, radius - 10),
        outline=(255, 255, 255, 20),
        width=1,
    )


def draw_figure(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], accent: tuple[int, int, int, int], flip: bool = False) -> None:
    x0, y0, x1, y1 = box
    w = x1 - x0
    h = y1 - y0
    cx = (x0 + x1) / 2
    body = [(cx - w * 0.13, y0 + h * 0.15), (cx + w * 0.14, y0 + h * 0.15), (cx + w * 0.1, y0 + h * 0.8), (cx - w * 0.16, y0 + h * 0.8)]
    draw.ellipse((cx - w * 0.16, y0 + h * 0.05, cx + w * 0.1, y0 + h * 0.22), fill=(236, 231, 221, 235))
    draw.polygon(body, fill=(236, 231, 221, 228))
    draw.line((cx - w * 0.22, y0 + h * 0.42, cx + w * 0.18, y0 + h * 0.38), fill=accent, width=4)
    draw.line((cx - w * 0.08, y0 + h * 0.18, cx + w * 0.12, y0 + h * 0.68), fill=accent, width=3)
    offset = -1 if flip else 1
    draw.arc((x0 + w * 0.08, y0 + h * 0.55, x1 - w * 0.08, y1 + h * 0.05), start=205, end=335, fill=accent, width=4)
    draw.arc((x0 + w * 0.02, y0 + h * 0.12, x1 - w * 0.18 * offset, y1 - h * 0.32), start=220, end=305, fill=(255, 255, 255, 26), width=10)


def render(output: Path, width: int, height: int) -> None:
    image = Image.new("RGBA", (width, height), hex_rgba("#05070a"))
    draw_gradient(image, "#0e1218", "#030406")

    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((int(width * 0.02), int(height * 0.04), int(width * 0.36), int(height * 0.42)), fill=hex_rgba("#84c5dc", 38))
    glow_draw.ellipse((int(width * 0.58), int(height * 0.06), int(width * 0.88), int(height * 0.32)), fill=hex_rgba("#ef9a92", 24))
    glow_draw.ellipse((int(width * 0.32), int(height * 0.48), int(width * 0.84), int(height * 0.94)), fill=hex_rgba("#b94759", 34))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    image.alpha_composite(glow)

    draw = ImageDraw.Draw(image)
    for step in range(8):
        y = int(height * (0.16 + step * 0.1))
        color = (132, 197, 220, 24) if step % 2 == 0 else (239, 154, 146, 20)
        draw.arc((40, y - 40, width - 40, y + 90), start=180, end=360, fill=color, width=2)

    main_box = (38, 46, width - 274, height - 190)
    side_box = (width - 220, 46, width - 38, height - 190)
    footer_y = height - 160
    rounded_panel(draw, main_box, (10, 13, 18, 220), (140, 177, 194, 44), 34)
    rounded_panel(draw, side_box, (10, 13, 18, 214), (140, 177, 194, 40), 34)
    rounded_panel(draw, (38, footer_y, width // 3 - 4, height - 34), (10, 13, 18, 214), (140, 177, 194, 34), 28)
    rounded_panel(draw, (width // 3 + 6, footer_y, 2 * width // 3 - 6, height - 34), (10, 13, 18, 214), (140, 177, 194, 34), 28)
    rounded_panel(draw, (2 * width // 3 + 4, footer_y, width - 38, height - 34), (10, 13, 18, 214), (140, 177, 194, 34), 28)

    windows = [
        (98, 214, 382, 764, hex_rgba("#84c5dc", 220), False),
        (512, 168, 764, 628, hex_rgba("#ef9a92", 220), True),
        (390, 520, 710, 866, hex_rgba("#d3b06c", 220), False),
    ]
    for x0, y0, x1, y1, accent, flip in windows:
        rounded_panel(draw, (x0, y0, x1, y1), (9, 13, 18, 194), (236, 231, 221, 42), 28)
        draw_figure(draw, (x0 + 28, y0 + 22, x1 - 28, y1 - 48), accent, flip=flip)
        draw.text((x0 + 18, y1 - 30), "figure", fill=(220, 227, 234, 140))

    draw.text((70, 86), "SLOW SHUTTER", fill=(220, 227, 234, 255))
    draw.text((70, 116), "EDITORIAL", fill=(220, 227, 234, 255))
    draw.text((70, 152), "Nocturnal human relay page with split focus, wet-glass drift, and long-exposure figure traces.", fill=(220, 227, 234, 176))
    draw.text((width - 194, 82), "Direction", fill=(220, 227, 234, 152))
    draw.text((width - 194, 128), "Humans without plain portraits", fill=(220, 227, 234, 188))
    draw.text((width - 194, 222), "Interaction", fill=(220, 227, 234, 152))
    draw.text((width - 194, 268), "Pointer rack focus + click flare", fill=(220, 227, 234, 188))

    for px, py, color in [(140, 982, (132, 197, 220, 255)), (472, 982, (239, 154, 146, 255)), (818, 982, (211, 176, 108, 255))]:
        draw.rounded_rectangle((px, py, px + 74, py + 12), radius=999, fill=color)

    image.convert("RGB").save(output)


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
