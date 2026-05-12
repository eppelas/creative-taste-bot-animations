#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def blend(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
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
    for ring in range(10, 0, -1):
        frac = ring / 10
        r = radius * frac
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color + (int(alpha * frac * frac * 0.75),))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius * 0.08)))


def render(output: Path, width: int, height: int) -> None:
    rng = random.Random(18)
    image = Image.new("RGBA", (width, height), (5, 5, 10, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    top = (8, 10, 20)
    bottom = (4, 4, 9)
    for y in range(height):
        t = y / max(1, height - 1)
        draw.line((0, y, width, y), fill=blend(top, bottom, t) + (255,))

    glow(image, (width * 0.32, height * 0.34), width * 0.28, (124, 212, 227), 58)
    glow(image, (width * 0.7, height * 0.52), width * 0.24, (255, 84, 105), 64)
    glow(image, (width * 0.82, height * 0.24), width * 0.16, (143, 128, 255), 48)

    wave_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    wave_draw = ImageDraw.Draw(wave_layer, "RGBA")
    for i in range(11):
        y = height * (0.16 + i * 0.07)
        points = []
        for step in range(44):
            t = step / 43
            x = width * (0.08 + t * 0.74)
            wobble = math.sin(t * 5.6 + i * 0.45) * 24
            wobble += math.cos(t * 12 + i * 0.22) * 8
            points.append((x, y + wobble))
        color = (255, 84, 105, 68) if i % 3 == 0 else (245, 231, 204, 36)
        wave_draw.line(points, fill=color, width=5 if i % 3 == 0 else 3)
    wave_layer = wave_layer.filter(ImageFilter.GaussianBlur(1.4))
    image.alpha_composite(wave_layer)

    ladder_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ladder_draw = ImageDraw.Draw(ladder_layer, "RGBA")
    ladder_x = width * 0.81
    for index in range(3):
        x = ladder_x + index * 18
        y = height * (0.18 + index * 0.16)
        h = height * (0.28 + index * 0.04)
        ladder_draw.rounded_rectangle((x, y, x + 18, y + h), radius=8, outline=(124, 212, 227, 88), width=2)
        for rung in range(7):
            yy = y + h * rung / 6
            rung_color = (245, 231, 204, 72) if rung % 2 == 0 else (255, 84, 105, 88)
            ladder_draw.line((x + 4, yy, x + 14, yy), fill=rung_color, width=2)
    image.alpha_composite(ladder_layer.filter(ImageFilter.GaussianBlur(0.8)))

    field_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    field_draw = ImageDraw.Draw(field_layer, "RGBA")
    columns = 6
    rows = 8
    for cx in range(columns):
        x = width * (0.14 + cx * 0.11)
        for ry in range(rows):
            y = height * (0.16 + ry * 0.09)
            y += math.sin(cx * 0.7 + ry * 0.8) * 12
            radius = 22 + rng.random() * 26
            fill = (245, 231, 204, 70)
            accent = (255, 84, 105, 74) if (cx + ry) % 3 == 0 else (124, 212, 227, 62)
            field_draw.ellipse((x - radius, y - radius * 0.58, x + radius, y + radius * 0.58), fill=fill, outline=accent, width=2)
            field_draw.ellipse((x - radius * 0.28, y - radius * 0.16, x + radius * 0.28, y + radius * 0.16), outline=(245, 231, 204, 96), width=1)
    image.alpha_composite(field_layer.filter(ImageFilter.GaussianBlur(1.2)))

    spores = Image.new("RGBA", image.size, (0, 0, 0, 0))
    spores_draw = ImageDraw.Draw(spores, "RGBA")
    for _ in range(260):
        x = rng.uniform(width * 0.08, width * 0.94)
        y = rng.uniform(height * 0.1, height * 0.92)
        size = rng.uniform(1.0, 3.2)
        color = (255, 84, 105, rng.randint(64, 132)) if rng.random() < 0.48 else (245, 231, 204, rng.randint(48, 120))
        spores_draw.ellipse((x - size, y - size, x + size, y + size), fill=color)
    image.alpha_composite(spores.filter(ImageFilter.GaussianBlur(0.2)))

    hud = Image.new("RGBA", image.size, (0, 0, 0, 0))
    hud_draw = ImageDraw.Draw(hud, "RGBA")
    hud_draw.rounded_rectangle((38, 36, 470, 222), radius=24, fill=(10, 12, 19, 175), outline=(244, 236, 224, 36), width=1)
    hud_draw.rounded_rectangle((782, 36, 1040, 470), radius=24, fill=(10, 12, 19, 175), outline=(244, 236, 224, 36), width=1)
    hud_draw.text((62, 62), "LIVING PATCH CONSOLE", fill=(242, 236, 226, 240))
    hud_draw.text((808, 70), "LAW SWITCHES", fill=(242, 236, 226, 185))
    for group in range(3):
        gy = 138 + group * 90
        for button in range(3):
            bx = 808 + button * 72
            active = (group == 0 and button == 2) or (group == 1 and button == 1) or (group == 2 and button == 0)
            fill = (255, 84, 105, 56) if active else (255, 255, 255, 12)
            outline = (124, 212, 227, 92) if active else (244, 236, 224, 28)
            hud_draw.rounded_rectangle((bx, gy, bx + 58, gy + 48), radius=14, fill=fill, outline=outline, width=2 if active else 1)
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
