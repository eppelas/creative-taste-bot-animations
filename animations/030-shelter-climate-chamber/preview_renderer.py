#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


BG = "#05070b"
INK = "#f0ece3"
CYAN = "#8fe3db"
MINT = "#bbf0bd"
ROSE = "#f4a6bc"
GOLD = "#f4cd88"
VIOLET = "#a7a0ff"
PANEL = (8, 12, 20, 198)
LINE = (211, 234, 236, 44)
MUTED = (240, 236, 227, 170)


def hex_rgba(value: str, alpha: int) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def vertical_gradient(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size)
    draw = ImageDraw.Draw(image)
    top_rgb = hex_rgba(top, 255)
    bottom_rgb = hex_rgba(bottom, 255)
    for y in range(height):
        t = y / max(height - 1, 1)
        color = tuple(int(lerp(top_rgb[i], bottom_rgb[i], t)) for i in range(3)) + (255,)
        draw.line((0, y, width, y), fill=color)
    return image


def radial_glow(size: tuple[int, int], center: tuple[float, float], radius: float, color: str, alpha: int) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for step in range(18, 0, -1):
        t = step / 18
        current_radius = radius * t
        current_alpha = int(alpha * (t**2) * 0.42)
        draw.ellipse(
            (
                center[0] - current_radius,
                center[1] - current_radius,
                center[0] + current_radius,
                center[1] + current_radius,
            ),
            fill=hex_rgba(color, current_alpha),
        )
    return layer.filter(ImageFilter.GaussianBlur(radius * 0.08))


def chamber_point(width: int, height: int, t: float, offset: float) -> tuple[float, float]:
    x = width * (0.16 + t * 0.68) + math.sin(t * 7.4 + offset) * width * 0.06
    y = height * (0.18 + t * 0.62) + math.cos(t * 10.2 + offset * 0.7) * height * 0.028
    return x, y


def draw_shelter(draw: ImageDraw.ImageDraw, x: float, y: float, radius: float, shell: str, accent: str, glow: str) -> None:
    draw.ellipse(
        (x - radius * 0.88, y - radius * 0.66, x + radius * 0.88, y + radius * 0.7),
        fill=hex_rgba(shell, 42),
        outline=hex_rgba(INK, 26),
        width=2,
    )
    draw.ellipse(
        (x - radius * 0.46, y - radius * 0.12, x + radius * 0.46, y + radius * 0.34),
        fill=hex_rgba(glow, 40),
    )
    for index in range(4):
        ring = 0.26 + index * 0.15
        draw.arc(
            (x - radius * (0.72 - ring * 0.12), y - radius * (0.56 - ring * 0.06), x + radius * (0.72 - ring * 0.12), y + radius * (0.48 - ring * 0.05)),
            start=190,
            end=356,
            fill=hex_rgba(accent, 58 - index * 8),
            width=1,
        )
    for dot in range(3):
        angle = dot * 2.1 + radius * 0.01
        ox = x + math.cos(angle) * radius * 0.22
        oy = y + math.sin(angle) * radius * 0.12 + radius * 0.1
        draw.ellipse((ox - radius * 0.07, oy - radius * 0.07, ox + radius * 0.07, oy + radius * 0.07), fill=hex_rgba(glow, 110 - dot * 18))


def draw_anchor(draw: ImageDraw.ImageDraw, x: float, y: float, accent: str, title: str, subtitle: str) -> None:
    box = (x - 86, y - 32, x + 86, y + 32)
    draw.rounded_rectangle(box, radius=16, fill=(6, 10, 18, 192), outline=hex_rgba(accent, 98), width=2)
    draw.text((x - 68, y - 18), title, fill=hex_rgba(accent, 255))
    draw.text((x - 68, y + 2), subtitle, fill=MUTED)


def draw_panel(base: Image.Image, width: int, height: int) -> None:
    panel = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(panel)
    box = (40, 34, min(width - 40, 760), 294)
    draw.rounded_rectangle(box, radius=28, fill=PANEL, outline=LINE, width=2)
    draw.text((64, 58), "CODE ANIMATION STUDY #030", fill=MUTED)
    draw.text((64, 96), "SHELTER CLIMATE CHAMBER", fill=hex_rgba(INK, 255))
    hint = (
        "A living habitat chamber of suspended shelters, climate ribs, and\n"
        "small occupant glows instead of a single figurine or dashboard."
    )
    draw.multiline_text((64, 144), hint, fill=hex_rgba(INK, 230), spacing=8)
    meta = (
        "Pointer warmth bends the nearest shelters. Floating anchors switch\n"
        "the world law: hush, bloom, or tide."
    )
    draw.multiline_text((64, 206), meta, fill=MUTED, spacing=8)
    draw.text((64, 258), "WORLD LAW", fill=MUTED)
    draw.text((168, 258), "hush", fill=hex_rgba(INK, 255))
    draw.text((248, 258), "CLIMATE", fill=MUTED)
    draw.text((334, 258), "0.41", fill=hex_rgba(INK, 255))
    draw.text((410, 258), "OCCUPANCY", fill=MUTED)
    draw.text((520, 258), "63%", fill=hex_rgba(INK, 255))
    base.alpha_composite(panel.filter(ImageFilter.GaussianBlur(0.2)))


def render(output: Path, width: int, height: int) -> None:
    random.seed(30)
    image = vertical_gradient((width, height), "#08101a", BG)

    for center, radius, color, alpha in [
        ((width * 0.18, height * 0.16), width * 0.24, CYAN, 72),
        ((width * 0.82, height * 0.22), width * 0.28, ROSE, 62),
        ((width * 0.56, height * 0.82), width * 0.24, VIOLET, 54),
    ]:
        image = Image.alpha_composite(image, radial_glow((width, height), center, radius, color, alpha))

    draw = ImageDraw.Draw(image)
    for index in range(10):
        y = height * 0.16 + index * (height * 0.08)
        points = []
        for step in range(28):
            x = step / 27 * width
            warp = math.sin(step * 0.42 + index * 0.7) * 8 + math.cos(step * 0.23 + index) * 6
            points.append((x, y + warp))
        draw.line(points, fill=(236, 238, 240, 14), width=1)

    habitat = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(habitat)
    shell_colors = [(CYAN, VIOLET, GOLD), (ROSE, CYAN, GOLD), (VIOLET, ROSE, CYAN)]
    shelter_points: list[tuple[float, float, float, tuple[str, str, str]]] = []

    for index in range(16):
        t = index / 15
        offset = 0.8 + index * 0.37
        x, y = chamber_point(width, height, t, offset)
        radius = 44 + math.sin(index * 0.9) * 8 + (1 - abs(0.5 - t) * 2) * 18
        palette = shell_colors[index % len(shell_colors)]
        shelter_points.append((x, y, radius, palette))
        image = Image.alpha_composite(image, radial_glow((width, height), (x, y), radius * 1.65, palette[2], 74))
        if index % 2 == 0:
            image = Image.alpha_composite(image, radial_glow((width, height), (x + radius * 1.1, y + radius * 0.2), radius * 0.6, palette[1], 52))

    for index, (x, y, radius, palette) in enumerate(shelter_points[:-1]):
        nx, ny, _, _ = shelter_points[index + 1]
        hdraw.line((x, y, nx, ny), fill=hex_rgba(palette[1], 44), width=3)
        hdraw.line((x - radius * 0.1, y - radius * 0.6, x + random.uniform(-18, 18), y + radius * 1.12), fill=hex_rgba(palette[1], 38), width=2)
        hdraw.line((x + radius * 0.08, y - radius * 0.56, x + random.uniform(-22, 22), y + radius * 1.18), fill=hex_rgba(palette[2], 28), width=2)

    habitat = habitat.filter(ImageFilter.GaussianBlur(2.2))
    image = Image.alpha_composite(image, habitat)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for x, y, radius, palette in shelter_points:
      draw_shelter(odraw, x, y, radius, palette[0], palette[1], palette[2])
      if random.random() > 0.45:
          child_x = x + random.uniform(42, 96)
          child_y = y + random.uniform(-18, 26)
          child_r = radius * random.uniform(0.22, 0.34)
          draw_shelter(odraw, child_x, child_y, child_r, palette[1], palette[0], palette[2])

    for index in range(190):
        x = random.uniform(0, width)
        y = random.uniform(0, height)
        r = random.uniform(1.0, 2.8)
        color = (CYAN, ROSE, MINT, VIOLET)[index % 4]
        odraw.ellipse((x - r, y - r, x + r, y + r), fill=hex_rgba(color, 46))
    overlay = overlay.filter(ImageFilter.GaussianBlur(0.4))
    image = Image.alpha_composite(image, overlay)

    anchors = [
        (width * 0.18, height * 0.24, CYAN, "HUSH", "cool shelter"),
        (width * 0.81, height * 0.4, ROSE, "BLOOM", "warm colony"),
        (width * 0.29, height * 0.78, VIOLET, "TIDE", "humid current"),
    ]
    tags = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(tags)
    for x, y, color, title, subtitle in anchors:
        draw_anchor(tdraw, x, y, color, title, subtitle)
    image = Image.alpha_composite(image, tags)

    draw_panel(image, width, height)

    image = image.convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


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
