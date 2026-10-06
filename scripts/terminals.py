"""Açılı kesik terminalleri Sen'deki gibi dik kesiğe çevirir.

Terminal = dış konturda iki eğri arasındaki kısa, eğik doğru parçası. Dik kesik için uca gelen
ve uçtan çıkan iki eğri aynı x'te bitecek şekilde kısaltılır ya da uzatılır (de Casteljau,
gerekirse t > 1 / t < 0). Nokta sayısı değişmez, bu yüzden masterlar uyumlu kalır.

Kesik uzunluğu Sen'den alınır (üst uç → Sen 'c' üst ucu, alt uç → Sen 'e' ucu) ve bir katsayıyla
gevşetilebilir: katsayı büyüdükçe uç daha az kısalır ama kesik daha uzun/yatık görünür.
"""

import math


def _split(P, t):
    """Kübik Bézier'i t'de böl; (sol, sağ) kontrol noktaları."""
    p0, p1, p2, p3 = P
    lerp = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)  # noqa: E731
    a, b, c = lerp(p0, p1), lerp(p1, p2), lerp(p2, p3)
    d, e = lerp(a, b), lerp(b, c)
    f = lerp(d, e)
    return (p0, a, d, f), (f, e, c, p3)


def _pt(P, t):
    return _split(P, t)[0][3]


def _solve(P, axis, value, lo, hi, prefer=None, steps=400):
    """P(t)[axis] = value olan t; [lo, hi] içindeki köklerden `prefer`'e en yakını."""
    roots = []
    prev_t, prev_v = lo, _pt(P, lo)[axis] - value
    for i in range(1, steps + 1):
        t = lo + (hi - lo) * i / steps
        v = _pt(P, t)[axis] - value
        if (prev_v < 0) != (v < 0):
            a, b = prev_t, t
            for _ in range(60):
                m = (a + b) / 2
                if (_pt(P, a)[axis] - value < 0) != (_pt(P, m)[axis] - value < 0):
                    b = m
                else:
                    a = m
            roots.append((a + b) / 2)
        prev_t, prev_v = t, v
    if not roots:
        raise ValueError(f"no t with axis {axis} = {value} in [{lo}, {hi}]")
    ref = (lo + hi) / 2 if prefer is None else prefer
    return min(roots, key=lambda r: abs(r - ref))


def find_terminals(glyph):
    """(kontur, i) listesi: i ile i+1 arasındaki eğik, iki yanı eğri olan doğru parçaları."""
    found = []
    outer = max(range(len(glyph.contours)), key=lambda ci: _area(glyph.contours[ci]))
    c = glyph.contours[outer]
    pts = c.points
    N = len(pts)
    for i, p in enumerate(pts):
        q = pts[(i + 1) % N]
        if not (p.type and q.type == "line"):
            continue
        if pts[i - 1].type is not None or pts[(i + 2) % N].type is not None:
            continue
        ang = math.degrees(math.atan2(q.y - p.y, q.x - p.x)) % 180
        if 80 < ang < 100 or ang < 1 or ang > 179:
            continue
        found.append((outer, i))
    return found


def _area(contour):
    pts = [(p.x, p.y) for p in contour.points if p.type]
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))) / 2


def make_vertical(glyph, contour_index, i, max_cut):
    """i→i+1 terminalini dik kesiğe çevirir.

    Kesim, dış uçtan glifin içine doğru taranarak kesik uzunluğu `max_cut`'ı geçmeyen ilk
    x'e konur: ne kadar az kısaltırsak harfin şekli o kadar korunur.
    """
    c = glyph.contours[contour_index]
    pts = c.points
    N = len(pts)
    idx_in = [(i - 3 + k) % N for k in range(4)]  # uca gelen eğri
    idx_out = [(i + 1 + k) % N for k in range(4)]  # uçtan çıkan eğri
    assert pts[idx_in[0]].type and pts[idx_out[3]].type, "terminal must sit between cubic curves"
    C_in = [(pts[k].x, pts[k].y) for k in idx_in]
    C_out = [(pts[k].x, pts[k].y) for k in idx_out]

    def root(C, X, ext, prefer):
        # önce eğrinin kendi üstünde ara, yoksa ucundan biraz uzat
        try:
            return _solve(C, 0, X, 0.0, 1.0, prefer=prefer)
        except ValueError:
            return _solve(C, 0, X, *ext, prefer=prefer)

    def cut_at(X):
        try:
            t_in = root(C_in, X, (1.0, 1.6), 1.0)
            t_out = root(C_out, X, (-0.6, 0.0), 0.0)
        except ValueError:
            return None
        return t_in, t_out, abs(_pt(C_in, t_in)[1] - _pt(C_out, t_out)[1])

    # dış uç hangisi: uç noktaları arasında glifin kenarına daha yakın olan
    a_end, b_end = C_in[3], C_out[0]
    inward = 1 if C_in[0][0] > a_end[0] else -1
    start = min(a_end[0], b_end[0]) if inward > 0 else max(a_end[0], b_end[0])
    chosen = best = None
    for step in range(0, 400):
        X = start + inward * step
        r = cut_at(X)
        if r is None:
            continue
        if best is None or r[2] < best[1][2]:
            best = (X, r)
        if r[2] <= max_cut:
            chosen = (X, r)
            break
    if chosen is None:
        # iç eğri bitmeden hedefe inilemiyorsa ulaşılabilen en kısa kesik
        chosen = best
    X, (t_in, t_out, L) = chosen
    new_in = _split(C_in, t_in)[0]
    new_out = _split(C_out, t_out)[1]
    for k, p in zip(idx_in, new_in):
        pts[k].x, pts[k].y = round(p[0]), round(p[1])
    for k, p in zip(idx_out, new_out):
        pts[k].x, pts[k].y = round(p[0]), round(p[1])
    pts[idx_in[3]].x = X
    pts[idx_out[0]].x = X
    return X, round(L)


def make_vertical_at(glyph, contour_index, i, X, cut):
    """Terminali verilen X'te, `cut` uzunluğunda dik keser.

    Dış kenar X'e kadar kısaltılır/uzatılır. İç kenarın uç noktası dış kenardan `cut` kadar
    içeri konur; tutamacı dış kenarın yönü ile iç kenarın kendi yönünün ortasına çevrilir, böylece
    kuyruk iç kenar kısa kalsa bile kırıksız biter. Nokta sayısı değişmez.
    """
    c = glyph.contours[contour_index]
    pts = c.points
    N = len(pts)
    idx_in = [(i - 3 + k) % N for k in range(4)]
    idx_out = [(i + 1 + k) % N for k in range(4)]
    C_in = [(pts[k].x, pts[k].y) for k in idx_in]
    C_out = [(pts[k].x, pts[k].y) for k in idx_out]
    outer_is_in = _outer_is_in(C_in, C_out)
    outer, inner = (C_in, C_out) if outer_is_in else (C_out, C_in)
    if outer_is_in:
        t = _solve(outer, 0, X, 0.0, 1.6, prefer=1.0)
        new_outer = _split(outer, t)[0]
        tip = new_outer[3]
        d = (new_outer[2][0] - tip[0], new_outer[2][1] - tip[1])  # içeri doğru teğet
    else:
        t = _solve(outer, 0, X, -0.6, 1.0, prefer=0.0)
        new_outer = _split(outer, t)[1]
        tip = new_outer[0]
        d = (new_outer[1][0] - tip[0], new_outer[1][1] - tip[1])
    ys = [p.y for cc in glyph.contours for p in cc.points if p.type]
    sign = -1 if tip[1] > (max(ys) + min(ys)) / 2 else 1  # üst uçta iç kenar aşağıda
    inner_tip = (X, tip[1] + sign * cut)

    def unit(v):
        n = math.hypot(*v) or 1
        return (v[0] / n, v[1] / n)

    # iç kenarın ucundaki yön: dış kenarın yönü ile iç kenarın kendi orijinal yönünün ortası;
    # yalnızca dış kenarı izlemek uç dik yükselirken iç kenarda kırık yaratıyor
    if outer_is_in:
        own = unit((inner[1][0] - inner[0][0], inner[1][1] - inner[0][1]))
        far, far_handle = inner[3], inner[2]
    else:
        own = unit((inner[2][0] - inner[3][0], inner[2][1] - inner[3][1]))
        far, far_handle = inner[0], inner[1]
    od = unit(d)
    du = unit((od[0] + own[0], od[1] + own[1]))
    dist = math.hypot(far[0] - inner_tip[0], far[1] - inner_tip[1])
    tip_h = (inner_tip[0] + du[0] * 0.4 * dist, inner_tip[1] + du[1] * 0.4 * dist)
    # karşı uçtaki tutamacın yönü korunur (komşu eğriyle süreklilik), boyu mesafeye oranlanır
    fu = unit((far_handle[0] - far[0], far_handle[1] - far[1]))
    far_h = (far[0] + fu[0] * 0.4 * dist, far[1] + fu[1] * 0.4 * dist)
    if outer_is_in:
        new_inner = (inner_tip, tip_h, far_h, far)
    else:
        new_inner = (far, far_h, tip_h, inner_tip)
    new_in, new_out = (new_outer, new_inner) if outer_is_in else (new_inner, new_outer)
    for k, p in zip(idx_in, new_in):
        pts[k].x, pts[k].y = round(p[0]), round(p[1])
    for k, p in zip(idx_out, new_out):
        pts[k].x, pts[k].y = round(p[0]), round(p[1])
    pts[idx_in[3]].x = pts[idx_out[0]].x = round(X)
    return round(X), cut


def _outer_is_in(C_in, C_out):
    """Uca gelen eğri mi dış kenar? Dış kenarın ucu glif kenarına daha uzak uzanır."""
    # dış kenar, terminalde iç kenara göre uca doğru daha fazla ilerler
    span_in = math.hypot(C_in[3][0] - C_in[0][0], C_in[3][1] - C_in[0][1])
    span_out = math.hypot(C_out[3][0] - C_out[0][0], C_out[3][1] - C_out[0][1])
    return span_in >= span_out


def terminal_rel_x(glyph, contour_index, i):
    """Terminal x'inin glif mürekkep genişliği içindeki göreli konumu (0..1)."""
    xs = [p.x for cc in glyph.contours for p in cc.points if p.type]
    x = glyph.contours[contour_index].points[i].x
    return (x - min(xs)) / (max(xs) - min(xs))


def sen_cut_lengths(sen):
    """Sen 'c' üst ucu ve 'e' ucundaki dik kesik uzunlukları."""
    out = {}
    for name, kind in (("c", "top"), ("e", "bottom")):
        g = sen[name]
        ys = [p.y for cc in g.contours for p in cc.points if p.type]
        mid = (max(ys) + min(ys)) / 2
        for cc in g.contours:
            pts = cc.points
            N = len(pts)
            for i, p in enumerate(pts):
                q = pts[(i + 1) % N]
                if p.type and q.type == "line" and p.x == q.x and pts[i - 1].type is None:
                    if (kind == "top") == (min(p.y, q.y) > mid):
                        out[kind] = abs(p.y - q.y)
    return out
