"""Dimensioned 2D technical drawings (PNG) for both adapters.

Each sheet contains:
  * TOP view  (X-Y): ring diameters, overall envelope, ears, hole pattern
  * FRONT view (Y-Z): the tilted top face and both wall heights

Every dimension is taken directly from the source sketch.
"""

from __future__ import annotations

import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon

sys.path.insert(0, os.path.dirname(__file__))
import adapter  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "renders")
INK, DIM, AUX = "#141414", "#0b57a4", "#b23b3b"


def _dim_h(ax, x0, x1, y, text):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=0.9,
                                shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2.0, y, text, color=DIM, fontsize=10, ha="center",
            va="center", backgroundcolor="white")


def _dim_v(ax, y0, y1, x, text):
    ax.annotate("", xy=(x, y1), xytext=(x, y0),
                arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=0.9,
                                shrinkA=0, shrinkB=0))
    ax.text(x, (y0 + y1) / 2.0, text, color=DIM, fontsize=10, ha="center",
            va="center", rotation=90, backgroundcolor="white")


def _ear_polygon(spec, ang, reach):
    """Outline of one mounting ear: straight flanks plus a rounded tip."""
    w = spec.ear_width / 2.0
    tipx = reach - w
    pts = [(-4.0, -w), (tipx, -w)]
    for k in range(25):
        t = math.radians(-90.0 + 180.0 * k / 24.0)
        pts.append((tipx + w * math.cos(t), w * math.sin(t)))
    pts += [(tipx, w), (-4.0, w)]
    a = math.radians(ang)
    return [(x * math.cos(a) - y * math.sin(a),
             x * math.sin(a) + y * math.cos(a)) for x, y in pts]


def top_view(ax, spec):
    r_out, r_in = spec.outer_r, spec.inner_r
    ax.add_patch(Circle((0, 0), r_out, fill=False, ec=INK, lw=1.9))
    ax.add_patch(Circle((0, 0), r_in, fill=False, ec=INK, lw=1.5))
    for ang, reach in spec.ears:
        ax.add_patch(Polygon(_ear_polygon(spec, ang, reach), closed=True,
                             fill=False, ec=INK, lw=1.3))
    for (x, y) in spec.hole_centres:
        ax.add_patch(Circle((x, y), spec.hole_dia / 2.0, fill=False,
                            ec=INK, lw=1.0))
        ax.plot([x - 5, x + 5], [y, y], color=AUX, lw=0.7)
        ax.plot([x, x], [y - 5, y + 5], color=AUX, lw=0.7)
    ax.plot([-r_out - 14, r_out + 14], [0, 0], color=AUX, lw=0.7,
            dashes=(9, 3, 2, 3))
    ax.plot([0, 0], [-r_out - 14, r_out + 14], color=AUX, lw=0.7,
            dashes=(9, 3, 2, 3))

    _dim_h(ax, -r_out, r_out, r_out + 9, f"OD {spec.od:g}")
    _dim_h(ax, -r_in, r_in, -r_out - 9, f"ID {spec.id:g}")
    _dim_h(ax, -spec.width / 2.0, spec.width / 2.0, -spec.width / 2.0 - 18,
           f"X = {spec.width:g}")
    _dim_v(ax, -spec.contour_height / 2.0, spec.contour_height / 2.0,
           spec.contour_height / 2.0 + 20, f"Y = {spec.contour_height:g}")
    ax.annotate("", xy=(r_in, -r_out - 22), xytext=(r_out, -r_out - 22),
                arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=0.9))
    ax.text((r_in + r_out) / 2.0, -r_out - 30,
            f"ширина кольца {spec.ring_wall:g}", color=DIM, fontsize=9,
            ha="center", va="center")
    ax.text(0, -r_out - 42, f"отверстия ⌀{spec.hole_dia:g}",
            color=AUX, fontsize=9, ha="center")

    lim = spec.contour_height / 2.0 + 46
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axis("off")


def front_view(ax, spec):
    r_out, r_in = spec.outer_r, spec.inner_r
    hl, hu = spec.height_lower, spec.height_upper
    m = (hu - hl) / (2.0 * r_out)
    c = (hl + hu) / 2.0
    top = lambda y: c + m * y

    n = 160
    ys = [-r_out + 2 * r_out * i / n for i in range(n + 1)]
    ax.add_patch(Polygon([(y, 0) for y in ys] + [(y, top(y)) for y in ys[::-1]],
                         closed=True, ec=INK, lw=1.9, fill=False))
    ax.plot([-r_in, -r_in], [0, top(-r_in)], color=INK, lw=1.1)
    ax.plot([r_in, r_in], [0, top(r_in)], color=INK, lw=1.1)
    ax.plot([-r_out, r_out], [0, 0], color=INK, lw=1.9)
    ax.plot([-r_in, r_in], [0, 0], color=INK, lw=1.3)

    _dim_v(ax, 0, top(-r_out), -r_out - 15, f"{hl:g}")
    _dim_v(ax, 0, top(r_out), r_out + 15, f"{hu:g}")
    _dim_h(ax, -r_out, r_out, -14, f"OD {spec.od:g}")
    ax.plot([-r_out - 20, r_out + 20], [0, 0], color=AUX, lw=0.7,
            dashes=(9, 3, 2, 3))
    ax.text(0, top(0) + 9, "плавное изменение высоты", color=INK,
            fontsize=9, ha="center")

    ax.set_xlim(-r_out - 34, r_out + 34)
    ax.set_ylim(-26, hu + 20)
    ax.set_aspect("equal")
    ax.axis("off")


def sheet(spec, path):
    fig, axes = plt.subplots(1, 2, figsize=(17, 8.8), dpi=110)
    fig.patch.set_facecolor("white")
    top_view(axes[0], spec)
    front_view(axes[1], spec)
    axes[0].set_title("ВИД СВЕРХУ  (X–Y)", fontsize=13, color=INK, pad=16)
    axes[1].set_title("ВИД СПЕРЕДИ  (Y–Z)", fontsize=13, color=INK, pad=16)
    fig.suptitle(f"{spec.name}   •   все размеры в мм", fontsize=16, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print("wrote", path)


def main():
    os.makedirs(OUT, exist_ok=True)
    sheet(adapter.spec_part1(), os.path.join(OUT, "part1_drawing.png"))
    sheet(adapter.spec_part2(), os.path.join(OUT, "part2_drawing.png"))


if __name__ == "__main__":
    main()
