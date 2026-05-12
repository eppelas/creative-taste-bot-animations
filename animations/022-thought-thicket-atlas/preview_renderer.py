#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


TAU = math.pi * 2.0


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(lerp(x, y, t)) for x, y in zip(a, b))


def add_glow(base: Image.Image, center: tuple[float, float], radius: float, color: tuple[int, int, int], alpha: int) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    for ring in range(12, 0, -1):
        frac = ring / 12
        rr = radius * frac
        draw.ellipse((x - rr, y - rr, x + rr, y + rr), fill=color + (int(alpha * frac * frac * 0.86),))
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius * 0.12)))


def draw_background(image: Image.Image) -> None:
    width, height = image.size
    draw = ImageDraw.Draw(image, "RGBA")

    top = (24, 26, 24)
    middle = (16, 17, 17)
    bottom = (9, 10, 10)
    for y in range(height):
        t = y / max(height - 1, 1)
        color = mix(mix(top, middle, min(1, t * 1.2)), bottom, max(0, (t - 0.44) / 0.56))
        draw.line((0, y, width, y), fill=color + (255,))

    add_glow(image, (width * 0.24, height * 0.16), width * 0.18, (240, 200, 108), 34)
    add_glow(image, (width * 0.72, height * 0.18), width * 0.18, (138, 213, 209), 30)
    add_glow(image, (width * 0.54, height * 0.68), width * 0.28, (215, 131, 158), 32)

    for row in range(1, 11):
        y = height * (row / 11) + math.sin(row * 0.7) * 6
        draw.line((width * 0.08, y, width * 0.92, y), fill=(241, 234, 220, 12), width=1)


def draw_connectors(image: Image.Image, groves: list[dict[str, float]]) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    for index in range(len(groves) - 1):
        a = groves[index]
        b = groves[index + 1]
        mid_y = min(a["y"], b["y"]) - image.size[1] * 0.09
        draw.line(
            (
                a["x"],
                a["y"] - a["radius"] * 0.2,
                a["x"],
                mid_y,
                b["x"],
                mid_y,
                b["x"],
                b["y"] - b["radius"] * 0.2,
            ),
            fill=(138, 213, 209, 64 if index % 2 == 0 else 44),
            width=2,
            joint="curve",
        )
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.6)))


def draw_grove(image: Image.Image, groove: dict[str, float], rng: random.Random) -> None:
    width, height = image.size
    x = groove["x"]
    y = groove["y"]
    radius = groove["radius"]

    add_glow(image, (x, y), radius * 1.24, (158, 216, 187), 38)
    add_glow(image, (x + radius * 0.18, y - radius * 0.1), radius * 0.92, (215, 131, 158), 28)

    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")

    for root in range(4):
        offset = (root / 3 - 0.5) * radius * 0.7
        draw.line(
            (
                x + offset,
                y + radius * 0.16,
                x + offset * 0.7,
                y + radius * 0.4,
                x + offset * 1.18,
                y + radius * 0.78,
                x + offset * 1.4,
                y + groove["root_depth"],
            ),
            fill=(241, 143, 88, 56),
            width=2,
            joint="curve",
        )

    for stem in range(int(groove["stems"])):
        t = stem / max(1, groove["stems"] - 1)
        sx = x + (t - 0.5) * radius * 1.24
        top_x = sx + math.sin(groove["sway"] + stem * 0.7) * radius * 0.16
        top_y = y - groove["height"] * lerp(0.7, 1.04, t)
        draw.line(
            (sx, y + radius * 0.14, sx + (top_x - sx) * 0.28, y - radius * 0.18, top_x, top_y),
            fill=(241, 234, 220, 84),
            width=2,
            joint="curve",
        )

    for rung in range(4):
        ladder_width = radius * lerp(0.32, 0.62, rung / 3)
        yy = y - radius * 0.1 - rung * radius * 0.18
        shift = math.sin(groove["phase"] + rung) * radius * 0.08
        draw.arc(
            (x - ladder_width + shift, yy - radius * 0.1, x + ladder_width + shift, yy + radius * 0.1),
            190,
            350,
            fill=(138, 213, 209, 88),
            width=2,
        )

    for blob in range(int(groove["satellites"])):
        angle = groove["phase"] + (blob / groove["satellites"]) * TAU
        orbit = radius * lerp(0.46, 1.08, (blob % 3) / 2 + 0.18)
        bx = x + math.cos(angle) * orbit
        by = y - radius * 0.18 + math.sin(angle * 1.4) * orbit * 0.46
        brx = radius * lerp(0.08, 0.2, rng.random())
        bry = brx * lerp(0.68, 0.94, rng.random())
        color = (158, 216, 187, 78) if blob % 2 == 0 else (240, 200, 108, 70)
        draw.ellipse((bx - brx, by - bry, bx + brx, by + bry), fill=color)

    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.5)))


def draw_pollen(image: Image.Image, groves: list[dict[str, float]], rng: random.Random) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    for groove in groves:
        for _ in range(int(groove["pollen"])):
            angle = rng.random() * TAU
            orbit = groove["radius"] * lerp(0.9, 2.1, rng.random())
            px = groove["x"] + math.cos(angle) * orbit
            py = groove["y"] - groove["radius"] * 0.34 - math.sin(angle * 1.7) * orbit * 0.28 - orbit * lerp(0.12, 0.44, rng.random())
            size = lerp(1.2, 4.2, rng.random() * rng.random())
            color = (240, 200, 108, rng.randint(44, 88)) if rng.random() > 0.5 else (138, 213, 209, rng.randint(40, 80))
            draw.ellipse((px - size, py - size, px + size, py + size), fill=color)
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.35)))


def draw_panels(image: Image.Image) -> None:
    width, height = image.size
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")

    draw.rounded_rectangle((18, 18, min(width * 0.48, 500), 308), radius=28, fill=(18, 20, 19, 210), outline=(241, 234, 220, 30), width=2)
    draw.rounded_rectangle((width - 116, 18, width - 18, 66), radius=24, fill=(18, 20, 19, 214), outline=(241, 234, 220, 26), width=2)
    draw.rounded_rectangle((18, height - 152, width - 18, height - 18), radius=20, fill=(18, 20, 19, 214), outline=(241, 234, 220, 28), width=2)
    draw.rounded_rectangle((36, 156, min(width * 0.42, 468), 272), radius=18, fill=(255, 255, 255, 10), outline=(241, 234, 220, 20), width=1)

    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.45)))

    text = Image.new("RGBA", image.size, (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(text)
    tdraw.text((36, 36), "CODE ANIMATION STUDY #022", fill=(241, 234, 220, 132))
    tdraw.text((36, 68), "Thought Thicket", fill=(241, 234, 220, 236))
    tdraw.text((36, 116), "Atlas", fill=(241, 234, 220, 236))
    tdraw.text(
        (36, 294),
        "Each sentence becomes one grove instead of one blade of grass.",
        fill=(241, 234, 220, 156),
    )
    tdraw.text((width - 84, 33), "Index", fill=(241, 234, 220, 220))

    tdraw.text((52, 170), "The first idea hides under a mineral canopy.", fill=(241, 234, 220, 212))
    tdraw.text((52, 194), "One late phrase arrives as a warmer bush.", fill=(241, 234, 220, 196))
    tdraw.text((52, 218), "An uncertain note makes a narrow ladder.", fill=(241, 234, 220, 196))
    tdraw.text((52, 242), "The loudest thought keeps branching.", fill=(241, 234, 220, 196))

    tdraw.text((34, height - 118), "GROVE COUNT", fill=(241, 234, 220, 126))
    tdraw.text((34, height - 88), "4", fill=(241, 234, 220, 228))
    tdraw.text((178, height - 118), "NOVELTY", fill=(241, 234, 220, 126))
    tdraw.text((178, height - 88), "0.62", fill=(241, 234, 220, 228))
    tdraw.text((332, height - 118), "PRESSURE BEND", fill=(241, 234, 220, 126))
    tdraw.text((332, height - 88), "field comb", fill=(241, 234, 220, 228))
    tdraw.text((532, height - 118), "MOOD DRIFT", fill=(241, 234, 220, 126))
    tdraw.text((532, height - 88), "warm hush", fill=(241, 234, 220, 228))
    tdraw.text(
        (710, height - 94),
        "Longer thoughts stretch the lattice into taller canopies and brighter upper pollen.",
        fill=(241, 234, 220, 156),
    )
    image.alpha_composite(text)


def render(output: Path, width: int, height: int) -> None:
    rng = random.Random(22)
    image = Image.new("RGBA", (width, height), (15, 16, 16, 255))
    draw_background(image)

    groves = [
        {"x": width * 0.18, "y": height * 0.7, "radius": width * 0.082, "stems": 6, "satellites": 6, "pollen": 15, "root_depth": height * 0.16, "height": height * 0.12, "phase": 0.4, "sway": 0.8},
        {"x": width * 0.38, "y": height * 0.58, "radius": width * 0.096, "stems": 8, "satellites": 8, "pollen": 18, "root_depth": height * 0.14, "height": height * 0.15, "phase": 1.2, "sway": 1.4},
        {"x": width * 0.62, "y": height * 0.48, "radius": width * 0.11, "stems": 10, "satellites": 9, "pollen": 24, "root_depth": height * 0.12, "height": height * 0.18, "phase": 2.3, "sway": 2.0},
        {"x": width * 0.8, "y": height * 0.66, "radius": width * 0.088, "stems": 7, "satellites": 7, "pollen": 16, "root_depth": height * 0.15, "height": height * 0.13, "phase": 3.1, "sway": 2.7},
    ]

    draw_connectors(image, groves)
    for groove in groves:
        draw_grove(image, groove, rng)
    draw_pollen(image, groves, rng)
    draw_panels(image)

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
