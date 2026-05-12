#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


BG = (5, 7, 10)
CYAN = (130, 215, 234)
MAGENTA = (255, 107, 151)
AMBER = (239, 187, 127)
ACID = (209, 239, 98)
TEXT = (214, 221, 225)
MUTED = (128, 144, 153)


def rgba(color: tuple[int, int, int], alpha: int) -> tuple[int, int, int, int]:
    return color[0], color[1], color[2], alpha


def font(size: int):
    for path in (
        "/System/Library/Fonts/Supplemental/Arial Narrow.ttf",
        "/System/Library/Fonts/Supplemental/Trebuchet MS.ttf",
        "/System/Library/Fonts/SFNS.ttf",
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


def gradient(size: tuple[int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size, BG + (255,))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / max(1, height - 1)
        color = (
            int(11 - 9 * t),
            int(15 - 12 * t),
            int(19 - 15 * t),
            255,
        )
        draw.line((0, y, width, y), fill=color)
    return image


def radial(size: tuple[int, int], center: tuple[float, float], radius: float, color: tuple[int, int, int], alpha: int) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for step in range(18, 0, -1):
        t = step / 18
        r = radius * t
        draw.ellipse(
            (center[0] - r, center[1] - r, center[0] + r, center[1] + r),
            fill=rgba(color, int(alpha * (t**2) * 0.34)),
        )
    return layer.filter(ImageFilter.GaussianBlur(radius * 0.08))


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def render(output: Path, width: int, height: int) -> None:
    rng = random.Random(49)
    image = gradient((width, height))
    for center, radius, color, alpha in (
        ((width * 0.5, height * 0.16), width * 0.24, (40, 58, 69), 130),
        ((width * 0.82, height * 0.28), width * 0.18, (127, 36, 53), 100),
        ((width * 0.18, height * 0.82), width * 0.19, (20, 71, 82), 90),
    ):
        image = Image.alpha_composite(image, radial((width, height), center, radius, color, alpha))

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    step = max(34, width // 28)
    for x in range(0, width, step):
        draw.line((x, 0, x, height), fill=(124, 160, 171, 18), width=1)
    for y in range(0, height, step):
        draw.line((0, y, width, y), fill=(124, 160, 171, 18), width=1)

    margin = 18
    main = (margin, 38, width - margin, height - 24)
    left_w = int((main[2] - main[0] - 16) * 0.63)
    right_x = main[0] + left_w + 16
    panel = (main[0], 58, main[0] + left_w, height - 220)
    stack = (right_x, 58, main[2], height - 220)

    for rect in (panel, stack):
        rounded(draw, rect, 28, (8, 11, 15, 226), (123, 174, 188, 44), 2)
        rounded(draw, (rect[0] + 12, rect[1] + 12, rect[2] - 12, rect[3] - 12), 22, None, (115, 157, 170, 28), 1)

    draw.text((main[0] + 6, 12), "#049 generated animation", font=mono(12), fill=rgba(MUTED, 210))
    draw.text((main[2] - 264, 12), "browser-native SVG + canvas dossier", font=mono(12), fill=rgba(MUTED, 210))

    title_font = font(44)
    small_font = mono(12)
    body_font = font(20)
    draw.text((panel[0] + 20, panel[1] + 18), "Code Animation Study #049", font=small_font, fill=rgba(MUTED, 220))
    draw.text((panel[0] + 20, panel[1] + 42), "Signal Husk\nDossier", font=title_font, fill=rgba(TEXT, 238), spacing=4)
    draw.text(
        (panel[2] - 270, panel[1] + 22),
        "One grounded three-dot organism with\nclocked relay windows and embedded\nroute-glass seams.",
        font=font(18),
        fill=rgba(TEXT, 190),
        spacing=4,
        align="right",
    )

    board = (panel[0] + 44, panel[1] + 106, panel[2] - 44, panel[3] - 42)
    rounded(draw, board, 32, (10, 15, 20, 164), (129, 187, 202, 34), 1)
    rounded(draw, (board[0] + 18, board[1] + 18, board[2] - 18, board[3] - 18), 26, None, (129, 187, 202, 20), 1)

    for i in range(18):
        cx = board[0] + 86 + (i % 6) * 62 + (i // 6) * 10
        cy = board[1] + 88 + (i // 6) * 126
        r = 34 if i % 3 == 0 else 18
        col = CYAN if i % 2 == 0 else MAGENTA
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=rgba(col, 30), width=1)

    for i in range(16):
        y = board[1] + 54 + (i // 4) * 122
        x0 = board[0] + 42 + (i % 4) * 138
        x3 = board[2] - 56 + (i % 3) * 14
        bend = math.sin(i * 0.7) * 18
        pts = [
            (x0, y),
            (x0 + 84, y + 10 + bend * 0.2),
            (x3 - 68, y - 8 + bend * 0.3),
            (x3, y + bend * 0.22),
        ]
        draw.line(pts, fill=rgba(CYAN if i % 2 == 0 else MAGENTA, 72), width=2)

    body = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(body, "RGBA")
    cx = board[0] + (board[2] - board[0]) * 0.33
    cy = board[1] + (board[3] - board[1]) * 0.43
    shell = [
        (cx - 74, cy - 154),
        (cx - 120, cy - 102),
        (cx - 112, cy + 26),
        (cx - 58, cy + 148),
        (cx + 42, cy + 150),
        (cx + 116, cy + 64),
        (cx + 108, cy - 76),
        (cx + 32, cy - 154),
    ]
    bdraw.polygon(shell, fill=(13, 19, 25, 236), outline=rgba(CYAN, 110))
    back = [
        (cx - 42, cy - 126),
        (cx - 114, cy - 54),
        (cx - 98, cy + 48),
        (cx - 10, cy + 118),
        (cx + 98, cy + 88),
        (cx + 130, cy - 14),
        (cx + 44, cy - 132),
    ]
    bdraw.polygon(back, fill=rgba(CYAN, 34), outline=rgba(CYAN, 54))
    bdraw.line((cx - 8, cy - 118, cx - 4, cy - 46, cx - 12, cy + 18, cx - 2, cy + 98), fill=rgba(MAGENTA, 180), width=3)
    bdraw.line((cx - 10, cy - 118, cx - 4, cy - 46, cx - 12, cy + 18, cx - 2, cy + 98), fill=rgba(CYAN, 80), width=14)
    for i in range(5):
        fx = cx + (i - 2) * 26
        bdraw.line((cx - 2, cy - 122, fx + (i - 2) * 12, cy - 204 + abs(i - 2) * 10), fill=rgba(CYAN if i % 2 == 0 else AMBER, 120), width=2)
    bead_positions = [
        (cx - 42, cy - 152), (cx - 24, cy - 174), (cx - 4, cy - 194), (cx + 18, cy - 174), (cx + 38, cy - 152)
    ]
    for i, (bx, by) in enumerate(bead_positions):
        col = CYAN if i % 2 == 0 else AMBER
        r = 6 if i == 2 else 5
        bdraw.ellipse((bx - r, by - r, bx + r, by + r), fill=rgba(col, 230))
    for ex, ey, r, col in ((cx - 20, cy - 74, 7, CYAN), (cx, cy - 82, 6, MAGENTA), (cx + 20, cy - 74, 7, CYAN)):
        bdraw.ellipse((ex - r, ey - r, ex + r, ey + r), fill=rgba(col, 235))
    bdraw.arc((cx - 18, cy - 50, cx + 18, cy - 18), start=14, end=166, fill=rgba(AMBER, 220), width=2)
    bdraw.line((cx - 56, cy + 146, cx - 116, cy + 246, cx - 162, cy + 298), fill=rgba(AMBER, 210), width=5)
    bdraw.line((cx + 52, cy + 146, cx + 112, cy + 244, cx + 186, cy + 300), fill=rgba(AMBER, 210), width=5)
    image = Image.alpha_composite(image, body.filter(ImageFilter.GaussianBlur(10)))
    image = Image.alpha_composite(image, body)

    for i in range(11):
        y = cy - 118 + i * 24
        x = cx + 94 + (i % 3) * 12
        draw.line((x, y, x + 16 + (i % 3) * 6, y), fill=rgba(ACID, 130), width=1)

    for i in range(6):
        x = board[0] + 38 + i * 72
        y = board[3] - 56 + math.sin(i * 0.8) * 4
        ex = x + 44 + (12 if i % 2 == 0 else -10)
        ey = y + (-12 if i % 2 == 0 else 12)
        draw.line((x, y, (x + ex) / 2, (y + ey) / 2, ex, ey), fill=rgba(CYAN if i % 2 == 0 else MAGENTA, 96), width=2)
        draw.ellipse((ex - 4, ey - 4, ex + 4, ey + 4), fill=rgba(CYAN if i % 2 == 0 else AMBER, 220))

    panel_x = stack[0] + 16
    panel_w = stack[2] - stack[0] - 32
    card_y = stack[1] + 16
    card_h = 118
    for idx in range(4):
        h = card_h if idx != 1 else 144
        box = (panel_x, card_y, panel_x + panel_w, card_y + h)
        rounded(draw, box, 22, (10, 14, 19, 204), (115, 157, 170, 38), 1)
        card_y += h + 16

    draw.text((panel_x + 16, stack[1] + 30), "PHASE OVERRIDES", font=small_font, fill=rgba(MUTED, 220))
    chips = [("BRACE", True), ("SIFT", False), ("FLARE", False)]
    chip_x = panel_x + 16
    chip_y = stack[1] + 56
    for label, active in chips:
        tw = 86 if label != "FLARE" else 84
        rounded(draw, (chip_x, chip_y, chip_x + tw, chip_y + 30), 999, rgba(CYAN if active else TEXT, 30 if active else 12), rgba(CYAN if active else TEXT, 58 if active else 24), 1)
        draw.text((chip_x + 14, chip_y + 8), label, font=mono(12), fill=rgba(TEXT, 220))
        chip_x += tw + 8

    draw.text((panel_x + 16, stack[1] + 106), "hold  ->  sift  ->  flare", font=mono(12), fill=rgba(TEXT, 170))

    readout_top = stack[1] + 150
    draw.text((panel_x + 16, readout_top + 14), "FIELD READOUTS", font=small_font, fill=rgba(TEXT, 220))
    for i, (label, value, col) in enumerate((("BRACING", 0.78, CYAN), ("DRIFT", 0.52, MAGENTA), ("BLOOM", 0.66, AMBER))):
        y = readout_top + 44 + i * 32
        draw.text((panel_x + 16, y), label, font=mono(12), fill=rgba(MUTED, 220))
        rounded(draw, (panel_x + 104, y + 2, panel_x + panel_w - 54, y + 12), 999, (255, 255, 255, 14), None, 1)
        rounded(draw, (panel_x + 104, y + 2, panel_x + 104 + (panel_w - 158) * value, y + 12), 999, rgba(col, 170), None, 1)
        draw.text((panel_x + panel_w - 42, y - 2), f"{value:.2f}", font=mono(12), fill=rgba(TEXT, 210))

    route_top = stack[1] + 312
    draw.text((panel_x + 16, route_top + 14), "ROUTE GLASS", font=small_font, fill=rgba(TEXT, 220))
    rounded(draw, (panel_x + 16, route_top + 34, panel_x + panel_w - 16, route_top + 132), 18, (255, 255, 255, 8), (115, 157, 170, 24), 1)
    for i in range(5):
        y = route_top + 56 + i * 18
        bend = 18 if i == 1 else -4 if i == 4 else 8
        points = [(panel_x + 32, y), (panel_x + 96, y - 8 + bend * 0.3), (panel_x + 154, y + 8 + bend), (panel_x + panel_w - 30, y - bend * 0.2)]
        draw.line(points, fill=rgba(MAGENTA if i == 1 else CYAN, 150 if i == 1 else 92), width=2)

    why_top = stack[1] + 446
    draw.text((panel_x + 16, why_top + 14), "WHY THIS BRANCH", font=small_font, fill=rgba(TEXT, 220))
    why = "Design-usable dossier language, one plausible body,\nand timed relay handoffs instead of detached cards\nor implausible extra anatomy."
    draw.multiline_text((panel_x + 16, why_top + 40), why, font=font(16), fill=rgba(TEXT, 178), spacing=4)

    footer_y = height - 188
    gap = 16
    card_w = (width - 36 - gap * 2) / 3
    for i, title in enumerate(("IDEA", "INTERACTION", "NEXT")):
        x = 18 + i * (card_w + gap)
        rounded(draw, (x, footer_y, x + card_w, footer_y + 146), 24, (8, 11, 15, 214), (123, 174, 188, 36), 1)
        draw.text((x + 16, footer_y + 16), title, font=small_font, fill=rgba(MUTED, 220))
        copy = (
            "Embedded specimen dossier\nwith scheduled release\nwindows." if i == 0 else
            "Relay cycle runs first;\npointer only biases the\nactive phase locally." if i == 1 else
            "Scale into a wider field\nmanual or make the\ntimetable editable."
        )
        draw.multiline_text((x + 16, footer_y + 42), copy, font=font(17), fill=rgba(TEXT, 180), spacing=4)

    rounded(draw, (width - 166, height - 54, width - 18, height - 18), 999, (7, 10, 14, 210), (123, 174, 188, 38), 1)
    draw.text((width - 142, height - 42), "BACK TO INDEX", font=mono(12), fill=rgba(TEXT, 220))

    for _ in range(220):
        x = rng.uniform(0, width)
        y = rng.uniform(0, height)
        r = rng.uniform(0.6, 2.1)
        col = CYAN if rng.random() < 0.58 else MAGENTA
        draw.ellipse((x - r, y - r, x + r, y + r), fill=rgba(col, rng.randint(18, 54)))

    overlay = overlay.filter(ImageFilter.GaussianBlur(0.6))
    image = Image.alpha_composite(image, overlay)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output, "PNG")


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
