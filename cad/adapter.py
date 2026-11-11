"""BMW E30 headlight adapter rings ("China" headlight spacers).

Corrected layout (millimetres).  Parts are NOT interchangeable:

* Part 1 - the TALL ring, sits on the left:
    base OD 135 / ID 112.5, height 39 -> 34, overall width 145.
* Part 2 - the THIN ring, sits on the right:
    base OD 163 / ID 140, height 9 -> 6, overall width 171.

Per part, ring centre O = (0; 0; 0); X right, Y up, Z height above the
bottom plane (Z = 0).

Each part carries six pads:

* three big mounting zones H with a raised boss and a blind counterbore
  (no central through hole);
* three solid pads S with no hole.

The top surface follows the cubic smoothstep
    Z = Zmax - (Zmax - Zmin)(3t^2 - 2t^3),  t = (Y - Ymin)/(Ymax - Ymin)
reproducing every tabulated value to better than 0.002 mm.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import cadquery as cq


@dataclass(frozen=True)
class Pad:
    """Circular pad at (x, y): boss of ``pad_dia`` and optional counterbore."""
    label: str
    x: float
    y: float
    pad_dia: float
    bore_dia: float = 0.0          # 0 = solid pad, no counterbore
    bore_depth: float = 0.0

    @property
    def bored(self) -> bool:
        return self.bore_dia > 0.0


@dataclass
class AdapterSpec:
    name: str
    od: float                      # outer diameter of the base ring
    id: float                      # inner diameter of the base ring
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

    # base ring + pad bosses, trimmed to the smoothstep top afterwards
    body = cq.Workplane("XY").circle(r_out).extrude(z_max)
    for p in spec.pads:
        body = body.union(cq.Workplane("XY").center(p.x, p.y)
                          .circle(p.pad_dia / 2.0).extrude(z_max))
    body = body.cut(cq.Workplane("XY").circle(r_in).extrude(z_max + 10))

    span = spec.width_span
    n = 360
    ys = [-span + 2.0 * span * i / n for i in range(n + 1)]
    prof = [(y, spec.z_of_y(y)) for y in ys]
    prof += [(ys[-1], z_max + 20.0), (ys[0], z_max + 20.0)]
    body = body.cut(cq.Workplane("YZ").polyline(prof).close()
                    .extrude(r_out + 60, both=True))

    # blind counterbores, depth measured from the local top surface
    for p in spec.pads:
        if p.bored:
            bottom = spec.z_of_y(p.y) - p.bore_depth
            body = body.cut(cq.Workplane("XY").center(p.x, p.y)
                            .circle(p.bore_dia / 2.0)
                            .extrude(z_max + 20 - bottom, taper=0)
                            .translate((0, 0, bottom)))
    return body


def spec_part1() -> AdapterSpec:
    """TALL ring (left): OD135 / ID112.5, height 39 -> 34, width 145.

    H1..H3 use the raw STL hole centres (no rotation).
    """
    return AdapterSpec(
        name="part1_tall_135",
        od=135.0, id=112.5,
        z_hi=39.0, z_lo=34.0, y_min=-72.5, y_max=67.5,
        pads=(
            Pad("H1", -63.27430, -0.26276, 18.45, 10.16, 2.5),
            Pad("H2", 63.27444, 0.26286, 18.45, 10.16, 2.5),
            Pad("H3", 0.26274, -63.27459, 18.45, 10.16, 2.5),
            Pad("S1", -56.0, 31.0, 11.0),
            Pad("S2", 56.0, -30.0, 11.0),
            Pad("S3", -30.0, -55.0, 11.0),
        ),
    )


def spec_part2() -> AdapterSpec:
    """THIN ring (right): OD163 / ID140, height 9 -> 6, width 171."""
    return AdapterSpec(
        name="part2_thin_163",
        od=163.0, id=140.0,
        z_hi=9.0, z_lo=6.0, y_min=-85.5, y_max=81.5,
        pads=(
            Pad("H1", -73.5, 18.5, 19.0, 10.16, 2.5),
            Pad("H2", 65.5, 37.5, 19.0, 10.16, 2.5),
            Pad("H3", -37.75, -65.4, 19.0, 10.16, 2.5),
            Pad("S1", -80.0, 0.0, 11.0),
            Pad("S2", 80.0, 0.0, 11.0),
            Pad("S3", 0.0, -80.0, 11.0),
        ),
    )


def make_part1() -> cq.Workplane:
    return build(spec_part1())


def make_part2() -> cq.Workplane:
    return build(spec_part2())
