"""Yeni a/e/æ şekillerinde eski görsel mesafeyi koruyacak kerning ayarı.

Her çift için x-height bölgesinde 10 birimlik yatay taramayla harfler arası boşluk ölçülür;
her satırın boşluğu en dar satırın en fazla `depth` ötesine kırpılıp ortalaması alınır
(tek bir uç noktanın değil, gözün gördüğü boşluğun ölçüsü). Mevcut çiftin değeri, yeni ölçü
eskisine eşit olacak şekilde değiştirilir. Kerning'i olmayan çiftlere yalnızca fark eşiği
aşıyorsa yeni çift eklenir.
"""

import sys
from pathlib import Path

from fontTools.pens.recordingPen import DecomposingRecordingPen

sys.path.insert(0, str(Path(__file__).parent))
from geom import contours_of, runs_at_y  # noqa: E402


class _G:
    def __init__(self, font, name):
        self.font, self.name = font, name

    def draw(self, pen):
        rec = DecomposingRecordingPen(self.font)
        self.font[self.name].draw(rec)
        rec.replay(pen)


def profiles(font, name, step=10):
    """{y: (sol x, sağ x)} — glifin her tarama yüksekliğindeki mürekkep sınırları."""
    key = (id(font), name)
    if key in _PROFILE_CACHE:
        return _PROFILE_CACHE[key]
    _PROFILE_CACHE[key] = out = _profiles(font, name, step)
    return out


_PROFILE_CACHE = {}


def _profiles(font, name, step):
    polys = contours_of(_G(font, name))
    if not polys:
        return {}
    ys = [p[1] for poly in polys for p in poly]
    out = {}
    for y in range(int(min(ys)) // step * step, int(max(ys)) + step, step):
        runs = runs_at_y(polys, y + 0.5)
        if runs:
            out[y] = (runs[0][0], runs[-1][1])
    return out


def optical_gap(font, left, right, kern, cache, depth_ratio=0.15, zone=None):
    pl = cache.setdefault(left, profiles(font, left))
    pr = cache.setdefault(right, profiles(font, right))
    xh = font.info.xHeight
    lo, hi = zone or (0, xh)
    adv = font[left].width + kern
    gaps = [adv + pr[y][0] - pl[y][1] for y in pl.keys() & pr.keys() if lo <= y <= hi]
    if not gaps:
        return None
    floor = min(gaps)
    depth = depth_ratio * xh
    return sum(min(g, floor + depth) for g in gaps) / len(gaps)


def raw_min_gap(font, left, right, kern):
    pl, pr = profiles(font, left), profiles(font, right)
    adv = font[left].width + kern
    gaps = [adv + pr[y][0] - pl[y][1] for y in pl.keys() & pr.keys()]
    return min(gaps) if gaps else None


def adjust(old_font, new_font, glyphs=("a", "e", "ae"), add_threshold=30, round_to=5):
    """Yeni fontun kerning'ini günceller; değişiklik listesini döndürür."""
    partners = [
        n for n in new_font.keys()
        if new_font[n].unicodes and len(n) <= 2 and n.isalpha() and n not in glyphs
    ]
    old_cache, new_cache = {}, {}
    changes = []
    for g in glyphs:
        for left, right in [(p, g) for p in partners] + [(g, p) for p in partners]:
            k_old = old_font.kerning.get((left, right), 0)
            g_old = optical_gap(old_font, left, right, k_old, old_cache)
            g_new = optical_gap(new_font, left, right, k_old, new_cache)
            if g_old is None or g_new is None:
                continue
            floor_old = raw_min_gap(old_font, left, right, k_old)
            limit = 0.6 * floor_old  # en dar boşluk eskisinin %60'ından aza inmesin
            k_optical = round((k_old + g_old - g_new) / round_to) * round_to
            if k_optical < k_old:
                # sıkıştırma: optik ölçüye göre, çarpışma sınırına kadar
                k_new = k_optical
                while k_new < k_old and raw_min_gap(new_font, left, right, k_new) < limit:
                    k_new += round_to
            else:
                # gevşetme yalnızca gerçek çarpışmada ve onu giderecek kadar
                k_new = k_old
                while raw_min_gap(new_font, left, right, k_new) < limit:
                    k_new += round_to
            exists = (left, right) in old_font.kerning
            if k_new == k_old:
                continue
            if not exists and abs(k_new) < add_threshold:
                continue
            new_font.kerning[(left, right)] = k_new
            changes.append({"pair": f"{left} {right}", "old": k_old, "new": k_new, "existed": exists})
    return changes



def inter_pairs(font, glyph, char, tx, sx, analog, inter_dir, round_to=5):
    """Inter'den alınan bir glifin kerning'i: Inter'in kendi çiftleri (HarfBuzz ile ölçülür),
    Regular–Black arasında glifin x ağırlığına (tx) interpole edilip yatay ölçekle (sx) küçültülür.

    Sen'in şekillerine karşı çarpışma kontrolü: en dar boşluk, `analog` harfle kurulan çiftin en dar
    boşluğunun %60'ından aza inerse gevşetilir.
    """
    import uharfbuzz as hb

    def table(weight):
        data = (inter_dir / f"Inter-{weight}.otf").read_bytes()
        hfont = hb.Font(hb.Face(data))

        def adv(text, kern):
            buf = hb.Buffer()
            buf.add_str(text)
            buf.guess_segment_properties()
            hb.shape(hfont, buf, {"kern": kern, "calt": False, "liga": False})
            return buf.glyph_positions[0].x_advance

        out = {}
        for name in font.keys():
            g = font[name]
            if not g.unicodes or len(name) > 2 or not name.isalpha() or name == glyph:
                continue
            p = chr(g.unicodes[0])
            for a, b, key in ((p, char, (name, glyph)), (char, p, (glyph, name))):
                k = adv(a + b, True) - adv(a + b, False)
                if k:
                    out[key] = k
        return out

    reg, black = table("Regular"), table("Black")
    changes = []
    for pair in sorted(set(reg) | set(black)):
        v = reg.get(pair, 0) + tx * (black.get(pair, 0) - reg.get(pair, 0))
        k = round(v * sx / round_to) * round_to
        left, right = pair
        aleft, aright = (analog if left == glyph else left), (analog if right == glyph else right)
        limit = 0.6 * raw_min_gap(font, aleft, aright, font.kerning.get((aleft, aright), 0))
        while raw_min_gap(font, left, right, k) < limit:
            k += round_to
        if not k:
            continue
        font.kerning[pair] = k
        changes.append({"pair": f"{left} {right}", "inter": round(v), "new": k})
    return changes
