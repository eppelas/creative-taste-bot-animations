#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


BG = "#eef4f4"
INK = "#294354"
MUTED = (41, 67, 84, 168)
LINE = (33, 60, 80, 34)
PAPER = (255, 255, 255, 154)
BLUE = "#8dd2ff"
BLUE_DEEP = "#4e9ecf"
PEACH = "#ffc3a6"


def hex_rgba(value: str, alpha: int) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def vertical_gradient(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size)
    draw = ImageDraw.Draw(image)
    top_rgb = hex_rgba(top, 255)
    bottom_rgb = hex_rgba(bottom, 255)
    for y in range(height):
        t = y / max(height - 1, 1)
        color = tuple(int(lerp(top_rgb[i], bottom_rgb[i], t)) for i in range(3)) + (255,)
        draw.line((0, y, width, y), fill=color)
    return image


def radial_glow(size: tuple[int, int], center: tuple[float, float], radius: float, color: str, alpha: int) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for step in range(18, 0, -1):
        t = step / 18
        current_radius = radius * t
        current_alpha = int(alpha * (t**2) * 0.4)
        draw.ellipse(
            (
                center[0] - current_radius,
                center[1] - current_radius,
                center[0] + current_radius,
                center[1] + current_radius,
            ),
            fill=hex_rgba(color, current_alpha),
        )
    return layer.filter(ImageFilter.GaussianBlur(radius * 0.08))


def draw_round_rect(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], radius: float, fill, outline, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_panel_shell(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float]) -> None:
    x0, y0, x1, y1 = box
    draw_round_rect(draw, box, min((x1 - x0), (y1 - y0)) * 0.12, PAPER, LINE, 2)


def draw_creature(base: Image.Image, width: int, height: int) -> None:
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    cx = width * 0.51
    cy = height * 0.59
    body_w = width * 0.34
    body_h = height * 0.19

    draw_round_rect(
        draw,
        (cx - body_w * 0.58, cy + body_h * 0.42, cx + body_w * 0.54, cy + body_h * 0.95),
        body_h * 0.18,
        hex_rgba("#d8e7ee", 132),
        hex_rgba(BLUE_DEEP, 48),
        2,
    )

    for leg_index in range(10):
        side = -1 if leg_index < 5 else 1
        local = leg_index % 5
        root_x = cx - body_w * 0.18 + local * body_w * 0.08
        root_y = cy + body_h * 0.2
        target_x = root_x + side * body_w * (0.22 + local * 0.01)
        target_y = cy + body_h * (0.7 + local * 0.08)
        mid_x = root_x + side * body_w * (0.08 + local * 0.01)
        mid_y = cy + body_h * 0.58
        draw.line((root_x, root_y, mid_x, mid_y, target_x, target_y), fill=hex_rgba(BLUE, 160), width=12, joint="curve")
        draw.line((root_x, root_y, mid_x, mid_y, target_x, target_y), fill=(255, 255, 255, 120), width=4, joint="curve")

    for probe_index in range(6):
        px = cx - body_w * 0.12 + probe_index * body_w * 0.08
        py = cy - body_h * (0.08 if probe_index % 2 == 0 else -0.02)
        tx = width * (0.61 + probe_index * 0.026)
        ty = height * (0.28 + probe_index * 0.07)
        draw.line((px, py, (px + tx) * 0.5, py - body_h * 0.68, tx, ty), fill=hex_rgba(INK, 120), width=2, joint="curve")
        draw.ellipse((tx - 3, ty - 3, tx + 3, ty + 3), fill=hex_rgba(INK, 220))

    glow = radial_glow((width, height), (cx - body_w * 0.05, cy - body_h * 0.03), body_w * 0.45, PEACH, 110)
    base.alpha_composite(glow)

    shell = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shell)
    shell_box = (cx - body_w * 0.48, cy - body_h * 0.38, cx + body_w * 0.48, cy + body_h * 0.38)
    sdraw.ellipse(shell_box, fill=hex_rgba("#dff3ff", 126), outline=hex_rgba(BLUE_DEEP, 160), width=2)
    sdraw.ellipse((cx - body_w * 0.3, cy - body_h * 0.18, cx + body_w * 0.22, cy + body_h * 0.12), fill=hex_rgba(PEACH, 96))
    sdraw.arc((cx - body_w * 0.34, cy - body_h * 0.28, cx + body_w * 0.34, cy + body_h * 0.08), 188, 360, fill=(255, 255, 255, 150), width=2)
    sdraw.arc((cx - body_w * 0.12, cy - body_h * 0.02, cx + body_w * 0.34, cy + body_h * 0.26), 198, 348, fill=(255, 255, 255, 120), width=2)

    for dot_index in range(26):
        x = cx - body_w * 0.3 + (dot_index % 13) * body_w * 0.046
        y = cy + body_h * 0.06 + (dot_index // 13) * body_h * 0.08
        radius = 2 if dot_index % 4 == 0 else 1
        sdraw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=hex_rgba(INK if dot_index % 3 == 0 else "#ffffff", 150))

    base.alpha_composite(shell)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.3)))


def draw_small_panels(base: Image.Image, width: int, height: int) -> None:
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    panels = [
        (0.05, 0.08, 0.2, 0.28, "blob"),
        (0.3, 0.08, 0.65, 0.16, "chips"),
        (0.73, 0.08, 0.95, 0.28, "branch"),
        (0.08, 0.34, 0.18, 0.48, "slider"),
        (0.82, 0.34, 0.95, 0.43, "shell"),
        (0.82, 0.44, 0.95, 0.55, "dial"),
        (0.81, 0.58, 0.96, 0.68, "tracks"),
        (0.03, 0.74, 0.2, 0.91, "orbit"),
        (0.22, 0.76, 0.41, 0.9, "wave"),
        (0.42, 0.76, 0.62, 0.9, "dots"),
        (0.64, 0.76, 0.81, 0.9, "swell"),
        (0.84, 0.76, 0.98, 0.9, "spray"),
    ]

    for left, top, right, bottom, kind in panels:
        box = (width * left, height * top, width * right, height * bottom)
        draw_panel_shell(draw, box)
        x0, y0, x1, y1 = box
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        pw = x1 - x0
        ph = y1 - y0

        if kind in {"blob", "shell"}:
          draw.ellipse((cx - pw * 0.22, cy - ph * 0.22, cx + pw * 0.2, cy + ph * 0.18), fill=hex_rgba(BLUE, 110), outline=hex_rgba(BLUE_DEEP, 90), width=2)
          draw.ellipse((cx - pw * 0.1, cy + ph * 0.02, cx + pw * 0.08, cy + ph * 0.2), fill=hex_rgba(PEACH, 90))
        elif kind == "chips":
            for index in range(7):
                px = x0 + pw * (0.22 + index * 0.1)
                py = y0 + ph * 0.5
                radius = ph * 0.14
                fill = BLUE_DEEP if index == 0 else (PEACH if index > 3 else BLUE)
                draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=hex_rgba(fill, 160), outline=hex_rgba("#ffffff", 120))
        elif kind == "branch":
            base_x = x0 + pw * 0.36
            base_y = y1 - ph * 0.12
            for index in range(6):
                draw.line(
                    (
                        base_x,
                        base_y,
                        base_x + pw * (-0.05 + index * 0.08),
                        y0 + ph * (0.18 + index * 0.1),
                    ),
                    fill=hex_rgba(BLUE_DEEP if index < 4 else PEACH, 120),
                    width=2,
                )
        elif kind == "slider":
            draw_round_rect(draw, (x0 + pw * 0.22, y0 + ph * 0.12, x0 + pw * 0.34, y1 - ph * 0.12), pw * 0.06, hex_rgba(PEACH, 120), None)
            draw_round_rect(draw, (x0 + pw * 0.54, y0 + ph * 0.16, x0 + pw * 0.8, y0 + ph * 0.54), pw * 0.12, hex_rgba(BLUE, 130), hex_rgba(BLUE_DEEP, 70))
        elif kind == "dial":
            radius = min(pw, ph) * 0.28
            for ring in range(3):
                draw.ellipse((cx - radius * (1 - ring * 0.24), cy - radius * (1 - ring * 0.24), cx + radius * (1 - ring * 0.24), cy + radius * (1 - ring * 0.24)), outline=hex_rgba(BLUE_DEEP, 50), width=2)
            draw.line((cx, cy, cx + radius * 0.62, cy - radius * 0.42), fill=hex_rgba(PEACH, 170), width=3)
            draw.ellipse((cx - radius * 0.16, cy - radius * 0.16, cx + radius * 0.16, cy + radius * 0.16), fill=hex_rgba(BLUE_DEEP, 180))
        elif kind == "tracks":
            for index in range(4):
                yy = y0 + ph * (0.22 + index * 0.2)
                draw.line((x0 + pw * 0.1, yy, x1 - pw * 0.1, yy), fill=LINE, width=2)
                px = x0 + pw * (0.28 + index * 0.16)
                color = BLUE if index % 2 else PEACH
                draw.ellipse((px - ph * 0.05, yy - ph * 0.05, px + ph * 0.05, yy + ph * 0.05), fill=hex_rgba(color, 180))
        elif kind == "orbit":
            radius = min(pw, ph) * 0.34
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=hex_rgba(INK, 60), width=2)
            draw.ellipse((cx - radius * 0.36, cy - radius * 0.36, cx + radius * 0.36, cy + radius * 0.36), fill=hex_rgba(BLUE, 180))
            for index in range(4):
                angle = index * (math.pi / 2)
                px = cx + math.cos(angle) * radius
                py = cy + math.sin(angle) * radius
                draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill=hex_rgba(INK, 220))
        elif kind in {"wave", "swell"}:
            color = BLUE_DEEP if kind == "wave" else BLUE
            for row in range(4):
                points = []
                for step in range(26):
                    t = step / 25
                    px = x0 + pw * t
                    py = y0 + ph * (0.52 + (row - 1.5) * 0.08) + math.sin(t * math.pi * 2.2 + row) * ph * 0.11
                    points.append((px, py))
                draw.line(points, fill=hex_rgba(color, 90), width=2)
        elif kind == "dots":
            for row in range(18):
                for col in range(24):
                    px = x0 + pw * (0.16 + col * 0.018)
                    py = y0 + ph * (0.18 + row * 0.03)
                    alpha = max(10, 80 - int(math.hypot(col - 12, row - 9) * 6))
                    draw.ellipse((px - 1, py - 1, px + 1, py + 1), fill=(41, 67, 84, alpha))
        elif kind == "spray":
            for index in range(100):
                px = x0 + pw * (0.12 + (index % 20) * 0.04)
                py = y0 + ph * (0.18 + (index // 20) * 0.15)
                radius = 1 + (index % 4) * 0.4
                color = BLUE if index % 5 else BLUE_DEEP
                draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=hex_rgba(color, 90))

    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.2)))


def draw_header(base: Image.Image, width: int, height: int) -> None:
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    box = (34, 34, min(width - 34, 748), 298)
    draw.rounded_rectangle(box, radius=28, fill=PAPER, outline=LINE, width=2)
    draw.text((58, 58), "CODE ANIMATION STUDY #031", fill=MUTED)
    draw.text((58, 94), "POROUS INTERFACE CREATURE", fill=hex_rgba(INK, 255))
    draw.multiline_text(
        (58, 142),
        "A pale design-board organism with translucent shell, root-legs,\n"
        "and live probes, so the interface reads like anatomy instead of\n"
        "a detached dashboard.",
        fill=hex_rgba(INK, 230),
        spacing=8,
    )
    draw.multiline_text(
        (58, 220),
        "Pointer movement changes gait and connector tension. Board nodes\n"
        "switch the creature law: drift, probe, or bloom.",
        fill=MUTED,
        spacing=8,
    )
    draw.text((58, 274), "BOARD LAW", fill=MUTED)
    draw.text((168, 274), "drift", fill=hex_rgba(INK, 255))
    draw.text((238, 274), "TENSION", fill=MUTED)
    draw.text((326, 274), "0.31", fill=hex_rgba(INK, 255))
    draw.text((396, 274), "WARMTH", fill=MUTED)
    draw.text((484, 274), "48%", fill=hex_rgba(INK, 255))
    base.alpha_composite(layer)


def draw_nodes(base: Image.Image, width: int, height: int) -> None:
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    nodes = [
        (width * 0.18, height * 0.19, BLUE_DEEP, "DRIFT", "slow gait"),
        (width * 0.5, height * 0.12, BLUE, "PROBE", "wider reach"),
        (width * 0.84, height * 0.2, PEACH, "BLOOM", "open pores"),
    ]
    for x, y, color, title, subtitle in nodes:
        draw.rounded_rectangle((x - 76, y - 30, x + 76, y + 30), radius=18, fill=PAPER, outline=hex_rgba(color, 100), width=2)
        draw.text((x - 56, y - 16), title, fill=hex_rgba(INK, 240))
        draw.text((x - 56, y + 4), subtitle, fill=MUTED)
    base.alpha_composite(layer)


def render(output: Path, width: int, height: int) -> None:
    random.seed(31)
    image = vertical_gradient((width, height), "#fbfdfd", BG)

    for center, radius, color, alpha in [
        ((width * 0.18, height * 0.18), width * 0.22, BLUE, 74),
        ((width * 0.82, height * 0.2), width * 0.24, PEACH, 72),
        ((width * 0.56, height * 0.84), width * 0.2, BLUE_DEEP, 38),
    ]:
        image = Image.alpha_composite(image, radial_glow((width, height), center, radius, color, alpha))

    dust = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(dust)
    for index in range(140):
        x = random.uniform(0, width)
        y = random.uniform(0, height)
        radius = random.uniform(1.0, 2.6)
        color = BLUE if index % 3 else INK
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=hex_rgba(color, 28 if color == INK else 34))
    image = Image.alpha_composite(image, dust.filter(ImageFilter.GaussianBlur(0.4)))

    draw_small_panels(image, width, height)
    draw_creature(image, width, height)
    draw_nodes(image, width, height)
    draw_header(image, width, height)

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
