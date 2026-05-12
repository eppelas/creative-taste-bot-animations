#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def mix(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


def rounded_rectangle(draw: ImageDraw.ImageDraw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    width = args.width
    height = args.height
    image = Image.new("RGBA", (width, height), (6, 7, 11, 255))
    draw = ImageDraw.Draw(image)

    top = (10, 12, 18)
    bottom = (5, 6, 10)
    for y in range(height):
      t = y / max(1, height - 1)
      draw.line((0, y, width, y), fill=mix(top, bottom, t), width=1)

    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    glows = [
        ((width * 0.18, height * 0.16), width * 0.18, (255, 85, 109, 58)),
        ((width * 0.8, height * 0.18), width * 0.2, (121, 217, 241, 46)),
        ((width * 0.55, height * 0.84), width * 0.2, (255, 157, 121, 30)),
    ]
    for (cx, cy), radius, color in glows:
        gdraw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color)
    glow = glow.filter(ImageFilter.GaussianBlur(70))
    image.alpha_composite(glow)
    draw = ImageDraw.Draw(image)

    for x in range(0, width, 84):
        draw.line((x, 0, x, height), fill=(255, 255, 255, 8), width=1)
    for y in range(0, height, 84):
        draw.line((0, y, width, y), fill=(255, 255, 255, 8), width=1)

    plate_w = int(min(width * 0.72, 980))
    plate_h = int(min(height * 0.8, 780))
    cx = width // 2
    cy = int(height * 0.58)
    plate = (cx - plate_w // 2, cy - plate_h // 2, cx + plate_w // 2, cy + plate_h // 2)
    rounded_rectangle(draw, plate, 34, fill=(10, 12, 18, 212), outline=(255, 220, 205, 34), width=2)

    glass = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glass_draw = ImageDraw.Draw(glass)
    inset = 18
    rounded_rectangle(
        glass_draw,
        (plate[0] + inset, plate[1] + inset, plate[2] - inset, plate[3] - inset),
        28,
        fill=(255, 255, 255, 10),
    )
    glass = glass.filter(ImageFilter.GaussianBlur(12))
    image.alpha_composite(glass)
    draw = ImageDraw.Draw(image)

    pointer_x = int(width * 0.59)
    pointer_y = int(height * 0.54)

    for i in range(14):
        lane_t = i / 13
        base_y = cy - plate_h * 0.31 + lane_t * plate_h * 0.62
        pts = []
        for step in range(50):
            t = step / 49
            x = cx - plate_w * 0.38 + t * plate_w * 0.76
            wave = math.sin(t * 6 + i * 0.7) * plate_h * 0.015
            pocket = math.cos(t * 10 - i * 0.4) * plate_h * 0.008
            pointer_pull = math.exp(-abs(x - pointer_x) / 190) * math.exp(-abs(base_y - pointer_y) / 150) * plate_h * 0.04 * (t - 0.5)
            y = base_y + wave + pocket + pointer_pull
            pts.append((x, y))
        color = (121, 217, 241, 88) if i % 4 == 0 else (255, 85, 109, 68)
        draw.line(pts, fill=color, width=2 if i % 3 == 0 else 1)

    for i in range(30):
        x = cx - plate_w * 0.34 + ((i * 71) % int(plate_w * 0.68))
        y = cy - plate_h * 0.3 + math.sin(i * 1.7) * plate_h * 0.16 + (i % 7) * 10
        s = 6 if i % 5 == 0 else 4
        fill = (216, 255, 103, 140) if i % 4 == 0 else (255, 244, 239, 120)
        draw.rectangle((x, y, x + s, y + s), fill=fill)

    body_x = cx - plate_w * 0.06
    body_y = cy + plate_h * 0.02
    body_w = plate_w * 0.24
    body_h = plate_h * 0.42

    body_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(body_layer)
    shell = [
        (body_x, body_y - body_h * 0.55),
        (body_x + body_w * 0.58, body_y - body_h * 0.48),
        (body_x + body_w * 0.62, body_y + body_h * 0.28),
        (body_x, body_y + body_h * 0.48),
        (body_x - body_w * 0.56, body_y + body_h * 0.16),
        (body_x - body_w * 0.42, body_y - body_h * 0.46),
    ]
    bdraw.polygon(shell, fill=(255, 115, 124, 44), outline=(255, 235, 226, 70))
    for i in range(4):
        cell_y = body_y - body_h * 0.22 + i * body_h * 0.16
        cell_w = body_w * (0.74 - i * 0.08)
        bdraw.ellipse(
            (body_x - cell_w, cell_y - body_h * 0.08, body_x + cell_w, cell_y + body_h * 0.08),
            outline=(121, 217, 241, 52) if i % 2 == 0 else (255, 85, 109, 50),
            width=2,
        )
    body_layer = body_layer.filter(ImageFilter.GaussianBlur(1))
    image.alpha_composite(body_layer)
    draw = ImageDraw.Draw(image)

    face_y = body_y - body_h * 0.21
    triad = [
        (body_x - body_w * 0.14, face_y + 2),
        (body_x + body_w * 0.14, face_y - 1),
        (body_x, face_y + body_w * 0.14),
    ]
    for ex, ey in triad:
        halo = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        hdraw = ImageDraw.Draw(halo)
        hdraw.ellipse((ex - 28, ey - 28, ex + 28, ey + 28), fill=(121, 217, 241, 64))
        hdraw.ellipse((ex - 18, ey - 18, ex + 18, ey + 18), fill=(255, 85, 109, 88))
        halo = halo.filter(ImageFilter.GaussianBlur(10))
        image.alpha_composite(halo)
        draw = ImageDraw.Draw(image)
        draw.ellipse((ex - 5, ey - 5, ex + 5, ey + 5), fill=(255, 247, 240, 230))

    for side in (-1, 1):
        root_base_x = body_x + side * body_w * 0.18
        root_base_y = body_y + body_h * 0.28
        for i in range(3):
            foot_x = root_base_x + side * (body_w * (0.36 + i * 0.14))
            foot_y = body_y + body_h * (0.62 + i * 0.1)
            fill = (255, 157, 121, 84) if i == 1 else (121, 217, 241, 74)
            draw.line(
                [
                    (root_base_x, root_base_y),
                    (root_base_x + side * body_w * (0.12 + i * 0.05), root_base_y + body_h * (0.11 + i * 0.1)),
                    (foot_x - side * body_w * 0.1, foot_y - body_h * 0.06),
                    (foot_x, foot_y),
                ],
                fill=fill,
                width=max(2, 5 - i),
            )

    for side in (-1, 1):
        crown_x = body_x + side * body_w * 0.34
        crown_y = body_y - body_h * 0.28
        for i in range(4):
            stem_x = crown_x + side * i * 8
            stem_y = crown_y - i * 12
            draw.line((crown_x, crown_y + i * 2, stem_x, stem_y), fill=(255, 235, 226, 74), width=1)
            fill = (216, 255, 103, 200) if i % 2 == 0 else (255, 255, 255, 180)
            draw.ellipse((stem_x - 3, stem_y - 3, stem_x + 3, stem_y + 3), fill=fill)

    rail_x = cx + plate_w * 0.26
    rail_y = cy - plate_h * 0.22
    card_w = plate_w * 0.18
    card_h = plate_h * 0.16
    for i in range(3):
        y = rail_y + i * (card_h + plate_h * 0.035)
        rounded_rectangle(draw, (rail_x, y, rail_x + card_w, y + card_h), 22, fill=(255, 255, 255, 10), outline=(255, 220, 205, 24), width=1)
        inner_x = rail_x + 18
        inner_y = y + card_h * 0.34
        count = 5 + i
        for p in range(count):
            t = p / max(1, count - 1)
            px = inner_x + t * (card_w - 36)
            py = inner_y + math.sin(t * 6 + i) * (6 + i * 2)
            fill = (255, 85, 109, 210) if p < 2 + i else (255, 248, 241, 138)
            draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill=fill)
        pts = []
        for s in range(21):
            t = s / 20
            px = inner_x + t * (card_w - 36)
            py = y + card_h * 0.72 + math.cos(t * 8 + i) * (5 + i * 2)
            pts.append((px, py))
        draw.line(pts, fill=(121, 217, 241, 90) if i == 1 else (255, 157, 121, 84), width=2)

    for i in range(5):
        offset = i * 14 + 10
        draw.line(
            (
                cx - plate_w * 0.24 + offset,
                cy - plate_h * 0.3 - i * 12,
                cx + plate_w * 0.18 + offset,
                cy + plate_h * 0.34 - i * 14,
            ),
            fill=(255, 255, 255, 24),
            width=1,
        )

    note = (22, 20, min(22 + 460, width - 22), 235)
    rounded_rectangle(draw, note, 24, fill=(10, 12, 18, 206), outline=(255, 220, 205, 28), width=2)
    chip_x = width - 152
    chip_y = height // 2 - 90
    for i in range(3):
        active = i == 0
        rounded_rectangle(
            draw,
            (chip_x, chip_y + i * 94, chip_x + 128, chip_y + 70 + i * 94),
            18,
            fill=(255, 255, 255, 16 if active else 10),
            outline=(216, 255, 103, 70) if active else (255, 220, 205, 24),
            width=2 if active else 1,
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
