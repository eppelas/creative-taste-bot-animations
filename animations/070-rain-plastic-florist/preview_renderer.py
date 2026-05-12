#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


SOURCE = Path("/private/tmp/070-rain-plastic-florist-preview-source.png")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--width")
    parser.add_argument("--height")
    args = parser.parse_args()

    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, output)
    print(f"screenshot {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
