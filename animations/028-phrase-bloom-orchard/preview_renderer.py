#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


PALETTE = {
    "bg_top": "#0d1119",
    "bg_bottom": "#06070c",
    "text": "#f4eee4",
    "muted": "#beb7ae",
    "rose": "#f6a7bc",
    "cyan": "#88d9e1",
    "mint": "#b6e2bc",
    "gold": "#f2c979",
    "violet": "#a69dff",
}


def hex_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def vertical_gradient(width: int, height: int, top: str, bottom: str) -> Image.Image:
    image = Image.new("RGBA", (width, height))
    top_rgb = hex_rgba(top)
    bottom_rgb = hex_rgba(bottom)
    pixels = image.load()
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(int(top_rgb[i] * (1 - t) + bottom_rgb[i] * t) for i in range(4))
        for x in range(width):
            pixels[x, y] = color
    return image


def draw_glow(base: Image.Image, center: tuple[float, float], radius: float, color: str, alpha: int) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=hex_rgba(color, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=max(8, int(radius * 0.3))))
    base.alpha_composite(layer)


def draw_organism(base: Image.Image, center: tuple[float, float], scale: float, colors: tuple[str, str, str]) -> None:
    draw = ImageDraw.Draw(base, "RGBA")
    x, y = center
    body_w = 78 * scale
    body_h = 108 * scale
    trunk_h = 170 * scale

    draw.line(
        ((x, y + body_h * 0.45), (x - 18 * scale, y - trunk_h * 0.36), (x + 8 * scale, y - trunk_h)),
        fill=hex_rgba("#fff3e5", 66),
        width=max(4, int(10 * scale)),
        joint="curve",
    )

    draw_glow(base, (x, y - trunk_h), 86 * scale, colors[2], 54)
    draw_glow(base, (x, y - trunk_h), 54 * scale, colors[0], 88)

    draw.ellipse(
        (x - body_w, y - trunk_h - body_h, x + body_w, y - trunk_h + body_h * 0.22),
        fill=hex_rgba(colors[0], 176),
        outline=hex_rgba("#ffffff", 52),
        width=2,
    )

    for offset in (-0.42, -0.16, 0.12, 0.4):
        y_line = y - trunk_h - body_h * 0.4 + body_h * (offset + 0.5)
        draw.arc(
            (x - body_w * 0.68, y_line - body_h * 0.18, x + body_w * 0.68, y_line + body_h * 0.18),
            start=188,
            end=352,
            fill=hex_rgba("#ffffff", 58),
            width=2,
        )

    orbit_data = [
        (-124, -20, 18, colors[1]),
        (112, 10, 16, colors[2]),
        (-88, 48, 13, colors[1]),
        (124, -56, 14, colors[0]),
        (8, 94, 11, colors[2]),
    ]
    for ox, oy, r, color in orbit_data:
        draw.line((x, y - trunk_h, x + ox * scale, y - trunk_h + oy * scale), fill=hex_rgba(color, 74), width=1)
        draw.ellipse(
            (x + (ox - r) * scale, y - trunk_h + (oy - r) * scale, x + (ox + r) * scale, y - trunk_h + (oy + r) * scale),
            fill=hex_rgba(color, 188),
        )

    for angle in range(0, 360, 18):
        import math

        rx = x + math.cos(math.radians(angle)) * 140 * scale
        ry = y - trunk_h + math.sin(math.radians(angle)) * 70 * scale
        draw.ellipse((rx - 3, ry - 3, rx + 3, ry + 3), fill=hex_rgba(colors[2], 220))


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a static preview for Phrase Bloom Orchard.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    image = vertical_gradient(args.width, args.height, PALETTE["bg_top"], PALETTE["bg_bottom"])

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw.rounded_rectangle((40, 40, 510, 430), radius=32, fill=(12, 15, 24, 196), outline=(255, 255, 255, 28), width=1)
    draw.rounded_rectangle((580, 1090, 1040, 1285), radius=28, fill=(12, 15, 24, 196), outline=(255, 255, 255, 28), width=1)

    draw.text((72, 78), "Code Animation Study #028", fill=hex_rgba(PALETTE["muted"], 255))
    draw.text((72, 120), "Phrase Bloom", fill=hex_rgba(PALETTE["text"], 255))
    draw.text((72, 164), "Orchard", fill=hex_rgba(PALETTE["text"], 255))
    draw.text((72, 222), "Each sentence grows one suspended organism", fill=hex_rgba(PALETTE["muted"], 255))
    draw.text((72, 252), "with a spine, buds, and a seed halo.", fill=hex_rgba(PALETTE["muted"], 255))
    draw.text((72, 314), "A shy idea hangs low and keeps a warm shell around it.", fill=hex_rgba(PALETTE["text"], 255))
    draw.text((72, 344), "One brighter sentence sends cyan spores upward.", fill=hex_rgba(PALETTE["text"], 255))

    draw.text((612, 1124), "ORGANISMS", fill=hex_rgba(PALETTE["muted"], 255))
    draw.text((612, 1152), "4", fill=hex_rgba(PALETTE["text"], 255))
    draw.text((730, 1124), "NOVELTY", fill=hex_rgba(PALETTE["muted"], 255))
    draw.text((730, 1152), "0.61", fill=hex_rgba(PALETTE["text"], 255))
    draw.text((612, 1208), "CANOPY", fill=hex_rgba(PALETTE["muted"], 255))
    draw.text((612, 1236), "warm hush", fill=hex_rgba(PALETTE["text"], 255))
    draw.text((770, 1208), "FIELD", fill=hex_rgba(PALETTE["muted"], 255))
    draw.text((770, 1236), "soft wake", fill=hex_rgba(PALETTE["text"], 255))

    image.alpha_composite(overlay)

    draw_glow(image, (260, 190), 180, PALETTE["cyan"], 30)
    draw_glow(image, (850, 170), 210, PALETTE["rose"], 24)
    draw_glow(image, (630, 1180), 180, PALETTE["violet"], 20)

    draw_organism(image, (580, 940), 1.05, (PALETTE["cyan"], PALETTE["mint"], PALETTE["gold"]))
    draw_organism(image, (340, 1110), 0.8, (PALETTE["rose"], PALETTE["violet"], PALETTE["cyan"]))
    draw_organism(image, (820, 760), 0.74, (PALETTE["mint"], PALETTE["gold"], PALETTE["rose"]))
    draw_organism(image, (880, 1000), 0.58, (PALETTE["violet"], PALETTE["cyan"], PALETTE["rose"]))

    final = image.convert("RGB")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    final.save(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
