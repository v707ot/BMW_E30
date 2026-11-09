"""BMW E30 headlight adapter rings ("China" headlight spacers).

Geometry follows the supplied coordinate system exactly:

* origin O(0,0) at the centre of the ring, X = horizontal, Y = up,
  Z = part height; all values in millimetres;
* every fastening element is a circular pad of a given outer diameter
  with a through hole, positioned by the centre coordinates;
* the part outline is the ring plus those pads, so the pads form the
  "ears" that reach the overall X/Y envelope;
* the top surface height varies smoothly along Y following a cubic
  smoothstep between the two stated heights.

Part 1 - big flange   : X 171, Y 167, ring OD 163 / ID 140, Z 9 -> 6
Part 2 - small flange : X 145, Y 140, ring OD 135 / ID 112.5, Z 39 -> 34
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import cadquery as cq


@dataclass(frozen=True)
class Hole:
    """A fastening element: a pad of ``pad_dia`` with a ``hole_dia`` hole."""
    x: float
    y: float
    pad_dia: float
    hole_dia: float


@dataclass
class AdapterSpec:
    name: str
    od: float                      # outer diameter of the ring
    id: float                      # inner diameter of the ring
    z_at_y_neg: float              # height at Y = -od/2
    z_at_y_pos: float              # height at Y = +od/2
    width: float                   # overall X envelope (ring + pads)
    contour_height: float          # overall Y envelope (ring + pads)
    holes: tuple = ()

    @property
    def outer_r(self) -> float:
        return self.od / 2.0

    @property
    def inner_r(self) -> float:
        return self.id / 2.0

    @property
    def ring_wall(self) -> float:
        """Radial width of the annulus ("ширина кольцевой части")."""
        return (self.od - self.id) / 2.0

    @property
    def z_max(self) -> float:
        return max(self.z_at_y_neg, self.z_at_y_pos)

    def z_of_y(self, y: float) -> float:
        """Top-surface height at ``y`` (cubic smoothstep, clamped at the ends)."""
        t = (y + self.od / 2.0) / self.od
        t = min(1.0, max(0.0, t))
        s = 1.0 - 3.0 * t * t + 2.0 * t * t * t
        return self.z_at_y_pos + (self.z_at_y_neg - self.z_at_y_pos) * s


def build(spec: AdapterSpec) -> cq.Workplane:
    """Return the finished adapter as a CadQuery solid."""
    r_out, r_in, z_max = spec.outer_r, spec.inner_r, spec.z_max

    # --- outline: ring disc + pads, central bore kept clear ----------
    body = cq.Workplane("XY").circle(r_out).extrude(z_max)
    for h in spec.holes:
        body = body.union(
            cq.Workplane("XY").center(h.x, h.y).circle(h.pad_dia / 2.0).extrude(z_max))
    body = body.cut(cq.Workplane("XY").circle(r_in).extrude(z_max + 10))

    # --- smoothstep top face -----------------------------------------
    # Cut away everything above the smoothstep curve, extruded along X.
    span = spec.contour_height / 2.0 + 12.0
    n = 240
    ys = [-span + 2.0 * span * i / n for i in range(n + 1)]
    prof = [(y, spec.z_of_y(y)) for y in ys]
    prof += [(ys[-1], z_max + 20.0), (ys[0], z_max + 20.0)]
    cutter = cq.Workplane("YZ").polyline(prof).close().extrude(r_out + 40, both=True)
    body = body.cut(cutter)

    # --- through holes -----------------------------------------------
    for h in spec.holes:
        body = body.cut(
            cq.Workplane("XY").center(h.x, h.y).circle(h.hole_dia / 2.0)
            .extrude(z_max + 10))
    return body


def spec_part1() -> AdapterSpec:
    return AdapterSpec(
        name="part1_big_flange",
        od=163.0, id=140.0,
        z_at_y_neg=9.0, z_at_y_pos=6.0,
        width=171.0, contour_height=167.0,
        holes=(
            Hole(+78.00,   0.00, 15.0, 7.0),
            Hole(-78.00,   0.00, 15.0, 7.0),
            Hole(+67.52, +31.49, 15.0, 3.0),
            Hole(-67.52, +31.49, 15.0, 3.0),
            Hole(-37.25, -64.52, 15.0, 3.0),
            Hole(  0.00, -78.00, 15.0, 7.0),
        ),
    )


def spec_part2() -> AdapterSpec:
    return AdapterSpec(
        name="part2_small_flange",
        od=135.0, id=112.5,
        z_at_y_neg=39.0, z_at_y_pos=34.0,
        width=145.0, contour_height=140.0,
        holes=(
            Hole(+65.50,   0.00, 14.0, 7.0),
            Hole(-65.50,   0.00, 14.0, 7.0),
            Hole(+53.26, +30.75, 16.0, 2.0),
            Hole(-53.26, +30.75, 16.0, 2.0),
            Hole(-30.75, -53.26, 16.0, 2.0),
            Hole(  0.00, -65.50, 14.0, 7.0),
        ),
    )


def make_part1() -> cq.Workplane:
    return build(spec_part1())


def make_part2() -> cq.Workplane:
    return build(spec_part2())
