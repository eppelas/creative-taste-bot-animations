#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


PALETTE = {
    "top": (245, 239, 230),
    "mid": (233, 224, 212),
    "bottom": (223, 212, 197),
    "ink": (32, 34, 39),
    "muted": (92, 92, 96),
    "cyan": (140, 182, 199),
    "sage": (152, 181, 158),
    "sand": (210, 180, 142),
    "rust": (204, 143, 115),
    "white": (255, 255, 255),
}


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def blend(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(lerp(a[i], b[i], t)) for i in range(3))


def add_gradient(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    for y in range(height):
        t = y / max(1, height - 1)
        if t < 0.5:
            color = blend(PALETTE["top"], PALETTE["mid"], t / 0.5)
        else:
            color = blend(PALETTE["mid"], PALETTE["bottom"], (t - 0.5) / 0.5)
        draw.line((0, y, width, y), fill=color)


def glow(base: Image.Image, center: tuple[float, float], radius: float, color: tuple[int, int, int, int], blur: float) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=blur))
    base.alpha_composite(layer)


def catmull(points: list[tuple[float, float]], t: float) -> tuple[float, float]:
    scaled = t * (len(points) - 1)
    index = min(len(points) - 2, int(scaled))
    local = scaled - index
    p0 = points[max(0, index - 1)]
    p1 = points[index]
    p2 = points[min(len(points) - 1, index + 1)]
    p3 = points[min(len(points) - 1, index + 2)]
    x = 0.5 * (
        (2 * p1[0])
        + (-p0[0] + p2[0]) * local
        + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * local * local
        + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * local * local * local
    )
    y = 0.5 * (
        (2 * p1[1])
        + (-p0[1] + p2[1]) * local
        + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * local * local
        + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * local * local * local
    )
    return x, y


def build_route(width: int, height: int) -> list[tuple[float, float]]:
    points = [
        (width * 0.18, height * 0.76),
        (width * 0.38, height * 0.46),
        (width * 0.62, height * 0.63),
        (width * 0.84, height * 0.32),
    ]
    return [catmull(points, i / 139) for i in range(140)]


def draw_fog(base: Image.Image, width: int, height: int) -> None:
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for band in range(10):
        y = height * (0.16 + band * 0.067)
        points = []
        for step in range(-3, 42):
            x = width * (step / 38)
            wave = math.sin(step * 0.65 + band * 0.8) * (18 + band * 2.4)
            points.append((x, y + wave))
        points.extend([(width + 120, y + 90), (-120, y + 90)])
        draw.polygon(points, fill=(255, 255, 255, 18 + band * 2))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=18))
    base.alpha_composite(layer)


def draw_ground(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    for y in range(int(height * 0.56), height, 46):
        draw.line((0, y, width, y - 18), fill=(54, 55, 60, 18), width=1)
    for x in range(0, width, 106):
        draw.line((x, height * 0.56, x + 90, height), fill=(54, 55, 60, 18), width=1)

    masses = [
        (0.08, 0.79, 0.26, 0.15, PALETTE["sage"]),
        (0.33, 0.73, 0.18, 0.11, PALETTE["sand"]),
        (0.68, 0.7, 0.24, 0.13, PALETTE["sage"]),
    ]
    for x, y, w, h, color in masses:
        box = (width * x, height * y, width * (x + w), height * (y + h))
        draw.rounded_rectangle(box, radius=34, fill=color + (44,), outline=(255, 255, 255, 48), width=1)


def draw_route(base: Image.Image, route: list[tuple[float, float]], width: int, height: int) -> None:
    draw = ImageDraw.Draw(base)
    for offset, alpha, w in [(-10, 54, 2), (0, 132, 3), (10, 44, 2)]:
        shifted = [(x, y + offset) for x, y in route]
        draw.line(shifted, fill=PALETTE["ink"] + (alpha,), width=w, joint="curve")

    for idx in range(10, len(route) - 10, 8):
        x, y = route[idx]
        draw.line((x, y + 10, x, height * 0.9), fill=PALETTE["ink"] + (42,), width=1)

    for idx in [0, 32, 72, 104, len(route) - 1]:
        x, y = route[idx]
        draw.line((x, y + 12, x, y - 30), fill=PALETTE["ink"] + (100,), width=2)
        draw.line((x - 10, y - 16, x, y - 30), fill=PALETTE["ink"] + (100,), width=2)
        draw.line((x + 10, y - 16, x, y - 30), fill=PALETTE["ink"] + (100,), width=2)
        draw.ellipse((x - 4, y - 38, x + 4, y - 30), fill=PALETTE["rust"] + (220,))

    for idx in range(18, len(route) - 18, 22):
        x, y = route[idx]
        width_local = 10 + (idx % 3) * 5
        height_local = 34 + (idx % 2) * 18
        shape = Image.new("RGBA", base.size, (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(shape)
        sdraw.polygon(
            [
                (x - width_local * 0.42, y + 18),
                (x - width_local * 0.2, y + 18 + height_local),
                (x + width_local * 0.2, y + 18 + height_local),
                (x + width_local * 0.42, y + 18),
            ],
            fill=(255, 255, 255, 60),
            outline=PALETTE["cyan"] + (34,),
        )
        shape = shape.filter(ImageFilter.GaussianBlur(radius=1.2))
        base.alpha_composite(shape)


def draw_particles(draw: ImageDraw.ImageDraw, route: list[tuple[float, float]]) -> None:
    for idx in range(0, 180):
        t = ((idx * 0.071) % 1.0)
        sample = route[int(t * (len(route) - 1))]
        offset = math.sin(idx * 0.7) * 8
        x = sample[0] + offset
        y = sample[1] + math.cos(idx * 0.5) * 6
        size = 2 + (idx % 3)
        color = PALETTE["cyan"] if idx % 4 == 0 else PALETTE["ink"]
        draw.rounded_rectangle((x - size, y - size * 0.6, x + size, y + size * 0.6), radius=2, fill=color + (150,))


def draw_anchors(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    anchors = [
        (width * 0.38, height * 0.46, PALETTE["sand"]),
        (width * 0.62, height * 0.63, PALETTE["rust"]),
    ]
    for x, y, color in anchors:
        draw.line((x, y, x, height * 0.91), fill=PALETTE["ink"] + (40,), width=1)
        draw.ellipse((x - 18, y - 18, x + 18, y + 18), fill=(255, 255, 255, 180), outline=color + (255,), width=4)
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), outline=PALETTE["ink"] + (120,), width=2)


def add_ui(base: Image.Image, width: int, height: int) -> None:
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    def panel(box: tuple[int, int, int, int], alpha: int = 188) -> None:
        draw.rounded_rectangle(box, radius=28, fill=(255, 252, 247, alpha), outline=(255, 255, 255, 168), width=2)

    panel((40, 42, 384, 430))
    panel((406, 42, width - 40, height - 286))
    panel((40, height - 242, width - 40, height - 40), 176)

    draw.text((70, 72), "#073 / pale fog infrastructure", fill=PALETTE["muted"])
    draw.text((70, 112), "FOG SPAN", fill=PALETTE["ink"])
    draw.text((70, 146), "SWITCHFIELD", fill=PALETTE["cyan"])
    draw.multiline_text(
        (70, 198),
        "Drag anchors to reroute one\nsuspended bridge field.\nNo mode rail. No pulse button.",
        fill=PALETTE["muted"],
        spacing=8,
    )

    chip_y = 296
    for idx, label in enumerate(["drag anchors", "diagonal bridges", "fog margins"]):
        x0 = 70 + idx * 98
        draw.rounded_rectangle((x0, chip_y, x0 + 90, chip_y + 28), radius=14, fill=(255, 255, 255, 108), outline=(220, 220, 220, 120), width=1)
        draw.text((x0 + 10, chip_y + 8), label, fill=PALETTE["ink"])

    notes = [
        ("Idea", "Pale infrastructure without falling back into another village or cute district."),
        ("Interaction", "Three draggable rings change bridge sag, gate spread, and traffic density."),
        ("Next", "A follow-up could add one survey tram or weather front without becoming a dashboard."),
    ]
    card_w = (width - 112) / 3
    for idx, (title, body) in enumerate(notes):
        x0 = 56 + idx * (card_w + 14)
        x1 = x0 + card_w
        draw.rounded_rectangle((x0, height - 222, x1, height - 58), radius=22, fill=(255, 255, 255, 102), outline=(255, 255, 255, 124), width=2)
        draw.text((x0 + 18, height - 198), title.upper(), fill=PALETTE["ink"])
        draw.multiline_text((x0 + 18, height - 164), body, fill=PALETTE["muted"], spacing=7)

    base.alpha_composite(layer)


def render(output: Path, width: int, height: int) -> None:
    image = Image.new("RGBA", (width, height), PALETTE["top"] + (255,))
    draw = ImageDraw.Draw(image, "RGBA")
    add_gradient(draw, width, height)

    glow(image, (width * 0.18, height * 0.18), width * 0.16, PALETTE["cyan"] + (36,), width * 0.05)
    glow(image, (width * 0.76, height * 0.16), width * 0.14, PALETTE["rust"] + (32,), width * 0.05)
    glow(image, (width * 0.56, height * 0.82), width * 0.2, PALETTE["sage"] + (34,), width * 0.07)

    draw_ground(draw, width, height)
    draw_fog(image, width, height)

    route = build_route(width, height)
    draw_route(image, route, width, height)
    draw = ImageDraw.Draw(image, "RGBA")
    draw_particles(draw, route)
    draw_anchors(draw, width, height)

    for x, y, r, color in [
        (width * 0.38, height * 0.46, 18, PALETTE["sand"]),
        (width * 0.62, height * 0.63, 18, PALETTE["rust"]),
    ]:
        glow(image, (x, y), 32, color + (56,), 12)

    add_ui(image, width, height)
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
