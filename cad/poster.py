"""Build one presentation poster per part: 3D render + dimensioned drawing."""

from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapter  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
R = os.path.join(ROOT, "renders")

BG, INK, DIM, GREY, RULE = (255, 255, 255), (18, 18, 18), (11, 87, 164), \
    (108, 114, 122), (222, 226, 232)


def _font(size, bold=False):
    p = f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf"
    return ImageFont.truetype(p, size) if os.path.exists(p) \
        else ImageFont.load_default()


def _fit(im, bw, bh):
    im = im.convert("RGB")
    s = min(bw / im.width, bh / im.height)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


def _lines(spec):
    out = [
        f"кольцо Ø{spec.od:g} / Ø{spec.id:g}, ширина {spec.ring_wall:g}",
        f"высота: {spec.z_hi:g} → {spec.z_lo:g} мм (smoothstep)",
    ]
    for e in spec.mounts:
        out.append(f"посадка {e.label} ({e.x:g}; {e.y:g}) — "
                   f"площадка Ø{e.pad_dia:g}, отв. Ø{e.hole_dia:g}")
    for e in spec.contour:
        out.append(f"контур {e.label} ({e.x:g}; {e.y:g}) — "
                   f"площадка Ø{e.pad_dia:g}")
    return out


def build(slug, spec, title):
    W, H = 2200, 1560
    p = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(p)
    d.text((80, 52), title, font=_font(58, True), fill=INK)
    d.text((82, 130), "Проставки под «китайские» фары BMW E30   •   все размеры в мм",
           font=_font(29), fill=GREY)
    d.line((80, 186, W - 80, 186), fill=RULE, width=3)

    _panel(p, d, 60, 220, 1010, 700)
    iso = _fit(Image.open(os.path.join(R, f"{slug}_iso.png")), 950, 640)
    p.paste(iso, (60 + (1010 - iso.width) // 2, 220 + (700 - iso.height) // 2))
    d.text((80, 940), "3D-модель — изометрия", font=_font(32, True), fill=DIM)

    _panel(p, d, 1100, 220, 1040, 700)
    drw = _fit(Image.open(os.path.join(R, f"{slug}_drawing.png")), 1000, 650)
    p.paste(drw, (1100 + (1040 - drw.width) // 2, 220 + (700 - drw.height) // 2))
    d.text((1120, 940), "Чертёж с размерами", font=_font(32, True), fill=DIM)

    for i, (view, cap) in enumerate([("front", "вид спереди"), ("top", "вид сверху")]):
        bx = 60 + i * 515
        _panel(p, d, bx, 1010, 495, 350)
        im = _fit(Image.open(os.path.join(R, f"{slug}_{view}.png")), 455, 270)
        p.paste(im, (bx + (495 - im.width) // 2, 1010 + 28))
        d.text((bx + 20, 1290), cap, font=_font(24), fill=GREY)

    _panel(p, d, 1100, 1010, 1040, 470)
    d.text((1128, 1030), "Элементы и размеры", font=_font(30, True), fill=INK)
    y = 1090
    for ln in _lines(spec):
        d.text((1130, y), "•  " + ln, font=_font(25), fill=INK)
        y += 46

    out = os.path.join(R, f"{slug}_poster.png")
    p.save(out)
    print("wrote", out)


def _panel(p, d, x, y, w, h):
    d.rounded_rectangle((x, y, x + w, y + h), 14, fill=(250, 251, 253),
                        outline=RULE, width=2)


def main():
    build("part1", adapter.spec_part1(), "Деталь №1 — кольцо Ø163/Ø140")
    build("part2", adapter.spec_part2(), "Деталь №2 — кольцо Ø145")


if __name__ == "__main__":
    main()
