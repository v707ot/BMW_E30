"""One combined sheet: both adapters side by side with their key dimensions."""

from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(os.path.dirname(HERE), "renders")

INK, DIM, GREY, RULE = (18, 18, 18), (11, 87, 164), (108, 114, 122), (222, 226, 232)


def _font(s, b=False):
    p = f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if b else ''}.ttf"
    return ImageFont.truetype(p, s) if os.path.exists(p) else ImageFont.load_default()


def _fit(im, bw, bh):
    im = im.convert("RGB")
    s = min(bw / im.width, bh / im.height)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


def main():
    W, H = 2400, 1500
    p = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(p)

    d.text((80, 55), "Проставки под «китайские» фары — BMW E30",
           font=_font(58, True), fill=INK)
    d.text((82, 135), "Две детали, 3D-модели построены строго по размерам эскиза  •  все размеры в мм",
           font=_font(29), fill=GREY)
    d.line((80, 192, W - 80, 192), fill=RULE, width=3)

    cols = [
        ("part1", "Деталь №1 — большой фланец", [
            "габарит X × Y — 171 × 167",
            "кольцо ⌀ — 163 / 140",
            "ширина кольца — 11,5",
            "высота — 9 → 6 (плавно)",
        ]),
        ("part2", "Деталь №2 — малый фланец", [
            "габарит X × Y — 145 × 140",
            "кольцо ⌀ — 135 / 112,5",
            "ширина кольца — 11,25",
            "высота — 39 → 34 (плавно)",
        ]),
    ]

    for i, (slug, title, lines) in enumerate(cols):
        x0 = 80 + i * 1180
        d.text((x0, 225), title, font=_font(40, True), fill=DIM)

        d.rounded_rectangle((x0, 290, x0 + 1080, 900), 14,
                            fill=(250, 251, 253), outline=RULE, width=2)
        iso = _fit(Image.open(os.path.join(R, f"{slug}_iso.png")), 1000, 560)
        p.paste(iso, (x0 + (1080 - iso.width) // 2, 290 + (610 - iso.height) // 2))
        d.text((x0 + 20, 845), "3D-модель", font=_font(28), fill=GREY)

        d.rounded_rectangle((x0, 930, x0 + 1080, 1420), 14,
                            fill=(250, 251, 253), outline=RULE, width=2)
        drw = _fit(Image.open(os.path.join(R, f"{slug}_drawing.png")), 1040, 430)
        p.paste(drw, (x0 + (1080 - drw.width) // 2, 940))

        y = 1390
        for j, ln in enumerate(lines):
            d.text((x0 + 20 + (j % 2) * 540, y + (j // 2) * 0), "• " + ln,
                   font=_font(26), fill=INK)

    out = os.path.join(R, "overview.png")
    p.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
