#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


TAU = math.pi * 2.0


MOOD = {
    "attention": 0.66,
    "warmth": 0.62,
    "tension": 0.86,
    "hue_a": (239, 210, 166),
    "hue_b": (225, 86, 103),
    "hue_c": (139, 196, 197),
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def add_glow(base: Image.Image, center: tuple[float, float], radius: float, color: tuple[int, int, int], alpha: int) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, alpha))
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius * 0.16)))


def draw_background(image: Image.Image) -> None:
    width, height = image.size
    px = image.load()
    for y in range(height):
      t = y / max(height - 1, 1)
      r = int(22 - t * 12)
      g = int(14 - t * 8)
      b = int(16 - t * 9)
      for x in range(width):
          px[x, y] = (r, g, b, 255)

    add_glow(image, (width * 0.18, height * 0.18), width * 0.18, (244, 215, 154), 20)
    add_glow(image, (width * 0.74, height * 0.76), width * 0.22, (142, 183, 188), 20)
    add_glow(image, (width * 0.52, height * 0.54), width * 0.36, (54, 22, 33), 90)

    draw = ImageDraw.Draw(image, "RGBA")
    for i in range(28):
        y = (i / 27) * height
        sway = math.sin(i * 0.42) * 12
        draw.line(
            (
                0,
                y + sway,
                width * 0.22,
                y - sway,
                width * 0.68,
                y + sway,
                width,
                y - sway * 0.3,
            ),
            fill=(255, 238, 216, 10 + (i % 4) * 2),
            width=1,
            joint="curve",
        )


def blob_points(cx: float, cy: float, radius: float, t: float) -> list[tuple[float, float]]:
    points = []
    target_angle = -0.52
    for i in range(85):
        angle = (i / 84) * TAU
        base = radius * (0.92 + math.sin(angle * 3 + t * 0.8) * 0.05)
        wobble = math.sin(angle * 5 - t * 1.1) * radius * 0.08 + math.cos(angle * 2 + t * 0.6) * radius * 0.04
        pointer_bias = math.cos(angle - target_angle) * radius * 0.12
        r = base + wobble + pointer_bias
        x = cx + math.cos(angle) * r
        y = cy + math.sin(angle) * r * 0.86
        points.append((x, y))
    return points


def draw_orbits(draw: ImageDraw.ImageDraw, cx: float, cy: float, radius: float, t: float) -> None:
    for i in range(8):
        ring = []
        ring_r = radius * (1.1 + i * 0.15)
        for step in range(89):
            angle = (step / 88) * TAU
            wave = math.sin(angle * (2 + i * 0.18) + t * (0.7 + i * 0.08)) * radius * 0.022
            pulse = math.cos(angle * 3 - t * 0.5 + i) * radius * 0.015
            x = cx + math.cos(angle) * (ring_r + wave + pulse)
            y = cy + math.sin(angle) * (ring_r * 0.72 + wave * 0.9)
            ring.append((x, y))
        draw.line(ring, fill=(255, 238, 216, max(8, 16 - i * 2)), width=1)


def draw_creature(image: Image.Image) -> None:
    width, height = image.size
    cx = width * 0.49
    cy = height * 0.54
    radius = min(width, height) * 0.17
    t = 3.8

    draw = ImageDraw.Draw(image, "RGBA")
    draw_orbits(draw, cx, cy, radius, t)

    points = blob_points(cx, cy, radius, t)
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)

    shell = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shell_draw = ImageDraw.Draw(shell, "RGBA")
    shell_draw.polygon(points, fill=(*MOOD["hue_b"], 240))
    add_glow(shell, (cx - radius * 0.2, cy - radius * 0.24), radius * 0.84, MOOD["hue_a"], 175)
    add_glow(shell, (cx + radius * 0.3, cy + radius * 0.18), radius * 0.78, MOOD["hue_c"], 84)

    lines = Image.new("RGBA", image.size, (0, 0, 0, 0))
    line_draw = ImageDraw.Draw(lines, "RGBA")
    for i in range(22):
        lane_y = cy - radius * 0.7 + (i / 21) * radius * 1.5
        amp = radius * (0.03 + (i % 5) * 0.008)
        lane = []
        for step in range(24):
            p = step / 23
            x = cx - radius * 1.1 + p * radius * 2.2
            y = lerp(
                lane_y,
                lane_y + math.sin(t + i + p * 3.4) * amp - math.cos(t * 0.8 + i * 0.4 + p * 2.1) * amp * 0.9,
                0.8,
            )
            lane.append((x, y))
        line_draw.line(lane, fill=(255, 248, 231, 14 + (i % 3) * 5), width=1)

    for i in range(140):
        seed = i * 12.9898
        px = cx + math.sin(seed) * radius * 0.8 + math.cos(t * 0.3 + seed) * radius * 0.08
        py = cy + math.cos(seed * 0.73) * radius * 0.56 + math.sin(t * 0.4 + seed) * radius * 0.08
        size = 1 + ((i * 7) % 3)
        color = (255, 245, 228, 86) if i % 5 == 0 else (54, 20, 31, 58)
        line_draw.rectangle((px, py, px + size, py + size), fill=color)

    shell.alpha_composite(lines)
    shell.putalpha(mask)
    image.alpha_composite(shell)

    draw = ImageDraw.Draw(image, "RGBA")
    draw.line(points + [points[0]], fill=(255, 238, 216, 56), width=2)

    draw_face(draw, cx, cy, radius)
    draw_tendrils(draw, cx, cy, radius, t)


def draw_face(draw: ImageDraw.ImageDraw, cx: float, cy: float, radius: float) -> None:
    eye_y = cy - radius * 0.08
    eye_offset_x = radius * 0.32
    eye_open = radius * 0.15
    pupil_shift = radius * 0.024

    for side in (-1, 1):
        x = cx + side * eye_offset_x
        draw.ellipse((x - radius * 0.14, eye_y - eye_open, x + radius * 0.14, eye_y + eye_open), fill=(253, 246, 232, 245))
        draw.ellipse((x + pupil_shift - radius * 0.048, eye_y - radius * 0.048, x + pupil_shift + radius * 0.048, eye_y + radius * 0.048), fill=(38, 14, 18, 230))
        draw.ellipse((cx + side * radius * 0.09, cy + radius * 0.115, cx + side * radius * 0.31, cy + radius * 0.185), fill=(72, 20, 30, 34))
        draw.ellipse((x + side * radius * 0.16 - radius * 0.12, cy + radius * 0.02, x + side * radius * 0.16 + radius * 0.12, cy + radius * 0.14), fill=(241, 128, 145, 46))

    mouth = []
    for i in range(32):
        p = i / 31
        angle = math.pi * (0.18 + p * 0.64)
        x = cx + math.cos(angle) * radius * 0.18
        y = cy + radius * 0.15 + math.sin(angle) * radius * 0.14
        mouth.append((x, y))
    draw.line(mouth, fill=(214, 106, 122, 180), width=max(2, int(radius * 0.03)))


def draw_tendrils(draw: ImageDraw.ImageDraw, cx: float, cy: float, radius: float, t: float) -> None:
    count = 10
    for i in range(count):
        angle = -math.pi * 0.95 + (i / (count - 1)) * math.pi * 1.9
        start_x = cx + math.cos(angle) * radius * 0.84
        start_y = cy + math.sin(angle) * radius * 0.58
        reach = radius * (0.45 + (i % 3) * 0.08 + MOOD["tension"] * 0.22)
        drift = math.sin(t * (0.8 + i * 0.08) + i) * radius * 0.08
        fill = (142, 183, 188, 54) if i % 2 == 0 else (255, 231, 198, 38)
        points = []
        for step in range(18):
            p = step / 17
            x = lerp(start_x, start_x + math.cos(angle) * reach * 1.2, p)
            y = lerp(start_y, start_y + math.sin(angle) * reach * 1.1, p)
            x += math.sin(p * math.pi) * math.cos(angle - 0.15) * reach * 0.18
            y += math.sin(p * math.pi) * drift * 0.6
            points.append((x, y))
        draw.line(points, fill=fill, width=2)
        if i % 2 == 0:
            x, y = points[-3]
            draw.rectangle((x - 3, y - 3, x + 3, y + 3), fill=(255, 244, 224, 70))


def draw_rail(image: Image.Image) -> None:
    width, height = image.size
    draw = ImageDraw.Draw(image, "RGBA")

    for i in range(9):
        y = height * 0.18 + i * 40
        pulse = 0.4 + math.sin(3.6 + i) * 0.25
        alpha = int((0.08 + pulse * 0.05) * 255)
        draw.line((width - 108, y, width - 60, y), fill=(255, 238, 216, alpha), width=1)
        draw.rectangle((width - 88, y - 4, width - 80, y + 4), fill=(207, 79, 102, int((0.18 + pulse * 0.14) * 255)))

    panel_left = width - 312
    panel_top = 86
    panel_right = width - 34
    panel_bottom = height - 86
    draw.rounded_rectangle((panel_left, panel_top, panel_right, panel_bottom), radius=22, outline=(255, 236, 213, 34), fill=(28, 18, 22, 136), width=1)

    card_y = panel_top + 20
    cards = [
        ("Bashful Drift", False),
        ("Alert Bloom", False),
        ("Sour Theater", False),
        ("Feral Lilt", True),
    ]
    for label, active in cards:
        draw.rounded_rectangle(
            (panel_left + 14, card_y, panel_right - 14, card_y + 74),
            radius=16,
            outline=(244, 215, 154, 74 if active else 30),
            fill=(255, 255, 255, 10),
            width=1,
        )
        draw.text((panel_left + 28, card_y + 18), label, fill=(249, 240, 223, 220))
        draw.text((panel_left + 28, card_y + 42), "Visible emotional hardware", fill=(249, 240, 223, 122))
        card_y += 86

    meter_top = panel_top + 388
    meters = [("Attention", 0.66), ("Warmth", 0.62), ("Tension", 0.86)]
    for label, value in meters:
        draw.text((panel_left + 20, meter_top), label.upper(), fill=(249, 240, 223, 118))
        draw.text((panel_right - 72, meter_top), f"{value:.2f}", fill=(249, 240, 223, 140))
        draw.rounded_rectangle((panel_left + 20, meter_top + 24, panel_right - 20, meter_top + 34), radius=999, fill=(255, 255, 255, 16))
        fill_right = panel_left + 20 + (panel_right - panel_left - 40) * value
        draw.rounded_rectangle((panel_left + 20, meter_top + 24, fill_right, meter_top + 34), radius=999, fill=(225, 86, 103, 188))
        meter_top += 72


def render(output: Path, width: int, height: int) -> None:
    image = Image.new("RGBA", (width, height), (20, 13, 15, 255))
    draw_background(image)
    draw_creature(image)
    draw_rail(image)
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
