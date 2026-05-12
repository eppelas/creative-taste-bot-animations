#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Menlo.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Supplemental/Courier New Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Courier New.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: tuple[int, int, int, int], outline: tuple[int, int, int, int], radius: int) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    width = args.width
    height = args.height

    image = Image.new("RGBA", (width, height), "#f5efe6")
    draw = ImageDraw.Draw(image, "RGBA")

    for y in range(height):
      t = y / max(1, height - 1)
      r = int(251 * (1 - t) + 228 * t)
      g = int(246 * (1 - t) + 214 * t)
      b = int(239 * (1 - t) + 194 * t)
      draw.line((0, y, width, y), fill=(r, g, b, 255))

    for cx, cy, radius, color in [
        (int(width * 0.16), int(height * 0.12), 220, (255, 255, 255, 120)),
        (int(width * 0.78), int(height * 0.18), 200, (139, 196, 204, 80)),
        (int(width * 0.58), int(height * 0.84), 250, (220, 157, 136, 48)),
    ]:
        glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow, "RGBA")
        glow_draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color)
        image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(radius=42)))

    grid = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    grid_draw = ImageDraw.Draw(grid, "RGBA")
    for x in range(0, width, 92):
        grid_draw.line((x, 0, x, height), fill=(48, 66, 74, 16), width=1)
    for y in range(0, height, 92):
        grid_draw.line((0, y, width, y), fill=(48, 66, 74, 18), width=1)
    image.alpha_composite(grid)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay, "RGBA")

    reservoirs = [
        (0.18, 0.29, 0.11, (185, 226, 234, 180), "NORTH"),
        (0.38, 0.23, 0.09, (166, 212, 206, 172), "EAST"),
        (0.58, 0.36, 0.13, (189, 230, 236, 190), "SPINE"),
        (0.77, 0.25, 0.1, (216, 197, 155, 170), "RIDGE"),
        (0.26, 0.6, 0.12, (216, 233, 208, 182), "SOUTH"),
        (0.49, 0.68, 0.15, (198, 236, 228, 190), "DELTA"),
        (0.77, 0.63, 0.11, (240, 207, 182, 170), "WEST"),
    ]
    links = [(0, 1), (1, 2), (2, 3), (0, 4), (1, 4), (2, 5), (3, 6), (4, 5), (5, 6), (1, 5), (2, 6)]

    points = []
    scale = min(width, height)
    for x, y, r, color, label in reservoirs:
        points.append((int(x * width), int(y * height), int(r * scale), color, label))

    for idx, (a_idx, b_idx) in enumerate(links):
        ax, ay, _, _, _ = points[a_idx]
        bx, by, _, _, _ = points[b_idx]
        mx = (ax + bx) / 2
        my = (ay + by) / 2
        bend = math.sin(idx * 0.8) * 24
        nx = -(by - ay)
        ny = bx - ax
        length = max(1, math.hypot(nx, ny))
        cx = mx + nx / length * bend
        cy = my + ny / length * bend * 0.6
        overlay_draw.line((ax, ay, cx, cy, bx, by), fill=(214, 228, 225, 150), width=22, joint="curve")
        overlay_draw.line((ax, ay, cx, cy, bx, by), fill=(111, 182, 192, 132), width=8, joint="curve")

    image.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(radius=3)))
    draw = ImageDraw.Draw(image, "RGBA")

    label_font = load_font(18)
    small_font = load_font(15)
    title_font = load_font(68, bold=True)
    body_font = load_font(24)
    meta_font = load_font(16)

    for idx, (x, y, radius, color, label) in enumerate(points):
        basin = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        basin_draw = ImageDraw.Draw(basin, "RGBA")
        basin_draw.ellipse((x - radius, y - int(radius * 0.82), x + radius, y + int(radius * 0.82)), fill=color, outline=(43, 56, 64, 58), width=3)
        basin_draw.ellipse((x - int(radius * 0.72), y - int(radius * 0.34), x + int(radius * 0.72), y + int(radius * 0.34)), outline=(255, 255, 255, 110), width=2)
        for p in range(22):
            angle = (p / 22) * math.tau + idx * 0.2
            px = x + math.cos(angle) * radius * 0.55
            py = y + math.sin(angle * 1.2) * radius * 0.32
            basin_draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill=(111, 182, 192, 110))
        image.alpha_composite(basin.filter(ImageFilter.GaussianBlur(radius=10)))
        draw.ellipse((x - radius, y - int(radius * 0.82), x + radius, y + int(radius * 0.82)), outline=(43, 56, 64, 42), width=2)
        draw.line((x - 42, y + int(radius * 0.9), x + 42, y + int(radius * 0.9)), fill=(43, 56, 64, 110), width=1)
        draw.text((x, y + int(radius * 1.04)), label, font=label_font, fill=(43, 56, 64, 184), anchor="ma")

    for idx, (a_idx, b_idx) in enumerate(links):
        if idx % 2 != 0:
            continue
        ax, ay, _, _, _ = points[a_idx]
        bx, by, _, _, _ = points[b_idx]
        t = 0.5
        x = ax + (bx - ax) * t
        y = ay + (by - ay) * t
        angle = math.atan2(by - ay, bx - ax)
        dx = math.cos(angle)
        dy = math.sin(angle)
        nx = -dy
        ny = dx
        corners = []
        for sx, sy in [(-34, -8), (34, -8), (34, 8), (-34, 8)]:
            corners.append((x + dx * sx + nx * sy, y + dy * sx + ny * sy))
        draw.polygon(corners, fill=(247, 241, 233, 228), outline=(43, 56, 64, 36))

    panel_fill = (252, 248, 241, 212)
    panel_outline = (48, 66, 74, 36)
    rounded_panel(draw, (24, 24, width - 24, 286), panel_fill, panel_outline, 34)
    rounded_panel(draw, (width - 316, 306, width - 24, 1040), panel_fill, panel_outline, 30)
    rounded_panel(draw, (24, height - 236, width - 24, height - 24), panel_fill, panel_outline, 28)
    rounded_panel(draw, (24, height - 92, 272, height - 24), panel_fill, panel_outline, 30)

    draw.text((52, 56), "GENERATED ANIMATION STUDY 065 / DAYLIGHT MEMBRANE INFRASTRUCTURE", font=meta_font, fill=(43, 56, 64, 160))
    draw.text((52, 88), "Service Bloom", font=title_font, fill=(43, 56, 64, 236))
    draw.text((52, 152), "Waterworks", font=title_font, fill=(111, 182, 192, 255))

    lede = (
        "A pale district-scale waterworks page that keeps the current living-infrastructure branch active "
        "without slipping back into a hero specimen, a cliff cutaway, or a dark control board."
    )
    draw.text((54, 232), lede, font=body_font, fill=(43, 56, 64, 178), spacing=6)

    chip_y = 314
    for i, label in enumerate(["CALM", "TIDE", "FLUSH"]):
        left = 52 + i * 124
        rounded_panel(draw, (left, chip_y, left + 106, chip_y + 42), (255, 252, 247, 236), (48, 66, 74, 28), 20)
        draw.ellipse((left + 10, chip_y + 14, left + 22, chip_y + 26), fill=(111, 182, 192, 220))
        draw.text((left + 34, chip_y + 12), label, font=small_font, fill=(43, 56, 64, 210))

    draw.text((width - 286, 338), "LIVE SURVEY", font=meta_font, fill=(43, 56, 64, 150))
    draw.text((width - 286, 372), "Reservoir balance", font=body_font, fill=(43, 56, 64, 230))
    draw.text((width - 286, 414), "The bars reflect the district pressure and current mode.", font=small_font, fill=(43, 56, 64, 156))

    bar_values = [74, 58, 83, 61, 69, 92, 66]
    for idx, ((_, _, _, _, label), value) in enumerate(zip(reservoirs, bar_values)):
        y = 470 + idx * 56
        draw.text((width - 286, y), label, font=small_font, fill=(43, 56, 64, 172))
        draw.rounded_rectangle((width - 206, y + 4, width - 88, y + 20), radius=8, fill=(43, 56, 64, 18))
        draw.rounded_rectangle((width - 206, y + 4, width - 206 + int(1.18 * value), y + 20), radius=8, fill=(111, 182, 192, 180))
        draw.text((width - 76, y), f"{value:02d}", font=small_font, fill=(43, 56, 64, 172), anchor="la")

    note_titles = ["IDEA", "INTERACTION", "NEXT"]
    note_bodies = [
        "Translate the membrane-waterworks image lane into one browser-native district sheet.",
        "Pointer warmth and click-planted pulses travel through the nearest basin group.",
        "A future pass could add tiny workers, seasonal labels, or route weather."
    ]
    note_width = (width - 68) // 3
    for idx, (title, body) in enumerate(zip(note_titles, note_bodies)):
        left = 36 + idx * note_width
        rounded_panel(draw, (left, height - 216, left + note_width - 12, height - 44), (255, 251, 245, 176), (48, 66, 74, 24), 22)
        draw.text((left + 18, height - 196), title, font=meta_font, fill=(43, 56, 64, 150))
        draw.text((left + 18, height - 164), body, font=small_font, fill=(43, 56, 64, 188), spacing=5)

    draw.text((48, height - 74), "BACK TO ANIMATION INDEX", font=small_font, fill=(43, 56, 64, 176))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
