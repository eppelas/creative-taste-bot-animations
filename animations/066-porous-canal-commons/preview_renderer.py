#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def poly_point(points: list[tuple[float, float]], t: float) -> tuple[float, float]:
    t = max(0.0, min(0.999, t))
    scaled = t * (len(points) - 1)
    idx = int(scaled)
    frac = scaled - idx
    ax, ay = points[idx]
    bx, by = points[idx + 1]
    return lerp(ax, bx, frac), lerp(ay, by, frac)


def rounded_box(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], radius: float, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    width = args.width
    height = args.height

    image = Image.new("RGBA", (width, height), "#f4eee5")
    draw = ImageDraw.Draw(image, "RGBA")

    for y in range(height):
      t = y / max(1, height - 1)
      r = int(lerp(250, 223, t))
      g = int(lerp(244, 202, t))
      b = int(lerp(236, 177, t))
      draw.line((0, y, width, y), fill=(r, g, b, 255))

    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow, "RGBA")
    for cx, cy, r, color in (
        (width * 0.18, height * 0.16, width * 0.16, (255, 255, 255, 120)),
        (width * 0.77, height * 0.18, width * 0.18, (135, 192, 203, 80)),
        (width * 0.58, height * 0.81, width * 0.22, (222, 154, 132, 64)),
    ):
        gdraw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
    glow = glow.filter(ImageFilter.GaussianBlur(48))
    image.alpha_composite(glow)

    grid = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grid, "RGBA")
    for x in range(0, width, 96):
        gdraw.line((x, 0, x, height), fill=(41, 54, 60, 16), width=1)
    for y in range(0, height, 96):
        gdraw.line((0, y, width, y), fill=(41, 54, 60, 14), width=1)
    grid = grid.filter(ImageFilter.GaussianBlur(0.3))
    image.alpha_composite(grid)

    canals = [
        [(0.08, 0.72), (0.22, 0.66), (0.36, 0.58), (0.53, 0.64), (0.68, 0.56), (0.86, 0.62)],
        [(0.16, 0.42), (0.34, 0.47), (0.46, 0.38), (0.62, 0.44), (0.82, 0.37)],
        [(0.28, 0.82), (0.4, 0.72), (0.56, 0.77), (0.72, 0.7)],
    ]

    for idx, path in enumerate(canals):
        points = [(x * width, y * height) for x, y in path]
        draw.line(points, fill=(255, 255, 255, 120), width=24 - idx * 4, joint="curve")
        draw.line(points, fill=(109, 174, 184, 168) if idx != 1 else (135, 192, 203, 190), width=14 - idx * 2, joint="curve")

    districts = [
        (0.18, 0.62, 0.13, 0.09, (184, 223, 229, 160), "LOWER BATHS"),
        (0.37, 0.52, 0.14, 0.10, (213, 162, 95, 120), "MARKET STEAM"),
        (0.57, 0.60, 0.15, 0.11, (154, 184, 157, 130), "GARDEN CISTERN"),
        (0.76, 0.50, 0.14, 0.10, (222, 154, 132, 128), "QUIET LOCK"),
        (0.48, 0.34, 0.18, 0.09, (140, 193, 203, 130), "UPPER GALLERY"),
    ]

    for idx, (cx, cy, sx, sy, color, label) in enumerate(districts):
        x = cx * width
        y = cy * height
        rx = sx * width
        ry = sy * height
        draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(250, 244, 236, 220), outline=(41, 54, 60, 40), width=2)
        inner = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        idraw = ImageDraw.Draw(inner, "RGBA")
        idraw.ellipse((x - rx * 0.92, y - ry * 0.9, x + rx * 0.92, y + ry * 0.9), fill=color)
        inner = inner.filter(ImageFilter.GaussianBlur(10))
        image.alpha_composite(inner)
        for ring in range(4):
            rr_x = rx * (0.28 + ring * 0.18)
            rr_y = ry * (0.26 + ring * 0.17)
            draw.ellipse((x - rr_x, y - rr_y, x + rr_x, y + rr_y), outline=(41, 54, 60, 18 + ring * 7), width=1)
        for room in range(4 + idx % 3):
            ang = room / (4 + idx % 3) * math.tau + idx * 0.55
            px = x + math.cos(ang) * rx * 0.46
            py = y + math.sin(ang) * ry * 0.4
            rounded_box(draw, (px - 14, py - 8, px + 14, py + 8), 8, (255, 255, 255, 110 if room % 2 == 0 else 70))
        tx = x + rx * 0.72
        ty = y - ry * 0.84
        draw.line((tx, ty, x + rx * 0.22, y - ry * 0.12), fill=(41, 54, 60, 34), width=1)
        draw.text((tx + 8, ty - 16), f"D{idx + 1}", fill=(41, 54, 60, 100))
        draw.text((x - rx * 0.54, y - ry - 26), label, fill=(41, 54, 60, 118))

    for i in range(8):
        bx = width * (0.14 + i * 0.095)
        by = height * (0.43 + ((i % 3) - 1) * 0.07)
        bw = width * 0.06
        bh = 10 + (i % 2) * 4
        rounded_box(draw, (bx - bw / 2, by - bh / 2, bx + bw / 2, by + bh / 2), bh / 2, (252, 246, 238, 240), (41, 54, 60, 54), 1)
        for j in range(-2, 3):
            draw.rectangle((bx + j * 14 - 2, by - bh / 2 + 3, bx + j * 14 + 2, by + bh / 2 - 3), fill=(109, 174, 184, 44))

    for i in range(28):
        lane = canals[i % 2]
        px, py = poly_point(lane, (i * 0.083 + 0.11) % 1.0)
        px *= width
        py *= height
        sway_x = math.cos(i * 0.7) * 3
        sway_y = math.sin(i * 0.9) * 2
        color = (222, 154, 132, 255) if i % 5 == 0 else (135, 192, 203, 255) if i % 3 == 0 else (154, 184, 157, 255)
        draw.ellipse((px - 3 + sway_x, py - 11 + sway_y, px + 3 + sway_x, py - 5 + sway_y), fill=color)
        draw.line((px + sway_x, py - 4 + sway_y, px + sway_x, py + 8 + sway_y), fill=(41, 54, 60, 84), width=1)

    for i in range(7):
        px, py = poly_point(canals[i % 3], (i * 0.13 + 0.16) % 1.0)
        px *= width
        py *= height
        rounded_box(draw, (px - 12, py - 5, px + 12, py + 5), 5, (252, 246, 238, 230), (41, 54, 60, 54), 1)

    steam = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(steam, "RGBA")
    anchors = [(d[0] * width, d[1] * height) for d in districts]
    for i in range(18):
        ax, ay = anchors[i % len(anchors)]
        x = ax + math.cos(i * 0.55) * (26 + (i % 4) * 10)
        y = ay - math.sin(i * 0.4) * (18 + (i % 5) * 8) - 20
        r = 18 + (i % 6) * 6
        sdraw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 54))
    steam = steam.filter(ImageFilter.GaussianBlur(18))
    image.alpha_composite(steam)

    panel = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(panel, "RGBA")
    rounded_box(pdraw, (36, 30, width - 36, 292), 28, (252, 246, 238, 210), (51, 67, 74, 38), 2)
    rounded_box(pdraw, (width - 318, 320, width - 36, 740), 28, (252, 246, 238, 204), (51, 67, 74, 38), 2)
    rounded_box(pdraw, (36, height - 244, width - 360, height - 36), 28, (252, 246, 238, 208), (51, 67, 74, 38), 2)
    rounded_box(pdraw, (width - 276, height - 92, width - 36, height - 36), 28, (252, 246, 238, 220), (51, 67, 74, 38), 2)
    panel = panel.filter(ImageFilter.GaussianBlur(0.2))
    image.alpha_composite(panel)

    draw = ImageDraw.Draw(image, "RGBA")
    draw.text((62, 52), "#066 GENERATED ANIMATION • INHABITED ENVIRONMENTAL SHEET", fill=(41, 54, 60, 122))
    draw.text((62, 96), "Porous Canal Commons", fill=(41, 54, 60, 255))
    draw.text((62, 144), "A pale public-world page rather than another detached infographic:", fill=(41, 54, 60, 176))
    draw.text((62, 170), "thermal canals, tiled rooms, and tiny passing figures share one", fill=(41, 54, 60, 176))
    draw.text((62, 196), "browser-native civic surface.", fill=(41, 54, 60, 176))

    button_y = 236
    buttons = [
        (62, "HUSH SHIFT", True),
        (242, "MARKET DRIFT", False),
        (446, "EVENING FLUSH", False),
    ]
    for x, label, active in buttons:
        rounded_box(draw, (x, button_y, x + 152, button_y + 34), 17, (255, 255, 255, 214), (109, 174, 184, 94 if active else 40), 2 if active else 1)
        draw.ellipse((x + 11, button_y + 11, x + 23, button_y + 23), fill=(109, 174, 184, 255))
        draw.text((x + 32, button_y + 10), label, fill=(41, 54, 60, 210))

    draw.text((width - 294, 344), "FIELD NOTES", fill=(41, 54, 60, 122))
    draw.text((width - 294, 374), "Embedded Interaction", fill=(41, 54, 60, 230))
    notes = [
        ("POINTER", "Heats the nearest district and lifts local steam."),
        ("CLICK", "Plants one pressure run through the canal network."),
        ("MODES", "Rotate the same world instead of swapping scenes."),
    ]
    yy = 430
    for label, text in notes:
        draw.text((width - 294, yy), label, fill=(41, 54, 60, 196))
        draw.text((width - 294, yy + 22), text, fill=(41, 54, 60, 158))
        yy += 96

    cols = [
        ("IDEA", "Shift the design-usable lane into a shared place."),
        ("INTERACTION", "Viewer warmth locally thickens steam and traffic."),
        ("NEXT", "Add stronger room stories without mascot collapse."),
    ]
    col_w = (width - 432) / 3
    for idx, (label, text) in enumerate(cols):
        x = 62 + idx * col_w
        draw.text((x, height - 220), label, fill=(41, 54, 60, 196))
        draw.text((x, height - 192), text, fill=(41, 54, 60, 160))

    draw.text((width - 244, height - 72), "BACK TO INDEX", fill=(41, 54, 60, 210))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
