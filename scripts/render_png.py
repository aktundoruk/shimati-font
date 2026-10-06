"""Karşılaştırma PNG'si: her varyant, Regular ve ExtraBold, birkaç örnek satır."""
import sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from hbrender import HBFont  # noqa: E402  (kerning dahil gerçek dizgi)
V = [("orijinal", "Sen orijinal"), ("dogrudan", "Doğrudan"), ("uyarlanmis", "Uyarlanmış")]
texts = sys.argv[1:] or ["hamburgefonstiv aeae", "nanene ooaa ağaç gece"]
size, W = 110, 2200
rows = [(v, lab, w, t) for t in texts for w in (400, 800) for v, lab in V]
H = 40 + len(rows) * int(size * 1.35) + len(texts) * 2 * 30
img = Image.new("L", (W, H), 255); d = ImageDraw.Draw(img)
lab_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 26)
y = 20
for i, (v, lab, w, t) in enumerate(rows):
    if i % 3 == 0 and i: y += 30; d.line([(0, y - 12), (W, y - 12)], fill=220, width=2)
    d.text((20, y + size * 0.55), f"{lab} {w}", font=lab_font, fill=150)
    HBFont(f"build/Sen-{v}-VF.ttf", w).draw(img, t, 330, y + size * 0.95, size)
    y += int(size * 1.35)
img.save("proof/karsilastirma.png"); print(img.size)
