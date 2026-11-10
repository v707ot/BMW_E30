"""BMW E30 headlight adapter rings ("China" headlight spacers).

Single coordinate system (millimetres):

* ring centre  O = (0; 0; 0);
* X - horizontal, Y - vertical, Z - height; top view uses X-Y;
* every marked element is a circular boss positioned by its centre
  coordinates.  Elements listed as mounting seats carry a through hole;
  elements on the outer contour carry no hole (``hole_dia = 0``);
* the top surface height varies smoothly along Y following the cubic
  smoothstep  Z = Zmax - (Zmax - Zmin)(3t^2 - 2t^3),
  t = (Y - Ymin) / (Ymax - Ymin).

Part 1 - ring OD 163 / ID 140, height 9 -> 6
Part 2 - ring OD 145 / ID 112.5, height 39 -> 34
"""

from __future__ import annotations

from dataclasses import dataclass, field

import cadquery as cq


@dataclass(frozen=True)
class Element:
    """A marked element: boss of ``pad_dia`` at (x, y), optional hole."""
    label: str
    x: float
    y: float
    pad_dia: float
    hole_dia: float = 0.0

    @property
    def mounting(self) -> bool:
        return self.hole_dia > 0.0


@dataclass
class AdapterSpec:
    name: str
    od: float                      # outer diameter of the ring
    id: float                      # inner diameter of the ring
    z_hi: float                    # height at Ymin
    z_lo: float                    # height at Ymax
    y_min: float                   # smoothstep lower bound
    y_max: float                   # smoothstep upper bound
    mounts: tuple = ()             # Elements with holes
    contour: tuple = ()            # Elements on the outer contour

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
    def elements(self) -> tuple:
        return tuple(self.mounts) + tuple(self.contour)

    @property
    def width_span(self) -> float:
        """Half-extent of the whole outline (ring plus bosses), in X/Y."""
        span = self.outer_r
        for e in self.elements:
            span = max(span, abs(e.x) + e.pad_dia / 2.0,
                       abs(e.y) + e.pad_dia / 2.0)
        return span

    def z_of_y(self, y: float) -> float:
        """Top-surface height at ``y`` (cubic smoothstep, clamped)."""
        t = (y - self.y_min) / (self.y_max - self.y_min)
        t = min(1.0, max(0.0, t))
        return self.z_hi - (self.z_hi - self.z_lo) * (3.0 * t * t - 2.0 * t * t * t)


def _boss(e: Element, height: float) -> cq.Workplane:
    return (cq.Workplane("XY").center(e.x, e.y)
            .circle(e.pad_dia / 2.0).extrude(height))


def build(spec: AdapterSpec) -> cq.Workplane:
    """Return the finished adapter as a CadQuery solid."""
    r_out, r_in, z_max = spec.outer_r, spec.inner_r, spec.z_max

    # outline: ring disc plus every element boss
    body = cq.Workplane("XY").circle(r_out).extrude(z_max)
    for e in spec.elements:
        body = body.union(_boss(e, z_max))
    body = body.cut(cq.Workplane("XY").circle(r_in).extrude(z_max + 10))

    # smoothstep top face, cut away everything above the curve
    span = max(abs(spec.y_min), abs(spec.y_max))
    for e in spec.elements:
        span = max(span, abs(e.y) + e.pad_dia)
    n = 320
    ys = [-span + 2.0 * span * i / n for i in range(n + 1)]
    prof = [(y, spec.z_of_y(y)) for y in ys]
    prof += [(ys[-1], z_max + 20.0), (ys[0], z_max + 20.0)]
    cutter = (cq.Workplane("YZ").polyline(prof).close()
              .extrude(r_out + 60, both=True))
    body = body.cut(cutter)

    # through holes (mounting seats only)
    for e in spec.mounts:
        if e.hole_dia > 0:
            body = body.cut(cq.Workplane("XY").center(e.x, e.y)
                            .circle(e.hole_dia / 2.0).extrude(z_max + 10))
    return body


def spec_part1() -> AdapterSpec:
    """Ring OD 163 / ID 140; mounts A, B, C; outer contour D, E, F."""
    return AdapterSpec(
        name="part1_ring_163",
        od=163.0, id=140.0,
        z_hi=9.0, z_lo=6.0, y_min=-81.5, y_max=81.5,
        mounts=(
            Element("A", -71.0, 17.0, 15.0, 6.0),
            Element("B",  65.0, 35.0, 15.0, 6.0),
            Element("C", -38.0, -63.0, 15.0, 6.0),
        ),
        contour=(
            Element("D", -86.0, 2.0, 15.0),
            Element("E",  81.0, 3.0, 15.0),
            Element("F",   1.0, -80.0, 15.0),
        ),
    )


def spec_part2() -> AdapterSpec:
    """Ring OD 145 / ID 112.5; mounts A, D, E; outer contour B, C, F."""
    return AdapterSpec(
        name="part2_ring_145",
        od=145.0, id=112.5,
        z_hi=39.0, z_lo=34.0, y_min=-80.0, y_max=80.0,
        mounts=(
            Element("A", -61.0, 31.0, 16.0, 6.0),
            Element("D",  66.0, -26.0, 16.0, 6.0),
            Element("E", -19.0, -68.0, 16.0, 6.0),
        ),
        contour=(
            Element("B", -78.0, -6.0, 16.0),
            Element("C",  75.0, -5.0, 16.0),
            Element("F",   0.0, -76.0, 16.0),
        ),
    )


def spec_part1_stl() -> AdapterSpec:
    """Part 1 variant using the hole pattern measured on the loaded STL.

    Central bore D73.181, three holes D10.1588 on radius 63.275
    (PCD 126.549) at the measured angles.
    """
    import math
    r_pcd, d_hole = 63.275, 10.1588
    angles = {  # from the STL hole centres
        "A": math.degrees(math.atan2(-0.2628, -63.2743)),
        "B": math.degrees(math.atan2(0.2629, 63.2744)),
        "C": math.degrees(math.atan2(-63.2746, 0.2627)),
    }
    mounts = tuple(
        Element(f"H{k}", r_pcd * math.cos(math.radians(a)),
                r_pcd * math.sin(math.radians(a)), 22.0, d_hole)
        for k, a in angles.items())
    return AdapterSpec(
        name="part1_stl_pattern",
        od=163.0, id=73.181,
        z_hi=9.0, z_lo=6.0, y_min=-81.5, y_max=81.5,
        mounts=mounts, contour=(),
    )


def make_part1() -> cq.Workplane:
    return build(spec_part1())


def make_part2() -> cq.Workplane:
    return build(spec_part2())
