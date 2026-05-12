#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def blend_vertical(top: tuple[int, int, int], bottom: tuple[int, int, int], height: int) -> Image.Image:
    image = Image.new("RGB", (1, height))
    pixels = image.load()
    for y in range(height):
        t = y / max(1, height - 1)
        pixels[0, y] = tuple(int(lerp(top[i], bottom[i], t)) for i in range(3))
    return image.resize((1080, height))


def radial_glow(size: tuple[int, int], center: tuple[float, float], radius: float, color: tuple[int, int, int], alpha: float) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    pixels = image.load()
    cx, cy = center
    for y in range(height):
      for x in range(width):
            d = math.hypot(x - cx, y - cy)
            if d > radius:
                continue
            t = 1 - d / radius
            pixels[x, y] = (*color, int(255 * alpha * t * t))
    return image.filter(ImageFilter.GaussianBlur(radius / 7))


def ridge_points(width: int, height: int, y_base: float, bend: float, amp: float, phase: float) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    count = 9
    for i in range(count):
        t = i / (count - 1)
        y = y_base + math.sin(t * math.pi * 2 + phase) * amp + (t - 0.5) * bend
        points.append((t * width, y * height))
    return points


def polyline_samples(points: list[tuple[float, float]], steps: int) -> list[tuple[float, float]]:
    sampled: list[tuple[float, float]] = []
    for i in range(len(points) - 1):
        ax, ay = points[i]
        bx, by = points[i + 1]
        for step in range(steps):
            t = step / steps
            sampled.append((lerp(ax, bx, t), lerp(ay, by, t)))
    sampled.append(points[-1])
    return sampled


def draw_scene(width: int, height: int) -> Image.Image:
    background = blend_vertical((32, 9, 15), (2, 2, 3), height).convert("RGBA")
    background = background.resize((width, height))

    composite = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    composite.alpha_composite(radial_glow((width, height), (width * 0.58, height * 0.54), width * 0.42, (229, 68, 85), 0.2))
    composite.alpha_composite(radial_glow((width, height), (width * 0.18, height * 0.2), width * 0.18, (139, 200, 214), 0.12))
    composite.alpha_composite(radial_glow((width, height), (width * 0.76, height * 0.18), width * 0.22, (255, 127, 124), 0.12))
    background.alpha_composite(composite)

    terrain = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    terrain_draw = ImageDraw.Draw(terrain)
    layers = [
        (0.72, (40, 10, 16, 235)),
        (0.81, (21, 7, 10, 246)),
        (0.9, (10, 5, 7, 255)),
    ]
    for idx, (y_base, color) in enumerate(layers):
        points = [(0, height)]
        for i in range(11):
            t = i / 10
            y = height * (
                y_base
                + math.sin(t * math.pi * 2 + idx * 0.7) * (0.025 + idx * 0.01)
                + math.cos(t * math.pi * 4 + idx) * 0.012
            )
            points.append((t * width, y))
        points.append((width, height))
        terrain_draw.polygon(points, fill=color)
    background.alpha_composite(terrain)

    ridge_specs = [
        (0.24, 0.1, 0.06, 0.0, 0.12),
        (0.39, 0.14, 0.08, 1.3, 0.14),
        (0.55, 0.08, 0.07, 2.6, 0.15),
        (0.72, 0.16, 0.06, 3.9, 0.18),
    ]
    for y_base, bend, amp, phase, thickness in ridge_specs:
        top = ridge_points(width, height, y_base, bend, amp, phase)
        bottom = list(reversed([(x, y + height * thickness) for x, y in top]))
        ridge = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ridge_draw = ImageDraw.Draw(ridge)
        ridge_draw.polygon(top + bottom, fill=(188, 42, 59, 168))
        ridge_draw.line(top, fill=(255, 199, 188, 120), width=2)
        ridge = ridge.filter(ImageFilter.GaussianBlur(1.2))
        glow = ridge.filter(ImageFilter.GaussianBlur(18))
        glow = ImageChops.multiply(glow, Image.new("RGBA", (width, height), (255, 120, 120, 220)))
        background.alpha_composite(glow)
        background.alpha_composite(ridge)

    route_seeds = [
        [(0.04, 0.76), (0.2, 0.66), (0.42, 0.55), (0.64, 0.45), (0.94, 0.34)],
        [(0.1, 0.88), (0.26, 0.74), (0.46, 0.65), (0.68, 0.61), (0.9, 0.58)],
        [(0.16, 0.3), (0.32, 0.42), (0.54, 0.54), (0.78, 0.7)],
        [(0.2, 0.16), (0.38, 0.28), (0.58, 0.33), (0.84, 0.28)],
    ]
    routes = [polyline_samples([(x * width, y * height) for x, y in seed], 22) for seed in route_seeds]

    route_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    route_draw = ImageDraw.Draw(route_layer)
    for index, route in enumerate(routes):
        base = (244, 95, 108, 110) if index < 2 else (242, 193, 151, 86)
        top = (255, 189, 183, 188) if index < 2 else (245, 214, 184, 140)
        route_draw.line(route, fill=base, width=9 if index < 2 else 6)
        route_draw.line(route, fill=top, width=4 if index < 2 else 3)
    background.alpha_composite(route_layer.filter(ImageFilter.GaussianBlur(2)))

    marker_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    marker_draw = ImageDraw.Draw(marker_layer)
    pylons = [
        (0.12, 0.69), (0.3, 0.58), (0.51, 0.48), (0.73, 0.39), (0.87, 0.33),
        (0.18, 0.82), (0.44, 0.64), (0.71, 0.61), (0.29, 0.25), (0.61, 0.31), (0.82, 0.27),
    ]
    for idx, (x, y) in enumerate(pylons):
        px = x * width
        py = y * height
        pole_height = 26 + (idx % 3) * 12
        marker_draw.line((px, py, px, py - pole_height), fill=(247, 222, 214, 112), width=1)
        marker_draw.line((px - 8, py - pole_height * 0.6, px + 8, py - pole_height * 0.6), fill=(247, 222, 214, 92), width=1)
        marker_draw.ellipse((px - 3, py - pole_height - 3, px + 3, py - pole_height + 3), fill=(255, 132, 124, 188))
        marker_draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill=(242, 193, 151, 48))
    background.alpha_composite(marker_layer)

    worker_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    worker_draw = ImageDraw.Draw(worker_layer)
    worker_positions = []
    for route_index, route in enumerate(routes):
        picks = [0.12, 0.42, 0.74] if route_index == 0 else ([0.28, 0.66] if route_index == 1 else [0.35, 0.7])
        for pick in picks:
            point = route[int((len(route) - 1) * pick)]
            worker_positions.append(point)
    for px, py in worker_positions:
        worker_draw.ellipse((px - 7, py - 7, px + 7, py + 7), fill=(229, 68, 85, 100))
        worker_draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill=(255, 234, 222, 232))
    background.alpha_composite(worker_layer.filter(ImageFilter.GaussianBlur(1)))

    pulse_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pulse_centers = [
        route_points[int(len(route_points) * pick)]
        for route_points, pick in [(routes[0], 0.48), (routes[1], 0.7), (routes[2], 0.4)]
    ]
    for px, py in pulse_centers:
        pulse_layer.alpha_composite(radial_glow((width, height), (px, py), 70, (255, 145, 130), 0.55))
    background.alpha_composite(pulse_layer)

    particle_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    particle_draw = ImageDraw.Draw(particle_layer)
    for i in range(220):
        x = ((i * 73) % width)
        y = ((i * 113) % height)
        size = 1 + (i % 4) * 0.6
        if i % 9 == 0:
            particle_draw.rectangle((x - size, y - size, x + size, y + size), fill=(242, 193, 151, 100))
        else:
            particle_draw.ellipse((x - size, y - size, x + size, y + size), fill=(229, 68, 85, 70 + (i % 5) * 20))
    background.alpha_composite(particle_layer.filter(ImageFilter.GaussianBlur(0.6)))

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    marks = [
        (0.08, 0.14, 60),
        (0.88, 0.18, 48),
        (0.78, 0.86, 72),
        (0.16, 0.78, 52),
    ]
    for x, y, size in marks:
        px = x * width
        py = y * height
        overlay_draw.ellipse((px - size, py - size, px + size, py + size), outline=(255, 226, 216, 38), width=1)
        overlay_draw.line((px - size - 10, py, px + size + 10, py), fill=(255, 226, 216, 34), width=1)
        overlay_draw.line((px, py - size - 10, px, py + size + 10), fill=(255, 226, 216, 34), width=1)
    background.alpha_composite(overlay)

    return background.convert("RGB")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    args = parser.parse_args()

    image = draw_scene(args.width, args.height)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
