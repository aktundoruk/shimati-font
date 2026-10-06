"""Shimati tanıtım sayfası: specimen/index.html (tek dosya, font sayfaya gömülü).

Önce scripts/release.py çalışmalı. Çizimler (yapı, eksen, glif inceleyici) kaynak masterların
konturlarından tarayıcıda çiziliyor; ağırlık kaydırıcısı iki master arasında nokta nokta interpole eder.
Sayfada kaynak fontların adı geçmez; telif ve lisans bilgisi paketteki OFL.txt'de ve font dosyalarında.
"""

import base64
import json
import unicodedata
from pathlib import Path

import ufoLib2
import uharfbuzz as hb
from fontTools.misc.transform import Transform
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "build" / "shimati-src"
DIST = ROOT / "dist"
OUT = ROOT / "specimen" / "index.html"
TEMPLATE = Path(__file__).resolve().parent / "specimen_template.html"

VERSION = "1.000"
WORD = "Shimati"
CARDS = ["n", "o", "a", "scedilla", "gbreve", "J"]


def contours(font, name, t=Transform()):
    g = font[name]
    out = []
    for c in g.contours:
        flat = []
        for p in c.points:
            x, y = t.transformPoint((p.x, p.y))
            code = {None: 0, "line": 1, "curve": 2, "move": 1, "qcurve": 3}[p.type] + (4 if p.smooth else 0)
            flat += [round(x), round(y), code]
        out.append(flat)
    for comp in g.components:
        out += contours(font, comp.baseGlyph, t.transform(comp.transformation))
    return out


def shape(vf_path, text, wght):
    blob = hb.Blob.from_file_path(str(vf_path))
    font = hb.Font(hb.Face(blob))
    font.set_variations({"wght": wght})
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    x, out = 0, []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        out.append([font.glyph_to_string(info.codepoint), x + pos.x_offset])
        x += pos.x_advance
    return out, x


def group_of(ch):
    cat = unicodedata.category(ch)
    if cat == "Lu":
        return "Büyük harfler"
    if cat == "Ll":
        return "Küçük harfler"
    if cat[0] == "N":
        return "Rakamlar"
    if cat[0] == "P":
        return "Noktalama"
    if cat[0] == "S":
        return "Simgeler"
    return None


def main():
    reg = ufoLib2.Font.open(SRC / "Shimati-Regular.ufo")
    xb = ufoLib2.Font.open(SRC / "Shimati-ExtraBold.ufo")
    vf = DIST / "Shimati" / "desktop" / "Shimati-Variable.ttf"
    woff2 = DIST / "Shimati" / "web" / "Shimati-Variable.woff2"
    tt = TTFont(vf)

    glyphs, chars = {}, []
    names = {g.name for g in reg if g.unicodes} | set(CARDS)
    word_r, wr = shape(vf, WORD, 400)
    word_b, wb = shape(vf, WORD, 800)
    names |= {n for n, _ in word_r}
    for n in sorted(names):
        g = reg[n]
        glyphs[n] = {"u": g.unicodes, "r": {"w": round(g.width), "c": contours(reg, n)},
                     "b": {"w": round(xb[n].width), "c": contours(xb, n)}}
        ra, rb = glyphs[n]["r"]["c"], glyphs[n]["b"]["c"]
        assert [len(c) for c in ra] == [len(c) for c in rb], f"{n}: masterlar uyumsuz"
    for n, d in glyphs.items():
        for u in d["u"]:
            ch = chr(u)
            grp = group_of(ch)
            if grp and not ch.isspace():
                chars.append([u, n, grp])
    chars.sort()

    data = {
        "upm": reg.info.unitsPerEm,
        "m": {"r": {"asc": reg.info.ascender, "cap": reg.info.capHeight, "xh": reg.info.xHeight,
                    "desc": reg.info.descender},
              "b": {"asc": xb.info.ascender, "cap": xb.info.capHeight, "xh": xb.info.xHeight,
                    "desc": xb.info.descender}},
        "word": {"r": word_r, "b": word_b, "wr": wr, "wb": wb},
        "cards": CARDS,
        "chars": chars,
        "g": glyphs,
        "count": {"glyphs": tt["maxp"].numGlyphs, "chars": len(tt.getBestCmap())},
    }
    font64 = base64.b64encode(woff2.read_bytes()).decode()
    html = TEMPLATE.read_text()
    for k, v in {"%%FONT%%": font64, "%%DATA%%": json.dumps(data, separators=(",", ":"), ensure_ascii=False),
                 "%%VERSION%%": VERSION, "%%GLYPHS%%": str(data["count"]["glyphs"]),
                 "%%CHARS%%": str(data["count"]["chars"])}.items():
        html = html.replace(k, v)
    for banned in ("Sen ", "Sen'", "Inter", "Philatype"):
        assert banned not in html.replace(font64, ""), f"sayfada '{banned}' geçiyor"
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html)
    print(f"{OUT.relative_to(ROOT)}  {OUT.stat().st_size // 1024} KB, {len(glyphs)} glif, {len(chars)} karakter")


if __name__ == "__main__":
    main()
