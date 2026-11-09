"""BMW E30 headlight adapter rings ("China" headlight spacers).

Part 1 - big flange   : X envelope 171, Y envelope 167, ring OD 163 / ID 140
Part 2 - small flange : X envelope 145, Y envelope 140, ring OD 135 / ID 112.5

Both parts are rings whose wall is tall on one side and short on the
opposite side.  The top face is a single plane tilted about the X axis,
so the wall height changes smoothly from ``height_lower`` at -Y to
``height_upper`` at +Y - the "smooth change of height from one side to
the opposite side" the sketch asks for.

Four mounting ears reach the stated overall X/Y envelope.  Ear size,
thickness and hole diameter were only partly legible on the sketch, so
they are grouped here and are trivial to change.

All dimensions in millimetres.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import cadquery as cq


@dataclass
class AdapterSpec:
    name: str
    od: float                       # outer diameter of the ring
    id: float                       # inner diameter of the ring
    height_lower: float             # wall height at -Y ("нижняя сторона")
    height_upper: float             # wall height at +Y ("противоположная сторона")
    width: float                    # overall X envelope (ring + ears)
    contour_height: float           # overall Y envelope (ring + ears)
    ear_width: float = 24.0         # tangential width of an ear
    hole_dia: float = 6.0           # mounting hole diameter
    hole_inset: float = 4.0         # hole centre inset from the outer rim
    n_holes: int = 4

    @property
    def outer_r(self) -> float:
        return self.od / 2.0

    @property
    def inner_r(self) -> float:
        return self.id / 2.0

    @property
    def ring_wall(self) -> float:
        """Radial width of the annulus (the sketch's "ширина кольцевой части")."""
        return (self.od - self.id) / 2.0

    @property
    def height_max(self) -> float:
        return max(self.height_lower, self.height_upper)

    def height_at(self, y: float) -> float:
        """Wall height of the tilted top plane at coordinate ``y``."""
        m = (self.height_upper - self.height_lower) / self.od
        c = (self.height_upper + self.height_lower) / 2.0
        return c + m * y

    @property
    def ears(self) -> tuple:
        """(angle_deg, reach_from_centre) for the four mounting ears."""
        return (
            (0.0, self.width / 2.0),
            (180.0, self.width / 2.0),
            (90.0, self.contour_height / 2.0),
            (270.0, self.contour_height / 2.0),
        )

    @property
    def hole_centres(self) -> tuple:
        out = []
        hr = self.outer_r - self.hole_inset
        for i in range(self.n_holes):
            a = math.radians(360.0 * i / self.n_holes)
            out.append((hr * math.cos(a), hr * math.sin(a)))
        return tuple(out)


def _ear(reach: float, width: float, thick: float) -> cq.Workplane:
    """A mounting ear running along +X from the centre to ``reach``, rounded tip."""
    rect = cq.Workplane("XY").center(reach / 2.0, 0).rect(reach, width).extrude(thick)
    tip = cq.Workplane("XY").center(reach - width / 2.0, 0).circle(width / 2.0).extrude(thick)
    return rect.union(tip)


def build(spec: AdapterSpec) -> cq.Workplane:
    """Return the finished adapter as a CadQuery solid."""
    r_out, r_in = spec.outer_r, spec.inner_r
    h_max = spec.height_max

    # Ring + ears, built to full height and trimmed afterwards so the
    # ears follow the same tilted top face as the ring.
    body = cq.Workplane("XY").circle(r_out).circle(r_in).extrude(h_max)
    for ang, reach in spec.ears:
        body = body.union(_ear(reach, spec.ear_width, h_max)
                          .rotate((0, 0, 0), (0, 0, 1), ang))

    # Tilted top: keep material below the plane through z=(hi+lo)/2.
    slope = (spec.height_upper - spec.height_lower) / spec.od
    cut = (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, (spec.height_upper + spec.height_lower) / 2.0),
                     rotate=(math.degrees(math.atan(slope)), 0, 0))
        .rect(4 * r_out, 4 * r_out)
        .extrude(3 * h_max)
    )
    body = body.cut(cut)

    for (x, y) in spec.hole_centres:
        body = body.cut(cq.Workplane("XY").center(x, y)
                        .circle(spec.hole_dia / 2.0).extrude(3 * h_max))
    return body


def spec_part1() -> AdapterSpec:
    return AdapterSpec(
        name="part1_big_flange",
        od=163.0, id=140.0,
        height_lower=9.0, height_upper=6.0,
        width=171.0, contour_height=167.0,
    )


def spec_part2() -> AdapterSpec:
    return AdapterSpec(
        name="part2_small_flange",
        od=135.0, id=112.5,
        height_lower=39.0, height_upper=34.0,
        width=145.0, contour_height=140.0,
    )


def make_part1() -> cq.Workplane:
    return build(spec_part1())


def make_part2() -> cq.Workplane:
    return build(spec_part2())
