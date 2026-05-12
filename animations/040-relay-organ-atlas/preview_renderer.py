#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def lerp_color(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / max(1, height - 1)
        draw.line([(0, y), (width, y)], fill=lerp_color(top, bottom, t))
    return image


def glow_ellipse(layer: Image.Image, bbox: tuple[float, float, float, float], color: tuple[int, int, int, int], blur: int) -> None:
    temp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(temp)
    draw.ellipse(bbox, fill=color)
    layer.alpha_composite(temp.filter(ImageFilter.GaussianBlur(blur)))


def rounded_panel(draw: ImageDraw.ImageDraw, bbox: tuple[int, int, int, int], radius: int = 26) -> None:
    draw.rounded_rectangle(bbox, radius=radius, fill=(14, 24, 34, 218), outline=(118, 170, 196, 48), width=1)


def curve_points(points: list[tuple[float, float]], steps: int = 18) -> list[tuple[float, float]]:
    if len(points) < 2:
        return points
    result: list[tuple[float, float]] = [points[0]]
    for idx in range(len(points) - 1):
        p0 = points[idx]
        p1 = points[idx + 1]
        for step in range(1, steps + 1):
            t = step / steps
            x = p0[0] + (p1[0] - p0[0]) * t
            y = p0[1] + (p1[1] - p0[1]) * t
            result.append((x, y))
    return result


def draw_polyline(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill: tuple[int, int, int, int], width: int) -> None:
    draw.line(curve_points(points), fill=fill, width=width, joint="curve")


def render(output: Path, width: int, height: int) -> None:
    image = gradient((width, height), (8, 17, 26), (5, 11, 18)).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))

    glow_ellipse(overlay, (60, 70, 360, 320), (123, 224, 243, 30), 34)
    glow_ellipse(overlay, (760, 90, 1060, 320), (243, 90, 125, 24), 28)
    glow_ellipse(overlay, (340, 870, 760, 1260), (159, 229, 215, 20), 40)

    grid = ImageDraw.Draw(overlay)
    for x in range(60, width - 60, 84):
      grid.line([(x, 30), (x, height - 30)], fill=(255, 255, 255, 10), width=1)
    for y in range(60, height - 40, 84):
      grid.line([(30, y), (width - 30, y)], fill=(255, 255, 255, 9), width=1)

    image.alpha_composite(overlay)
    draw = ImageDraw.Draw(image, "RGBA")

    rounded_panel(draw, (18, 18, 1062, 236), 28)
    rounded_panel(draw, (18, 254, 286, 1038), 28)
    rounded_panel(draw, (304, 254, 776, 1038), 28)
    rounded_panel(draw, (794, 254, 1062, 1038), 28)
    rounded_panel(draw, (18, 1056, 1062, 1332), 28)

    draw.rounded_rectangle((326, 278, 754, 1012), radius=22, fill=(7, 16, 24, 240), outline=(118, 170, 196, 24), width=1)

    for i in range(14):
        band = []
        for j in range(7):
            x = 344 + j * 58
            y = 340 + i * 34 + math.sin(i * 0.36 + j * 0.46) * 8
            band.append((x, y))
        draw_polyline(draw, band, (123, 224, 243, 18 if i % 2 == 0 else 12), 2 if i % 3 == 0 else 1)

    aura = [(540, 370), (456, 438), (430, 618), (540, 872), (650, 618), (624, 438)]
    draw.polygon(aura, fill=(123, 224, 243, 18))
    body = [(540, 386), (470, 448), (448, 610), (540, 836), (632, 610), (610, 448)]
    inner = [(540, 438), (492, 500), (484, 634), (540, 770), (596, 634), (588, 500)]
    draw.polygon(body, fill=(255, 255, 255, 14), outline=(210, 230, 240, 82))
    draw.polygon(inner, fill=(255, 255, 255, 10), outline=(159, 229, 215, 42))

    draw_polyline(draw, [(512, 430), (468, 370), (406, 320), (364, 286)], (123, 224, 243, 200), 3)
    draw_polyline(draw, [(568, 430), (612, 372), (676, 320), (718, 288)], (245, 141, 128, 200), 3)
    draw_polyline(draw, [(502, 792), (454, 880), (376, 954), (298, 1000)], (159, 229, 215, 210), 5)
    draw_polyline(draw, [(578, 792), (626, 880), (704, 954), (782, 1000)], (159, 229, 215, 210), 5)
    draw_polyline(draw, [(474, 496), (520, 560), (574, 658), (596, 748)], (123, 224, 243, 226), 4)
    draw_polyline(draw, [(606, 488), (560, 566), (506, 670), (482, 754)], (240, 210, 125, 220), 4)
    draw_polyline(draw, [(540, 454), (560, 560), (548, 656), (540, 740)], (243, 90, 125, 190), 3)

    glow_ellipse(image, (456, 520, 624, 654), (123, 224, 243, 90), 20)
    glow_ellipse(image, (478, 540, 602, 642), (245, 141, 128, 54), 16)
    draw.ellipse((476, 534, 604, 646), outline=(220, 231, 239, 90), width=2)
    draw.ellipse((514, 566, 566, 598), fill=(255, 255, 255, 18), outline=(220, 231, 239, 120), width=1)
    draw.ellipse((502, 575, 514, 587), fill=(123, 224, 243, 255))
    draw.ellipse((536, 582, 550, 596), fill=(240, 210, 125, 255))
    draw.ellipse((570, 575, 582, 587), fill=(245, 141, 128, 255))

    draw.text((40, 42), "ANIMATION 040 / RELAY ORGAN ATLAS", fill=(220, 231, 239, 180))
    draw.text((40, 84), "Believable signal anatomy as a real page", fill=(238, 244, 247, 240))
    draw.text((40, 128), "A darker multi-pane relay atlas with one grounded body,", fill=(206, 220, 228, 188))
    draw.text((40, 150), "local pressure weather, and page-like interface logic.", fill=(206, 220, 228, 188))

    draw.text((42, 280), "ATLAS COLUMNS", fill=(220, 231, 239, 164))
    left_notes = [
        "Upper probes scan turbulence first.",
        "Relay torso carries the current lanes.",
        "Root braces widen under stress.",
    ]
    for idx, note in enumerate(left_notes):
        top = 326 + idx * 124
        draw.rounded_rectangle((36, top, 268, top + 94), radius=18, fill=(17, 28, 38, 236), outline=(118, 170, 196, 34), width=1)
        draw.text((50, top + 16), note, fill=(214, 224, 232, 196))

    draw.text((812, 280), "SUPPORT METERS", fill=(220, 231, 239, 164))
    labels = [("L arch", 0.58), ("Core", 0.74), ("R arch", 0.61)]
    for idx, (label, val) in enumerate(labels):
        y = 342 + idx * 92
        draw.text((812, y), label.upper(), fill=(214, 224, 232, 176))
        draw.rounded_rectangle((812, y + 28, 1030, y + 42), radius=7, fill=(255, 255, 255, 18))
        draw.rounded_rectangle((812, y + 28, 812 + int(218 * val), y + 42), radius=7, fill=(123, 224, 243, 220))
        draw.text((996, y), f"{int(val * 100)}%", fill=(214, 224, 232, 190))

    draw.text((40, 1082), "EMBEDDED REVIEW HINTS", fill=(220, 231, 239, 164))
    draw.text((40, 1122), "Check the stance first: stable lower braces, local refraction,", fill=(206, 220, 228, 188))
    draw.text((40, 1144), "and motion that stays inside the same body.", fill=(206, 220, 228, 188))

    footer = [("Believability", "0.78"), ("Refraction", "0.42"), ("Stress", "0.36"), ("Drift", "Brace / local")]
    for idx, (title, value) in enumerate(footer):
        x0 = 40 + idx * 254
        draw.rounded_rectangle((x0, 1188, x0 + 230, 1306), radius=18, fill=(17, 28, 38, 236), outline=(118, 170, 196, 34), width=1)
        draw.text((x0 + 16, 1204), title.upper(), fill=(220, 231, 239, 164))
        draw.text((x0 + 16, 1246), value, fill=(238, 244, 247, 232))

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()
    render(args.output, args.width, args.height)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
