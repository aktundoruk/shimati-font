"""Kerning denetimi: son fonttaki tüm harf çiftlerini Sen'in orijinaliyle karşılaştırır.

Her çift için x-height bölgesindeki optik boşluk (kerning dahil) ve en dar boşluk ölçülür.
Raporlar: değen/çok yaklaşan çiftler (en dar boşluk < 0.04 em) ve optik boşluğu Sen'dekine göre
çiftin iki harfinin tipik boşluğuna oranla en çok değişen çiftler. Ölçüler daraltma öncesi (UFO
kaynağı yeniden ölçeklendiği için) yerine son UFO üzerinden, Sen'in değerleri daraltma oranıyla.
"""
import json
import sys
from pathlib import Path

import ufoLib2

sys.path.insert(0, str(Path(__file__).parent))
import kerning  # noqa: E402
from kerning import optical_gap, raw_min_gap  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LETTERS = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") + \
    ["ccedilla", "gbreve", "idotless", "odieresis", "scedilla", "udieresis",
     "Ccedilla", "Gbreve", "Idotaccent", "Odieresis", "Scedilla", "Udieresis"]


def audit(master):
    new = ufoLib2.Font.open(ROOT / f"variants/uyarlanmis/Sen-{master}.ufo")
    old = ufoLib2.Font.open(ROOT / f"sources/Sen-{master}.ufo")
    scale = json.loads((ROOT / "build/olcumler.json").read_text())["uyarlanmis"]["condense"][master]["scale_x"]
    em = 1024
    cn, co = {}, {}
    touching, changed = [], []
    for a in LETTERS:
        for b in LETTERS:
            kn = new.kerning.get((a, b), 0)
            ko = old.kerning.get((a, b), 0)
            gn = raw_min_gap(new, a, b, kn)
            if gn is None:
                continue
            if gn < 0.04 * em:
                go = raw_min_gap(old, a, b, ko) * scale
                if go - gn > 10:  # Sen'de böyle değildi
                    touching.append((a, b, kn, round(gn), round(go)))
            on = optical_gap(new, a, b, kn, cn)
            oo = optical_gap(old, a, b, ko, co)
            if on is None or oo is None:
                continue
            changed.append((round(on - oo * scale), a, b, kn, ko))
    kerning._PROFILE_CACHE.clear()
    changed.sort()
    return touching, changed[:12], changed[-12:]


if __name__ == "__main__":
    for m in ("Regular", "ExtraBold"):
        t, tight, loose = audit(m)
        print(f"== {m}\nDeğen/çok yakın (yeni):", t)
        print("En çok sıkışan (fark, sol, sağ, yeni k, eski k):", tight)
        print("En çok açılan:", loose)
