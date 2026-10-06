"""Gövde kalınlığını koruyarak daraltma ve genel aralık sıkıştırma (tracking).

Daraltma: her master için x koordinatları Regular ile ExtraBold arasında biraz daha kalın bir
ağırlıktan (t) alınır ve s ile ölçeklenir; y koordinatları değişmez. t ve s, dikey gövde (n)
kalınlığı aynı kalacak ve küçük harflerin ortalama genişliği `factor` oranına inecek şekilde
çözülür. Yatay çizgiler (y kalınlığı) dokunulmadan kalır. Noktalar (i, j, ., : ...) yuvarlak
kalsın diye yalnızca yerleri taşınır, boyları değişmez.
"""

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from geom import contours_of, runs_at_y  # noqa: E402

LOWER = "abcdefghijklmnopqrstuvwxyz"


class _G:
    def __init__(self, font, name):
        self.font, self.name = font, name

    def draw(self, pen):
        from fontTools.pens.recordingPen import DecomposingRecordingPen
        rec = DecomposingRecordingPen(self.font)
        self.font[self.name].draw(rec)
        rec.replay(pen)


def _stem(font):
    r = runs_at_y(contours_of(_G(font, "n")), font.info.xHeight * 0.4)[0]
    return r[1] - r[0]


def _avg_width(font):
    return sum(font[c].width for c in LOWER) / len(LOWER)


def _is_dot(contour, xh):
    pts = [(p.x, p.y) for p in contour.points if p.type]
    if len(contour.points) < 8 or any(p.type == "line" for p in contour.points):
        return False
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    return w < 0.5 * xh and h < 0.5 * xh and 0.85 < w / h < 1.18


def _bbox(contour):
    xs, ys = [p.x for p in contour.points], [p.y for p in contour.points]
    return min(xs), min(ys), max(xs), max(ys)


def _dots(glyph, xh):
    """Glifteki bağımsız noktalar: yuvarlak, küçük ve başka bir konturla iç içe olmayan konturlar
    (8'in iç boşlukları, ° ve % halkaları nokta sayılmaz)."""
    boxes = [_bbox(c) for c in glyph.contours]

    def inside(a, b):
        return b[0] <= a[0] and b[1] <= a[1] and a[2] <= b[2] and a[3] <= b[3]

    out = set()
    for i, c in enumerate(glyph.contours):
        if not _is_dot(c, xh):
            continue
        if any(j != i and (inside(boxes[i], boxes[j]) or inside(boxes[j], boxes[i])) for j in range(len(boxes))):
            continue
        out.add(i)
    return out


def _solve_t(f, target, lo, hi):
    for _ in range(50):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if f(m) > target else (lo, m)
    return (lo + hi) / 2


def condense(R, B, factor, ref=None):
    """R ve B'yi (Regular, ExtraBold) yerinde daraltır; kullanılan t ve s değerlerini döndürür.

    `ref` (Regular, ExtraBold): oranın hesaplandığı sabit referans (Sen'in orijinal masterları);
    verilmezse R ve B kullanılır. Böylece tek bir harfin genişliği değişince oran kaymaz.
    """
    sR, sB = _stem(R), _stem(B)
    wR, wB = (_avg_width(f) for f in (ref or (R, B)))
    src = {"Regular": copy.deepcopy(R), "ExtraBold": copy.deepcopy(B)}
    log = {}
    for name, font, t0 in (("Regular", R, 0.0), ("ExtraBold", B, 1.0)):
        stem0, w0 = sR + t0 * (sB - sR), wR + t0 * (wB - wR)

        def ratio(t):
            return stem0 / (sR + t * (sB - sR)) * (wR + t * (wB - wR)) / w0

        t = _solve_t(ratio, factor, t0, t0 + 1.0)
        s = stem0 / (sR + t * (sB - sR))

        def X(xr, xb):
            return round(s * (xr + t * (xb - xr)))

        xh = font.info.xHeight
        for g in font:
            gr, gb = src["Regular"][g.name], src["ExtraBold"][g.name]
            dots = _dots(g, xh)
            for i, (c, cr, cb) in enumerate(zip(g.contours, gr.contours, gb.contours)):
                if i in dots:
                    xs = [p.x for p in c.points]
                    cx_old = (min(xs) + max(xs)) / 2
                    xr = [p.x for p in cr.points]
                    xb = [p.x for p in cb.points]
                    cx_new = s * ((min(xr) + max(xr)) / 2 + t * ((min(xb) + max(xb)) / 2 - (min(xr) + max(xr)) / 2))
                    for p in c.points:
                        p.x = round(p.x + cx_new - cx_old)
                    continue
                for p, pr, pb in zip(c.points, cr.points, cb.points):
                    p.x = X(pr.x, pb.x)
            for c, cr, cb in zip(g.components, gr.components, gb.components):
                xx, xy, yx, yy, dx, dy = c.transformation
                c.transformation = (xx, xy, yx, yy, X(cr.transformation[4], cb.transformation[4]), dy)
            ar = {a.name: a.x for a in gr.anchors}
            ab = {a.name: a.x for a in gb.anchors}
            for a in g.anchors:
                a.x = X(ar[a.name], ab[a.name])
            g.width = X(gr.width, gb.width)
        kr, kb = src["Regular"].kerning, src["ExtraBold"].kerning
        font.kerning.clear()
        for pair in set(kr) | set(kb):
            v = round(s * (kr.get(pair, 0) + t * (kb.get(pair, 0) - kr.get(pair, 0))) / 5) * 5
            if v:
                font.kerning[pair] = v
        log[name] = {"t": round(t, 3), "weight_x": round(400 + t * 500), "scale_x": round(s, 4),
                     "stem": [round(stem0), _stem(font)],
                     "avg_width_ref": round(w0), "avg_width": round(_avg_width(font))}
    return log


def track(font, d):
    """Her yan boşluktan d birim çıkarır (aksanlar gibi sıfır genişlikli glifler hariç).

    Bileşiklerde bileşen ofseti, bileşenin kendi kaymasını telafi edecek şekilde düzeltilir;
    böylece bileşik glif bir bütün olarak d kadar kayar."""
    shift = {g.name: (d if g.width > 0 and g.name != "space" else 0) for g in font}
    for g in font:
        k = shift[g.name]
        if not k:
            continue
        for c in g.contours:
            for p in c.points:
                p.x -= k
        for a in g.anchors:
            a.x -= k
        for c in g.components:
            xx, xy, yx, yy, dx, dy = c.transformation
            c.transformation = (xx, xy, yx, yy, dx - k + shift[c.baseGlyph], dy)
        g.width -= 2 * k
    return d
