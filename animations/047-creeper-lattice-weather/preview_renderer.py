#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def mix(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


def alpha(color: tuple[int, int, int], value: int) -> tuple[int, int, int, int]:
    return color + (value,)


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], radius: int, fill, outline):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=1)


def wrap_text(text: str, draw: ImageDraw.ImageDraw, max_width: float, text_font: ImageFont.ImageFont) -> str:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if draw.textlength(candidate, font=text_font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Avenir Next.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Trebuchet MS.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size, index=1 if bold else 0)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_gradient_background(width: int, height: int) -> Image.Image:
    top = hex_rgb("#f6f2e8")
    mid = hex_rgb("#edf0e6")
    bottom = hex_rgb("#dbe2d0")
    image = Image.new("RGBA", (width, height), top + (255,))
    pixels = image.load()
    for y in range(height):
      t = y / max(1, height - 1)
      if t < 0.56:
          color = mix(top, mid, t / 0.56)
      else:
          color = mix(mid, bottom, (t - 0.56) / 0.44)
      for x in range(width):
          pixels[x, y] = color + (255,)
    return image


def draw_radial_glow(layer: Image.Image, center: tuple[float, float], radius: float, color: tuple[int, int, int], strength: int):
    draw = ImageDraw.Draw(layer, "RGBA")
    for ring in range(8, 0, -1):
        t = ring / 8
        r = radius * t
        a = int(strength * (t ** 2) * 0.45)
        draw.ellipse((center[0] - r, center[1] - r, center[0] + r, center[1] + r), fill=alpha(color, a))


def build_points(width: int, height: int) -> tuple[list[dict], list[dict], list[dict]]:
    random.seed(47)
    cols, rows = 7, 6
    margin_x = width * 0.12
    margin_top = height * 0.12
    usable_width = width - margin_x * 2
    usable_height = height * 0.72

    anchors = []
    for row in range(rows):
        for col in range(cols):
            anchors.append(
                {
                    "x": margin_x + usable_width * (col / (cols - 1)) + random.uniform(-24, 24),
                    "y": margin_top + usable_height * (row / (rows - 1)) + random.uniform(-20, 20),
                    "row": row,
                    "col": col,
                }
            )

    vines = []
    for _ in range(40):
        anchor = random.choice(anchors)
        vines.append(
            {
                "anchor": anchor,
                "length": random.uniform(height * 0.14, height * 0.34) + anchor["row"] * 24,
                "segments": random.randint(8, 11),
                "offset": random.uniform(0, math.pi * 2),
                "thickness": random.uniform(1.0, 2.3),
                "bias": random.uniform(-1, 1),
                "branch_t": random.uniform(0.24, 0.8),
                "branch_length": random.uniform(16, 46),
                "beads": [
                    {
                        "t": random.uniform(0.16, 0.94),
                        "radius": random.uniform(3, 8),
                        "color": random.choice(["#79c8d2", "#89b48f", "#d78f73", "#d2da63"]),
                    }
                    for _ in range(random.randint(2, 4))
                ],
            }
        )

    spores = []
    for _ in range(108):
        spores.append(
            {
                "x": random.uniform(margin_x * 0.6, width - margin_x * 0.6),
                "y": random.uniform(height * 0.18, height * 0.94),
                "z": random.random(),
                "size": random.uniform(1.2, 3.8),
            }
        )

    return anchors, vines, spores


def render(output: Path, width: int, height: int) -> None:
    base = draw_gradient_background(width, height)
    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_radial_glow(glow, (width * 0.16, height * 0.18), width * 0.18, hex_rgb("#79c8d2"), 70)
    draw_radial_glow(glow, (width * 0.82, height * 0.18), width * 0.14, hex_rgb("#d78f73"), 55)
    draw_radial_glow(glow, (width * 0.54, height * 0.86), width * 0.2, hex_rgb("#89b48f"), 60)
    draw_radial_glow(glow, (width * 0.55, height * 0.62), width * 0.28, (255, 255, 255), 90)
    base = Image.alpha_composite(base, glow.filter(ImageFilter.GaussianBlur(28)))

    grid_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    grid_draw = ImageDraw.Draw(grid_layer, "RGBA")
    spacing = min(int(width * 0.04), 38)
    grid_color = alpha(hex_rgb("#24323a"), 18)
    for x in range(0, width, spacing):
        grid_draw.line((x, 0, x, height), fill=grid_color, width=1)
    for y in range(0, height, spacing):
        grid_draw.line((0, y, width, y), fill=grid_color, width=1)
    base = Image.alpha_composite(base, grid_layer)

    anchors, vines, spores = build_points(width, height)
    field = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(field, "RGBA")

    for anchor in anchors:
        for other in anchors:
            if (other["row"] == anchor["row"] and other["col"] == anchor["col"] + 1) or (
                other["col"] == anchor["col"] and other["row"] == anchor["row"] + 1
            ):
                draw.line((anchor["x"], anchor["y"], other["x"], other["y"]), fill=alpha(hex_rgb("#24323a"), 28), width=1)
        draw.rectangle((anchor["x"] - 3.5, anchor["y"] - 3.5, anchor["x"] + 3.5, anchor["y"] + 3.5), fill=alpha(hex_rgb("#24323a"), 42))
        draw.rectangle((anchor["x"] - 7.5, anchor["y"] - 7.5, anchor["x"] + 7.5, anchor["y"] + 7.5), outline=alpha(hex_rgb("#79c8d2"), 28), width=1)

    for vine in vines:
        points = []
        for i in range(vine["segments"] + 1):
            t = i / vine["segments"]
            local_wave = math.sin(vine["offset"] + t * 5.4) * (16 + 18 * t) + math.cos(vine["offset"] * 1.7 + t * 9.2) * (8 + 12 * t)
            curl = math.sin(vine["offset"] * 2.3 + t * 12) * 0.22 * 46 * t
            x = vine["anchor"]["x"] + vine["bias"] * 18 * t + local_wave + width * 0.01 * math.sin(t * 3.1)
            y = vine["anchor"]["y"] + t * vine["length"] + math.sin(vine["offset"] + t * 8) * 8
            points.append((x, y))

        draw.line(points, fill=alpha(hex_rgb("#5d7d65"), 90), width=max(1, int(vine["thickness"])))
        branch_index = max(1, min(len(points) - 1, int(vine["branch_t"] * (len(points) - 1))))
        branch_point = points[branch_index]
        branch_angle = vine["bias"] * 0.9
        branch_end = (
            branch_point[0] + math.cos(branch_angle) * vine["branch_length"],
            branch_point[1] + math.sin(branch_angle) * 20,
        )
        draw.line((branch_point, branch_end), fill=alpha(hex_rgb("#79967f"), 68), width=1)

        for bead in vine["beads"]:
            point = points[min(len(points) - 1, int(bead["t"] * (len(points) - 1)))]
            r = bead["radius"] * 0.9
            bead_color = hex_rgb(bead["color"])
            draw.ellipse((point[0] - r, point[1] - r * 0.76, point[0] + r, point[1] + r * 0.76), fill=alpha(bead_color, 102), outline=alpha((255, 255, 255), 120))
            dot = max(1.0, r * 0.18)
            draw.ellipse((point[0] - r * 0.22 - dot, point[1] - r * 0.18 - dot, point[0] - r * 0.22 + dot, point[1] - r * 0.18 + dot), fill=alpha((255, 255, 255), 84))

    for spore in spores:
        fill = (255, 255, 255) if spore["z"] > 0.66 else hex_rgb("#79c8d2") if spore["z"] > 0.33 else hex_rgb("#d2da63")
        a = int(40 + spore["z"] * 60)
        if spore["z"] > 0.62:
            draw.rectangle((spore["x"] - spore["size"] * 0.5, spore["y"] - spore["size"] * 0.5, spore["x"] + spore["size"] * 0.5, spore["y"] + spore["size"] * 0.5), fill=alpha(fill, a))
        else:
            draw.ellipse((spore["x"] - spore["size"] * 0.5, spore["y"] - spore["size"] * 0.5, spore["x"] + spore["size"] * 0.5, spore["y"] + spore["size"] * 0.5), fill=alpha(fill, a))

    base = Image.alpha_composite(base, field.filter(ImageFilter.GaussianBlur(0.3)))

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay, "RGBA")
    ink = hex_rgb("#24323a")
    line = alpha(ink, 34)
    panel = (255, 255, 255, 184)

    left_box = (16, 16, min(16 + 500, width - 16), min(16 + 392, height - 16))
    right_box = (max(width - 392, 16), 16, width - 16, min(16 + 214, height - 16))
    rounded_panel(od, left_box, 24, panel, line)
    rounded_panel(od, right_box, 24, panel, line)
    rounded_panel(od, (width - 150, height - 56, width - 16, height - 16), 20, panel, line)

    mono_small = font(13)
    mono_value = font(18)
    title_font = font(48, bold=True)
    body_font = font(18)
    small_body = font(15)

    od.text((34, 32), "CODE ANIMATION STUDY #047", fill=alpha(ink, 160), font=mono_small)
    od.text((34, 56), "Creeper Lattice\nWeather", fill=alpha(ink, 240), font=title_font, spacing=-4)
    intro = wrap_text(
        "A pale distributed field that turns the latest creeper-lattice image branch into browser-native motion: hanging stems, bead capsules, and quiet calibration marks spread across the page instead of resolving into one hero specimen or another dark console.",
        od,
        left_box[2] - left_box[0] - 36,
        body_font,
    )
    od.multiline_text((34, 150), intro, fill=alpha(ink, 198), font=body_font, spacing=5)
    intro_box = od.multiline_textbbox((34, 150), intro, font=body_font, spacing=5)

    sections = [
        ("IDEA", "Denser lower-field growth and calmer upper air give the page a specimen-weather logic instead of a centered poster object."),
        ("INTERACTION", "Move to bend the local current. Press or drag to seed temporary weather cells that make nearby creepers open, knot, or rain pollen."),
        ("NEXT", "This branch could widen into a larger HTML editorial page, a semantic garden weather board, or a quiet print-ready motion system with text overlays."),
    ]
    y = intro_box[3] + 18
    for label, copy in sections:
        od.text((34, y), label, fill=alpha(ink, 160), font=mono_small)
        wrapped = wrap_text(copy, od, left_box[2] - left_box[0] - 36, small_body)
        od.multiline_text((34, y + 18), wrapped, fill=alpha(ink, 195), font=small_body, spacing=4)
        copy_box = od.multiline_textbbox((34, y + 18), wrapped, font=small_body, spacing=4)
        y = copy_box[3] + 14

    od.text((right_box[0] + 18, right_box[1] + 16), "FIELD LAWS", fill=alpha(ink, 160), font=mono_small)
    chip_y = right_box[1] + 42
    chips = [("Drift", True), ("Knot", False), ("Rain", False)]
    chip_x = right_box[0] + 18
    for label, active in chips:
        box = (chip_x, chip_y, chip_x + 98, chip_y + 34)
        rounded_panel(od, box, 16, (255, 255, 255, 166 if active else 120), alpha(ink, 48 if active else 28))
        od.text((chip_x + 16, chip_y + 9), label.upper(), fill=alpha(ink, 220), font=mono_small)
        chip_x += 106

    od.text((right_box[0] + 18, right_box[1] + 92), "DENSITY", fill=alpha(ink, 140), font=mono_small)
    od.text((right_box[0] + 18, right_box[1] + 108), "68%", fill=alpha(ink, 230), font=mono_value)
    od.text((right_box[0] + 124, right_box[1] + 92), "WAKE", fill=alpha(ink, 140), font=mono_small)
    od.text((right_box[0] + 124, right_box[1] + 108), "SOFT", fill=alpha(ink, 230), font=mono_value)
    od.text((right_box[0] + 224, right_box[1] + 92), "BLOOM", fill=alpha(ink, 140), font=mono_small)
    od.text((right_box[0] + 224, right_box[1] + 108), "CALM", fill=alpha(ink, 230), font=mono_value)

    right_copy = wrap_text(
        "The chips swap the same field between hanging draft, tangled pull, and spore shower without introducing a separate UI object. The whole page stays one living diagram.",
        od,
        right_box[2] - right_box[0] - 36,
        small_body,
    )
    od.multiline_text((right_box[0] + 18, right_box[1] + 150), right_copy, fill=alpha(ink, 190), font=small_body, spacing=4)
    od.text((width - 136, height - 44), "BACK TO INDEX", fill=alpha(ink, 220), font=mono_small)

    base = Image.alpha_composite(base, overlay)

    output.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(output)


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
