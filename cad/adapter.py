"""BMW E30 headlight adapter rings ("China" headlight spacers).

Final specification (millimetres).

Coordinate system: ring centre O = (0; 0; 0); +X right, -X left, +Y up,
-Y down; Z = 0 is the bottom plane; top view uses X-Y.

Each part is a ring with six circular pads:

* three big mounting zones A, B, C (pad D15) carrying a through hole;
* three solid pads D, E, F (D11) with no hole.

The top surface follows the cubic smoothstep
    Z = Zmax - (Zmax - Zmin)(3t^2 - 2t^3),  t = (Y - Ymin)/(Ymax - Ymin)
which reproduces every tabulated value to better than 0.002 mm.

Part 1 - ring OD 163 / ID 140, height 9 -> 6, envelope 171 x 167
Part 2 - ring OD 135 / ID 112.5, height 39 -> 34, envelope 145 x 140
"""

from __future__ import annotations

from dataclasses import dataclass, field

import cadquery as cq


@dataclass(frozen=True)
class Pad:
    """A circular pad of ``pad_dia`` at (x, y) with an optional through hole."""
    label: str
    x: float
    y: float
    pad_dia: float
    hole_dia: float = 0.0

    @property
    def drilled(self) -> bool:
        return self.hole_dia > 0.0


@dataclass
class AdapterSpec:
    name: str
    od: float                      # outer diameter of the ring
    id: float                      # inner diameter of the ring
    z_hi: float                    # height at Ymin (lower side)
    z_lo: float                    # height at Ymax (upper side)
    y_min: float                   # smoothstep lower bound
    y_max: float                   # smoothstep upper bound
    pads: tuple = ()               # Pad

    @property
    def outer_r(self) -> float:
        return self.od / 2.0

    @property
    def inner_r(self) -> float:
        return self.id / 2.0

    @property
    def ring_wall(self) -> float:
        return (self.od - self.id) / 2.0

    @property
    def z_max(self) -> float:
        return max(self.z_hi, self.z_lo)

    @property
    def width_span(self) -> float:
        """Half-extent of the whole outline (ring plus pads)."""
        span = self.outer_r
        for p in self.pads:
            span = max(span, abs(p.x) + p.pad_dia / 2.0,
                       abs(p.y) + p.pad_dia / 2.0)
        return span

    def z_of_y(self, y: float) -> float:
        t = (y - self.y_min) / (self.y_max - self.y_min)
        t = min(1.0, max(0.0, t))
        return self.z_hi - (self.z_hi - self.z_lo) * (3.0 * t * t - 2.0 * t * t * t)


def build(spec: AdapterSpec) -> cq.Workplane:
    """Return the finished adapter as a CadQuery solid."""
    r_out, r_in, z_max = spec.outer_r, spec.inner_r, spec.z_max

    body = cq.Workplane("XY").circle(r_out).extrude(z_max)
    for p in spec.pads:
        body = body.union(cq.Workplane("XY").center(p.x, p.y)
                          .circle(p.pad_dia / 2.0).extrude(z_max))
    body = body.cut(cq.Workplane("XY").circle(r_in).extrude(z_max + 10))

    # smoothstep top face
    span = spec.width_span
    n = 360
    ys = [-span + 2.0 * span * i / n for i in range(n + 1)]
    prof = [(y, spec.z_of_y(y)) for y in ys]
    prof += [(ys[-1], z_max + 20.0), (ys[0], z_max + 20.0)]
    body = body.cut(cq.Workplane("YZ").polyline(prof).close()
                    .extrude(r_out + 60, both=True))

    for p in spec.pads:
        if p.drilled:
            body = body.cut(cq.Workplane("XY").center(p.x, p.y)
                            .circle(p.hole_dia / 2.0).extrude(z_max + 10))
    return body


def spec_part1() -> AdapterSpec:
    """Ring OD163 / ID140; big zones A, B, C; solid pads D, E, F."""
    return AdapterSpec(
        name="part1_ring_163",
        od=163.0, id=140.0,
        z_hi=9.0, z_lo=6.0, y_min=-85.5, y_max=81.5,
        pads=(
            Pad("A", -71.0, 17.0, 15.0, 10.1588),
            Pad("B", 62.0, 35.0, 15.0, 10.1588),
            Pad("C", -39.0, -60.0, 15.0, 10.1588),
            Pad("D", -80.0, 0.0, 11.0),
            Pad("E", 80.0, 0.0, 11.0),
            Pad("F", 0.0, -80.0, 11.0),
        ),
    )


def spec_part2() -> AdapterSpec:
    """Ring OD135 / ID112.5; big zones A, B, C; solid pads D, E, F."""
    return AdapterSpec(
        name="part2_ring_135",
        od=135.0, id=112.5,
        z_hi=39.0, z_lo=34.0, y_min=-72.5, y_max=67.5,
        pads=(
            Pad("A", -54.929, 31.410, 15.0, 10.1588),
            Pad("B", 54.929, -31.410, 15.0, 10.1588),
            Pad("C", -31.410, -54.929, 15.0, 10.1588),
            Pad("D", -67.0, 0.0, 11.0),
            Pad("E", 67.0, 0.0, 11.0),
            Pad("F", 0.0, -67.0, 11.0),
        ),
    )


def make_part1() -> cq.Workplane:
    return build(spec_part1())


def make_part2() -> cq.Workplane:
    return build(spec_part2())
