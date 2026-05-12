#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


BG = (5, 7, 11)
TEXT = (235, 237, 241)
MUTED = (146, 158, 170)
CYAN = (138, 210, 239)
SALMON = (255, 156, 142)
AMBER = (245, 193, 115)
CRIMSON = (255, 85, 118)


def rgba(color: tuple[int, int, int], alpha: int) -> tuple[int, int, int, int]:
    return color[0], color[1], color[2], alpha


def font(size: int):
    for path in (
        "/System/Library/Fonts/Supplemental/Arial Narrow.ttf",
        "/System/Library/Fonts/Supplemental/Trebuchet MS.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
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
        t = y / max(height - 1, 1)
        color = (int(10 - 7 * t), int(13 - 11 * t), int(19 - 15 * t), 255)
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
            fill=rgba(color, int(alpha * 0.22 * (t**2))),
        )
    return layer.filter(ImageFilter.GaussianBlur(radius * 0.09))


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def line_echo(draw: ImageDraw.ImageDraw, points, fill, width: int) -> None:
    for offset, alpha in ((0, 255), (4, 80), (8, 28)):
        shifted = [(x + offset, y + offset * 0.2) for x, y in points]
        draw.line(shifted, fill=rgba(fill, alpha), width=max(1, width - offset // 4))


def render(output: Path, width: int, height: int) -> None:
    image = gradient((width, height))
    for center, radius, color, alpha in (
        ((width * 0.2, height * 0.16), width * 0.22, CYAN, 120),
        ((width * 0.78, height * 0.14), width * 0.18, SALMON, 120),
        ((width * 0.56, height * 0.78), width * 0.22, AMBER, 80),
    ):
        image = Image.alpha_composite(image, radial((width, height), center, radius, color, alpha))

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    grid = max(42, width // 22)
    for x in range(0, width, grid):
        draw.line((x, 0, x, height), fill=(255, 255, 255, 14), width=1)
    for y in range(0, height, grid):
        draw.line((0, y, width, y), fill=(255, 255, 255, 14), width=1)

    title_box = (28, 34, width - 332, 286)
    rail_box = (width - 286, 150, width - 28, height - 44)
    notes_box = (34, height - 300, width - 370, height - 40)
    rounded(draw, title_box, 30, (10, 15, 22, 214), (172, 206, 222, 36), 2)
    rounded(draw, rail_box, 28, (10, 15, 22, 214), (172, 206, 222, 34), 2)
    rounded(draw, notes_box, 28, (10, 15, 22, 176), (172, 206, 222, 30), 2)

    draw.text((48, 54), "#064 generated animation / dark human editorial control surface", font=mono(12), fill=rgba(MUTED, 220))
    draw.text((48, 90), "NIGHT PROOF", font=font(54), fill=rgba(TEXT, 244))
    draw.text((48, 144), "SWITCHBOARD", font=font(54), fill=rgba(SALMON, 238))
    draw.multiline_text(
        (48, 206),
        "Copyshop glass, reflected proof slips,\nrack-focus drag, and shutter weather\ninside one nocturnal page surface.",
        font=font(22),
        fill=rgba(TEXT, 182),
        spacing=6,
    )

    chip_x = 48
    for label, tint in (("proof bias", CYAN), ("street flood", SALMON), ("afterimage drift", AMBER)):
        rounded(draw, (chip_x, 250, chip_x + 164, 282), 999, rgba(tint, 34), rgba(tint, 88), 1)
        draw.ellipse((chip_x + 10, 261, chip_x + 20, 271), fill=rgba(tint, 240))
        draw.text((chip_x + 30, 257), label.upper(), font=mono(11), fill=rgba(TEXT, 220))
        chip_x += 174

    stage = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(stage, "RGBA")

    for idx in range(18):
        x = 70 + idx * 56 + math.sin(idx * 0.6) * 8
        y = 280 + (idx % 5) * 44
        trail = [(x, y), (x + 18, y + 220 + idx * 6)]
        tint = CYAN if idx % 3 == 0 else SALMON if idx % 3 == 1 else AMBER
        sdraw.line(trail, fill=rgba(tint, 42), width=2 + (idx % 3))

    slips = [
        (96, 360, 380, 504, -0.12, CYAN),
        (332, 300, 710, 476, 0.08, SALMON),
        (228, 564, 640, 722, -0.04, AMBER),
        (566, 470, 896, 632, 0.06, CRIMSON),
    ]
    for x0, y0, x1, y1, angle, tint in slips:
        pane = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        pdraw = ImageDraw.Draw(pane, "RGBA")
        rounded(pdraw, (x0, y0, x1, y1), 26, (15, 21, 30, 182), (235, 237, 241, 34), 2)
        for row in range(6):
            yy = y0 + 24 + row * ((y1 - y0 - 48) / 5)
            pdraw.line((x0 + 18, yy, x1 - 18, yy), fill=(235, 237, 241, 30), width=1)
        pdraw.rectangle((x0 + 18, y1 - 24, x0 + (x1 - x0) * 0.44, y1 - 18), fill=rgba(tint, 170))
        pane = pane.rotate(math.degrees(angle), resample=Image.Resampling.BICUBIC, center=((x0 + x1) / 2, (y0 + y1) / 2))
        stage.alpha_composite(pane)

    figure = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(figure, "RGBA")
    base_x = 530
    base_y = 760
    for offset, tint in ((-58, CYAN), (0, TEXT), (56, SALMON)):
        px = base_x + offset
        fdraw.ellipse((px - 24, base_y - 270, px + 20, base_y - 222), fill=rgba(TEXT if tint == TEXT else tint, 62 if tint != TEXT else 92))
        points = [
            (px, base_y - 220),
            (px + 26, base_y - 158),
            (px + 18, base_y - 36),
            (px, base_y + 90),
            (px - 18, base_y - 34),
            (px - 28, base_y - 160),
            (px, base_y - 220),
        ]
        line_echo(fdraw, points, tint if tint != TEXT else (214, 220, 226), 4)
        line_echo(fdraw, [(px - 8, base_y - 100), (px - 84, base_y - 30)], tint if tint != TEXT else CYAN, 3)
        line_echo(fdraw, [(px + 8, base_y - 86), (px + 90, base_y - 10)], tint if tint != TEXT else AMBER, 3)
        line_echo(fdraw, [(px - 4, base_y + 86), (px - 26, base_y + 188)], tint if tint != TEXT else SALMON, 3)
        line_echo(fdraw, [(px + 4, base_y + 86), (px + 30, base_y + 182)], tint if tint != TEXT else CYAN, 3)

    image.alpha_composite(stage.filter(ImageFilter.GaussianBlur(0.3)))
    image.alpha_composite(figure.filter(ImageFilter.GaussianBlur(0.2)))

    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow, "RGBA")
    for x, y, rx, ry, tint, alpha in (
        (228, 420, 150, 72, CYAN, 48),
        (510, 378, 190, 86, SALMON, 44),
        (462, 650, 220, 94, AMBER, 40),
    ):
        gdraw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=rgba(tint, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(24))
    image.alpha_composite(glow)

    draw = ImageDraw.Draw(image, "RGBA")
    draw.text((width - 256, 176), "EXPOSURE RAIL", font=mono(12), fill=rgba(MUTED, 224))
    draw.text((width - 256, 204), "proof", font=font(24), fill=rgba(TEXT, 228))
    slider_y = 270
    for label, value, tint in (("FOCUS SPREAD", 0.56, CYAN), ("GLASS GLOW", 0.48, SALMON), ("TRAIL DRAG", 0.42, AMBER)):
        draw.text((width - 256, slider_y), label, font=mono(11), fill=rgba(MUTED, 220))
        rounded(draw, (width - 256, slider_y + 24, width - 70, slider_y + 38), 999, (255, 255, 255, 14), None, 1)
        rounded(draw, (width - 256, slider_y + 24, width - 256 + int(186 * value), slider_y + 38), 999, rgba(tint, 188), None, 1)
        slider_y += 92

    rail_notes = [
        ("RACK FOCUS", CYAN),
        ("WET REFLECTIONS", SALMON),
        ("SHUTTER STREAK", AMBER),
    ]
    y = 560
    for label, tint in rail_notes:
        rounded(draw, (width - 256, y, width - 70, y + 52), 18, (255, 255, 255, 8), rgba(tint, 38), 1)
        draw.ellipse((width - 238, y + 20, width - 226, y + 32), fill=rgba(tint, 240))
        draw.text((width - 212, y + 17), label, font=mono(11), fill=rgba(TEXT, 216))
        y += 64

    note_titles = ("IDEA", "INTERACTION", "NEXT")
    note_copy = (
        "Believable public-task scene split into reflected proof fragments.",
        "Hover pulls focus; click leaves one short scanner-flash mark.",
        "Could turn typed copy into the active strip or widen into multiple kiosks.",
    )
    block_w = (notes_box[2] - notes_box[0] - 40) / 3
    for idx in range(3):
        x0 = notes_box[0] + 14 + idx * (block_w + 6)
        x1 = x0 + block_w
        rounded(draw, (x0, notes_box[1] + 14, x1, notes_box[3] - 14), 20, (255, 255, 255, 8), (255, 255, 255, 16), 1)
        draw.text((x0 + 12, notes_box[1] + 28), note_titles[idx], font=mono(11), fill=rgba(TEXT, 220))
        draw.multiline_text((x0 + 12, notes_box[1] + 60), note_copy[idx], font=font(16), fill=rgba(TEXT, 176), spacing=5)

    noise = ImageDraw.Draw(image, "RGBA")
    rng = random.Random(64)
    for _ in range(2400):
        noise.point((rng.randrange(width), rng.randrange(height)), fill=(255, 255, 255, rng.randrange(8, 20)))

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
