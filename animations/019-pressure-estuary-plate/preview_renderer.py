#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def glow(
    image: Image.Image,
    center: tuple[float, float],
    radius: float,
    color: tuple[int, int, int],
    alpha: int,
) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    for ring in range(12, 0, -1):
        frac = ring / 12
        r = radius * frac
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color + (int(alpha * frac * frac * 0.8),))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius * 0.08)))


def render(output: Path, width: int, height: int) -> None:
    rng = random.Random(19)
    image = Image.new("RGBA", (width, height), (5, 6, 10, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    top = (10, 12, 19)
    bottom = (4, 5, 8)
    for y in range(height):
        t = y / max(1, height - 1)
        draw.line((0, y, width, y), fill=mix(top, bottom, t) + (255,))

    glow(image, (width * 0.26, height * 0.16), width * 0.22, (119, 217, 231), 52)
    glow(image, (width * 0.54, height * 0.6), width * 0.24, (255, 91, 115), 66)
    glow(image, (width * 0.78, height * 0.34), width * 0.18, (139, 127, 249), 44)

    veil = Image.new("RGBA", image.size, (0, 0, 0, 0))
    veil_draw = ImageDraw.Draw(veil, "RGBA")
    for y in range(24):
        yy = height * (0.12 + y * 0.032)
        points = []
        for step in range(36):
            t = step / 35
            xx = width * t
            wave = math.sin(t * 7.2 + y * 0.35) * 12 + math.cos(t * 13.5 + y * 0.22) * 4
            points.append((xx, yy + wave))
        veil_draw.line(points, fill=(243, 237, 227, rng.randint(8, 16)), width=1)
    image.alpha_composite(veil)

    lane_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    lane_draw = ImageDraw.Draw(lane_layer, "RGBA")
    lane_positions = [0.14, 0.23, 0.34, 0.45, 0.56, 0.67, 0.78, 0.87]
    for idx, lane in enumerate(lane_positions):
        x = width * lane
        points = []
        for step in range(30):
            t = step / 29
            y = height * (0.06 + t * 0.9)
            sway = math.sin(t * 8 + idx * 0.7) * 22 + math.cos(t * 10.5 + idx) * 8
            points.append((x + sway, y))
        lane_draw.line(points, fill=(255, 91, 115, 72), width=16)
        lane_draw.line(points, fill=(119, 217, 231, 38), width=6)
        lane_draw.line(points, fill=(243, 237, 227, 34), width=1)
    image.alpha_composite(lane_layer.filter(ImageFilter.GaussianBlur(1.6)))

    capsule_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    capsule_draw = ImageDraw.Draw(capsule_layer, "RGBA")
    for col, lane in enumerate(lane_positions[1:-1]):
        for row in range(4):
            cx = width * lane + math.sin(col * 0.9 + row * 0.7) * 12
            cy = height * (0.18 + row * 0.18 + (col % 2) * 0.04)
            rx = 34 + row * 3
            ry = 20 + row * 2
            fill = (243, 237, 227, 20)
            outline = (243, 237, 227, 44)
            inner = (255, 91, 115, 72) if (col + row) % 2 == 0 else (119, 217, 231, 62)

            capsule_draw.ellipse((cx - rx * 1.25, cy - ry * 1.45, cx + rx * 1.25, cy + ry * 1.45), fill=(255, 255, 255, 10))
            capsule_draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=fill, outline=outline, width=1)
            capsule_draw.ellipse((cx - rx * 0.52, cy - ry * 0.28, cx + rx * 0.52, cy + ry * 0.28), fill=inner)
            capsule_draw.line((cx - rx * 0.84, cy, cx + rx * 0.84, cy), fill=(139, 127, 249, 54), width=1)
            capsule_draw.line((cx, cy - ry * 0.82, cx, cy + ry * 0.82), fill=(139, 127, 249, 40), width=1)
    image.alpha_composite(capsule_layer.filter(ImageFilter.GaussianBlur(0.9)))

    mote_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    mote_draw = ImageDraw.Draw(mote_layer, "RGBA")
    for i in range(320):
        x = rng.uniform(width * 0.1, width * 0.9)
        y = rng.uniform(height * 0.1, height * 0.92)
        size = rng.uniform(0.8, 2.4)
        if i % 11 == 0:
            s = size * 2.4
            mote_draw.rectangle((x - s, y - s, x + s, y + s), fill=(243, 237, 227, rng.randint(42, 92)))
        else:
            color = (255, 91, 115, rng.randint(52, 112)) if i % 2 == 0 else (119, 217, 231, rng.randint(34, 84))
            mote_draw.ellipse((x - size, y - size, x + size, y + size), fill=color)
    image.alpha_composite(mote_layer.filter(ImageFilter.GaussianBlur(0.2)))

    focus = Image.new("RGBA", image.size, (0, 0, 0, 0))
    focus_draw = ImageDraw.Draw(focus, "RGBA")
    glow(image, (width * 0.54, height * 0.72), width * 0.14, (243, 237, 227), 38)
    focus_draw.ellipse((width * 0.43, height * 0.61, width * 0.65, height * 0.83), outline=(243, 237, 227, 38), width=2)
    image.alpha_composite(focus.filter(ImageFilter.GaussianBlur(0.4)))

    hud = Image.new("RGBA", image.size, (0, 0, 0, 0))
    hud_draw = ImageDraw.Draw(hud, "RGBA")
    hud_draw.rounded_rectangle((36, 36, 492, 242), radius=24, fill=(9, 11, 18, 178), outline=(243, 237, 227, 34), width=1)
    hud_draw.rounded_rectangle((790, 36, 1040, 504), radius=24, fill=(9, 11, 18, 178), outline=(243, 237, 227, 34), width=1)
    hud_draw.text((60, 62), "PRESSURE ESTUARY PLATE", fill=(243, 237, 227, 236))
    hud_draw.text((816, 68), "PATCH SWITCHES", fill=(243, 237, 227, 188))
    for row in range(3):
        y = 152 + row * 96
        for col in range(3):
            x = 816 + col * 70
            active = (row == 0 and col == 0) or (row == 1 and col == 0) or (row == 2 and col == 1)
            fill = (255, 91, 115, 54) if active else (255, 255, 255, 12)
            outline = (119, 217, 231, 88) if active else (243, 237, 227, 26)
            hud_draw.rounded_rectangle((x, y, x + 56, y + 46), radius=14, fill=fill, outline=outline, width=2 if active else 1)
    image.alpha_composite(hud.filter(ImageFilter.GaussianBlur(0.35)))

    output.parent.mkdir(parents=True, exist_ok=True)
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
