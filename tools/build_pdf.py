"""Builds pack/palette-pack.pdf: FARBY, 12 palettes in the Jergusino brand
(1080 x 1350, Ink / Cream / Yellow, Slithen + Edwardian + Borisna). Edit PALETTES and re-run."""
import re
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from fontTools.ttLib import TTFont as FT
from fontTools.pens.boundsPen import BoundsPen

import os
import tempfile

# Run from anywhere: python3 tools/build_pdf.py   (needs reportlab and fonttools)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "tools") + "/"
OUT = os.path.join(ROOT, "pack", "palette-pack.pdf")

# The site's .woff fonts (already patched with Slovak letters) -> temporary .ttf for reportlab
FD = tempfile.mkdtemp() + "/"
for _n in ("Slithen", "Borisna", "Edwardian"):
    _f = FT(os.path.join(ROOT, "assets", "fonts", _n + ".woff"))
    _f.flavor = None
    _f.save(FD + _n + ".ttf")

INK, CREAM, YEL = "#060909", "#FAF1D6", "#FFC600"

W, H = 1080, 1350
F = 43
T = 68
SMALL = 68
G = 17
LINE = 1.3

FILES = {"SL": "Slithen.ttf", "BO": "Borisna.ttf", "ED": "Edwardian.ttf"}
for k, f in FILES.items():
    pdfmetrics.registerFont(TTFont(k, FD + f))

_ft = {k: FT(FD + f) for k, f in FILES.items()}
_gs = {k: v.getGlyphSet() for k, v in _ft.items()}
_cm = {k: v.getBestCmap() for k, v in _ft.items()}
_upem = {k: v["head"].unitsPerEm for k, v in _ft.items()}


def gb(font, ch):
    name = _cm[font].get(ord(ch))
    if not name:
        return None
    bp = BoundsPen(_gs[font])
    _gs[font][name].draw(bp)
    return bp.bounds


def ymax(font, text, size):
    v = [gb(font, ch)[3] for ch in text if ch != " " and gb(font, ch)]
    return max(v) / _upem[font] * size if v else 0


def ymin(font, text, size):
    v = [gb(font, ch)[1] for ch in text if ch != " " and gb(font, ch)]
    return min(v) / _upem[font] * size if v else 0


def tw(text, font, size):
    return pdfmetrics.stringWidth(text, font, size)


def missing(text, font):
    return [ch for ch in text if ord(ch) not in _cm[font] and ch != " "]


SL_CAP = ymax("SL", "H", 1000) / 1000
ED_CAP = ymax("ED", "x", 1000) / 1000

c = canvas.Canvas(OUT, pagesize=(W, H))
c.setTitle("FARBY: 12 paliet, ktoré spolu fungujú")
c.setAuthor("Jergusino")
c.setSubject("Balík farebných paliet")


def rect(x, y_top, w, h, col):
    c.setFillColor(HexColor(col))
    c.rect(x, H - y_top - h, w, h, stroke=0, fill=1)


def text(x, base, s, font, size, col):
    bad = missing(s, font)
    assert not bad, (s, font, bad)
    c.setFillColor(HexColor(col))
    c.setFont(font, size)
    c.drawString(x, H - base, s)


def text_at(x, base, s, size=SMALL):
    for part in re.split(r"(@)", s):
        if not part:
            continue
        text(x, base, part, "BO", size, YEL if part == "@" else CREAM)
        x += tw(part, "BO", size)


def wrap(s, font, size, width):
    lines, cur = [], ""
    for w_ in s.split():
        t = (cur + " " + w_).strip()
        if tw(t, font, size) > width and cur:
            lines.append(cur)
            cur = w_
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def group_top_left(lines, width=960):
    y = F + 0.7 * SMALL
    for ln in lines:
        for sub in wrap(ln, "BO", SMALL, width):
            text_at(F, y, sub)
            y += SMALL * LINE
    return y


def page_ink():
    rect(0, 0, W, H, INK)


def headline(txt, size, script=None):
    base = H - F
    text(F, base, txt, "SL", size, CREAM)
    top = base - ymax("SL", txt, size)
    if script:
        cap = SL_CAP * size
        s_size = 0.27 * cap / ED_CAP
        s_base = top - G + ymin("ED", script, s_size)
        text(F, s_base, script, "ED", s_size, YEL)
        assert tw(script, "ED", s_size) < W - 2 * F, "script too wide"
    return top


def fit(txt, lo, hi):
    em = tw(txt, "SL", 1000) / 1000
    return max(lo, min(hi, (W - 2 * F) / em))


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(h):
    def f(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h)
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


PALETTES = [
    ("Sunset Pop", "teplá a energická. na plagáty a social.",
     [("oranž", "#FF6B35"), ("broskyňa", "#F7C59F"), ("krém", "#EFEFD0"), ("modrá", "#1A659E"), ("námornícka", "#004E89")]),
    ("Pastelový sen", "jemná a mäkká. na lifestyle, wellness a značky.",
     [("ružová", "#FFD6E0"), ("vanilka", "#FFEFCF"), ("ľadová", "#D4F0F0"), ("mätová", "#B8E0D2"), ("levanduľa", "#C5CAE9")]),
    ("Polnoc", "hlboká a pokojná. na tech a tmavé témy.",
     [("noc", "#0B132B"), ("atrament", "#1C2541"), ("tyrkys", "#5BC0BE"), ("jantár", "#E8A33D"), ("hmla", "#F5F0E6")]),
    ("Nočný klub", "tmavá a drzá, no stále čitateľná. na eventy, hudbu a plagáty.",
     [("noc", "#1B1A2E"), ("sliva", "#3D2C5E"), ("malina", "#D6456B"), ("jantár", "#F29E4C"), ("krém", "#F4E9D8")]),
    ("Zem a hlina", "prirodzená a teplá. na remeslo, kaviarne a handmade.",
     [("kakao", "#3D2C1E"), ("hrdza", "#8C5A3C"), ("piesok", "#C69C6D"), ("ovsená", "#E8D9B5"), ("šalvia", "#5F6F52")]),
    ("Minimal", "kľudná neutrálna báza a dva akcenty. na čistý dizajn.",
     [("uhlie", "#141414"), ("kameň", "#D8D2C4"), ("hmla", "#F3EFE6"), ("smaragd", "#2F5D50"), ("akcent", "#D9582B")]),
    ("Les", "zeleň a hlina. na eko, outdoor a zdravie.",
     [("smrek", "#1F3D2B"), ("machy", "#4F7A4A"), ("lúka", "#A9B97A"), ("hrdza", "#C97B4A"), ("ovsená", "#F1E8D2")]),
    ("Oceán", "modrá s pieskom a korálom. na travel, vodu a leto.",
     [("hlbina", "#0B3C5D"), ("vlna", "#328CC1"), ("príboj", "#9AD1D4"), ("piesok", "#F2E3C3"), ("koral", "#F26B4F")]),
    ("Retro 70s", "teplý vintage vibe. na plagáty a obaly.",
     [("paprika", "#E4572E"), ("horčica", "#F3A712"), ("olivová", "#A8C686"), ("nebo", "#669BBC"), ("indigo", "#29335C")]),
    ("Signal", "žltá a takmer čierna. silný kontrast, vždy čitateľné.",
     [("čierna", "#060909"), ("uhlie", "#2A2A22"), ("signal", "#FFC600"), ("maslo", "#FFE27A"), ("papier", "#F7F3E3")]),
    ("Višňa a krém", "elegantná a prémiová. na módu, gastro a svadby.",
     [("víno", "#3B0A1E"), ("bordó", "#7A1F3D"), ("višňa", "#C9485B"), ("broskyňa", "#F2C6B4"), ("krém", "#FBF1E6")]),
    ("Letný mix", "hravá, ale nosná. na mladú značku, merch a reels.",
     [("koral", "#F25F5C"), ("citrón", "#FFE066"), ("mäta", "#70C1B3"), ("modrá", "#247BA0"), ("kameň", "#50514F")]),
]

if __name__ == "__main__" and "--json" in sys.argv:
    import json
    print(json.dumps([{"name": n, "desc": d, "colors": [{"name": a, "hex": h} for a, h in cs]} for n, d, cs in PALETTES], ensure_ascii=False))
    sys.exit()

# 1 · Cover
page_ink()
headline("FARBY", fit("FARBY", 2 * T, 700), script="balík")
group_top_left(["12 paliet, ktoré spolu fungujú.", "každá má 5 farieb a ich kódy.", "@jergusino"])
c.showPage()

# 2 · How to
page_ink()
group_top_left(["1  vyber paletu", "2  skopíruj hex kód", "3  hoď ju do projektu", "a drž 60 / 30 / 10."])
spec = [("#004E89", 0.6, "60 %"), ("#F7C59F", 0.3, "30 %"), ("#FF6B35", 0.1, "10 %")]
x = F
bw = W - 2 * F
y0, h0 = 560, 190
for col, share, lab in spec:
    w_ = bw * share
    rect(x, y0, w_, h0, col)
    text_at(x, y0 + h0 + 22 + 0.7 * SMALL, lab)
    x += w_
headline("3 KROKY", fit("3 KROKY", 2 * T, 460), script="ako na to")
c.showPage()

# 3..14 · Palettes
for idx, (name, desc, cols) in enumerate(PALETTES):
    page_ink()
    hexes = [h for _, h in cols]
    pool = hexes + [INK]
    ratio, bi, bj = max((contrast(hexes[i], pool[j]), i, j) for i in range(5) for j in range(len(pool)) if pool[j] != hexes[i])
    group_top_left([desc, f"pár: {pool[bj]} na {hexes[bi]}"])

    sw_w, sw_h, gap = 300, 136, 12
    y = 322
    tx = F + sw_w + 28
    for nm, hx in cols:
        rect(F, y, sw_w, sw_h, hx)
        if contrast(hx, INK) < 1.25:
            c.setStrokeColor(HexColor(CREAM))
            c.setLineWidth(2)
            c.rect(F + 1, H - y - sw_h + 1, sw_w - 2, sw_h - 2, stroke=1, fill=0)
        r_, g_, b_ = rgb(hx)
        l1 = f"{nm}  {hx.upper()}"
        assert tw(l1, "BO", SMALL) < W - F - tx, l1
        text_at(tx, y + 50, l1)
        text_at(tx, y + 122, f"rgb {r_} {g_} {b_}")
        y += sw_h + gap

    headline(name.upper(), 2 * T, script=f"paleta {idx + 1:02d}")
    c.showPage()

# 15 · End
page_ink()
group_top_left(["ak ti palety pomohli,", "pošli ich ďalej.", "mail@jergusino.com", "@jergusino"])
sc = (W - 2 * F) / 1033.0
iw, ih = 1038 * sc, 358 * sc
c.drawImage(BASE + "lockup.png", F - 2 * sc, F - 3 * sc, width=iw, height=ih, mask=None)
c.showPage()
c.save()
print("saved", OUT)
