"""UFO glif konturlarını düğüm noktalarıyla PNG'ye çizer: outline_png.py out.png ufo:glyph [ufo:glyph ...]"""
import sys
import ufoLib2
from PIL import Image, ImageDraw
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from geom import contours_of  # noqa: E402

S = 0.9
items = [a.rsplit(":", 1) for a in sys.argv[2:]]
W = sum(int(ufoLib2.Font.open(u)[g].width * S) + 60 for u, g in items) + 60
img = Image.new("RGB", (W, int(1000 * S)), "white")
d = ImageDraw.Draw(img)
X = 60
base = int(780 * S)
for u, gname in items:
    f = ufoLib2.Font.open(u)
    g = f[gname]
    for y in (0, f.info.xHeight):
        d.line([(X - 30, base - y * S), (X + g.width * S + 30, base - y * S)], fill=(210, 210, 210), width=2)
    for poly in contours_of(g):
        d.line([(X + x * S, base - y * S) for x, y in poly + poly[:1]], fill="black", width=3)
    for c in g.contours:
        for i, p in enumerate(c.points):
            r = 6 if p.type else 4
            col = (220, 70, 30) if p.type else (60, 110, 220)
            d.ellipse([X + p.x * S - r, base - p.y * S - r, X + p.x * S + r, base - p.y * S + r], outline=col, width=2)
    X += int(g.width * S) + 60
img.save(sys.argv[1])
