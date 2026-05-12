#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def hex_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), alpha)


def serif(size: int):
    for path in (
        "/System/Library/Fonts/Supplemental/Palatino.ttc",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def mono(size: int):
    for path in (
        "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def gradient_background(size: tuple[int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size)
    draw = ImageDraw.Draw(image)
    top = hex_rgba("#f6eee5")
    bottom = hex_rgba("#dcc9b5")
    for y in range(height):
      t = y / max(1, height - 1)
      color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3)) + (255,)
      draw.line((0, y, width, y), fill=color)
    return image


def glow(size: tuple[int, int], center: tuple[float, float], radius: float, color: str, alpha: int) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for step in range(18, 0, -1):
        t = step / 18
        r = radius * t
        draw.ellipse(
            (center[0] - r, center[1] - r, center[0] + r, center[1] + r),
            fill=hex_rgba(color, int(alpha * (t**2) * 0.34)),
        )
    return layer.filter(ImageFilter.GaussianBlur(radius * 0.08))


def add_tile(draw: ImageDraw.ImageDraw, box, accent: str, label: str, subtitle: str, variant: int) -> None:
    rounded(draw, box, 24, hex_rgba("#fffaf3", 116), hex_rgba("#2f3940", 20), 1)
    x0, y0, x1, y1 = box
    draw.text((x0 + 12, y0 + 10), label, font=mono(10), fill=hex_rgba("#2f3940", 146))
    draw.text((x1 - 70, y0 + 10), subtitle, font=mono(10), fill=hex_rgba("#2f3940", 118))
    cx = (x0 + x1) / 2
    cy = y0 + (y1 - y0) * 0.56
    accent_fill = hex_rgba(accent, 170)
    ink = hex_rgba("#2f3940", 225)

    if variant == 0:
        draw.rounded_rectangle((x0 + 18, y0 + 82, x1 - 18, y1 - 22), radius=22, fill=hex_rgba(accent, 44))
        draw.arc((cx - 56, cy - 46, cx + 8, cy + 18), 200, 360, fill=ink, width=8)
        draw.arc((cx - 6, cy - 52, cx + 58, cy + 12), 180, 350, fill=ink, width=8)
        draw.ellipse((cx - 34, cy - 30, cx - 26, cy - 22), fill=ink)
        draw.ellipse((cx + 14, cy - 26, cx + 22, cy - 18), fill=ink)
        draw.arc((cx - 12, cy - 8, cx + 12, cy + 6), 10, 170, fill=accent_fill, width=5)
    elif variant == 1:
        draw.line((x0 + 24, cy + 30, x1 - 24, cy + 30), fill=ink, width=6)
        draw.arc((cx - 48, cy - 20, cx - 2, cy + 38), 180, 330, fill=ink, width=7)
        draw.arc((cx - 4, cy - 26, cx + 50, cy + 34), 190, 350, fill=ink, width=7)
        draw.line((cx - 22, cy + 10, cx + 18, cy + 10), fill=accent_fill, width=6)
    elif variant == 2:
        draw.line((cx, y0 + 34, cx, y1 - 30), fill=ink, width=8)
        draw.arc((cx - 38, y0 + 26, cx + 38, y0 + 76), 180, 360, fill=ink, width=7)
        draw.arc((cx - 30, cy - 8, cx + 30, cy + 26), 180, 340, fill=accent_fill, width=7)
    else:
        draw.rounded_rectangle((x0 + 24, y0 + 24, x1 - 24, y1 - 24), radius=20, outline=hex_rgba("#2f3940", 32), width=3)
        draw.line((x0 + 34, cy + 6, x1 - 34, cy - 18), fill=ink, width=6)
        draw.line((x0 + 36, cy + 22, x1 - 36, cy + 4), fill=accent_fill, width=4)
        draw.ellipse((cx - 20, cy - 10, cx - 12, cy - 2), fill=hex_rgba("#d79b92"))
        draw.ellipse((cx + 14, cy + 2, cx + 22, cy + 10), fill=hex_rgba("#8caea1"))


def render(output: Path, width: int, height: int) -> None:
    image = gradient_background((width, height))
    for center, radius, color, alpha in (
        ((width * 0.16, height * 0.12), width * 0.18, "#ffffff", 128),
        ((width * 0.82, height * 0.16), width * 0.16, "#8dbdcd", 60),
        ((width * 0.2, height * 0.82), width * 0.18, "#d79b92", 58),
        ((width * 0.74, height * 0.82), width * 0.16, "#9eac82", 56),
    ):
        image = Image.alpha_composite(image, glow((width, height), center, radius, color, alpha))

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    for x in range(0, width, 92):
        draw.line((x, 0, x, height), fill=(47, 57, 64, 18), width=1)
    for y in range(0, height, 92):
        draw.line((0, y, width, y), fill=(47, 57, 64, 18), width=1)

    margin = 18
    gap = 14
    left_w = 320
    footer_h = 180

    intro = (margin, margin, margin + left_w, 260)
    status = (margin, intro[3] + gap, margin + left_w, 468)
    mural = (intro[2] + gap, margin, width - margin, height - footer_h - gap - margin)
    footer1 = (margin, height - footer_h, width // 3 - 6, height - margin)
    footer2 = (width // 3 + 6, height - footer_h, 2 * width // 3 - 6, height - margin)
    footer3 = (2 * width // 3 + 6, height - footer_h, width - margin, height - margin)

    for rect in (intro, status, mural, footer1, footer2, footer3):
        rounded(draw, rect, 28, hex_rgba("#fffaf3", 168), hex_rgba("#2f3940", 42), 1)

    draw.text((intro[0] + 16, intro[1] + 16), "CODE ANIMATION STUDY #058", font=mono(12), fill=hex_rgba("#2f3940", 160))
    draw.text((intro[0] + 16, intro[1] + 44), "Bathhouse", font=serif(48), fill=hex_rgba("#2f3940", 235))
    draw.text((intro[0] + 16, intro[1] + 92), "Commons Mural", font=serif(48), fill=hex_rgba("#2f3940", 235))
    for i, line in enumerate((
        "A shared mural wall of awkward communal tiles,",
        "steam pockets, and soft public-bath rhythms.",
        "Pointer warmth lifts the nearest scene.",
    )):
        draw.text((intro[0] + 18, intro[1] + 150 + i * 24), line, font=serif(18), fill=hex_rgba("#2f3940", 174))

    draw.text((status[0] + 16, status[1] + 16), "COMMONS READOUT", font=mono(12), fill=hex_rgba("#2f3940", 160))
    readouts = [("Tile Temperature", "Warm"), ("Steam Bias", "Soft Drift"), ("Crowd Mode", "Hush")]
    for i, (label, value) in enumerate(readouts):
        top = status[1] + 48 + i * 52
        rounded(draw, (status[0] + 16, top, status[2] - 16, top + 42), 18, hex_rgba("#ffffff", 104), hex_rgba("#2f3940", 20), 1)
        draw.text((status[0] + 28, top + 8), label.upper(), font=mono(10), fill=hex_rgba("#2f3940", 134))
        draw.text((status[0] + 28, top + 22), value, font=serif(21), fill=hex_rgba("#2f3940", 214))

    inner = (mural[0] + 18, mural[1] + 18, mural[2] - 18, mural[3] - 18)
    rounded(draw, inner, 26, hex_rgba("#f8efe3", 210), hex_rgba("#2f3940", 24), 1)
    for x in range(inner[0], inner[2], 220):
        draw.line((x, inner[1], x, inner[3]), fill=hex_rgba("#2f3940", 12), width=1)
    for y in range(inner[1], inner[3], 180):
        draw.line((inner[0], y, inner[2], y), fill=hex_rgba("#2f3940", 12), width=1)

    stream_overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    stream_draw = ImageDraw.Draw(stream_overlay, "RGBA")
    wave_colors = [hex_rgba("#8dbdcd", 64), hex_rgba("#d79b92", 52), hex_rgba("#9eac82", 52)]
    for idx in range(6):
        y = inner[1] + 70 + idx * 92
        pts = []
        for x in range(inner[0] + 10, inner[2] - 10, 22):
            offset = (idx % 2) * 14
            dy = 10 if (x // 22) % 2 == 0 else -8
            pts.append((x, y + dy + offset))
        stream_draw.line(pts, fill=wave_colors[idx % len(wave_colors)], width=3)
    stream_overlay = stream_overlay.filter(ImageFilter.GaussianBlur(2))
    overlay.alpha_composite(stream_overlay)

    tiles = [
        ((inner[0] + 12, inner[1] + 12, inner[0] + 350, inner[1] + 286), "#8dbdcd", "POOL 01", "shared soak", 0),
        ((inner[0] + 374, inner[1] + 12, inner[0] + 568, inner[1] + 146), "#d79b92", "BENCH 02", "towel fold", 1),
        ((inner[0] + 592, inner[1] + 12, inner[0] + 774, inner[1] + 286), "#9eac82", "BRUSH 03", "vertical", 2),
        ((inner[0] + 374, inner[1] + 160, inner[0] + 774, inner[1] + 286), "#8a7889", "MIRROR 04", "drift line", 3),
        ((inner[0] + 12, inner[1] + 304, inner[0] + 206, inner[1] + 438), "#9eac82", "HOOKS 05", "drying line", 1),
        ((inner[0] + 226, inner[1] + 304, inner[0] + 420, inner[1] + 438), "#8dbdcd", "SOAP 06", "slip path", 0),
        ((inner[0] + 440, inner[1] + 304, inner[0] + 774, inner[1] + 578), "#d79b92", "COMMONS 07", "gossip lane", 0),
        ((inner[0] + 12, inner[1] + 454, inner[0] + 206, inner[1] + 588), "#8a7889", "DRAIN 08", "pool hinge", 3),
        ((inner[0] + 226, inner[1] + 454, inner[0] + 420, inner[1] + 588), "#8dbdcd", "STEAM 09", "upper shelf", 2),
        ((inner[0] + 12, inner[1] + 604, inner[0] + 206, inner[1] + 738), "#9eac82", "STEPS 10", "entry seam", 2),
        ((inner[0] + 226, inner[1] + 604, inner[0] + 420, inner[1] + 738), "#d79b92", "WHISPER 11", "tile hush", 1),
        ((inner[0] + 440, inner[1] + 604, inner[0] + 774, inner[1] + 738), "#8a7889", "LEDGER 12", "attendance", 3),
    ]

    for tile in tiles:
        add_tile(draw, *tile)

    for fx, fy, color, alpha in (
        (inner[0] + 120, inner[1] + 120, "#8dbdcd", 76),
        (inner[0] + 650, inner[1] + 160, "#d79b92", 66),
        (inner[0] + 520, inner[1] + 480, "#9eac82", 60),
    ):
        overlay.alpha_composite(glow((width, height), (fx, fy), 94, color, alpha))

    footers = [
        ("IDEA", "A design-usable public wall instead of another isolated poster or dark dashboard object."),
        ("INTERACTION", "Pointer warmth lifts steam and ripples; click rotates hush, rinse, and gossip."),
        ("NEXT", "This mural grammar could widen into a full civic bathhouse world with deeper little rooms."),
    ]
    for box, (title, text) in zip((footer1, footer2, footer3), footers):
        draw.text((box[0] + 16, box[1] + 16), title, font=mono(11), fill=hex_rgba("#2f3940", 160))
        draw.text((box[0] + 16, box[1] + 48), text, font=serif(18), fill=hex_rgba("#2f3940", 175))

    image.alpha_composite(overlay)
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
