#!/usr/bin/env python3

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


BG = "#05060a"
CYAN = "#87dff1"
MAGENTA = "#f95ca8"
AMBER = "#f6ca62"
MINT = "#bde8ab"
TEXT = "#ebede6"


def hex_rgba(value: str, alpha: int) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def noise(x: float, y: float, seed: float = 0.0) -> float:
    return (
        math.sin(x * 1.37 + seed * 3.1)
        + math.sin(y * 1.81 - seed * 0.7)
        + math.sin((x + y) * 0.93 + seed * 1.6)
        + math.sin(math.hypot(x * 1.4, y * 0.7) * 2.4 + seed * 2.2)
    ) * 0.25


def rounded_rect(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], radius: float, fill=None, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def render(output: Path, width: int, height: int) -> None:
    image = Image.new("RGBA", (width, height), BG)
    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)

    gdraw.ellipse((width * 0.12, height * 0.08, width * 0.42, height * 0.34), fill=hex_rgba(MAGENTA, 28))
    gdraw.ellipse((width * 0.58, height * 0.10, width * 0.9, height * 0.4), fill=hex_rgba(CYAN, 28))
    gdraw.ellipse((width * 0.34, height * 0.62, width * 0.74, height * 0.94), fill=hex_rgba(AMBER, 18))
    glow = glow.filter(ImageFilter.GaussianBlur(70))
    image.alpha_composite(glow)

    draw = ImageDraw.Draw(image)

    for x in range(0, width, 48):
        draw.line((x, 0, x, height), fill=hex_rgba(TEXT, 10), width=1)
    for y in range(0, height, 48):
        draw.line((0, y, width, y), fill=hex_rgba(TEXT, 10), width=1)

    for band_index in range(18):
        pts = []
        for x in range(-40, width + 41, 16):
            nx = x * 0.006
            y = (
                ((height * 0.07 * band_index) + band_index * 28) % (height + 180)
                - 90
                + math.sin(nx * 13 + band_index) * 8
                + noise(nx, band_index * 0.4, band_index) * (18 + band_index * 1.3)
            )
            pts.append((x, y))
        draw.line(pts, fill=hex_rgba("#7f9ec3", 26), width=1)

    frame = (width * 0.11, height * 0.08, width * 0.89, height * 0.92)
    draw.rectangle(frame, outline=hex_rgba(TEXT, 30), width=1)

    chart_boxes = [
        (width * 0.18, height * 0.16, 66, 26, 0),
        (width * 0.36, height * 0.16, 66, 26, 1),
        (width * 0.54, height * 0.16, 66, 26, 2),
        (width * 0.72, height * 0.16, 66, 26, 3),
        (width * 0.15, height * 0.76, 96, 34, 4),
        (width * 0.69, height * 0.77, 96, 34, 5),
    ]
    palette = [CYAN, MAGENTA, AMBER]
    for x, y, w, h, seed in chart_boxes:
        draw.rectangle((x, y, x + w, y + h), outline=hex_rgba(TEXT, 36), width=1)
        pts = []
        for i in range(0, w + 1, 4):
            v = y + h * 0.55 + math.sin((i + seed * 17) * 0.12) * h * 0.18 + noise(i * 0.03, seed * 0.8, seed) * h * 0.3
            pts.append((x + i, v))
        draw.line(pts, fill=hex_rgba(palette[seed % 3], 180), width=2)

    body_glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(body_glow)
    segments = []
    for i in range(26):
        t = i / 25
        sy = height * (0.08 + 0.84 * t)
        sx = width * 0.5 + math.sin(t * 5.8 + 0.4) * width * 0.13 + math.sin(t * 13.4 - 0.7) * width * 0.035
        sw = 34 + math.sin(t * 6.2) * 10 + (1 - abs(t - 0.45) * 1.6) * 24
        sh = 14 + math.cos(t * 8.4) * 3
        rot = math.sin(t * 24) * 0.12
        segments.append((sx, sy, sw, sh, rot))
        bdraw.ellipse((sx - sw * 1.35, sy - sw * 0.8, sx + sw * 1.35, sy + sw * 0.8), fill=hex_rgba(CYAN, 34 if i % 3 else 44))
    body_glow = body_glow.filter(ImageFilter.GaussianBlur(24))
    image.alpha_composite(body_glow)
    draw = ImageDraw.Draw(image)

    for i in range(len(segments) - 1):
        ax, ay, aw, _, _ = segments[i]
        bx, by, bw, _, _ = segments[i + 1]
        draw.line((ax, ay, bx, by), fill=hex_rgba("#6281aa", 60), width=int(max(8, (aw + bw) * 0.22)))

    for idx, (sx, sy, sw, sh, _rot) in enumerate(segments):
        rounded_rect(
            draw,
            (sx - sw, sy - sh, sx + sw, sy + sh),
            sh,
            fill=hex_rgba("#0d1520", 246),
            outline=hex_rgba(TEXT, 36),
            width=1,
        )
        draw.line((sx - sw * 0.72, sy, sx + sw * 0.72, sy), fill=hex_rgba(CYAN, 150), width=2)
        draw.rectangle((sx - sw * 0.22, sy - sh * 0.42, sx + sw * 0.08, sy + sh * 0.42), fill=hex_rgba(MAGENTA, 108))
        draw.rectangle((sx + sw * 0.12, sy - sh * 0.34, sx + sw * 0.3, sy + sh * 0.34), fill=hex_rgba(AMBER, 104))
        for n in (-1, 0, 1):
            draw.line((sx - sw * 0.9, sy + n * sh * 0.48, sx - sw * 1.18, sy + n * sh * 0.68), fill=hex_rgba(MINT, 64), width=1)

        tx = sx + (sw + 26 if sx < width * 0.5 else -(sw + 98))
        ty = sy - 10
        draw.line((sx, sy, tx, ty, tx + (22 if sx < width * 0.5 else 76), ty), fill=hex_rgba(TEXT, 48), width=1)
        tag_box = (tx if sx < width * 0.5 else tx, ty - 12, tx + 72, ty + 8)
        draw.rectangle(tag_box, fill=hex_rgba("#060a10", 188), outline=hex_rgba(CYAN, 72), width=1)

    pulse = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(pulse)
    center = (width * 0.53, height * 0.61)
    for radius, color, alpha in ((96, CYAN, 70), (62, MAGENTA, 62), (132, AMBER, 42)):
        pdraw.ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), outline=hex_rgba(color, alpha), width=3)
    pulse = pulse.filter(ImageFilter.GaussianBlur(1))
    image.alpha_composite(pulse)

    panel = (28, 24, min(width - 28, 520), 220)
    rounded_rect(draw, panel, 20, fill=hex_rgba("#0a0d14", 192), outline=hex_rgba(TEXT, 34), width=1)
    dock = (width - min(360, width - 56) - 28, 24, width - 28, 236)
    rounded_rect(draw, dock, 20, fill=hex_rgba("#0a0d14", 192), outline=hex_rgba(TEXT, 34), width=1)

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a static preview for Segmented Fault Organism.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()
    render(args.output, args.width, args.height)
    print(f"rendered {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
