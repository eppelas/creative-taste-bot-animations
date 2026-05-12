#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


PALETTE = {
    "paper": (239, 228, 211),
    "paper_bright": (251, 245, 236),
    "paper_deep": (216, 194, 173),
    "ink": (42, 53, 45),
    "sage": (112, 141, 114),
    "mint": (149, 189, 163),
    "pond": (141, 190, 192),
    "clay": (210, 143, 114),
    "amber": (209, 161, 94),
    "plum": (143, 125, 144),
    "line": (74, 86, 78, 28),
}


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], fill, outline, radius: int) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=1)


def draw_terrace(draw: ImageDraw.ImageDraw, width: int, height: int, y_norm: float, amp: float, color) -> None:
    y = height * y_norm
    points: list[tuple[float, float]] = [(0, y + 180)]
    for x in range(0, width + 24, 24):
        wave = math.sin(x * 0.008 + y_norm * 10) * amp
        points.append((x, y + wave))
    points.extend([(width, height + 120), (0, height + 120)])
    draw.polygon(points, fill=color)


def draw_route(draw: ImageDraw.ImageDraw, start, end, via, color, width: int) -> None:
    points = []
    for step in range(25):
        t = step / 24
        x = (1 - t) * (1 - t) * start[0] + 2 * (1 - t) * t * via[0] + t * t * end[0]
        y = (1 - t) * (1 - t) * start[1] + 2 * (1 - t) * t * via[1] + t * t * end[1]
        points.append((x, y))
    draw.line(points, fill=color, width=width, joint="curve")
    for x, y in points[4::6]:
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 255, 255, 120))


def draw_house(draw: ImageDraw.ImageDraw, x: float, y: float, scale: float) -> None:
    w = 58 * scale
    h = 46 * scale
    body = [
        (x - w * 0.45, y + h * 0.1),
        (x - w * 0.15, y - h * 0.55),
        (x, y - h * 0.62),
        (x + w * 0.2, y - h * 0.5),
        (x + w * 0.46, y + h * 0.08),
        (x + w * 0.3, y + h * 0.42),
        (x, y + h * 0.54),
        (x - w * 0.3, y + h * 0.4),
    ]
    draw.polygon(body, fill=(149, 189, 163, 150), outline=(42, 53, 45, 54))
    draw.line(
        [(x - w * 0.3, y), (x, y - h * 0.86), (x + w * 0.34, y)],
        fill=(42, 53, 45, 64),
        width=2,
    )
    draw.line([(x - w * 0.06, y + h * 0.12), (x - w * 0.04, y + h * 0.86)], fill=(112, 141, 114, 100), width=3)
    draw.ellipse((x - 4, y - h * 0.1 - 4, x + 8, y - h * 0.1 + 8), fill=(209, 161, 94, 160))
    for i in range(3):
        draw.arc(
            (x - 44 + i * 16, y - 96 - i * 6, x - 8 + i * 16, y - 28),
            start=200,
            end=330,
            fill=(112, 141, 114, 94),
            width=3,
        )


def draw_carrier(draw: ImageDraw.ImageDraw, x: float, y: float, scale: float) -> None:
    draw.ellipse((x - 18 * scale, y + 3 * scale, x + 18 * scale, y + 13 * scale), fill=(42, 53, 45, 12))
    draw.polygon(
        [
            (x - 10 * scale, y + 6 * scale),
            (x - 8 * scale, y - 20 * scale),
            (x, y - 24 * scale),
            (x + 8 * scale, y - 20 * scale),
            (x + 10 * scale, y + 6 * scale),
            (x, y + 18 * scale),
        ],
        fill=(149, 189, 163, 194),
        outline=(42, 53, 45, 64),
    )
    draw.ellipse((x - 6 * scale, y - 8 * scale, x - 2 * scale, y - 4 * scale), fill=PALETTE["ink"])
    draw.ellipse((x + 2 * scale, y - 8 * scale, x + 6 * scale, y - 4 * scale), fill=PALETTE["ink"])
    draw.ellipse((x - 2 * scale, y - 1 * scale, x + 2 * scale, y + 3 * scale), fill=PALETTE["clay"])
    draw.rounded_rectangle(
        (x - 5 * scale, y - 16 * scale, x + 5 * scale, y - 8 * scale),
        radius=2,
        fill=(209, 161, 94, 210),
    )


def render(width: int, height: int) -> Image.Image:
    image = Image.new("RGBA", (width, height), PALETTE["paper_bright"])
    base = ImageDraw.Draw(image, "RGBA")

    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(int(lerp(PALETTE["paper_bright"][i], PALETTE["paper_deep"][i], t)) for i in range(3))
        base.line((0, y, width, y), fill=color)

    for cx, cy, radius, color in [
        (0.18, 0.14, 0.2, (255, 255, 255, 128)),
        (0.82, 0.18, 0.24, (141, 190, 192, 40)),
        (0.18, 0.84, 0.28, (210, 143, 114, 34)),
        (0.76, 0.82, 0.28, (149, 189, 163, 36)),
    ]:
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay, "RGBA")
        r = radius * width
        od.ellipse((cx * width - r, cy * height - r, cx * width + r, cy * height + r), fill=color)
        overlay = overlay.filter(ImageFilter.GaussianBlur(radius=60))
        image.alpha_composite(overlay)

    shell = ImageDraw.Draw(image, "RGBA")
    left_box = (24, 24, 334, height - 24)
    world_box = (350, 24, width - 24, height - 24)
    rounded_panel(shell, left_box, (255, 251, 245, 210), PALETTE["line"], 34)
    rounded_panel(shell, world_box, (255, 250, 243, 158), PALETTE["line"], 34)

    world = Image.new("RGBA", (int(world_box[2] - world_box[0]), int(world_box[3] - world_box[1])), (0, 0, 0, 0))
    wd = ImageDraw.Draw(world, "RGBA")
    w = world.size[0]
    h = world.size[1]

    for y_norm, amp, alpha in [
        (0.28, 34, 70),
        (0.42, 42, 84),
        (0.58, 48, 96),
        (0.74, 56, 110),
    ]:
        draw_terrace(wd, w, h, y_norm, amp, (112, 141, 114, alpha))

    for i in range(6):
        y = h * (0.18 + i * 0.12)
        points = []
        for x in range(0, w + 18, 18):
            offset = math.sin(x * 0.01 + i) * (7 + i * 1.2)
            points.append((x, y + offset))
        wd.line(points, fill=(143, 125, 144, 26 + i * 6), width=1)

    pools = [(0.54, 0.58, 70), (0.78, 0.72, 58), (0.44, 0.84, 48)]
    for x_norm, y_norm, radius in pools:
        x = w * x_norm
        y = h * y_norm
        wd.ellipse((x - radius, y - radius * 0.54, x + radius, y + radius * 0.54), fill=(141, 190, 192, 68))
        wd.ellipse((x - radius * 0.5, y - radius * 0.22, x + radius * 0.5, y + radius * 0.22), fill=(255, 255, 255, 54))

    houses = [
        (0.22, 0.46, 1.02),
        (0.49, 0.52, 1.08),
        (0.63, 0.57, 0.84),
        (0.74, 0.84, 1.12),
        (0.78, 0.95, 0.76),
        (0.18, 0.96, 0.84),
    ]
    resolved = []
    for x_norm, y_norm, scale in houses:
        x = w * x_norm
        y = h * y_norm
        resolved.append((x, y, scale))
        draw_house(wd, x, y, scale)

    route_specs = [
        (resolved[0], resolved[1], (w * 0.36, h * 0.54), (141, 190, 192, 148), 4),
        (resolved[1], resolved[2], (w * 0.56, h * 0.5), (112, 141, 114, 136), 4),
        (resolved[2], resolved[3], (w * 0.69, h * 0.74), (210, 143, 114, 150), 4),
        (resolved[3], resolved[4], (w * 0.77, h * 0.9), (141, 190, 192, 136), 4),
    ]
    for start, end, via, color, line_width in route_specs:
        draw_route(wd, (start[0], start[1]), (end[0], end[1]), via, color, line_width)

    carriers = [
        (w * 0.22, h * 0.46, 1.0),
        (w * 0.52, h * 0.51, 0.88),
        (w * 0.63, h * 0.58, 0.82),
        (w * 0.74, h * 0.84, 1.0),
        (w * 0.78, h * 0.95, 0.78),
    ]
    for x, y, scale in carriers:
        draw_carrier(wd, x, y, scale)

    image.alpha_composite(world, (int(world_box[0]), int(world_box[1])))

    shell = ImageDraw.Draw(image, "RGBA")
    shell.text((42, 42), "CREATIVE TASTE BOT MOTION STUDY #067", fill=(42, 53, 45, 220))
    shell.text((42, 82), "Moss", fill=(42, 53, 45, 255))
    shell.text((42, 142), "Courier", fill=(42, 53, 45, 255))
    shell.text((42, 202), "Hollow", fill=(112, 141, 114, 255))
    shell.text((390, 42), "INHABITED SCENE / BROWSER-NATIVE NARRATIVE", fill=(42, 53, 45, 210))
    shell.text((390, 66), "Couriers thread the", fill=(42, 53, 45, 255))
    shell.text((390, 114), "hollow", fill=(42, 53, 45, 255))

    pill_positions = [(760, 96, "9 CARRIERS"), (896, 96, "4 REED POOLS"), (1040, 96, "STORY-SAFE LOOP")]
    pill_colors = [PALETTE["amber"], PALETTE["pond"], PALETTE["plum"]]
    for (x, y, label), color in zip(pill_positions, pill_colors):
      rounded_panel(shell, (x, y, x + 116, y + 34), (255, 251, 245, 166), PALETTE["line"], 17)
      shell.ellipse((x + 10, y + 12, x + 20, y + 22), fill=color)
      shell.text((x + 28, y + 10), label, fill=(42, 53, 45, 220))

    card = (388, 402, 804, 796)
    rounded_panel(shell, card, (255, 251, 245, 196), PALETTE["line"], 28)
    shell.text((408, 422), "Errand weather", fill=(42, 53, 45, 240))
    shell.text((706, 422), "HUSH CURRENT", fill=(42, 53, 45, 160))
    lines = [
        "Pointer proximity softens the nearest district,",
        "bending reed smoke, roof tassels, and creature",
        "attention. Click drops a warm errand pulse that",
        "brightens one route and pulls the carriers into",
        "a shared reroute.",
    ]
    y = 468
    for line in lines:
        shell.text((408, y), line, fill=(82, 91, 84, 192))
        y += 36

    bars = [
        ("BRIDGE LANE", 0.47, PALETTE["amber"]),
        ("CANAL LANE", 0.45, PALETTE["pond"]),
        ("ROOF LANE", 0.33, PALETTE["clay"]),
    ]
    y = 642
    for label, value, color in bars:
        shell.text((408, y), label, fill=(42, 53, 45, 220))
        shell.text((762, y), f"{int(value * 100)}%", fill=(82, 91, 84, 190))
        shell.rounded_rectangle((408, y + 22, 788, y + 34), radius=6, fill=(42, 53, 45, 18))
        shell.rounded_rectangle((408, y + 22, 408 + 380 * value, y + 34), radius=6, fill=color)
        y += 54

    return image.convert("RGB")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    image = render(args.width, args.height)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
