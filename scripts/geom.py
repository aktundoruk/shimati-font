"""Glif ölçümü için küçük yardımcılar: konturları düzleştirip tarama çizgisiyle kesişim bulur."""

from fontTools.pens.recordingPen import RecordingPen


def contours_of(glyph, glyphset=None):
    """Glifi (UFO ya da fontTools glyphset) düzleştirilmiş poligon listesine çevirir."""
    pen = RecordingPen()
    glyph.draw(pen)
    polys, cur, start = [], [], None
    for op, args in pen.value:
        if op == "moveTo":
            cur = [args[0]]
        elif op == "lineTo":
            cur.append(args[0])
        elif op == "curveTo":
            p0 = cur[-1]
            p1, p2, p3 = args
            for i in range(1, 33):
                t = i / 32
                mt = 1 - t
                cur.append((
                    mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0],
                    mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1],
                ))
        elif op == "qCurveTo":
            raise ValueError("quadratic outline not supported")
        elif op in ("closePath", "endPath"):
            if cur:
                polys.append(cur)
            cur = []
        elif op == "addComponent":
            raise ValueError("decompose components first")
    return polys


def runs_at_y(polys, y):
    """y yüksekliğindeki yatay çizgide mürekkep aralıkları [(x0, x1), ...]."""
    xs = []
    for poly in polys:
        n = len(poly)
        for i in range(n):
            (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
    xs.sort()
    return [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]


def runs_at_x(polys, x):
    """x konumundaki dikey çizgide mürekkep aralıkları [(y0, y1), ...]."""
    swapped = [[(py, px) for px, py in poly] for poly in polys]
    return runs_at_y(swapped, x)


def bounds(polys):
    xs = [p[0] for poly in polys for p in poly]
    ys = [p[1] for poly in polys for p in poly]
    return min(xs), min(ys), max(xs), max(ys)
