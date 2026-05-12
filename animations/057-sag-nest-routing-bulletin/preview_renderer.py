#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def hex_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


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


def vertical_gradient(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size)
    draw = ImageDraw.Draw(image)
    a = hex_rgba(top)
    b = hex_rgba(bottom)
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(int(lerp(a[i], b[i], t)) for i in range(3)) + (255,)
        draw.line((0, y, width, y), fill=color)
    return image


def radial_glow(size: tuple[int, int], center: tuple[float, float], radius: float, color: str, alpha: int) -> Image.Image:
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


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def add_text_block(draw: ImageDraw.ImageDraw, x: int, y: int, lines: list[str], font, fill, line_gap: int) -> None:
    for index, line in enumerate(lines):
        draw.text((x, y + index * line_gap), line, font=font, fill=fill)


def creature_card(draw: ImageDraw.ImageDraw, box, tone: str, title: str, tag: str) -> None:
    tones = {
        "cream": "#f8f1e7",
        "green": "#e4efe5",
        "warm": "#f3e4de",
    }
    rounded(draw, box, 20, hex_rgba(tones[tone], 240), hex_rgba("#2e3b45", 24), 1)
    draw.text((box[0] + 12, box[1] + 10), tag, font=mono(10), fill=hex_rgba("#2e3b45", 148))
    draw.text((box[0] + 12, box[1] + 28), title, font=serif(22), fill=hex_rgba("#2e3b45", 230))

    cx = (box[0] + box[2]) / 2
    cy = box[1] + 92
    body_fill = {"cream": "#efe7dc", "green": "#cfe2d6", "warm": "#ead7cf"}[tone]
    draw.ellipse((cx - 42, cy - 34, cx + 40, cy + 38), fill=hex_rgba(body_fill, 250), outline=hex_rgba("#2e3b45", 42), width=2)
    draw.ellipse((cx - 28, cy - 48, cx - 8, cy - 28), fill=hex_rgba("#f5cd58", 255), outline=hex_rgba("#2e3b45", 80), width=2)
    draw.ellipse((cx + 4, cy - 48, cx + 24, cy - 28), fill=hex_rgba("#f5cd58", 255), outline=hex_rgba("#2e3b45", 80), width=2)
    draw.ellipse((cx - 22, cy - 42, cx - 14, cy - 34), fill=hex_rgba("#1d2529", 255))
    draw.ellipse((cx + 10, cy - 42, cx + 18, cy - 34), fill=hex_rgba("#1d2529", 255))
    draw.arc((cx - 12, cy - 20, cx + 12, cy), start=10, end=170, fill=hex_rgba("#1d2529", 255), width=2)
    draw.ellipse((cx - 32, cy - 8, cx - 6, cy + 10), fill=hex_rgba("#d49186", 56))
    draw.ellipse((cx + 2, cy - 8, cx + 28, cy + 10), fill=hex_rgba("#d49186", 56))


def render(output: Path, width: int, height: int) -> None:
    size = (width, height)
    image = vertical_gradient(size, "#f7f0e6", "#dcc9b3")
    for center, radius, color, alpha in (
        ((width * 0.12, height * 0.1), width * 0.18, "#ffffff", 126),
        ((width * 0.84, height * 0.14), width * 0.16, "#7ca8be", 56),
        ((width * 0.18, height * 0.86), width * 0.18, "#d49186", 58),
        ((width * 0.76, height * 0.84), width * 0.16, "#95af88", 58),
    ):
        image = Image.alpha_composite(image, radial_glow(size, center, radius, color, alpha))

    ui = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(ui, "RGBA")

    for x in range(0, width, 92):
        draw.line((x, 0, x, height), fill=(46, 59, 69, 18), width=1)
    for y in range(0, height, 92):
        draw.line((0, y, width, y), fill=(46, 59, 69, 18), width=1)

    margin = 18
    gap = 14
    header_h = 168
    left_w = 292
    right_w = 300
    footer_h = 182

    header_left = (margin, margin, width - 356, margin + header_h)
    header_right = (header_left[2] + gap, margin, width - margin, margin + header_h)
    left_col = (margin, header_left[3] + gap, margin + left_w, height - footer_h - margin - gap)
    stage = (left_col[2] + gap, left_col[1], width - right_w - margin - gap, left_col[3])
    right_col = (stage[2] + gap, left_col[1], width - margin, left_col[3])
    footer = (margin, stage[3] + gap, width - margin, height - margin)

    for rect in (header_left, header_right, left_col, stage, right_col, footer):
        rounded(draw, rect, 28, hex_rgba("#fffaf2", 172), hex_rgba("#2e3b45", 52), 1)

    draw.text((header_left[0] + 16, header_left[1] + 16), "CREATIVE TASTE BOT / CODE ANIMATION / 057", font=mono(12), fill=hex_rgba("#2e3b45", 166))
    draw.text((header_left[0] + 16, header_left[1] + 44), "Sag & Nest", font=serif(52), fill=hex_rgba("#2e3b45", 238))
    draw.text((header_left[0] + 16, header_left[1] + 96), "Routing Bulletin", font=serif(52), fill=hex_rgba("#2e3b45", 238))
    draw.text((header_left[0] + 18, header_left[1] + 142), "Pale foldout neighborhood map with draggable route slips and creature errands.", font=serif(19), fill=hex_rgba("#2e3b45", 176))

    for i, (label, value) in enumerate((("MOOD", "soft drift"), ("OPEN SLIPS", "05 notes"), ("FIELD WIND", "0.28 south"))):
        x = header_left[0] + 18 + i * 156
        rounded(draw, (x, header_left[1] + 186, x + 142, header_left[1] + 236), 18, hex_rgba("#ffffff", 110), hex_rgba("#2e3b45", 24), 1)
        draw.text((x + 12, header_left[1] + 196), label, font=mono(10), fill=hex_rgba("#2e3b45", 146))
        draw.text((x + 12, header_left[1] + 212), value, font=serif(21), fill=hex_rgba("#2e3b45", 224))

    draw.text((header_right[0] + 16, header_right[1] + 16), "INTERACTION", font=mono(12), fill=hex_rgba("#2e3b45", 166))
    add_text_block(
        draw,
        header_right[0] + 16,
        header_right[1] + 46,
        [
            "Drag slips into new districts, let route gravity",
            "slowly re-cluster them, and switch morning,",
            "twilight, or rain without breaking the paper",
            "map feeling. Pointer movement acts like breeze,",
            "not like a detached HUD control."
        ],
        serif(18),
        hex_rgba("#2e3b45", 172),
        22,
    )

    draw.text((left_col[0] + 16, left_col[1] + 16), "LEGEND", font=mono(12), fill=hex_rgba("#2e3b45", 166))
    legend_lines = ["Main path / navy dash", "Side path / blue weave", "Warm errand / rose stitch", "Quiet pocket / blank cream", "Creature pause / yellow eyes"]
    for i, line in enumerate(legend_lines):
        y = left_col[1] + 46 + i * 28
        draw.line((left_col[0] + 16, y + 18, left_col[2] - 16, y + 18), fill=hex_rgba("#2e3b45", 20), width=1)
        draw.text((left_col[0] + 16, y), line, font=mono(11), fill=hex_rgba("#2e3b45", 150))

    draw.text((left_col[0] + 16, left_col[1] + 212), "CURRENT QUEUE", font=mono(12), fill=hex_rgba("#2e3b45", 166))
    queue = ["01 Sag Hill / rest", "02 The Slope / gather", "03 Hollow Lane / errand", "04 Moss Courtyard / rest", "05 Low Pipes / errand"]
    for i, line in enumerate(queue):
        y = left_col[1] + 242 + i * 26
        draw.text((left_col[0] + 16, y), line, font=mono(11), fill=hex_rgba("#2e3b45", 154))

    draw.text((left_col[0] + 16, left_col[1] + 402), "CARE CUSTOMS", font=mono(12), fill=hex_rgba("#2e3b45", 166))
    customs = ["Leave room for something good.", "Big words move slower than tiny passages.", "Routes listen before they turn.", "If a slip feels heavy, set it near the bench."]
    add_text_block(draw, left_col[0] + 16, left_col[1] + 432, customs, serif(16), hex_rgba("#2e3b45", 168), 24)

    rounded(draw, stage, 26, hex_rgba("#f3ebdf", 154), hex_rgba("#2e3b45", 24), 1)
    inner = (stage[0] + 18, stage[1] + 18, stage[2] - 18, stage[3] - 18)
    rounded(draw, inner, 26, hex_rgba("#eadfce", 210), hex_rgba("#2e3b45", 16), 1)

    for fold in range(1, 5):
        x = int(lerp(inner[0], inner[2], fold / 5))
        draw.line((x, inner[1], x, inner[3]), fill=hex_rgba("#473929", 24), width=2)

    map_area = (inner[0] + 210, inner[1] + 16, inner[2] - 220, inner[3] - 142)
    draw.text((inner[0] + 18, inner[1] + 12), "WELCOME TO", font=mono(11), fill=hex_rgba("#2e3b45", 144))
    draw.text((inner[0] + 18, inner[1] + 34), "Sag & Nest", font=serif(34), fill=hex_rgba("#213547", 238))
    draw.text((inner[0] + 18, inner[1] + 76), "steady views / soft wind", font=serif(17), fill=hex_rgba("#2e3b45", 170))

    for x in range(map_area[0], map_area[2], 54):
        draw.line((x, map_area[1], x, map_area[3]), fill=hex_rgba("#2e3b45", 12), width=1)
    for y in range(map_area[1], map_area[3], 54):
        draw.line((map_area[0], y, map_area[2], y), fill=hex_rgba("#2e3b45", 12), width=1)

    routes = [
        ((map_area[0] + 20, map_area[1] + 40), (map_area[0] + 170, map_area[1] + 110), (map_area[2] - 80, map_area[1] + 190), "#213547", 8),
        ((map_area[0] + 20, map_area[3] - 80), (map_area[0] + 180, map_area[3] - 180), (map_area[2] - 40, map_area[1] + 120), "#213547", 8),
        ((map_area[0] + 160, map_area[1] + 24), (map_area[0] + 120, map_area[1] + 220), (map_area[0] + 190, map_area[3] - 22), "#7ca8be", 5),
        ((map_area[2] - 150, map_area[1] + 24), (map_area[2] - 110, map_area[1] + 220), (map_area[2] - 220, map_area[3] - 26), "#7ca8be", 5),
        ((map_area[0] + 72, map_area[1] + 210), (map_area[0] + 280, map_area[1] + 240), (map_area[2] - 34, map_area[1] + 140), "#d49186", 4),
        ((map_area[0] + 110, map_area[3] - 22), (map_area[0] + 270, map_area[3] - 86), (map_area[2] - 30, map_area[3] - 18), "#d49186", 4),
    ]

    for a, b, c, color, width_px in routes:
        draw.line((a, b, c), fill=hex_rgba(color, 146), width=width_px)
        for step in range(7):
            t = step / 6
            x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * b[0] + t * t * c[0]
            y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * b[1] + t * t * c[1]
            r = 3 if step % 3 else 5
            draw.ellipse((x - r, y - r, x + r, y + r), fill=hex_rgba(color, 188))

    card_boxes = [
        ((map_area[0] + 12, map_area[1] + 26, map_area[0] + 188, map_area[1] + 188), "cream", "Sag Hill", "rest"),
        ((map_area[0] + 256, map_area[1] + 72, map_area[0] + 432, map_area[1] + 234), "green", "The Slope", "gather"),
        ((map_area[2] - 194, map_area[1] + 52, map_area[2] - 18, map_area[1] + 214), "cream", "Hollow Lane", "errand"),
        ((map_area[0] + 108, map_area[3] - 210, map_area[0] + 284, map_area[3] - 48), "cream", "Moss Courtyard", "rest"),
        ((map_area[2] - 262, map_area[3] - 170, map_area[2] - 86, map_area[3] - 8), "green", "Low Pipes", "errand"),
    ]
    for box, tone, title, tag in card_boxes:
        creature_card(draw, box, tone, title, tag)

    for x, y, label in ((map_area[0] + 6, map_area[3] - 74, "N"), (map_area[2] - 94, map_area[3] - 40, "DAY"), (map_area[0] + 340, map_area[1] + 12, "S")):
        draw.ellipse((x, y, x + 54, y + 54), fill=hex_rgba("#fffaf2", 92), outline=hex_rgba("#2e3b45", 42), width=1)
        draw.text((x + 15, y + 17), label, font=mono(12), fill=hex_rgba("#2e3b45", 156))

    right_start = right_col[1] + 16
    draw.text((right_col[0] + 16, right_start), "ROUTE NOTES", font=mono(12), fill=hex_rgba("#2e3b45", 166))
    rounded(draw, (right_col[0] + 14, right_start + 26, right_col[2] - 14, right_start + 116), 18, hex_rgba("#ffffff", 98), hex_rgba("#2e3b45", 20), 1)
    draw.text((right_col[0] + 26, right_start + 40), "Sag Hill", font=serif(23), fill=hex_rgba("#2e3b45", 224))
    draw.text((right_col[0] + 26, right_start + 70), "Quiet standing spot with slow wind and no urgent traffic.", font=serif(15), fill=hex_rgba("#2e3b45", 168))
    rounded(draw, (right_col[0] + 14, right_start + 132, right_col[2] - 14, right_start + 294), 18, hex_rgba("#ffffff", 98), hex_rgba("#2e3b45", 20), 1)
    draw.text((right_col[0] + 26, right_start + 146), "POCKET RESIDENT", font=mono(11), fill=hex_rgba("#2e3b45", 146))
    draw.ellipse((right_col[0] + 74, right_start + 190, right_col[0] + 226, right_start + 318), fill=hex_rgba("#efe7dc", 252), outline=hex_rgba("#2e3b45", 34), width=2)
    draw.ellipse((right_col[0] + 102, right_start + 214, right_col[0] + 130, right_start + 242), fill=hex_rgba("#f5cd58", 255), outline=hex_rgba("#2e3b45", 70), width=2)
    draw.ellipse((right_col[0] + 156, right_start + 214, right_col[0] + 184, right_start + 242), fill=hex_rgba("#f5cd58", 255), outline=hex_rgba("#2e3b45", 70), width=2)
    draw.ellipse((right_col[0] + 112, right_start + 222, right_col[0] + 120, right_start + 230), fill=hex_rgba("#1d2529", 255))
    draw.ellipse((right_col[0] + 166, right_start + 222, right_col[0] + 174, right_start + 230), fill=hex_rgba("#1d2529", 255))
    draw.arc((right_col[0] + 126, right_start + 248, right_col[0] + 162, right_start + 268), start=10, end=170, fill=hex_rgba("#1d2529", 255), width=2)

    reminders_y = right_start + 322
    draw.text((right_col[0] + 16, reminders_y), "SMALL REMINDERS", font=mono(12), fill=hex_rgba("#2e3b45", 166))
    reminders = [
        "Drag slips to alter the board's soft logic.",
        "Routes settle slowly, not instantly.",
        "Rain mode narrows paths and deepens blue flow."
    ]
    add_text_block(draw, right_col[0] + 16, reminders_y + 28, reminders, serif(16), hex_rgba("#2e3b45", 166), 26)

    lower_y = inner[3] - 108
    slip_w = (inner[2] - inner[0] - 24) / 3
    for i, (title, text) in enumerate((
        ("Between places", "Some paths are not for today."),
        ("Passages", "The board clusters slips around hidden route families."),
        ("Weather mood", "Morning airy, twilight warmer, rain tighter."),
    )):
        x0 = inner[0] + i * slip_w + 4 * i
        box = (int(x0), lower_y, int(x0 + slip_w - 8), inner[3] - 16)
        rounded(draw, box, 18, hex_rgba("#fffaf2", 110), hex_rgba("#2e3b45", 18), 1)
        draw.text((box[0] + 14, box[1] + 12), title.upper(), font=mono(11), fill=hex_rgba("#2e3b45", 146))
        draw.text((box[0] + 14, box[1] + 38), text, font=serif(16), fill=hex_rgba("#2e3b45", 168))

    draw.text((right_col[0] + 16, right_col[3] - 118), "BRANCH FIT", font=mono(12), fill=hex_rgba("#2e3b45", 166))
    branch_lines = [
        "Design-usable HTML object, not another dark console.",
        "Keeps creature warmth without mascot centralization.",
        "Extends the foldout civic image lane into motion.",
    ]
    add_text_block(draw, right_col[0] + 16, right_col[3] - 90, branch_lines, serif(15), hex_rgba("#2e3b45", 166), 22)

    card_w = (footer[2] - footer[0] - 28) / 3
    labels = [
        ("IDEA", "Turn the Sag & Nest foldout into a living browser object."),
        ("INTERACTION", "Drag cards, stir the field, and switch the shared weather."),
        ("NEXT", "Later accept real Telegram fragments as incoming slips."),
    ]
    for i, (label, text) in enumerate(labels):
        x0 = footer[0] + 8 + i * (card_w + 6)
        box = (int(x0), footer[1] + 10, int(x0 + card_w - 6), footer[3] - 10)
        rounded(draw, box, 22, hex_rgba("#fffaf2", 114), hex_rgba("#2e3b45", 20), 1)
        draw.text((box[0] + 14, box[1] + 14), label, font=mono(12), fill=hex_rgba("#2e3b45", 154))
        draw.text((box[0] + 14, box[1] + 42), text, font=serif(18), fill=hex_rgba("#2e3b45", 172))

    image = Image.alpha_composite(image, ui)
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
