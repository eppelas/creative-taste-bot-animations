#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(lerp(x, y, t)) for x, y in zip(a, b))


def glow(image: Image.Image, center: tuple[float, float], radius: float, color: tuple[int, int, int], alpha: int) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    for ring in range(12, 0, -1):
        frac = ring / 12
        rr = radius * frac
        draw.ellipse((x - rr, y - rr, x + rr, y + rr), fill=color + (int(alpha * frac * frac * 0.82),))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius * 0.1)))


def frond_points(x: float, y: float, length: float, angle: float) -> list[tuple[float, float]]:
    return [
        (x, y),
        (x + math.cos(angle - 0.58) * length * 0.22, y - length * 0.28),
        (x + math.cos(angle - 0.18) * length * 0.38, y - length * 0.66),
        (x + math.cos(angle + 0.08) * length * 0.46, y - length),
    ]


def render(output: Path, width: int, height: int) -> None:
    rng = random.Random(21)
    image = Image.new("RGBA", (width, height), (242, 234, 220, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    top = (244, 236, 223)
    mid = (234, 223, 207)
    bottom = (228, 212, 191)
    for y in range(height):
        t = y / max(1, height - 1)
        color = mix(mix(top, mid, min(1, t * 1.4)), bottom, max(0, (t - 0.5) / 0.5))
        draw.line((0, y, width, y), fill=color + (255,))

    glow(image, (width * 0.16, height * 0.12), width * 0.22, (255, 255, 255), 120)
    glow(image, (width * 0.68, height * 0.12), width * 0.18, (255, 255, 255), 86)
    glow(image, (width * 0.58, height * 0.72), width * 0.18, (166, 216, 200), 70)
    glow(image, (width * 0.74, height * 0.5), width * 0.12, (242, 197, 64), 84)
    glow(image, (width * 0.86, height * 0.56), width * 0.11, (231, 110, 56), 52)

    hatch = Image.new("RGBA", image.size, (0, 0, 0, 0))
    hatch_draw = ImageDraw.Draw(hatch, "RGBA")
    for index in range(170):
        y = (index / 170) * height
        offset = math.sin(index * 0.6) * 7
        hatch_draw.line((0, y + offset, width, y - offset * 0.5), fill=(120, 102, 87, 16), width=1)
    image.alpha_composite(hatch.filter(ImageFilter.GaussianBlur(0.3)))

    lattice = Image.new("RGBA", image.size, (0, 0, 0, 0))
    lattice_draw = ImageDraw.Draw(lattice, "RGBA")
    cols = 12
    rows = 12
    step_x = width / cols
    step_y = height / rows
    for row in range(-1, rows + 2):
      offset = step_x * (0.5 if row % 2 == 0 else 0)
      for col in range(-1, cols + 2):
        x = col * step_x + offset
        y = row * step_y
        n1 = (x + step_x * 0.5, y + step_y * 0.5)
        n2 = (x - step_x * 0.5, y + step_y * 0.5)
        lattice_draw.line((x, y, n1[0], n1[1]), fill=(132, 116, 99, 42), width=1)
        lattice_draw.line((x, y, n2[0], n2[1]), fill=(132, 116, 99, 36), width=1)
        lattice_draw.ellipse((x - 1.3, y - 1.3, x + 1.3, y + 1.3), fill=(255, 249, 240, 112))
    image.alpha_composite(lattice.filter(ImageFilter.GaussianBlur(0.28)))

    pools = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pool_draw = ImageDraw.Draw(pools, "RGBA")
    pool_specs = [
        (0.68, 0.24, 0.15, 0.09, (255, 255, 255, 76)),
        (0.45, 0.36, 0.12, 0.08, (185, 173, 201, 62)),
        (0.31, 0.59, 0.18, 0.1, (166, 216, 200, 82)),
        (0.61, 0.52, 0.13, 0.1, (242, 197, 64, 88)),
        (0.82, 0.44, 0.12, 0.08, (231, 110, 56, 48)),
        (0.13, 0.92, 0.12, 0.03, (242, 197, 64, 76)),
    ]
    for cx, cy, rx_frac, ry_frac, color in pool_specs:
        rx = width * rx_frac
        ry = height * ry_frac
        pool_draw.ellipse((cx * width - rx, cy * height - ry, cx * width + rx, cy * height + ry), fill=color)
        pool_draw.ellipse(
            (cx * width - rx * 0.8, cy * height - ry * 0.8, cx * width + rx * 0.8, cy * height + ry * 0.8),
            outline=(255, 255, 255, 92),
            width=2,
        )
    image.alpha_composite(pools.filter(ImageFilter.GaussianBlur(8)))

    fronds = Image.new("RGBA", image.size, (0, 0, 0, 0))
    frond_draw = ImageDraw.Draw(fronds, "RGBA")
    for index in range(30):
        base_x = rng.uniform(0.04, 0.96) * width
        base_y = lerp(height * 0.5, height * 0.97, rng.random() ** 0.6)
        length = rng.uniform(70, 190)
        angle = -math.pi / 2 + rng.uniform(-0.42, 0.42)
        color = rng.choice(
            [
                (88, 84, 92, 116),
                (122, 133, 140, 118),
                (162, 144, 136, 108),
            ]
        )
        points = frond_points(base_x, base_y, length, angle)
        frond_draw.line(points, fill=color, width=int(rng.uniform(2, 4)), joint="curve")

        segments = rng.randint(6, 11)
        for seg in range(segments + 1):
            t = seg / segments
            px = lerp(points[0][0], points[-1][0], t)
            py = lerp(points[0][1], points[-1][1], t) - math.sin(t * math.pi) * length * 0.08
            blade = (1 - t * 0.68) * rng.uniform(9, 24)
            wobble = math.sin(index * 0.9 + seg * 0.8) * 0.18
            for direction in (-1, 1):
                bx = px + math.cos(angle + math.pi / 2 + wobble * direction) * blade * direction
                by = py + math.sin(angle + math.pi / 2 + wobble * direction) * blade * direction
                frond_draw.line((px, py, bx, by), fill=color, width=2)
    image.alpha_composite(fronds.filter(ImageFilter.GaussianBlur(0.45)))

    motes = Image.new("RGBA", image.size, (0, 0, 0, 0))
    mote_draw = ImageDraw.Draw(motes, "RGBA")
    for _ in range(160):
        x = rng.uniform(0, width)
        y = rng.uniform(0, height)
        r = rng.uniform(1, 3.4)
        mote_draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, rng.randint(36, 96)))
    image.alpha_composite(motes.filter(ImageFilter.GaussianBlur(0.3)))

    panels = Image.new("RGBA", image.size, (0, 0, 0, 0))
    panels_draw = ImageDraw.Draw(panels, "RGBA")
    panels_draw.rounded_rectangle((18, 18, min(width * 0.48, 520), 260), radius=28, fill=(250, 246, 238, 196), outline=(120, 102, 87, 34), width=2)
    panels_draw.rounded_rectangle((18, height - 140, width - 18, height - 18), radius=18, fill=(250, 246, 238, 208), outline=(120, 102, 87, 30), width=2)
    panels_draw.rounded_rectangle((width - 120, 18, width - 18, 64), radius=24, fill=(250, 246, 238, 214), outline=(120, 102, 87, 26), width=2)
    image.alpha_composite(panels.filter(ImageFilter.GaussianBlur(0.35)))

    text = Image.new("RGBA", image.size, (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text)
    text_draw.text((36, 34), "CODE ANIMATION STUDY #021", fill=(74, 70, 63, 128))
    text_draw.text((36, 66), "Lattice Frond", fill=(74, 70, 63, 232))
    text_draw.text((36, 114), "Delta", fill=(74, 70, 63, 232))
    text_draw.text(
        (36, 170),
        "A pale procedural habitat built from rhombus\nscaffolds, pooled islands, and feathery frond colonies.",
        fill=(74, 70, 63, 170),
        spacing=8,
    )
    text_draw.text((width - 84, 32), "Index", fill=(74, 70, 63, 220))
    text_draw.text((32, height - 104), "CURRENT BEND", fill=(74, 70, 63, 148))
    text_draw.text((32, height - 76), "soft drift", fill=(74, 70, 63, 210))
    text_draw.text((176, height - 104), "POOL OPENING", fill=(74, 70, 63, 148))
    text_draw.text((176, height - 76), "0.58", fill=(74, 70, 63, 210))
    text_draw.text((318, height - 104), "FROND CHORUS", fill=(74, 70, 63, 148))
    text_draw.text((318, height - 76), "warm stir", fill=(74, 70, 63, 210))
    text_draw.text(
        (510, height - 86),
        "Move slowly to comb the scaffold. Drag faster to send a warm current through the lower frond bed.",
        fill=(74, 70, 63, 170),
    )
    image.alpha_composite(text)

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
