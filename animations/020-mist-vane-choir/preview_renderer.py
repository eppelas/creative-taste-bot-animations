#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


PALETTES = [
    ((134, 214, 210), (199, 239, 218), (247, 209, 157)),
    ((184, 180, 255), (134, 214, 210), (255, 255, 255)),
    ((239, 177, 196), (247, 209, 157), (199, 239, 218)),
    ((179, 216, 238), (255, 255, 255), (184, 180, 255)),
]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def mix_color(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(lerp(x, y, t)) for x, y in zip(a, b))


def vertical_gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size)
    pixels = image.load()
    for y in range(height):
      t = y / max(1, height - 1)
      color = mix_color(top, bottom, t)
      for x in range(width):
        pixels[x, y] = color
    return image


def add_radial_glow(base: Image.Image, center: tuple[float, float], radius: float, color: tuple[int, int, int], alpha: int) -> None:
    width, height = base.size
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx, cy = center
    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
    draw.ellipse(bbox, fill=(*color, alpha))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius * 0.22))
    base.alpha_composite(overlay)


def draw_fibers(image: Image.Image, rng: random.Random) -> None:
    width, height = image.size
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for _ in range(max(84, width // 14)):
        x = rng.uniform(0, width)
        y = rng.uniform(0.06 * height, 0.98 * height)
        length = rng.uniform(0.08, 0.22) * height
        drift = rng.uniform(-34, 34)
        lift = rng.uniform(-12, 12)
        weight = rng.uniform(1.0, 2.0)
        alpha = int(rng.uniform(30, 78))
        points = [
            (x, y),
            (x + drift * 0.18, y - length * 0.22 + lift),
            (x + drift * 0.64, y + length * 0.34),
            (x + drift, y + length),
        ]
        draw.line(points, fill=(255, 255, 255, alpha), width=int(weight), joint="curve")

    overlay = overlay.filter(ImageFilter.GaussianBlur(0.8))
    image.alpha_composite(overlay)


def draw_vanes(image: Image.Image, rng: random.Random) -> None:
    width, height = image.size
    vane_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))

    for index in range(max(20, width // 56)):
        palette = PALETTES[index % len(PALETTES)]
        cx = rng.uniform(0.08, 0.92) * width
        cy = rng.uniform(0.12, 0.84) * height
        size = rng.uniform(0.05, 0.12) * min(width, height)
        openness = rng.uniform(0.44, 1.05)
        stretch = rng.uniform(0.78, 1.42)
        angle = rng.uniform(-0.22, 0.22)
        half_w = size * (0.42 + openness * 0.32)
        half_h = size * stretch * (0.8 + openness * 0.26)

        local_size = (int(half_w * 2 + 70), int(half_h * 2 + 70))
        local = Image.new("RGBA", local_size, (0, 0, 0, 0))
        mask = Image.new("L", local_size, 0)
        local_draw = ImageDraw.Draw(local)
        mask_draw = ImageDraw.Draw(mask)
        mx, my = local_size[0] / 2, local_size[1] / 2
        points = [
            (mx, my - half_h),
            (mx + half_w, my - half_h * 0.58),
            (mx + half_w, my + half_h * 0.34),
            (mx, my + half_h),
            (mx - half_w, my + half_h * 0.34),
            (mx - half_w, my - half_h * 0.58),
        ]

        mask_draw.polygon(points, fill=210)
        for y in range(local_size[1]):
            t = y / max(1, local_size[1] - 1)
            if t < 0.5:
                color = mix_color(palette[0], palette[1], t * 2)
            else:
                color = mix_color(palette[1], palette[2], (t - 0.5) * 2)
            local_draw.line([(0, y), (local_size[0], y)], fill=(*color, 155))

        local.putalpha(mask)
        local_draw = ImageDraw.Draw(local)
        local_draw.line(
            [(mx, my - half_h * 0.88), (mx + half_w * 0.08, my), (mx + half_w * 0.06, my + half_h * 0.9)],
            fill=(255, 255, 255, 120),
            width=2,
        )
        local_draw.polygon(points, outline=(255, 255, 255, 138), width=2)
        local = local.filter(ImageFilter.GaussianBlur(0.55))
        local = local.rotate(math.degrees(angle), resample=Image.Resampling.BICUBIC, expand=True)

        glow = local.copy().filter(ImageFilter.GaussianBlur(16))
        alpha_scale = rng.uniform(0.45, 0.74)
        glow.putalpha(glow.getchannel("A").point(lambda p: int(p * alpha_scale)))
        gx = int(cx - glow.size[0] / 2)
        gy = int(cy - glow.size[1] / 2)
        lx = int(cx - local.size[0] / 2)
        ly = int(cy - local.size[1] / 2)

        vane_layer.alpha_composite(glow, (gx, gy))
        vane_layer.alpha_composite(local, (lx, ly))

    image.alpha_composite(vane_layer)


def draw_motes(image: Image.Image, rng: random.Random) -> None:
    width, height = image.size
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for _ in range(max(120, width // 8)):
        x = rng.uniform(0, width)
        y = rng.uniform(0.02 * height, height)
        r = rng.uniform(1.2, 4.2)
        alpha = int(rng.uniform(42, 140))
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, alpha))
    overlay = overlay.filter(ImageFilter.GaussianBlur(0.45))
    image.alpha_composite(overlay)


def draw_pressure_rings(image: Image.Image) -> None:
    width, height = image.size
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    center = (width * 0.54, height * 0.62)
    for index, scale in enumerate((0.18, 0.28, 0.4)):
        rx = width * scale
        ry = height * scale * 0.34
        alpha = int(82 - index * 20)
        draw.ellipse(
            [center[0] - rx, center[1] - ry, center[0] + rx, center[1] + ry],
            outline=(255, 255, 255, alpha),
            width=2,
        )
    overlay = overlay.filter(ImageFilter.GaussianBlur(0.5))
    image.alpha_composite(overlay)


def draw_panels(image: Image.Image) -> None:
    width, height = image.size
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    def rounded_panel(box: tuple[float, float, float, float], radius: int) -> None:
        draw.rounded_rectangle(box, radius=radius, fill=(255, 255, 255, 128), outline=(59, 69, 88, 28), width=2)

    rounded_panel((18, 18, min(width * 0.5, 560), 240), 24)
    rounded_panel((18, height - 140, width - 18, height - 18), 20)
    rounded_panel((width - 120, 18, width - 18, 62), 22)
    overlay = overlay.filter(ImageFilter.GaussianBlur(0.35))
    image.alpha_composite(overlay)

    text = Image.new("RGBA", image.size, (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text)
    text_draw.text((40, 42), "Code Animation Study #020", fill=(41, 49, 65, 150))
    text_draw.text((40, 76), "Mist Vane Choir", fill=(41, 49, 65, 235))
    text_draw.text(
        (40, 116),
        "A pale atmospheric branch of translucent HTML with\nsoft vanes, wet fibers, and fog pressure interaction.",
        fill=(41, 49, 65, 168),
        spacing=7,
    )
    text_draw.text((width - 88, 30), "Index", fill=(41, 49, 65, 210))
    text_draw.text((42, height - 112), "Pressure front   ringing", fill=(41, 49, 65, 186))
    text_draw.text((42, height - 84), "Choir openness   0.67", fill=(41, 49, 65, 186))
    text_draw.text((42, height - 56), "Fiber drift   low sweep", fill=(41, 49, 65, 186))
    image.alpha_composite(text)


def render(output: Path, width: int, height: int) -> None:
    rng = random.Random(20)
    base = vertical_gradient((width, height), (238, 241, 244), (216, 220, 227)).convert("RGBA")
    add_radial_glow(base, (width * 0.16, height * 0.16), width * 0.2, (255, 255, 255), 190)
    add_radial_glow(base, (width * 0.76, height * 0.24), width * 0.18, (199, 239, 218), 86)
    add_radial_glow(base, (width * 0.68, height * 0.76), width * 0.18, (184, 180, 255), 58)

    fog = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    fog_draw = ImageDraw.Draw(fog)
    fog_draw.ellipse(
        [width * -0.08, height * 0.42, width * 0.58, height * 1.08],
        fill=(255, 255, 255, 90),
    )
    fog_draw.ellipse(
        [width * 0.34, height * 0.36, width * 1.06, height * 1.02],
        fill=(248, 250, 255, 84),
    )
    fog = fog.filter(ImageFilter.GaussianBlur(40))
    base.alpha_composite(fog)

    draw_fibers(base, rng)
    draw_vanes(base, rng)
    draw_motes(base, rng)
    draw_pressure_rings(base)
    draw_panels(base)

    final = Image.new("RGB", (width, height), (255, 255, 255))
    final.paste(base, mask=base.getchannel("A"))
    final.save(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    render(args.output, args.width, args.height)
    print(f"screenshot {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
