"""Build one presentation poster per part: 3D render + dimensioned drawing."""

from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
R = os.path.join(ROOT, "renders")

BG, INK, DIM, GREY, RULE = (255, 255, 255), (18, 18, 18), (11, 87, 164), \
    (108, 114, 122), (222, 226, 232)

PARTS = [
    ("part1", "Деталь №1 — большой фланец", [
        "габарит по X — 171 мм",
        "габарит по Y — 167 мм",
        "наружный ⌀ кольца — 163 мм",
        "внутренний ⌀ — 140 мм",
        "ширина кольцевой части — 11,5 мм",
        "высота с нижней стороны — 9 мм",
        "высота с противоположной — 6 мм",
        "макс. высота по Z — 9 мм",
    ]),
    ("part2", "Деталь №2 — малый фланец", [
        "габарит по X — 145 мм",
        "габарит по Y — 140 мм",
        "наружный ⌀ кольца — 135 мм",
        "внутренний ⌀ — 112,5 мм",
        "ширина кольцевой части — 11,25 мм",
        "высота с нижней стороны — 39 мм",
        "высота с противоположной — 34 мм",
        "макс. высота по Z — 39 мм",
    ]),
]


def _font(size: int, bold: bool = False):
    p = f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf"
    return ImageFont.truetype(p, size) if os.path.exists(p) \
        else ImageFont.load_default()


def _fit(im: Image.Image, bw: int, bh: int) -> Image.Image:
    im = im.convert("RGB")
    s = min(bw / im.width, bh / im.height)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


def _panel(im: Image.Image, x: int, y: int, w: int, h: int, d) -> None:
    d.rounded_rectangle((x, y, x + w, y + h), 14, fill=(250, 251, 253),
                        outline=RULE, width=2)


def build(slug: str, title: str, lines: list) -> str:
    W, H = 2200, 1500
    p = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(p)

    d.text((80, 58), title, font=_font(60, True), fill=INK)
    d.text((82, 138), "Проставки под «китайские» фары BMW E30   •   все размеры в мм",
           font=_font(30), fill=GREY)
    d.line((80, 196, W - 80, 196), fill=RULE, width=3)

    # left: 3D render
    _panel(p, 60, 232, 1010, 760, d)
    iso = _fit(Image.open(os.path.join(R, f"{slug}_iso.png")), 950, 700)
    p.paste(iso, (60 + (1010 - iso.width) // 2, 232 + (760 - iso.height) // 2))
    d.text((80, 1010), "3D-модель — изометрия", font=_font(34, True), fill=DIM)

    # left: front + top small renders
    for i, (view, cap) in enumerate([("front", "вид спереди"), ("top", "вид сверху")]):
        bx = 60 + i * 515
        _panel(p, bx, 1060, 495, 380, d)
        im = _fit(Image.open(os.path.join(R, f"{slug}_{view}.png")), 455, 300)
        p.paste(im, (bx + (495 - im.width) // 2, 1060 + 30))
        d.text((bx + 20, 1370), cap, font=_font(26), fill=GREY)

    # right: dimensioned drawing
    _panel(p, 1100, 232, 1040, 760, d)
    drw = _fit(Image.open(os.path.join(R, f"{slug}_drawing.png")), 1000, 710)
    p.paste(drw, (1100 + (1040 - drw.width) // 2, 232 + (760 - drw.height) // 2))
    d.text((1120, 1010), "Чертёж с размерами", font=_font(34, True), fill=DIM)

    # right: spec table
    _panel(p, 1100, 1060, 1040, 380, d)
    d.text((1130, 1085), "Размеры (по эскизу)", font=_font(30, True), fill=INK)
    col_x = (1130, 1620)
    for i, ln in enumerate(lines):
        cx = col_x[i // 4]
        cy = 1145 + (i % 4) * 62
        d.text((cx, cy), "•  " + ln, font=_font(27), fill=INK)

    out = os.path.join(R, f"{slug}_poster.png")
    p.save(out)
    print("wrote", out)
    return out


def main():
    for slug, title, lines in PARTS:
        build(slug, title, lines)


if __name__ == "__main__":
    main()
