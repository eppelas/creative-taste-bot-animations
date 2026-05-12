#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


PALETTE = {
    "ink": (48, 64, 77),
    "cyan": (132, 192, 207),
    "sage": (149, 178, 157),
    "rose": (222, 154, 144),
    "amber": (210, 161, 94),
    "plum": (129, 116, 143),
    "paper": (239, 228, 213),
    "paper_deep": (219, 197, 173),
}


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def rounded_panel(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], fill: tuple[int, int, int, int], outline=(255, 255, 255, 90), radius=30) -> None:
    draw.rounded_rectangle(rect, radius=radius, fill=fill, outline=outline, width=2)


def draw_background(image: Image.Image) -> None:
    width, height = image.size
    draw = ImageDraw.Draw(image, "RGBA")
    top = (247, 239, 229)
    bottom = PALETTE["paper_deep"]
    for y in range(height):
        t = y / max(height - 1, 1)
        r = int(lerp(top[0], bottom[0], t))
        g = int(lerp(top[1], bottom[1], t))
        b = int(lerp(top[2], bottom[2], t))
        draw.line((0, y, width, y), fill=(r, g, b, 255))

    for x, y, radius, color in [
        (0.14, 0.12, 220, (*PALETTE["cyan"], 28)),
        (0.84, 0.16, 240, (*PALETTE["rose"], 22)),
        (0.76, 0.82, 280, (*PALETTE["sage"], 24)),
    ]:
        layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        glow = ImageDraw.Draw(layer, "RGBA")
        cx = int(width * x)
        cy = int(height * y)
        for ring in range(radius, 0, -10):
            alpha = int(color[3] * (ring / radius) ** 2)
            glow.ellipse((cx - ring, cy - ring, cx + ring, cy + ring), fill=(color[0], color[1], color[2], alpha))
        image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(28)))


def draw_grid(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = rect
    for x in range(x0, x1, 90):
        draw.line((x, y0, x, y1), fill=(48, 64, 77, 18), width=1)
    for y in range(y0, y1, 90):
        draw.line((x0, y, x1, y), fill=(48, 64, 77, 18), width=1)


def draw_tray_field(image: Image.Image, rect: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = rect
    width = x1 - x0
    height = y1 - y0
    field = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(field, "RGBA")

    for lane in range(18):
        color = [PALETTE["cyan"], PALETTE["sage"], PALETTE["rose"]][lane % 3]
        points = []
        lane_y = y0 + height * (0.08 + lane / 20)
        for step in range(28):
            t = step / 27
            x = x0 + width * t
            y = lane_y + math.sin(t * math.pi * (1.6 + lane * 0.08) + lane * 0.45) * (18 + (lane % 4) * 6)
            y += math.cos(t * 9 + lane) * 5
            points.append((x, y))
        draw.line(points, fill=(*color, 72), width=2, joint="curve")

    for i in range(84):
        px = x0 + (i * 57) % width
        py = y0 + ((i * 91) % height)
        size = 2 + (i % 3)
        color = [PALETTE["cyan"], PALETTE["rose"], PALETTE["sage"], (255, 255, 255)][i % 4]
        draw.ellipse((px - size, py - size, px + size, py + size), fill=(*color, 94))

    image.alpha_composite(field.filter(ImageFilter.GaussianBlur(0.6)))

    scan = Image.new("RGBA", image.size, (0, 0, 0, 0))
    scan_draw = ImageDraw.Draw(scan, "RGBA")
    scan_rect = (x0 + 26, y0 + int(height * 0.22), x1 - 26, y0 + int(height * 0.42))
    scan_draw.rounded_rectangle(scan_rect, radius=60, fill=(255, 255, 255, 34))
    image.alpha_composite(scan.filter(ImageFilter.GaussianBlur(10)))


def draw_specimen(image: Image.Image, rect: tuple[int, int, int, int], tilt: float, accent: tuple[int, int, int], label: str, subtitle: str) -> None:
    card = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(card, "RGBA")
    x0, y0, x1, y1 = rect
    rounded_panel(draw, rect, (255, 255, 255, 74), outline=(255, 255, 255, 110), radius=28)
    draw.rounded_rectangle((x0 + 10, y0 + 10, x1 - 10, y1 - 10), radius=22, outline=(255, 255, 255, 82), width=1)

    cx = (x0 + x1) // 2
    cy = y0 + int((y1 - y0) * 0.42)
    rx = (x1 - x0) * 0.24
    ry = (y1 - y0) * 0.26
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(*accent, 42))
    draw.ellipse((cx - rx * 0.6, cy - ry * 0.72, cx + rx * 0.55, cy + ry * 0.62), fill=(255, 255, 255, 38))

    filaments = [
        ((x0 + 28, cy + 12), (cx - 20, cy - 46), (x1 - 30, cy - 26)),
        ((x0 + 36, cy + 70), (cx + 10, cy + 10), (x1 - 26, cy + 60)),
        ((x0 + 46, cy + 104), (cx + 6, cy + 34), (x1 - 42, cy + 30)),
    ]
    extra = [PALETTE["sage"], PALETTE["amber"], PALETTE["plum"]]
    for idx, pts in enumerate(filaments):
        draw.line(pts, fill=(*(accent if idx == 0 else extra[idx]), 176), width=4, joint="curve")

    for ox, oy, r in [(-38, -24, 15), (18, 2, 11), (30, -40, 9)]:
        draw.ellipse((cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r), fill=(255, 255, 255, 170), outline=(48, 64, 77, 24), width=1)

    draw.text((x0 + 16, y0 + 14), label, fill=(48, 64, 77, 180))
    draw.text((x1 - 76, y0 + 14), subtitle, fill=(48, 64, 77, 140))
    draw.text((x0 + 18, y1 - 52), "Membrane pane", fill=(48, 64, 77, 220))

    rotated = card.rotate(tilt, resample=Image.Resampling.BICUBIC, center=((x0 + x1) / 2, (y0 + y1) / 2))
    image.alpha_composite(rotated)


def render(output_path: Path, width: int, height: int) -> None:
    image = Image.new("RGBA", (width, height), (*PALETTE["paper"], 255))
    draw_background(image)
    draw = ImageDraw.Draw(image, "RGBA")

    outer = (22, 22, width - 22, height - 22)
    draw.rounded_rectangle(outer, radius=36, outline=(255, 255, 255, 52), width=2)

    intro = (44, 44, 324, height - 210)
    desk = (346, 44, width - 308, height - 210)
    side = (width - 286, 44, width - 44, height - 210)
    notes = (44, height - 184, width - 44, height - 44)
    for rect, fill in [
        (intro, (255, 250, 243, 156)),
        (desk, (255, 250, 243, 122)),
        (side, (255, 250, 243, 146)),
        (notes, (255, 250, 243, 150)),
    ]:
        rounded_panel(draw, rect, fill)

    draw_grid(draw, outer)

    # Desk internals.
    dx0, dy0, dx1, dy1 = desk
    header = (dx0 + 18, dy0 + 18, dx1 - 18, dy0 + 118)
    tray = (dx0 + 18, dy0 + 132, dx0 + int((dx1 - dx0) * 0.58), dy1 - 116)
    ledger = (tray[2] + 14, dy0 + 132, dx1 - 18, dy1 - 116)
    footer = (dx0 + 18, dy1 - 100, dx1 - 18, dy1 - 18)
    for rect in [header, tray, ledger, footer]:
        draw.rounded_rectangle(rect, radius=24, fill=(255, 255, 255, 46), outline=(255, 255, 255, 86), width=1)

    draw_tray_field(image, tray)

    draw_specimen(image, (tray[0] + 26, tray[1] + 36, tray[0] + 216, tray[1] + 296), -6, PALETTE["cyan"], "A1", "Wet")
    draw_specimen(image, (tray[0] + 220, tray[1] + 84, tray[0] + 420, tray[1] + 344), 4, PALETTE["sage"], "B7", "Trace")
    draw_specimen(image, (tray[0] + 340, tray[1] + 224, tray[0] + 544, tray[1] + 484), -3, PALETTE["rose"], "C2", "Bloom")

    # Intro metrics.
    metric_boxes = [
      (intro[0] + 18, intro[1] + 176, intro[0] + 126, intro[1] + 254),
      (intro[0] + 140, intro[1] + 176, intro[0] + 248, intro[1] + 254),
      (intro[0] + 18, intro[1] + 266, intro[0] + 126, intro[1] + 344),
      (intro[0] + 140, intro[1] + 266, intro[0] + 248, intro[1] + 344),
    ]
    for rect in metric_boxes:
        draw.rounded_rectangle(rect, radius=18, fill=(255, 255, 255, 42), outline=(255, 255, 255, 84), width=1)

    # Chips and footer.
    for idx, color in enumerate([PALETTE["cyan"], PALETTE["sage"], PALETTE["rose"]]):
        x = intro[0] + 20 + idx * 78
        draw.rounded_rectangle((x, intro[1] + 366, x + 66, intro[1] + 398), radius=16, fill=(*color, 54), outline=(255, 255, 255, 94), width=1)

    for idx in range(3):
        x0 = notes[0] + 14 + idx * ((notes[2] - notes[0] - 42) // 3 + 7)
        x1 = x0 + (notes[2] - notes[0] - 42) // 3
        draw.rounded_rectangle((x0, notes[1] + 14, x1, notes[3] - 14), radius=22, fill=(255, 255, 255, 46), outline=(255, 255, 255, 92), width=1)

    image.convert("RGB").save(output_path, quality=96)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    render(args.output, args.width, args.height)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
