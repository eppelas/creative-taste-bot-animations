#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


PALETTE = {
    "sky_top": (251, 248, 244),
    "sky_mid": (240, 231, 221),
    "sky_bottom": (217, 194, 173),
    "chalk": (231, 216, 199),
    "silt": (201, 177, 154),
    "ink": (37, 54, 58),
    "water": (111, 170, 181),
    "water_soft": (186, 221, 226),
    "jade": (159, 194, 177),
    "amber": (212, 162, 99),
    "coral": (221, 143, 122),
    "fog": (255, 251, 245, 160),
    "white": (255, 255, 255),
}


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def blend(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def add_vertical_gradient(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    for y in range(height):
      t = y / max(1, height - 1)
      if t < 0.46:
          color = blend(PALETTE["sky_top"], PALETTE["sky_mid"], t / 0.46)
      else:
          color = blend(PALETTE["sky_mid"], PALETTE["sky_bottom"], (t - 0.46) / 0.54)
      draw.line((0, y, width, y), fill=color)


def add_clouds(base: Image.Image, width: int, height: int) -> None:
    cloud = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(cloud)
    ellipses = [
        (0.22, 0.14, 0.30, 0.08),
        (0.54, 0.18, 0.34, 0.09),
        (0.72, 0.28, 0.26, 0.07),
        (0.34, 0.30, 0.38, 0.10),
    ]
    for cx, cy, rx, ry in ellipses:
        box = (
            int((cx - rx) * width),
            int((cy - ry) * height),
            int((cx + rx) * width),
            int((cy + ry) * height),
        )
        draw.ellipse(box, fill=(255, 255, 255, 90))
    cloud = cloud.filter(ImageFilter.GaussianBlur(radius=32))
    base.alpha_composite(cloud)


def add_channel(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], color: tuple[int, int, int], width_px: int, alpha: int) -> None:
    flat = [(int(x), int(y)) for x, y in points]
    draw.line(flat, fill=color + (alpha,), width=width_px, joint="curve")
    draw.line(flat, fill=(255, 255, 255, min(110, alpha)), width=max(1, width_px // 5), joint="curve")


def add_basin(base: Image.Image, center: tuple[float, float], rx: float, ry: float, tint: str) -> None:
    width, height = base.size
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx, cy = center
    box = (int(cx - rx), int(cy - ry), int(cx + rx), int(cy + ry))
    mid = PALETTE["jade"] if tint == "jade" else PALETTE["water"]
    glow = PALETTE["white"] + (160,)
    draw.ellipse(box, fill=mid + (72,), outline=glow)
    for ring in range(1, 4):
        scale = 1 - ring * 0.18
        ring_box = (
            int(cx - rx * scale),
            int(cy - ry * scale * 0.7),
            int(cx + rx * scale),
            int(cy + ry * scale * 0.7),
        )
        draw.ellipse(ring_box, outline=mid + (84,), width=1)
    blur = layer.filter(ImageFilter.GaussianBlur(radius=18))
    base.alpha_composite(blur)
    base.alpha_composite(layer)


def add_tower(base: Image.Image, x: float, y: float, h: float, w: float) -> None:
    width, height = base.size
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rectangle((x - w / 2, y, x + w / 2, y + h), fill=(255, 255, 255, 92))
    cap = [
        (x - w * 2.1, y + h * 0.1),
        (x, y - h * 0.26),
        (x + w * 2.1, y + h * 0.1),
        (x, y + h * 0.42),
    ]
    draw.polygon(cap, fill=PALETTE["jade"] + (88,), outline=(255, 255, 255, 120))
    glow = layer.filter(ImageFilter.GaussianBlur(radius=14))
    base.alpha_composite(glow)
    base.alpha_composite(layer)


def add_ferry(draw: ImageDraw.ImageDraw, x: float, y: float, size: float, glow: bool = False) -> None:
    hull = [
        (x - size * 1.6, y),
        (x, y - size * 0.42),
        (x + size * 1.8, y),
        (x, y + size * 0.42),
    ]
    draw.polygon(hull, fill=PALETTE["amber"] + ((220,) if glow else (180,)))
    draw.ellipse((x - size * 0.36, y - size * 1.15, x + size * 0.36, y - size * 0.45), fill=(255, 246, 236, 190))


def add_lantern(base: Image.Image, x: float, y: float, radius: float) -> None:
    width, height = base.size
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.line((x, y + radius * 3, x, y), fill=(101, 111, 104, 90), width=2)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=PALETTE["amber"] + (200,))
    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((x - radius * 7, y - radius * 7, x + radius * 7, y + radius * 7), fill=(255, 220, 168, 76))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=18))
    base.alpha_composite(glow)
    base.alpha_composite(layer)


def add_workers(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    positions = [
        (0.18, 0.67), (0.27, 0.63), (0.35, 0.70), (0.43, 0.66),
        (0.54, 0.71), (0.63, 0.65), (0.74, 0.69), (0.84, 0.64),
    ]
    for idx, (x, y) in enumerate(positions):
        px = x * width
        py = y * height
        size = 4 + (idx % 3)
        draw.ellipse((px - size, py - size, px + size, py + size), fill=PALETTE["ink"] + (110,))
        draw.ellipse((px - size * 0.45, py - size * 2.0, px + size * 0.45, py - size * 1.1), fill=(255, 241, 219, 150))


def add_ui(base: Image.Image, width: int, height: int) -> None:
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    def panel(box: tuple[int, int, int, int], fill_alpha: int = 182) -> None:
        draw.rounded_rectangle(box, radius=28, fill=(250, 245, 238, fill_alpha), outline=(255, 255, 255, 170), width=2)

    panel((44, 46, 730, 288))
    panel((38, height - 252, width - 38, height - 36), 172)
    draw.rounded_rectangle((width - 188, 50, width - 44, 96), radius=24, fill=(250, 245, 238, 180), outline=(255, 255, 255, 170), width=2)

    draw.text((74, 74), "#068 / inhabited translucent floodplain", fill=PALETTE["muted"] if "muted" in PALETTE else (80, 92, 96), font_size=18)
    draw.text((74, 104), "CHALK MEMBRANE", fill=PALETTE["ink"], font_size=58)
    draw.text((74, 166), "FLOODPLAIN", fill=PALETTE["water"], font_size=58)
    draw.text(
        (74, 224),
        "Overcast ferry-stop scene with breathing membrane towers,\ndrifting rafts, and dock-beacon wakeups instead of another sheet UI.",
        fill=(80, 92, 96),
        font_size=23,
        spacing=8,
    )
    draw.text((width - 162, 66), "BACK TO INDEX", fill=PALETTE["ink"], font_size=16)

    note_w = (width - 100) / 3
    labels = [
        ("IDEA", "One explicit floodplain stop with ferries, catwalks,\nand translucent service basins."),
        ("INTERACTION", "The preview shows the dock beacon waking routes,\nlanterns, and membrane pressure."),
        ("NEXT", "Could expand into adjacent rooms: dock office,\nsluice stair, or night crossing."),
    ]
    for idx, (title, body) in enumerate(labels):
        x0 = 50 + idx * note_w
        x1 = x0 + note_w - 12
        draw.rounded_rectangle((x0, height - 232, x1, height - 58), radius=20, fill=(255, 255, 255, 88), outline=(255, 255, 255, 120), width=2)
        draw.text((x0 + 18, height - 210), title, fill=PALETTE["ink"], font_size=18)
        draw.text((x0 + 18, height - 176), body, fill=(82, 96, 100), font_size=22, spacing=8)

    beacon = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(beacon)
    cx, cy = 176, 266
    for radius, alpha in [(16, 90), (28, 52), (42, 24)]:
        bdraw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(221, 143, 122, alpha), width=4)
    bdraw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=PALETTE["coral"] + (220,))
    beacon = beacon.filter(ImageFilter.GaussianBlur(radius=2))
    layer.alpha_composite(beacon)

    base.alpha_composite(layer)


def render(output: Path, width: int, height: int) -> None:
    base = Image.new("RGBA", (width, height), PALETTE["sky_top"] + (255,))
    draw = ImageDraw.Draw(base, "RGBA")

    add_vertical_gradient(draw, width, height)
    add_clouds(base, width, height)

    basins = [
        (0.14, 0.59, 0.11, 0.062, "water"),
        (0.28, 0.56, 0.12, 0.068, "jade"),
        (0.42, 0.60, 0.13, 0.072, "water"),
        (0.58, 0.55, 0.12, 0.066, "jade"),
        (0.72, 0.60, 0.13, 0.072, "water"),
        (0.86, 0.57, 0.11, 0.064, "jade"),
    ]

    channels = []
    for idx in range(len(basins) - 1):
        ax, ay, _, _, _ = basins[idx]
        bx, by, _, _, _ = basins[idx + 1]
        p1 = (ax * width, ay * height)
        p2 = (bx * width, by * height)
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2 - (18 if idx % 2 == 0 else -14)
        channels.append([p1, (mx - 60, my), (mx + 60, my + 12), p2])

    for path in channels:
        add_channel(draw, path, PALETTE["water"], 20, 110)

    for idx, (x, y, rx, ry, tint) in enumerate(basins):
        add_basin(base, (x * width, y * height), rx * width, ry * height, tint)
        if idx < len(basins) - 1:
            add_tower(base, x * width + 18, (y - 0.22) * height, 0.18 * height, 0.018 * width)

    span_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(span_layer)
    tower_points = [(x * width + 18, (y - 0.04) * height) for x, y, *_ in basins[:-1]]
    for idx in range(len(tower_points) - 1):
        x1, y1 = tower_points[idx]
        x2, y2 = tower_points[idx + 1]
        midx = (x1 + x2) / 2
        midy = (y1 + y2) / 2 + 28
        sdraw.line((x1, y1, midx, midy, x2, y2), fill=(255, 255, 255, 88), width=2)
        sdraw.line((x1, y1, midx, midy, x2, y2), fill=(111, 170, 181, 42), width=6)
    span_layer = span_layer.filter(ImageFilter.GaussianBlur(radius=1))
    base.alpha_composite(span_layer)

    ferry_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(ferry_layer)
    ferry_positions = [(0.22, 0.58), (0.36, 0.575), (0.49, 0.59), (0.68, 0.57), (0.81, 0.585)]
    for idx, (x, y) in enumerate(ferry_positions):
        add_ferry(fdraw, x * width, y * height, 10 + idx, glow=idx in (1, 3))
    glow = ferry_layer.filter(ImageFilter.GaussianBlur(radius=4))
    base.alpha_composite(glow)
    base.alpha_composite(ferry_layer)

    for idx, (x, y, rx, ry, _) in enumerate(basins):
        lantern_offset = rx * width * 0.78
        add_lantern(base, x * width - lantern_offset, y * height + 12, 4.6)
        add_lantern(base, x * width + lantern_offset * 0.84, y * height + 18, 4.0)

    add_workers(draw, width, height)

    ground = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(ground)
    points = []
    for step in range(17):
        x = step / 16 * width
        y = height * 0.72 + math.sin(step * 0.7) * 10 + math.cos(step * 0.43) * 8
        points.append((x, y))
    polygon = [(0, height), *points, (width, height)]
    gdraw.polygon(polygon, fill=PALETTE["silt"] + (190,))
    ground = ground.filter(ImageFilter.GaussianBlur(radius=2))
    base.alpha_composite(ground)

    add_ui(base, width, height)

    vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    vdraw.rectangle((0, 0, width, height), fill=(255, 255, 255, 0))
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=0))
    base = base.filter(ImageFilter.GaussianBlur(radius=0.2))
    base.save(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    render(args.output, args.width, args.height)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
