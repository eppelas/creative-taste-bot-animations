#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


DEFAULT_TEXT = (
    "A quiet repair room keeps three moods at once: one pane sweats, one pane "
    "reflects, one pane stores a rumor. A second thought arrives more softly, "
    "asking whether the grove should open wider when language gets kinder? "
    "Then a sharper clause lands and the whole field answers with embers, "
    "roots, and a brief misregistered shimmer."
)

PALETTE = [
    ((158, 185, 159), (219, 226, 207)),
    ((136, 182, 184), (212, 238, 234)),
    ((210, 165, 109), (243, 216, 182)),
    ((215, 149, 136), (240, 201, 192)),
]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def hash_string(text: str) -> int:
    h = 2166136261
    for char in text:
      h ^= ord(char)
      h = (h * 16777619) & 0xFFFFFFFF
    return h


def titleize(text: str) -> str:
    cleaned = " ".join(text.replace(":", " ").replace(",", " ").split())
    words = cleaned.split()[:4]
    return " ".join(word[:1].upper() + word[1:] for word in words) or "Untitled Grove"


def parse_groves(text: str) -> list[dict]:
    clauses = [part.strip() for part in text.replace("\n", " ").split(".") if part.strip()]
    if not clauses:
        clauses = ["A blank register waits for the next clause"]
    output = []
    total = len(clauses)
    for index, clause in enumerate(clauses[:4]):
        words = clause.split()
        hashed = hash_string(clause)
        density = clamp(len(words) / 18, 0.45, 1.4)
        energy = clamp((clause.count("!") + clause.count("?")) * 0.34 + clause.count(",") * 0.08 + 0.25, 0.22, 1.6)
        softness = clamp(sum(ch.lower() in "aeiouауоыиэяюёе" for ch in clause) / max(len(clause), 1) * 9, 0.25, 1.2)
        output.append(
            {
                "label": titleize(clause),
                "x": clamp(0.2 + (index % 2) * 0.36 + (hashed % 17) / 100, 0.14, 0.86),
                "y": clamp(0.28 + (index // 2) * 0.3 + ((hashed >> 3) % 19) / 120, 0.2, 0.84),
                "density": density,
                "energy": energy,
                "softness": softness,
                "palette": PALETTE[hashed % len(PALETTE)],
                "seed": hashed,
                "words": len(words),
                "index": index,
                "total": total,
            }
        )
    return output


def draw_gradient_background(image: Image.Image) -> None:
    width, height = image.size
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(height):
        mix = y / max(height - 1, 1)
        r = int(24 - mix * 12)
        g = int(35 - mix * 15)
        b = int(37 - mix * 16)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    for x, y, radius, color in [
        (0.18, 0.16, 240, (136, 182, 184, 38)),
        (0.82, 0.14, 260, (215, 149, 136, 28)),
        (0.62, 0.78, 280, (158, 185, 159, 28)),
    ]:
        glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow, "RGBA")
        cx = int(width * x)
        cy = int(height * y)
        for ring in range(radius, 0, -8):
            alpha = int(color[3] * (ring / radius) ** 2)
            glow_draw.ellipse((cx - ring, cy - ring, cx + ring, cy + ring), fill=(color[0], color[1], color[2], alpha))
        image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(30)))


def draw_panel(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], fill: tuple[int, int, int, int]) -> None:
    draw.rounded_rectangle(rect, radius=34, fill=fill, outline=(236, 235, 222, 34), width=2)


def draw_curve(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill: tuple[int, int, int, int], width: int) -> None:
    draw.line(points, fill=fill, width=width, joint="curve")


def render(output_path: Path, width: int, height: int) -> None:
    groves = parse_groves(DEFAULT_TEXT)
    image = Image.new("RGBA", (width, height), (16, 25, 26, 255))
    draw_gradient_background(image)
    draw = ImageDraw.Draw(image, "RGBA")

    left = (42, 42, 360, height - 42)
    right = (386, 42, width - 42, height - 42)
    draw_panel(draw, left, (18, 28, 29, 198))
    draw_panel(draw, right, (12, 20, 20, 176))

    for x in range(420, width - 42, 88):
        draw.line((x, 42, x, height - 42), fill=(236, 235, 222, 12), width=1)
    for y in range(96, height - 42, 88):
        draw.line((386, y, width - 42, y), fill=(236, 235, 222, 10), width=1)

    # left panel blocks
    draw.rounded_rectangle((66, 66, 230, 108), radius=18, fill=(236, 235, 222, 20), outline=(236, 235, 222, 28))
    draw.rounded_rectangle((66, 378, 336, 584), radius=24, fill=(6, 12, 12, 150), outline=(236, 235, 222, 34))
    for idx, top in enumerate((622, 700, 778, 856)):
        col = idx % 2
        row = idx // 2
        x0 = 66 + col * 136
        y0 = 622 + row * 80
        draw.rounded_rectangle((x0, y0, x0 + 122, y0 + 64), radius=18, fill=(236, 235, 222, 16), outline=(236, 235, 222, 24))

    # field currents
    field_width = right[2] - right[0]
    field_height = right[3] - right[1]
    base = Image.new("RGBA", image.size, (0, 0, 0, 0))
    base_draw = ImageDraw.Draw(base, "RGBA")
    for groove in groves:
        gx = right[0] + groove["x"] * field_width
        gy = right[1] + groove["y"] * field_height
        stroke, leaf = groove["palette"]
        for lane in range(3):
            points = []
            for step in range(25):
                t = step / 24
                x = gx + (t - 0.5) * field_width * 0.76 + math.cos(t * 9 + groove["index"] * 2.1 + lane) * 14
                y = gy + math.sin(t * math.pi * 2 + lane) * (24 + lane * 10) + math.sin(t * 7 + groove["index"]) * (14 + groove["energy"] * 12)
                points.append((x, y))
            draw_curve(base_draw, points, (*stroke, 56), 2)
        halo = Image.new("RGBA", image.size, (0, 0, 0, 0))
        halo_draw = ImageDraw.Draw(halo, "RGBA")
        radius = int(46 + groove["words"] * 4)
        halo_draw.ellipse((gx - radius, gy - radius, gx + radius, gy + radius), outline=(*stroke, 34), width=16)
        image.alpha_composite(halo.filter(ImageFilter.GaussianBlur(18)))
        branch_count = 4 + round(groove["density"] * 5)
        for branch in range(branch_count):
            angle = (math.pi * 2 / branch_count) * branch + (groove["seed"] % 13) * 0.04
            outer = radius * (0.62 + (branch % 3) * 0.18)
            bend = math.sin(branch + groove["seed"] * 0.00004) * (16 + groove["softness"] * 10)
            points = [
                (gx, gy),
                (gx + math.cos(angle) * (outer * 0.32), gy + math.sin(angle) * (outer * 0.12) + bend * 0.15),
                (gx + math.cos(angle) * (outer * 0.68), gy + math.sin(angle) * (outer * 0.62) + bend),
                (gx + math.cos(angle) * outer, gy + math.sin(angle) * outer + bend * 1.1),
            ]
            draw_curve(base_draw, points, (*stroke, 210), 3)
            for leaf_idx in range(4):
                t = leaf_idx / 3 if leaf_idx else 0
                lx = gx + math.cos(angle) * outer * (0.38 + t * 0.48)
                ly = gy + math.sin(angle) * outer * (0.32 + t * 0.56) + bend * (0.35 + t)
                size = 3 + groove["softness"] * 5 * (1 - t * 0.25)
                base_draw.ellipse((lx - size, ly - size * 0.5, lx + size, ly + size * 0.5), fill=(*leaf, 240))
        for spark in range(8):
            angle = (math.pi * 2 / 8) * spark
            orbit = radius * (1.1 + (spark % 3) * 0.12)
            sx = gx + math.cos(angle) * orbit
            sy = gy + math.sin(angle) * orbit * (0.8 + groove["softness"] * 0.16)
            fill = (*stroke, 255) if spark % 3 == 0 else (236, 235, 222, 210)
            size = 2 + groove["energy"] * 2
            base_draw.ellipse((sx - size, sy - size, sx + size, sy + size), fill=fill)
    image.alpha_composite(base.filter(ImageFilter.GaussianBlur(0.3)))

    # status and footer
    draw.rounded_rectangle((412, 66, width - 214, 142), radius=22, fill=(255, 255, 255, 12), outline=(236, 235, 222, 28))
    chip_y = height - 374
    for idx, groove in enumerate(groves):
        draw.rounded_rectangle((414, chip_y + idx * 74, 742, chip_y + idx * 74 + 60), radius=20, fill=(255, 255, 255, 12), outline=(236, 235, 222, 20))
    footer_top = height - 172
    card_w = (width - 456) // 3
    for idx in range(3):
        x0 = 414 + idx * (card_w + 12)
        draw.rounded_rectangle((x0, footer_top, x0 + card_w, height - 66), radius=22, fill=(255, 255, 255, 10), outline=(236, 235, 222, 22))

    image.convert("RGB").save(output_path, quality=96)


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
