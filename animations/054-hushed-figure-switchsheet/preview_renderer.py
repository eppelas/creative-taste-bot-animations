#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


PAPER_TOP = (247, 239, 231)
PAPER_MID = (239, 228, 213)
PAPER_BOTTOM = (220, 202, 183)
INK = (46, 58, 68)
MUTED = (110, 108, 104)
CYAN = (130, 191, 213)
ROSE = (216, 139, 138)
MOSS = (151, 168, 132)
AMBER = (214, 166, 111)
PLUM = (119, 101, 125)


def rgba(color: tuple[int, int, int], alpha: int) -> tuple[int, int, int, int]:
    return color[0], color[1], color[2], alpha


def load_font(size: int):
    for path in (
        "/System/Library/Fonts/Supplemental/Palatino.ttc",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def load_mono(size: int):
    for path in (
        "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def gradient(width: int, height: int) -> Image.Image:
    image = Image.new("RGBA", (width, height), PAPER_BOTTOM + (255,))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(
            round(PAPER_TOP[i] + (PAPER_BOTTOM[i] - PAPER_TOP[i]) * t) for i in range(3)
        ) + (255,)
        draw.line((0, y, width, y), fill=color)
    return image


def add_halo(base: Image.Image, cx: float, cy: float, radius: float, color: tuple[int, int, int], alpha: int) -> Image.Image:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=rgba(color, alpha))
    return Image.alpha_composite(base, layer.filter(ImageFilter.GaussianBlur(radius=max(8, int(radius * 0.28)))))


def draw_grid(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    for x in range(0, width + 96, 96):
        draw.line((x, 0, x, height), fill=rgba(INK, 18), width=1)
    for y in range(0, height + 96, 96):
        draw.line((0, y, width, y), fill=rgba(INK, 18), width=1)


def draw_figure(draw: ImageDraw.ImageDraw, cx: float, base_y: float, scale: float, accent: tuple[int, int, int]) -> None:
    head_y = base_y - 120 * scale
    shoulder_y = base_y - 86 * scale
    hip_y = base_y - 28 * scale
    head_w = 16 * scale
    line_w = max(2, int(6 * scale))
    thin = max(1, int(3 * scale))

    draw.ellipse((cx - head_w, head_y - head_w * 1.1, cx + head_w, head_y + head_w * 1.1), fill=rgba(accent, 34), outline=rgba(INK, 160), width=thin)
    draw.line((cx, head_y + head_w * 0.9, cx - 8 * scale, shoulder_y, cx - 14 * scale, hip_y), fill=rgba(INK, 188), width=line_w, joint="curve")
    draw.line((cx - 6 * scale, shoulder_y + 8 * scale, cx - 46 * scale, shoulder_y + 40 * scale, cx - 56 * scale, shoulder_y + 86 * scale), fill=rgba(accent, 190), width=max(2, int(4 * scale)), joint="curve")
    draw.line((cx - 2 * scale, shoulder_y + 6 * scale, cx + 44 * scale, shoulder_y + 34 * scale, cx + 54 * scale, shoulder_y + 84 * scale), fill=rgba(INK, 176), width=max(2, int(4 * scale)), joint="curve")
    draw.line((cx - 14 * scale, hip_y, cx - 34 * scale, base_y - 10 * scale, cx - 20 * scale, base_y + 58 * scale), fill=rgba(INK, 188), width=max(2, int(5 * scale)), joint="curve")
    draw.line((cx - 14 * scale, hip_y, cx + 18 * scale, base_y - 14 * scale, cx + 34 * scale, base_y + 50 * scale), fill=rgba(INK, 188), width=max(2, int(5 * scale)), joint="curve")
    draw.arc((cx - 18 * scale, head_y + 10 * scale, cx + 18 * scale, head_y + 28 * scale), 15, 165, fill=rgba(INK, 120), width=thin)
    draw.ellipse((cx - 8 * scale, head_y - 2 * scale, cx - 4 * scale, head_y + 2 * scale), fill=rgba(INK, 180))
    draw.ellipse((cx + 4 * scale, head_y - 2 * scale, cx + 8 * scale, head_y + 2 * scale), fill=rgba(INK, 180))

    reflection = Image.new("RGBA", draw._image.size, (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(reflection, "RGBA")
    rdraw.polygon(
        [
            (cx - 26 * scale, base_y + 10 * scale),
            (cx + 22 * scale, base_y + 10 * scale),
            (cx + 6 * scale, base_y + 84 * scale),
            (cx - 16 * scale, base_y + 84 * scale),
        ],
        fill=rgba(accent, 48),
    )
    reflection = reflection.filter(ImageFilter.GaussianBlur(radius=max(3, int(10 * scale))))
    draw._image.alpha_composite(reflection)


def draw_card(draw: ImageDraw.ImageDraw, box, label: str, code: str, accent: tuple[int, int, int], scale: float) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=26, fill=(255, 249, 242, 172), outline=rgba(INK, 34), width=1)
    draw.rounded_rectangle((x0 + 10, y0 + 10, x1 - 10, y1 - 10), radius=20, outline=rgba((255, 255, 255), 94), width=1)
    glow = Image.new("RGBA", draw._image.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow, "RGBA")
    gdraw.ellipse((x0 + 24, y0 + 18, x1 - 24, y0 + (y1 - y0) * 0.54), fill=rgba((255, 255, 255), 68))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=16))
    draw._image.alpha_composite(glow)

    for i in range(4):
      draw.line((x0 + 20 + i * 28, y0 + 24 + i * 10, x0 + 36 + i * 28, y0 + 96 + i * 16), fill=rgba((255, 255, 255), 82), width=1)

    draw.line((x0 + 24, y0 + 150, x1 - 24, y0 + 182), fill=rgba(accent, 112), width=2)
    draw.line((x0 + 30, y0 + 214, x1 - 30, y0 + 208), fill=rgba(INK, 48), width=2)
    draw_figure(draw, (x0 + x1) * 0.5, y0 + 180, scale, accent)

    draw.text((x0 + 16, y1 - 34), label.upper(), font=load_mono(11), fill=rgba(MUTED, 214))
    draw.text((x1 - 54, y1 - 34), code.upper(), font=load_mono(11), fill=rgba(MUTED, 214))


def render(output: Path, width: int, height: int) -> None:
    image = gradient(width, height)
    for cx, cy, radius, color, alpha in (
        (width * 0.18, height * 0.16, width * 0.18, CYAN, 34),
        (width * 0.82, height * 0.16, width * 0.16, ROSE, 30),
        (width * 0.18, height * 0.82, width * 0.14, MOSS, 24),
        (width * 0.72, height * 0.8, width * 0.14, AMBER, 22),
    ):
        image = add_halo(image, cx, cy, radius, color, alpha)

    draw = ImageDraw.Draw(image, "RGBA")
    draw_grid(draw, width, height)

    panel = (34, 34, 470, 324)
    draw.rounded_rectangle(panel, radius=28, fill=(255, 250, 243, 176), outline=rgba(INK, 28), width=1)
    draw.text((58, 58), "CODE ANIMATION STUDY #054", font=load_mono(12), fill=rgba(MUTED, 210))
    draw.text((58, 98), "Hushed Figure\nSwitchsheet", font=load_font(52), fill=rgba(INK, 235), spacing=0)
    draw.text((58, 220), "Human illustration modules instead of", font=load_font(20), fill=rgba(INK, 190))
    draw.text((58, 246), "another dark dashboard or creature plate.", font=load_font(20), fill=rgba(INK, 190))
    draw.text((58, 282), "Route weather + pointer focus", font=load_font(18), fill=rgba(MUTED, 210))

    side = (836, 40, 1046, 728)
    draw.rounded_rectangle(side, radius=28, fill=(255, 250, 243, 176), outline=rgba(INK, 28), width=1)
    draw.text((860, 66), "SHEET MODES", font=load_mono(12), fill=rgba(MUTED, 210))

    mode_boxes = [
        ((858, 106, 1024, 206), "QUEUE", "Queue braid", CYAN),
        ((858, 220, 1024, 320), "HUSH", "Hushed drift", MOSS),
        ((858, 334, 1024, 434), "DRIFT", "Rain offset", AMBER),
    ]
    for box, title, subtitle, accent in mode_boxes:
        draw.rounded_rectangle(box, radius=18, fill=(255, 252, 246, 162), outline=rgba(INK, 28), width=1)
        draw.text((box[0] + 14, box[1] + 14), title, font=load_mono(11), fill=rgba(MUTED, 214))
        draw.text((box[0] + 14, box[1] + 42), subtitle, font=load_font(22), fill=rgba(INK, 205))
        draw.line((box[0] + 14, box[3] - 18, box[2] - 14, box[3] - 18), fill=rgba(accent, 140), width=2)

    status_rows = [
        ((858, 470, 1024, 524), "FOCUS", "Station A3"),
        ((858, 536, 1024, 590), "WEATHER", "Hushed drift"),
        ((858, 602, 1024, 656), "PULSE", "Low traffic"),
    ]
    for box, label, value in status_rows:
        draw.rounded_rectangle(box, radius=16, fill=(255, 252, 246, 154), outline=rgba(INK, 24), width=1)
        draw.text((box[0] + 12, box[1] + 12), label, font=load_mono(10), fill=rgba(MUTED, 206))
        draw.text((box[0] + 12, box[1] + 28), value, font=load_font(18), fill=rgba(INK, 210))

    cards = [
        ((118, 372, 326, 628), "Station A3", "Lean", CYAN, 1.0),
        ((400, 332, 646, 636), "Route B7", "Carry", ROSE, 1.06),
        ((690, 382, 898, 628), "Slip C2", "Wait", MOSS, 0.96),
        ((200, 708, 430, 1002), "Atrium D5", "Bend", AMBER, 1.08),
        ((540, 696, 782, 1006), "Hall E1", "Turn", PLUM, 1.02),
    ]
    for box, label, code, accent, scale in cards:
        draw_card(draw, box, label, code, accent, scale)

    route_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(route_layer, "RGBA")
    points = [
        (222, 486),
        (522, 474),
        (794, 490),
        (308, 846),
        (664, 852),
    ]
    colors = [CYAN, ROSE, MOSS, AMBER]
    for idx in range(len(points) - 1):
        ax, ay = points[idx]
        bx, by = points[idx + 1]
        mx = (ax + bx) * 0.5
        rdraw.line((ax, ay, mx, ay - 42 + idx * 10, bx, by), fill=rgba(colors[idx % len(colors)], 114), width=2, joint="curve")
    route_layer = route_layer.filter(ImageFilter.GaussianBlur(radius=1))
    image.alpha_composite(route_layer)

    focus = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(focus, "RGBA")
    fdraw.ellipse((382, 204, 760, 582), fill=rgba((255, 255, 255), 56))
    fdraw.ellipse((520, 524, 864, 868), fill=rgba(MOSS, 40))
    focus = focus.filter(ImageFilter.GaussianBlur(radius=42))
    image.alpha_composite(focus)

    footer_y = 1136
    footer_w = (width - 68 - 24 * 2) // 3
    notes = [
        ("IDEA", "Human modules keep the design lane alive,\nnot another interface creature."),
        ("INTERACTION", "Pointer focus sharpens nearby cards\nand bends the sheet weather."),
        ("NEXT", "Later: feed real text fragments into\nthe module arrangement."),
    ]
    for idx, (title, copy) in enumerate(notes):
        x = 34 + idx * (footer_w + 24)
        draw.rounded_rectangle((x, footer_y, x + footer_w, 1310), radius=24, fill=(255, 250, 243, 170), outline=rgba(INK, 26), width=1)
        draw.text((x + 18, footer_y + 18), title, font=load_mono(12), fill=rgba(MUTED, 210))
        draw.text((x + 18, footer_y + 58), copy, font=load_font(22), fill=rgba(INK, 190), spacing=5)

    noise = ImageDraw.Draw(image, "RGBA")
    for x in range(0, width, 4):
        for y in range(0, height, 4):
            alpha = 8 if (x + y) % 16 == 0 else 0
            if alpha:
                noise.point((x, y), fill=(255, 255, 255, alpha))

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
