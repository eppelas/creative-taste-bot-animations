#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def draw_scene(width: int, height: int) -> Image.Image:
    image = Image.new("RGBA", (width, height), "#05070a")
    draw = ImageDraw.Draw(image, "RGBA")

    for y in range(height):
      t = y / max(1, height - 1)
      r = round(lerp(9, 5, t))
      g = round(lerp(11, 7, t))
      b = round(lerp(16, 10, t))
      draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    for cx, cy, radius, color in (
        (0.18, 0.18, 0.24, (255, 68, 95, 26)),
        (0.78, 0.16, 0.26, (133, 218, 241, 18)),
        (0.50, 0.84, 0.24, (223, 255, 98, 14)),
    ):
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay, "RGBA")
        x = cx * width
        y = cy * height
        r = radius * min(width, height)
        odraw.ellipse((x - r, y - r, x + r, y + r), fill=color)
        image = Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(radius=42)))

    draw = ImageDraw.Draw(image, "RGBA")

    pointer_x = width * 0.62
    pointer_y = height * 0.48
    pressure = 0.58

    def field(x: float, y: float, bias: float = 0.0) -> tuple[float, float, float]:
        nx = x / width
        ny = y / height
        swirl = math.sin(nx * 7.4 + 1.4 + bias) * 0.7 + math.cos(ny * 8.1 - 1.1 - bias * 0.6) * 0.45
        dx = x - pointer_x
        dy = y - pointer_y
        dist = math.hypot(dx, dy) + 1.0
        influence = max(0.0, 1.0 - dist / min(width, height) * 1.1)
        angle = swirl + influence * pressure * 2.4
        return math.cos(angle), math.sin(angle * 1.12), influence

    for lane in range(9):
        points = []
        y_base = height * (0.18 + lane * 0.08)
        for x in range(-20, width + 21, 12):
            vx, vy, influence = field(x, y_base, lane * 0.6)
            y = y_base + math.sin(x * 0.011 + lane * 0.9 + 0.42) * (8 + lane * 1.5) + influence * 26 * math.sin(2 + lane)
            points.append((x, y))
        color = (255, 68, 95, 31) if lane % 3 == 0 else (133, 218, 241, 20) if lane % 2 == 0 else (255, 226, 204, 15)
        draw.line(points, fill=color, width=1)

    seam_nodes: list[tuple[float, float]] = []
    for i in range(18):
        t = i / 17
        x = width * (0.08 + t * 0.84)
        y = height * 0.58 + math.sin(t * 7.2) * height * 0.09 + math.sin(t * 18.4) * height * 0.018
        pull = max(0.0, 1.0 - math.hypot(x - pointer_x, y - pointer_y) / 240.0) * pressure * 34.0
        seam_nodes.append((x, y - pull))

    for i in range(36, 0, -1):
        alpha = max(2, 6 - i // 8)
        draw.line(seam_nodes, fill=(255, 90, 103, alpha), width=26 + i)
    draw.line(seam_nodes, fill=(255, 150, 110, 160), width=22)
    draw.line(seam_nodes, fill=(255, 236, 214, 220), width=2)

    for i in range(len(seam_nodes) - 1):
        ax, ay = seam_nodes[i]
        bx, by = seam_nodes[i + 1]
        mx = (ax + bx) * 0.5
        my = (ay + by) * 0.5
        dx = bx - ax
        dy = by - ay
        length = math.hypot(dx, dy) or 1.0
        nx = -dy / length
        ny = dx / length
        open_amount = 8 + math.sin(1.8 + i * 0.7) * 5 + max(0.0, 1.0 - math.hypot(mx - pointer_x, my - pointer_y) / 220.0) * pressure * 24.0
        color = (223, 255, 98, 56) if i % 3 == 0 else (255, 68, 95, 46)
        draw.line(
            [(mx - nx * open_amount, my - ny * open_amount), (mx + nx * open_amount, my + ny * open_amount)],
            fill=color,
            width=1,
        )

    for i in range(38):
        lane = i % 3
        x = width * (0.1 + ((i * 0.14) % 0.8))
        y = height * (0.16 + lane * 0.22) + math.sin(i * 1.7) * height * 0.04 + (height * 0.18 if lane == 2 else 0)
        vx, vy, influence = field(x, y, ((i % 6) - 2.5) * 0.07)
        x += vx * 10 + influence * 26
        y += vy * 8 - influence * 16
        w = 12 + (i % 4) * 6
        h = 2 if i % 5 == 0 else 6
        color = (223, 255, 98, 199) if i % 9 == 0 else (133, 218, 241, 199) if i % 4 == 0 else (255, 143, 97, 194) if i % 3 == 0 else (255, 226, 204, 36)
        draw.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), radius=2, fill=color)

    for i in range(max(120, int(width * 0.11))):
        x = (i * 73) % width
        y = (i * 29 + (i % 7) * 41) % height
        vx, vy, influence = field(x, y, i * 0.17)
        size = 1 + ((i * 17) % 13) / 6
        color = (255, 143, 97, 97) if influence > 0.38 else (255, 68, 95, 71) if size > 2 else (255, 226, 204, 46)
        draw.ellipse((x - size, y - size, x + size, y + size), fill=color)

    phrases = [
        ("SIGNAL FIELD", 0.22, 0.0, 1.0),
        ("RELAY WEATHER", 0.48, 0.8, 0.74),
        ("PRESSURE GLYPH", 0.68, 1.3, 0.58),
    ]
    for text, lane, wobble, alpha in phrases:
        idx = lane * (len(seam_nodes) - 1)
        base = int(idx)
        blend = idx - base
        ax, ay = seam_nodes[base]
        bx, by = seam_nodes[min(base + 1, len(seam_nodes) - 1)]
        px = ax + (bx - ax) * blend
        py = ay + (by - ay) * blend
        vx, vy, _ = field(px, py, wobble)
        x = px + vx * 42 + math.sin(wobble) * 14
        y = py - 42 + vy * 16 + math.cos(wobble * 0.9) * 10
        glow = 22
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay, "RGBA")
        odraw.ellipse((x - glow * 1.9, y - glow, x + glow * 1.9, y + glow), fill=(255, 68, 95, int(36 * alpha)))
        image = Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(radius=16)))
        draw = ImageDraw.Draw(image, "RGBA")
        draw.rectangle((x - 10, y - 10, x + 10, y + 10), outline=(255, 226, 204, int(112 * alpha)), width=1)
        draw.line((x - 12, y, px, py), fill=(133, 218, 241, int(84 * alpha)), width=1)
        draw.text((x + 18, y - 8), text, fill=(239, 231, 218, int(225 * alpha)))

    draw.line((pointer_x - 18, pointer_y, pointer_x + 18, pointer_y), fill=(255, 226, 204, 82), width=1)
    draw.line((pointer_x, pointer_y - 18, pointer_x, pointer_y + 18), fill=(255, 226, 204, 82), width=1)
    draw.ellipse((pointer_x - 34, pointer_y - 34, pointer_x + 34, pointer_y + 34), outline=(255, 68, 95, 96), width=1)

    panel = (38, 34, min(width - 38, 632), 334)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay, "RGBA")
    odraw.rounded_rectangle(panel, radius=24, fill=(8, 10, 14, 196), outline=(255, 226, 204, 28), width=1)
    image = Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(radius=0.5)))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.text((62, 58), "CODE ANIMATION STUDY #033", fill=(239, 231, 218, 132))
    draw.text((62, 94), "Utterance Fault Weather", fill=(239, 231, 218, 235))
    draw.text((62, 138), "A dark relay-weather plate where short phrases become", fill=(239, 231, 218, 174))
    draw.text((62, 160), "pressure glyphs inside a segmented fault seam.", fill=(239, 231, 218, 174))
    draw.text((62, 196), "ACTIVE PHRASE", fill=(239, 231, 218, 132))
    draw.text((62, 214), "signal field", fill=(239, 231, 218, 225))
    draw.text((230, 196), "PRESSURE", fill=(239, 231, 218, 132))
    draw.text((230, 214), "0.58", fill=(239, 231, 218, 225))
    draw.text((334, 196), "FLUX COUNT", fill=(239, 231, 218, 132))
    draw.text((334, 214), "3", fill=(239, 231, 218, 225))
    draw.rounded_rectangle((62, 250, 372, 296), radius=16, outline=(255, 226, 204, 38), fill=(255, 255, 255, 8), width=1)
    draw.text((80, 266), "signal field", fill=(239, 231, 218, 225))
    draw.rounded_rectangle((386, 250, 504, 296), radius=16, outline=(255, 226, 204, 38), fill=(255, 255, 255, 8), width=1)
    draw.text((404, 266), "Inject phrase", fill=(239, 231, 218, 225))
    draw.rounded_rectangle((518, 250, 612, 296), radius=16, outline=(223, 255, 98, 90), fill=(255, 255, 255, 8), width=1)
    draw.text((540, 266), "Mic pulse", fill=(239, 231, 218, 225))

    return image.convert("RGB")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    image = draw_scene(args.width, args.height)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
