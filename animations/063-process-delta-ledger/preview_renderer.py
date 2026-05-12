#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


PALETTE = {
    "paper": (242, 231, 216),
    "wash": (251, 245, 238),
    "ink": (34, 51, 61),
    "muted": (95, 109, 118),
    "teal": (131, 188, 201),
    "mint": (156, 185, 166),
    "coral": (222, 147, 123),
    "amber": (212, 162, 88),
    "plum": (134, 109, 135),
}


def load_font(size: int, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/SFNSMono.ttf"]
        if mono
        else [
            "/System/Library/Fonts/Supplemental/Palatino.ttc",
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
            "/System/Library/Fonts/Supplemental/Georgia.ttf",
        ]
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def blend(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def draw_vertical_gradient(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    top = (250, 243, 234)
    bottom = (221, 200, 171)
    for y in range(height):
      t = y / max(1, height - 1)
      draw.line([(0, y), (width, y)], fill=blend(top, bottom, t))


def add_washes(base: Image.Image) -> None:
    wash = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(wash)
    centers = [
        (0.14, 0.12, PALETTE["wash"], 220),
        (0.82, 0.18, PALETTE["teal"], 240),
        (0.18, 0.84, PALETTE["coral"], 260),
        (0.76, 0.72, PALETTE["mint"], 230),
    ]
    for px, py, color, radius in centers:
        x = int(base.width * px)
        y = int(base.height * py)
        for ring in range(radius, 0, -10):
            alpha = int(18 * (ring / radius) ** 1.8)
            draw.ellipse(
                [x - ring, y - ring, x + ring, y + ring],
                fill=(*color, alpha),
            )
    wash = wash.filter(ImageFilter.GaussianBlur(28))
    base.alpha_composite(wash)


def add_grid(base: Image.Image) -> None:
    grid = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(grid)
    for x in range(0, base.width, 88):
        draw.line([(x, 0), (x, base.height)], fill=(*PALETTE["ink"], 18), width=1)
    for y in range(0, base.height, 88):
        draw.line([(0, y), (base.width, y)], fill=(*PALETTE["ink"], 18), width=1)
    mask = Image.new("L", base.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse(
        [base.width * 0.12, base.height * 0.1, base.width * 0.88, base.height * 0.82],
        fill=255,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(120))
    grid.putalpha(ImageChops.multiply(grid.getchannel("A"), mask))
    base.alpha_composite(grid)


def draw_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill_alpha: int = 178) -> None:
    draw.rounded_rectangle(box, radius=28, fill=(255, 250, 244, fill_alpha), outline=(*PALETTE["ink"], 30), width=2)
    inset = 1
    draw.rounded_rectangle(
        (box[0] + inset, box[1] + inset, box[2] - inset, box[3] - inset),
        radius=27,
        outline=(255, 255, 255, 94),
        width=1,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    random.seed(63)
    image = Image.new("RGBA", (args.width, args.height), PALETTE["paper"])
    draw = ImageDraw.Draw(image)
    draw_vertical_gradient(draw, args.width, args.height)
    add_washes(image)
    add_grid(image)

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    o = ImageDraw.Draw(overlay)

    banner_box = (28, 28, args.width - 28, 240)
    legend_box = (args.width - 310, 292, args.width - 28, 770)
    notes_box = (28, args.height - 238, args.width - 28, args.height - 28)
    draw_panel(o, banner_box)
    draw_panel(o, legend_box)
    draw_panel(o, notes_box)

    serif_big = load_font(74)
    serif_body = load_font(28)
    serif_small = load_font(22)
    mono_small = load_font(16, mono=True)
    mono_med = load_font(18, mono=True)

    ink = PALETTE["ink"]
    muted = PALETTE["muted"]

    o.text((54, 54), "Code Animation Study #063", font=mono_small, fill=(*muted, 255))
    o.text((54, 82), "Process ", font=serif_big, fill=(*ink, 255))
    process_width = o.textbbox((54, 82), "Process ", font=serif_big)[2]
    o.text((54 + process_width - 6, 82), "Delta", font=serif_big, fill=(*PALETTE["coral"], 255))
    delta_width = o.textbbox((54, 82), "Process Delta", font=serif_big)[2]
    o.text((54 + delta_width - 4, 82), " Ledger", font=serif_big, fill=(*ink, 255))
    lede = (
        "A flatter living paper diagram that breaks the recent cutaway and "
        "console shell: drifting slips, connector currents, and warm stamp "
        "bursts keep the page design-native while the motion stays procedural."
    )
    o.text((56, 168), lede, font=serif_small, fill=(*muted, 255), spacing=6)

    chip_y = 60
    chips = [("intake drift", PALETTE["amber"]), ("pointer wake", PALETTE["teal"]), ("click plants stamp", PALETTE["mint"])]
    chip_x = args.width - 430
    for label, color in chips:
        text_w = o.textbbox((0, 0), label.upper(), font=mono_small)[2]
        width = text_w + 54
        o.rounded_rectangle((chip_x, chip_y, chip_x + width, chip_y + 34), radius=17, fill=(255, 250, 244, 190), outline=(*ink, 34), width=1)
        o.ellipse((chip_x + 12, chip_y + 10, chip_x + 24, chip_y + 22), fill=(*color, 255))
        o.text((chip_x + 30, chip_y + 9), label.upper(), font=mono_small, fill=(*ink, 220))
        chip_y += 44

    o.text((args.width - 286, 316), "Stamp register", font=mono_med, fill=(*muted, 255))
    o.text((args.width - 286, 346), "Click plants a local marker that briefly\nre-braids the nearest slips and currents.", font=serif_small, fill=(*muted, 255), spacing=8)

    stamp_labels = ["ROUTE HUSH", "PRINT RELAY", "SOCIAL SPLICE"]
    for idx, label in enumerate(stamp_labels):
        y = 440 + idx * 94
        o.rounded_rectangle((args.width - 286, y, args.width - 54, y + 74), radius=18, fill=(255, 252, 248, 172), outline=(*ink, 24), width=1)
        o.text((args.width - 264, y + 14), f"SEAL 0{idx + 1}", font=mono_small, fill=(*muted, 230))
        o.text((args.width - 264, y + 34), label, font=serif_small, fill=(*ink, 255))

    field = Image.new("RGBA", image.size, (0, 0, 0, 0))
    f = ImageDraw.Draw(field)

    anchors: list[tuple[float, float]] = []
    for row in range(3):
        for col in range(4):
            x = 126 + col * 176 + (18 if row % 2 else -8)
            y = 360 + row * 210 + (24 if col % 2 else -26)
            anchors.append((x + random.randint(-26, 26), y + random.randint(-18, 18)))

    for idx, (ax, ay) in enumerate(anchors):
        next_ax, next_ay = anchors[(idx + 1) % len(anchors)]
        ctrl_x = (ax + next_ax) / 2 + (next_ay - ay) * 0.22
        ctrl_y = (ay + next_ay) / 2 - (next_ax - ax) * 0.12
        points = []
        steps = 24
        for step in range(steps + 1):
            t = step / steps
            x = (1 - t) ** 2 * ax + 2 * (1 - t) * t * ctrl_x + t ** 2 * next_ax
            y = (1 - t) ** 2 * ay + 2 * (1 - t) * t * ctrl_y + t ** 2 * next_ay
            points.append((x, y))
        f.line(points, fill=(*ink, 58), width=3)
        f.line(points, fill=(255, 255, 255, 46), width=1)

    colors = [PALETTE["teal"], PALETTE["mint"], PALETTE["coral"], PALETTE["amber"], PALETTE["plum"]]
    tags = ["ROUTE HUSH", "CIVIC FOLD", "SOFT PROOF", "MARGIN BLOOM", "PRINT RELAY", "QUIET HATCH"]
    for idx, (x, y) in enumerate(anchors):
        w = random.randint(120, 154)
        h = random.randint(58, 80)
        tilt = random.uniform(-0.12, 0.12)
        layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        box = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        ld.rounded_rectangle(box, radius=16, fill=(255, 250, 243, 240), outline=(*ink, 34), width=2)
        ld.rounded_rectangle((box[0] + 12, box[1] + 12, box[0] + 58, box[1] + 28), radius=10, fill=(*colors[idx % len(colors)], 34))
        ld.line((box[0] + 18, y - 4, box[2] - 18, y - 4), fill=(*ink, 44), width=2)
        ld.line((box[0] + 18, y + 16, box[2] - 38, y + 16), fill=(*ink, 36), width=2)
        ld.ellipse((box[2] - 22, box[1] + 18, box[2] - 10, box[1] + 30), fill=(*colors[(idx + 2) % len(colors)], 180))
        ld.text((box[0] + 16, box[1] + 18), tags[idx % len(tags)], font=mono_small, fill=(*ink, 210))
        rotated = layer.rotate(math.degrees(tilt), resample=Image.Resampling.BICUBIC, center=(x, y))
        field.alpha_composite(rotated)

    for idx, label in enumerate(["ROUTE HUSH", "SOCIAL SPLICE", "PRINT RELAY"]):
        x = 180 + idx * 240
        y = 298 + idx * 126
        f.ellipse((x - 62, y - 62, x + 62, y + 62), outline=(*colors[idx], 66), width=3)
        f.rounded_rectangle((x - 54, y - 18, x + 54, y + 18), radius=14, outline=(*ink, 42), width=2)
        f.text((x - 40, y - 8), label, font=mono_small, fill=(*ink, 120))

    field = field.filter(ImageFilter.GaussianBlur(0.15))
    image.alpha_composite(field)

    note_titles = ["Idea", "Interaction", "Next"]
    note_copy = [
        "Use the recent process-paper social-diagram cue as a full-page motion system instead of another helper mascot sheet or interface chassis.",
        "Pointer movement shears nearby connectors and lifts paper warmth; click plants a seal that briefly reorganizes the local route law.",
        "A sequel could let typed fragments become new slips so the ledger grows into a larger social map without losing print-like clarity.",
    ]
    note_width = (notes_box[2] - notes_box[0] - 36) // 3
    for idx, title in enumerate(note_titles):
        x0 = notes_box[0] + 12 + idx * (note_width + 6)
        x1 = x0 + note_width
        y0 = notes_box[1] + 14
        y1 = notes_box[3] - 14
        o.rounded_rectangle((x0, y0, x1, y1), radius=20, fill=(255, 253, 249, 92), outline=(*ink, 22), width=1)
        o.text((x0 + 16, y0 + 14), title.upper(), font=mono_small, fill=(*muted, 230))
        o.text((x0 + 16, y0 + 42), note_copy[idx], font=serif_small, fill=(*ink, 238), spacing=7)

    o.rounded_rectangle((args.width - 176, args.height - 76, args.width - 28, args.height - 28), radius=24, fill=(255, 250, 244, 188), outline=(*ink, 30), width=1)
    o.text((args.width - 156, args.height - 60), "BACK TO INDEX", font=mono_small, fill=(*ink, 220))

    overlay = overlay.filter(ImageFilter.GaussianBlur(0.1))
    image.alpha_composite(overlay)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
