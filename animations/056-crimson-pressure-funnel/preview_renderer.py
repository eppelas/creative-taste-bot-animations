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
        outline=(255, 255, 255, 18),
        width=1,
    )


def render(output: Path, width: int, height: int) -> None:
    image = Image.new("RGBA", (width, height), hex_rgba("#040507"))
    draw_gradient(image, "#11161b", "#020304")

    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((int(width * 0.04), int(height * 0.04), int(width * 0.34), int(height * 0.36)), fill=hex_rgba("#86c6dd", 34))
    glow_draw.ellipse((int(width * 0.6), int(height * 0.06), int(width * 0.9), int(height * 0.34)), fill=hex_rgba("#ff6f80", 28))
    glow_draw.ellipse((int(width * 0.34), int(height * 0.44), int(width * 0.86), int(height * 0.96)), fill=hex_rgba("#c43b4f", 42))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    image.alpha_composite(glow)

    draw = ImageDraw.Draw(image)
    for step in range(14):
        y = int(height * (0.12 + step * 0.055))
        color = (134, 198, 221, 18) if step % 2 == 0 else (241, 232, 215, 12)
        draw.line((0, y, width, y), fill=color, width=1)

    main_box = (40, 46, width - 284, height - 184)
    side_box = (width - 230, 46, width - 40, height - 184)
    footer_y = height - 156
    rounded_panel(draw, main_box, (8, 10, 14, 224), (172, 197, 210, 36), 34)
    rounded_panel(draw, side_box, (8, 10, 14, 220), (172, 197, 210, 30), 34)
    rounded_panel(draw, (40, footer_y, width // 3 - 4, height - 34), (8, 10, 14, 220), (172, 197, 210, 28), 28)
    rounded_panel(draw, (width // 3 + 6, footer_y, 2 * width // 3 - 6, height - 34), (8, 10, 14, 220), (172, 197, 210, 28), 28)
    rounded_panel(draw, (2 * width // 3 + 4, footer_y, width - 40, height - 34), (8, 10, 14, 220), (172, 197, 210, 28), 28)

    readout = (74, 206, 236, 882)
    well_panel = (258, 206, width - 316, 882)
    rounded_panel(draw, readout, (11, 14, 18, 184), (241, 232, 215, 26), 28)
    rounded_panel(draw, well_panel, (11, 14, 18, 166), (241, 232, 215, 22), 28)

    well_gap = 14
    well_width = (well_panel[2] - well_panel[0] - 40 - well_gap * 2) // 3
    well_top = well_panel[1] + 18
    well_bottom = well_panel[3] - 18
    for idx in range(3):
        x0 = well_panel[0] + 18 + idx * (well_width + well_gap)
        x1 = x0 + well_width
        rounded_panel(draw, (x0, well_top, x1, well_bottom), (14, 18, 24, 88), (241, 232, 215, 14), 22)
        mouth_y = int(well_top + (well_bottom - well_top) * 0.1)
        throat_y = int(well_top + (well_bottom - well_top) * 0.72)
        center_x = (x0 + x1) // 2
        draw.line((x0 + 22, mouth_y, x1 - 22, mouth_y), fill=(241, 232, 215, 28), width=2)
        draw.polygon(
            [
                (x0 + int(well_width * 0.22), mouth_y),
                (x1 - int(well_width * 0.22), mouth_y),
                (x1 - int(well_width * 0.38), throat_y),
                (x0 + int(well_width * 0.38), throat_y),
            ],
            fill=(196, 59, 79, 28),
            outline=(241, 232, 215, 18),
        )
        for row in range(110):
            frac = row / 109
            px = center_x + int((frac - 0.5) * well_width * 0.36 * (0.6 + frac))
            py = int(mouth_y + (throat_y - mouth_y) * frac)
            size = 2 if row % 4 else 3
            draw.rounded_rectangle((px - size, py - size, px + size, py + size), radius=2, fill=(196, 59, 79, 175))
            if row % 7 == 0:
                draw.rectangle((px + 8, py - 1, px + 10, py + 1), fill=(241, 232, 215, 124))

    for offset, label, value in [(0, "X drift", "04.8"), (1, "Y pull", "-02.1"), (2, "Pulse", "18")]:
        y0 = 244 + offset * 170
        draw.text((96, y0), label, fill=(219, 227, 233, 148))
        draw.text((96, y0 + 34), value, fill=(219, 227, 233, 215))
        draw.rounded_rectangle((96, y0 + 78, 208, y0 + 88), radius=999, fill=(255, 255, 255, 18))
        draw.rounded_rectangle((96, y0 + 78, 158 + offset * 14, y0 + 88), radius=999, fill=(255, 111, 128, 228))

    draw.text((68, 84), "CRIMSON PRESSURE", fill=(219, 227, 233, 255))
    draw.text((68, 116), "FUNNEL", fill=(219, 227, 233, 255))
    draw.text((68, 150), "Distributed dark-red signal poster with three shared wells, pointer shear, and rotating pressure laws.", fill=(219, 227, 233, 176))
    draw.text((width - 202, 86), "Mode", fill=(219, 227, 233, 152))
    draw.text((width - 202, 128), "Weighted Drop", fill=(219, 227, 233, 204))
    draw.text((width - 202, 222), "Branch", fill=(219, 227, 233, 152))
    draw.text((width - 202, 264), "HTML / motion bridge", fill=(219, 227, 233, 204))

    for px, color in [(142, (196, 59, 79, 255)), (472, (255, 111, 128, 255)), (820, (134, 198, 221, 255))]:
        draw.rounded_rectangle((px, 982, px + 74, 12 + 982), radius=999, fill=color)

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
