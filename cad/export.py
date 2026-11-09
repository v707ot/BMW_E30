"""Export the two adapters to STEP and STL, and print a dimension report."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import adapter  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "models")


def report(name: str, solid) -> None:
    bb = solid.val().BoundingBox()
    print(f"{name}")
    print(f"  envelope  X={bb.xlen:.2f}  Y={bb.ylen:.2f}  Z={bb.zlen:.2f} mm")
    print(f"  volume    {solid.val().Volume() / 1000.0:.1f} cm^3")


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for maker in (adapter.make_part1, adapter.make_part2):
        solid = maker()
        name = maker.__name__.replace("make_", "")
        report(name, solid)
        for ext in ("step", "stl"):
            path = os.path.join(OUT, f"{name}.{ext}")
            if ext == "step":
                solid.val().exportStep(path)
            else:
                solid.val().exportStl(path, tolerance=0.05)
            print(f"  wrote {path}")


if __name__ == "__main__":
    main()
