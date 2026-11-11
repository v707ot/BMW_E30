"""Dimensioned 2D technical drawings (PNG) for both adapters.

TOP view (X-Y): ring, every element (holes, pads/ears, slot) with its
centre coordinates.  FRONT view (Y-Z): the smoothstep top profile.
"""

from __future__ import annotations

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, FancyBboxPatch

sys.path.insert(0, os.path.dirname(__file__))
import adapter  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "renders")
INK, DIM, AUX, MNT, SLOT = "#141414", "#0b57a4", "#b23b3b", "#1a7a3c", "#a24bcc"


def _dim_h(ax, x0, x1, y, text, size=10):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=0.9,
                                shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2.0, y, text, color=DIM, fontsize=size, ha="center",
            va="center", backgroundcolor="white")


def _dim_v(ax, y0, y1, x, text, size=10):
    ax.annotate("", xy=(x, y1), xytext=(x, y0),
                arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=0.9,
                                shrinkA=0, shrinkB=0))
    ax.text(x, (y0 + y1) / 2.0, text, color=DIM, fontsize=size, ha="center",
            va="center", rotation=90, backgroundcolor="white")


def _mark(ax, x, y):
    ax.plot([x - 6, x + 6], [y, y], color=AUX, lw=0.7)
    ax.plot([x, x], [y - 6, y + 6], color=AUX, lw=0.7)


def top_view(ax, spec):
    r_out, r_in = spec.outer_r, spec.inner_r
    ax.add_patch(Circle((0, 0), r_out, fill=False, ec=INK, lw=2.0))
    ax.add_patch(Circle((0, 0), r_in, fill=False, ec=INK, lw=1.5))

    for p in spec.pads:
        ax.add_patch(Circle((p.x, p.y), p.pad_dia / 2.0, fill=False, ec=INK, lw=1.4))
        if p.hole_dia > 0:
            ax.add_patch(Circle((p.x, p.y), p.hole_dia / 2.0, fill=False, ec=INK, lw=1.0))
        _mark(ax, p.x, p.y)
        ax.text(p.x, p.y + 10, p.label, color=INK, fontsize=13, fontweight="bold", ha="center")
        ax.text(p.x, p.y - 11, f"({p.x:g}; {p.y:g})", color=INK, fontsize=7, ha="center")

    for h in spec.holes:
        ax.add_patch(Circle((h.x, h.y), h.dia / 2.0, fill=False, ec=MNT, lw=1.2))
        _mark(ax, h.x, h.y)
        ax.text(h.x, h.y + 10, h.label, color=MNT, fontsize=12, fontweight="bold", ha="center")
        ax.text(h.x, h.y - 11, f"({h.x:g}; {h.y:g})", color=MNT, fontsize=7, ha="center")

    for s in spec.slots:
        ax.add_patch(FancyBboxPatch((s.x - s.length / 2, s.y - s.width / 2),
                                    s.length, s.width,
                                    boxstyle="round,pad=0,rounding_size=1",
                                    fill=False, ec=SLOT, lw=1.3,
                                    transform=matplotlib.transforms.Affine2D()
                                    .rotate_deg_around(s.x, s.y, s.angle)
                                    + ax.transData))
        _mark(ax, s.x, s.y)
        ax.text(s.x, s.y + 10, s.label, color=SLOT, fontsize=13, fontweight="bold", ha="center")
        ax.text(s.x, s.y - 13, f"({s.x:g}; {s.y:g})", color=SLOT, fontsize=7, ha="center")

    ax.plot([-r_out - 16, r_out + 16], [0, 0], color=AUX, lw=0.7, dashes=(9, 3, 2, 3))
    ax.plot([0, 0], [-r_out - 16, r_out + 16], color=AUX, lw=0.7, dashes=(9, 3, 2, 3))

    _dim_h(ax, -r_out, r_out, r_out + 9, f"Ø{spec.od:g}")
    _dim_h(ax, -r_in, r_in, -r_out - 9, f"Ø{spec.id:g}")
    ax.text(0, -r_out - 22, f"ширина кольца {spec.ring_wall:g}", color=DIM,
            fontsize=9, ha="center")

    lim = max(spec.width_span, 60) + 30
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axis("off")


def front_view(ax, spec):
    r_out, r_in = spec.outer_r, spec.inner_r
    span = max(abs(spec.y_min), abs(spec.y_max))
    n = 360
    ys = [-span + 2.0 * span * i / n for i in range(n + 1)]
    ax.add_patch(Polygon([(y, 0) for y in ys] + [(y, spec.z_of_y(y)) for y in ys[::-1]],
                         closed=True, ec=INK, lw=1.9, fill=False))
    ax.plot([-r_in, -r_in], [0, spec.z_of_y(-r_in)], color=INK, lw=1.1)
    ax.plot([r_in, r_in], [0, spec.z_of_y(r_in)], color=INK, lw=1.1)
    ax.plot([-r_out, r_out], [0, 0], color=INK, lw=1.9)
    ax.plot([-r_in, r_in], [0, 0], color=INK, lw=1.3)

    _dim_v(ax, 0, spec.z_of_y(-span), -r_out - 16, f"{spec.z_hi:g}")
    _dim_v(ax, 0, spec.z_of_y(span), r_out + 16, f"{spec.z_lo:g}")
    _dim_h(ax, -r_out, r_out, -16, f"Ø{spec.od:g}")
    ax.plot([-r_out - 22, r_out + 22], [0, 0], color=AUX, lw=0.7, dashes=(9, 3, 2, 3))
    ax.text(0, spec.z_of_y(0) + 14, "плавное изменение высоты (smoothstep)",
            color=INK, fontsize=9, ha="center")

    ax.set_xlim(-r_out - 36, r_out + 36)
    ax.set_ylim(-30, spec.z_max + 34)
    ax.set_aspect("equal")
    ax.axis("off")


def sheet(spec, path):
    fig, axes = plt.subplots(1, 2, figsize=(17, 9.2), dpi=110)
    fig.patch.set_facecolor("white")
    top_view(axes[0], spec)
    front_view(axes[1], spec)
    axes[0].set_title("ВИД СВЕРХУ  (X–Y)", fontsize=13, color=INK, pad=16)
    axes[1].set_title("ВИД СПЕРЕДИ  (Y–Z)", fontsize=13, color=INK, pad=16)
    fig.suptitle(f"{spec.name}   •   все размеры в мм   •   "
                 "зелёный — отверстия, чёрный — ушки, фиолетовый — паз",
                 fontsize=13, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print("wrote", path)


def main():
    os.makedirs(OUT, exist_ok=True)
    sheet(adapter.spec_part1(), os.path.join(OUT, "part1_drawing.png"))
    sheet(adapter.spec_part2(), os.path.join(OUT, "part2_drawing.png"))


if __name__ == "__main__":
    main()
