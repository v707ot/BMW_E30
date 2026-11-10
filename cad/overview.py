"""One combined sheet: both adapters side by side with their key elements."""

from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapter  # noqa: E402

R = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "renders")
INK, DIM, GREY, RULE = (18, 18, 18), (11, 87, 164), (108, 114, 122), (222, 226, 232)


def _font(s, b=False):
    p = f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if b else ''}.ttf"
    return ImageFont.truetype(p, s) if os.path.exists(p) else ImageFont.load_default()


def _fit(im, bw, bh):
    im = im.convert("RGB")
    s = min(bw / im.width, bh / im.height)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


def main():
    W, H = 2400, 1560
    p = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(p)
    d.text((80, 52), "Проставки под «китайские» фары — BMW E30",
           font=_font(56, True), fill=INK)
    d.text((82, 130), "Две детали, построены по заданной системе координат   •   все размеры в мм",
           font=_font(28), fill=GREY)
    d.line((80, 186, W - 80, 186), fill=RULE, width=3)

    cols = [("part1", adapter.spec_part1(), "Деталь №1 — Ø163 / Ø140"),
            ("part2", adapter.spec_part2(), "Деталь №2 — Ø145")]
    for i, (slug, spec, title) in enumerate(cols):
        x0 = 80 + i * 1180
        d.text((x0, 214), title, font=_font(38, True), fill=DIM)
        d.rounded_rectangle((x0, 274, x0 + 1080, 830), 14,
                            fill=(250, 251, 253), outline=RULE, width=2)
        iso = _fit(Image.open(os.path.join(R, f"{slug}_iso.png")), 1000, 520)
        p.paste(iso, (x0 + (1080 - iso.width) // 2, 274 + (556 - iso.height) // 2))
        d.rounded_rectangle((x0, 860, x0 + 1080, 1480), 14,
                            fill=(250, 251, 253), outline=RULE, width=2)
        drw = _fit(Image.open(os.path.join(R, f"{slug}_drawing.png")), 1040, 420)
        p.paste(drw, (x0 + (1080 - drw.width) // 2, 880))
        y = 1330
        d.text((x0 + 22, y), f"Ø{spec.od:g} / Ø{spec.id:g}   •   "
               f"высота {spec.z_hi:g} → {spec.z_lo:g}", font=_font(26, True), fill=INK)
        y += 44
        for e in spec.mounts:
            d.text((x0 + 22, y), f"посадка {e.label} ({e.x:g}; {e.y:g}) "
                   f"Ø{e.pad_dia:g}/отв. Ø{e.hole_dia:g}", font=_font(23), fill=(26, 122, 60))
            y += 38
        for e in spec.contour:
            d.text((x0 + 22, y), f"контур {e.label} ({e.x:g}; {e.y:g}) "
                   f"Ø{e.pad_dia:g}", font=_font(23), fill=INK)
            y += 38

    out = os.path.join(R, "overview.png")
    p.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
