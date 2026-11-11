"""BMW E30 headlight adapter rings ("China" headlight spacers).

Coordinate system (millimetres): ring centre O = (0; 0; 0); X horizontal,
Y vertical, Z height; top view uses X-Y.

Elements are given by their centre coordinates and the top-surface height
at that point.  The top surface follows the cubic smoothstep
    Z = Zmax - (Zmax - Zmin)(3t^2 - 2t^3),  t = (Y - Ymin)/(Ymax - Ymin)
which reproduces every tabulated value to < 0.002 mm.

Part 1 - ring OD 163 / ID 140, height 9 -> 6
    pads (mounting seats) A, B, C; ears D, E, F on the outer contour.
Part 2 - ring OD 145 / ID 112.5, height 39 -> 34
    slot S1 and pads S2, S3; three holes H1, H2, H3 from the STL.
    The three outer-contour points of the earlier sketch are NOT used
    here, so nothing is duplicated.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import cadquery as cq


@dataclass(frozen=True)
class Hole:
    """A through hole at (x, y) of diameter ``dia``."""
    label: str
    x: float
    y: float
    dia: float


@dataclass(frozen=True)
class Pad:
    """A round boss of ``pad_dia`` at (x, y) with an optional through hole."""
    label: str
    x: float
    y: float
    pad_dia: float
    hole_dia: float = 0.0


@dataclass(frozen=True)
class Slot:
    """A through slot of ``length`` x ``width`` at (x, y), rotated ``angle``."""
    label: str
    x: float
    y: float
    length: float
    width: float
    angle: float


@dataclass
class AdapterSpec:
    name: str
    od: float                      # outer diameter of the ring
    id: float                      # inner diameter of the ring
    z_hi: float                    # height at Ymin (lower side)
    z_lo: float                    # height at Ymax (upper side)
    y_min: float                   # smoothstep lower bound
    y_max: float                   # smoothstep upper bound
    pads: tuple = ()               # Pad (bosses, e.g. ears)
    holes: tuple = ()              # Hole (through holes in the ring)
    slots: tuple = ()              # Slot

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


def _pad(p: Pad, height: float) -> cq.Workplane:
    return (cq.Workplane("XY").center(p.x, p.y)
            .circle(p.pad_dia / 2.0).extrude(height))


def build(spec: AdapterSpec) -> cq.Workplane:
    """Return the finished adapter as a CadQuery solid."""
    r_out, r_in, z_max = spec.outer_r, spec.inner_r, spec.z_max

    body = cq.Workplane("XY").circle(r_out).extrude(z_max)
    for p in spec.pads:
        body = body.union(_pad(p, z_max))
    body = body.cut(cq.Workplane("XY").circle(r_in).extrude(z_max + 10))

    # smoothstep top face
    span = max(abs(spec.y_min), abs(spec.y_max))
    for p in spec.pads:
        span = max(span, abs(p.y) + p.pad_dia)
    n = 360
    ys = [-span + 2.0 * span * i / n for i in range(n + 1)]
    prof = [(y, spec.z_of_y(y)) for y in ys]
    prof += [(ys[-1], z_max + 20.0), (ys[0], z_max + 20.0)]
    body = body.cut(cq.Workplane("YZ").polyline(prof).close()
                    .extrude(r_out + 60, both=True))

    for h in spec.holes:
        body = body.cut(cq.Workplane("XY").center(h.x, h.y)
                        .circle(h.dia / 2.0).extrude(z_max + 10))
    for p in spec.pads:
        if p.hole_dia > 0:
            body = body.cut(cq.Workplane("XY").center(p.x, p.y)
                            .circle(p.hole_dia / 2.0).extrude(z_max + 10))
    for s in spec.slots:
        cut = (cq.Workplane("XY").center(s.x, s.y)
               .slot2D(s.length - s.width, s.width)
               .extrude(z_max + 10))
        body = body.cut(cut.rotate((s.x, s.y, 0), (s.x, s.y, 1), s.angle))
    return body


def spec_part1() -> AdapterSpec:
    """Ring OD163 / ID140; pads A,B,C; ears D,E,F (width 171, height 167)."""
    return AdapterSpec(
        name="part1_ring_163",
        od=163.0, id=140.0,
        z_hi=9.0, z_lo=6.0, y_min=-81.5, y_max=81.5,
        holes=(
            Hole("A", -71.0, 17.0, 6.0),
            Hole("B", 65.0, 35.0, 6.0),
            Hole("C", -38.0, -63.0, 6.0),
        ),
        pads=(
            Pad("D", -78.0, 0.0, 15.0, 6.0),
            Pad("E", 78.0, 0.0, 15.0, 6.0),
            Pad("F", 0.0, -78.0, 15.0, 6.0),
        ),
    )


def spec_part2() -> AdapterSpec:
    """Ring OD145 / ID112.5; slot S1; pads S2,S3; STL holes H1,H2,H3."""
    return AdapterSpec(
        name="part2_ring_145",
        od=145.0, id=112.5,
        z_hi=39.0, z_lo=34.0, y_min=-72.5, y_max=72.5,
        holes=(
            Hole("S2", 66.0, -26.0, 6.0),
            Hole("S3", -19.0, -68.0, 6.0),
            Hole("H1", -63.27430, -0.26276, 10.15880),
            Hole("H2", 63.27444, 0.26286, 10.15884),
            Hole("H3", 0.26274, -63.27459, 10.15881),
        ),
        slots=(
            Slot("S1", -61.0, 31.0, 12.0, 2.0, -25.0),
        ),
    )


def make_part1() -> cq.Workplane:
    return build(spec_part1())


def make_part2() -> cq.Workplane:
    return build(spec_part2())
