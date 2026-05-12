#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def blend(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


def polygon_points(cx: float, cy: float, rx: float, ry: float, steps: int = 140) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for i in range(steps):
      angle = (i / steps) * math.tau
      radial = (
          1
          + math.sin(angle * 3.0 + 0.8) * 0.05
          + math.cos(angle * 5.0 - 0.45) * 0.038
          + math.sin(angle * 2.0 - 1.4) * 0.022
      )
      pts.append((cx + math.cos(angle) * rx * radial, cy + math.sin(angle) * ry * (radial + 0.012)))
    return pts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    width = args.width
    height = args.height
    output = Path(args.output)

    image = Image.new("RGBA", (width, height), (17, 12, 18, 255))
    px = image.load()
    top = (24, 17, 26)
    bottom = (12, 9, 14)

    for y in range(height):
        t = y / max(1, height - 1)
        row = blend(top, bottom, t)
        for x in range(width):
            px[x, y] = (*row, 255)

    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse((110, 90, 420, 390), fill=(255, 126, 147, 44))
    gdraw.ellipse((700, 80, 980, 330), fill=(131, 218, 214, 28))
    gdraw.ellipse((260, 720, 920, 1280), fill=(255, 126, 147, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(88))
    image = Image.alpha_composite(image, glow)

    mote = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    mdraw = ImageDraw.Draw(mote)
    random.seed(23)
    colors = [(255, 126, 147, 22), (131, 218, 214, 18), (244, 201, 149, 16)]
    for _ in range(90):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(2, 7)
        mdraw.ellipse((x - r, y - r, x + r, y + r), fill=random.choice(colors))
    mote = mote.filter(ImageFilter.GaussianBlur(2.2))
    image = Image.alpha_composite(image, mote)

    creature = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(creature)
    cx = width * 0.5
    cy = height * 0.59
    rx = width * 0.23
    ry = height * 0.16

    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse((cx - rx * 1.12, cy + ry * 0.66, cx + rx * 1.12, cy + ry * 1.02), fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(36))
    image = Image.alpha_composite(image, shadow)

    points = polygon_points(cx, cy, rx, ry)
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)

    body = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    bpx = body.load()
    for y in range(int(cy - ry * 1.25), int(cy + ry * 1.3)):
        for x in range(int(cx - rx * 1.3), int(cx + rx * 1.3)):
            dx = (x - (cx - rx * 0.14)) / (rx * 1.02)
            dy = (y - (cy - ry * 0.3)) / (ry * 1.02)
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 1.45:
                continue
            t = min(1.0, dist / 1.2)
            if t < 0.18:
                color = blend((246, 215, 175), (246, 190, 158), t / 0.18)
            elif t < 0.5:
                color = blend((246, 190, 158), (214, 106, 141), (t - 0.18) / 0.32)
            elif t < 0.84:
                color = blend((214, 106, 141), (88, 34, 70), (t - 0.5) / 0.34)
            else:
                color = blend((88, 34, 70), (38, 19, 31), (t - 0.84) / 0.16)
            alpha = 255 if mask.getpixel((x, y)) > 0 else 0
            if alpha:
                bpx[x, y] = (*color, 255)
    body.putalpha(mask)

    touch_glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(touch_glow)
    for tx, ty, outer, color in (
        (cx - rx * 0.42, cy + ry * 0.06, 120, (255, 180, 193, 76)),
        (cx + rx * 0.26, cy - ry * 0.08, 90, (255, 220, 172, 64)),
    ):
        tdraw.ellipse((tx - outer, ty - outer, tx + outer, ty + outer), fill=color)
    touch_glow = touch_glow.filter(ImageFilter.GaussianBlur(52))
    body = Image.alpha_composite(body, touch_glow)
    body = body.filter(ImageFilter.GaussianBlur(0.3))
    image = Image.alpha_composite(image, body)

    face = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(face)
    eye_y = cy - ry * 0.17
    eye_gap = rx * 0.29
    for eye_x in (cx - eye_gap, cx + eye_gap):
        fdraw.ellipse((eye_x - 30, eye_y - 20, eye_x + 30, eye_y + 20), fill=(248, 239, 223, 246))
        fdraw.ellipse((eye_x - 10, eye_y - 10, eye_x + 12, eye_y + 12), fill=(31, 18, 24, 255))
        fdraw.ellipse((eye_x - 7, eye_y - 8, eye_x - 1, eye_y - 2), fill=(255, 255, 255, 230))

    mouth_y = cy + ry * 0.11
    mouth = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    mdraw = ImageDraw.Draw(mouth)
    mdraw.arc((cx - rx * 0.23, mouth_y - 22, cx + rx * 0.23, mouth_y + 42), start=18, end=162, fill=(47, 18, 31, 235), width=6)
    mouth = mouth.filter(ImageFilter.GaussianBlur(0.4))
    face = Image.alpha_composite(face, mouth)

    for cheek_x in (cx - eye_gap * 1.08, cx + eye_gap * 1.08):
        fdraw.arc((cheek_x - 28, mouth_y - 36, cheek_x + 28, mouth_y + 12), start=28, end=158, fill=(255, 186, 166, 150), width=10)

    for side in (-1, 1):
        fdraw.line(
            (
                cx + side * rx * 0.6,
                cy - 8,
                cx + side * rx * 0.8,
                cy - ry * 0.12,
                cx + side * rx * 0.76,
                cy + ry * 0.22,
            ),
            fill=(131, 218, 214, 96),
            width=3,
            joint="curve",
        )

    image = Image.alpha_composite(image, face)

    orbit = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(orbit)
    for i in range(6):
        angle = i * 0.9 + 0.4
        ox = cx + math.cos(angle) * rx * (0.92 + i * 0.08)
        oy = cy + math.sin(angle * 1.3) * (ry * 0.6 + i * 10)
        color = (131, 218, 214, 112) if i % 2 == 0 else (244, 201, 149, 104)
        odraw.rectangle((ox - 4, oy - 4, ox + 4, oy + 4), fill=color)
    orbit = orbit.filter(ImageFilter.GaussianBlur(0.5))
    image = Image.alpha_composite(image, orbit)

    ui = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    uidraw = ImageDraw.Draw(ui)

    def panel(box: tuple[int, int, int, int], radius: int = 28) -> None:
        uidraw.rounded_rectangle(box, radius=radius, fill=(29, 19, 28, 182), outline=(255, 234, 214, 30), width=2)

    panel((18, 18, 470, 240))
    panel((width - 132, 18, width - 18, 72), radius=30)
    panel((18, height - 126, width - 18, height - 18), radius=24)
    panel((width // 2 - 62, 318, width // 2 + 62, 370), radius=30)

    uidraw.text((42, 42), "Code Animation Study #023", fill=(248, 239, 223, 136))
    uidraw.text((42, 78), "Blush Membrane Creature", fill=(248, 239, 223, 245))
    uidraw.text((42, 120), "A direct-touch creature study: slow petting warms the body;", fill=(248, 239, 223, 184))
    uidraw.text((42, 146), "fast pokes make the membrane tense and recoil.", fill=(248, 239, 223, 184))
    uidraw.text((width - 98, 39), "Index", fill=(248, 239, 223, 232))
    uidraw.text((width // 2 - 10, 333), "hm", fill=(248, 239, 223, 235))
    uidraw.text((42, height - 102), "Temperament", fill=(248, 239, 223, 136))
    uidraw.text((42, height - 74), "warming", fill=(248, 239, 223, 236))
    uidraw.text((252, height - 102), "Blush pressure", fill=(248, 239, 223, 136))
    uidraw.text((252, height - 74), "0.68", fill=(248, 239, 223, 236))
    uidraw.text((440, height - 102), "Gaze drift", fill=(248, 239, 223, 136))
    uidraw.text((440, height - 74), "right curious", fill=(248, 239, 223, 236))
    uidraw.text((650, height - 87), "The creature is relaxing under short, gentle grooming strokes.", fill=(248, 239, 223, 186))

    ui = ui.filter(ImageFilter.GaussianBlur(0.2))
    image = Image.alpha_composite(image, ui)
    image = ImageChops.screen(image, Image.new("RGBA", (width, height), (10, 6, 10, 20)))
    image.save(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
