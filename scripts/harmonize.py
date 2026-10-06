"""Inter'in a ve e gliflerini Sen'in iki masterına (Regular, ExtraBold) uyarlar.

İki varyant üretir:
  dogrudan   - yalnızca x-height'e göre eşit ölçek + dikey gövdeye göre tek ağırlık seçimi
  uyarlanmis - Sen'in genişlik ritmine göre yatay ölçek, dikey ve yatay kalınlığın ayrı ayrı
               eşlenmesi (anizotropik interpolasyon), overshoot eşleme, Sen'e göre boşluk

Inter'in Regular→Black aralığı nokta nokta doğrusal olduğu için (ölçüldü, sapma < 2/2048)
x ve y koordinatları Regular ve Black arasında birbirinden bağımsız interpole edilebiliyor.
"""

import copy
import json
import shutil
import sys
from pathlib import Path

import ufoLib2
from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.pens.pointPen import SegmentToPointPen
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).parent))
from geom import bounds, contours_of, runs_at_x, runs_at_y  # noqa: E402
from kerning import adjust as adjust_kerning, optical_gap  # noqa: E402
from terminals import (  # noqa: E402
    _outer_is_in, find_terminals, make_vertical, make_vertical_at, sen_cut_lengths, terminal_rel_x,
)

ROOT = Path(__file__).resolve().parent.parent
MASTERS = ["Regular", "ExtraBold"]
INTER_XH = 1118
# Regular'da dik kesik, Sen'in kesik uzunluğunun en fazla bu katı olabilir (uç daha az kısalır).
# ExtraBold'da kesik yeri Regular'daki göreli konumdan alınır, uzunluğu Sen'inkinin bu katıdır.
TERMINAL_K_REGULAR = 1.25
TERMINAL_K_EXTRABOLD = 1.0
# Kesimin yeri: 0 = Sen'deki kadar kısa (k ile bulunan konum), 1 = Inter'in orijinal uç noktası.
# Aradaki değerlerde iç kenar dış kenara paralel uzatılır, kesik uzunluğu sabit kalır.
TERMINAL_LENGTH = 0.5
# ExtraBold'da aynı ölçek: 0 = Regular'ın kısa kesim konumu (göreli), 1 = Inter'in uç noktası.
TERMINAL_LENGTH_EXTRABOLD = 0.25
# Hangi uçlar dik kesilsin: "top" = a'nın (ve æ, ª'nın a kısmının) kemeri, "bottom" = e'nin kuyruğu.
# e, Inter'in orijinal açılı ucuyla bırakılıyor.
CUT_TERMINALS = ("top",)
# æ iki bölmeli ve sıkışık; Black ötesine ekstrapolasyon a ile e arasındaki boşlukları kapatıyor.
AE_TY_CAP = 1.2
# Boşluk düzeltmesi bu nötr harflere göre yapılır (kerning gerektirmeyen ortaklar).
NEUTRAL_PARTNERS = ["n", "o", "i", "l", "H", "O"]
# Düz gövdeli harfler: (Inter karakteri, Sen'deki referans harf, yükseklik). Gövde kalınlığı ve
# boşluklar referans harften alınır; Inter'deki glif/referans boşluk oranı korunur.
STRAIGHT = {"I": ("I", "H", "capHeight"), "idotless": ("ı", "n", "xHeight")}
INTER_CAP = 1490
# Düz harflerin kerning'i bu harflerin kerning'ini izler (I → H; ı/i sağda → n, solda → l).
KERN_ANALOG_LEFT = {"I": "H", "idotless": "l", "i": "l"}
KERN_ANALOG_RIGHT = {"I": "H", "idotless": "n", "i": "n"}


class OpsGlyph:
    def __init__(self, ops):
        self.ops = ops

    def draw(self, pen):
        for op, args in self.ops:
            getattr(pen, op)(*args)


class SenGlyph:
    def __init__(self, font, name):
        self.font, self.name = font, name

    def draw(self, pen):
        rec = DecomposingRecordingPen(self.font)
        self.font[self.name].draw(rec)
        rec.replay(pen)


class InterGlyph:
    """Inter Regular ve Black arasında x ve y için ayrı ağırlıkla interpole edilen glif."""

    def __init__(self, name):
        self.name = name
        self.ops = {}
        self.adv = {}
        for w in ("Regular", "Black"):
            font = TTFont(ROOT / f"upstream/inter/Inter-{w}.otf")
            gname = font.getBestCmap()[ord(name)]
            pen = RecordingPen()
            font.getGlyphSet()[gname].draw(pen)
            self.ops[w] = pen.value
            self.adv[w] = font["hmtx"][gname][0]
        assert [o for o, _ in self.ops["Regular"]] == [o for o, _ in self.ops["Black"]]

    def at(self, tx, ty):
        out = []
        for (op, ra), (_, ba) in zip(self.ops["Regular"], self.ops["Black"]):
            out.append((op, tuple(
                (r[0] + tx * (b[0] - r[0]), r[1] + ty * (b[1] - r[1])) for r, b in zip(ra, ba)
            )))
        return OpsGlyph(out)

    def advance(self, tx):
        return self.adv["Regular"] + tx * (self.adv["Black"] - self.adv["Regular"])


# --- ölçümler -------------------------------------------------------------

def stem_n(g, xh):
    return _w(runs_at_y(contours_of(g), xh * 0.4)[0])


def o_side(g):
    P = contours_of(g)
    x0, y0, x1, y1 = bounds(P)
    return _w(runs_at_y(P, (y0 + y1) / 2)[0])


def o_top(g):
    P = contours_of(g)
    x0, y0, x1, y1 = bounds(P)
    return _w(runs_at_x(P, (x0 + x1) / 2)[-1])


def ink(g):
    return bounds(contours_of(g))


def _w(run):
    return run[1] - run[0]


def solve(f, target, lo=0.0, hi=1.0):
    """f(t) yaklaşık doğrusal; secant ile f(t) = target çöz (ekstrapolasyona izin verir)."""
    a, b = lo, hi
    fa, fb = f(a) - target, f(b) - target
    for _ in range(8):
        if abs(fb - fa) < 1e-9:
            break
        c = b - fb * (b - a) / (fb - fa)
        a, fa, b, fb = b, fb, c, f(c) - target
    return b


# --- dönüşüm --------------------------------------------------------------

def transform(glyph, sx, sy, ymap, dx):
    out = []
    for op, args in glyph.ops:
        out.append((op, tuple((round(x * sx + dx), round(ymap(y * sy))) for x, y in args)))
    return OpsGlyph(out)


def write_outline(ufo_glyph, ops_glyph):
    ufo_glyph.clearContours()
    ops_glyph.draw(SegmentToPointPen(ufo_glyph.getPointPen()))


def top_extreme_x(ops_glyph):
    pts = [p for op, args in ops_glyph.ops if op in ("moveTo", "lineTo", "curveTo") for p in args[-1:]]
    ymax = max(p[1] for p in pts)
    xs = [p[0] for p in pts if p[1] >= ymax - 1]
    return sum(xs) / len(xs)


def left_stem(g, y):
    return runs_at_y(contours_of(g), y)[0]


def build_straight(sen, variant):
    """I ve ı: Inter'in düz çubuklarını Sen'in gövde kalınlığı ve boşluk sistemine oturtur.

    Inter'de ikisi de dikdörtgen; uyarlanınca gövde Sen'in H / n gövdesine, boşluklar H / n'nin
    sol boşluğuna (Inter'deki oranla) eşitlenir. Sen'in I serifleri ve ı bayrağı böylece kalkar.
    """
    log = {}
    for name, (char, ref, height) in STRAIGHT.items():
        ig, iref = InterGlyph(char), InterGlyph(ref)
        h = getattr(sen.info, height)
        sy = h / (INTER_CAP if height == "capHeight" else INTER_XH)
        s_ref = SenGlyph(sen, ref)
        r_stem = _w(left_stem(s_ref, h * 0.2))
        r_lsb = ink(s_ref)[0]
        old_g = SenGlyph(sen, name)
        old_stem = left_stem(old_g, h * 0.5) if name == "idotless" else runs_at_y(contours_of(old_g), h * 0.5)[0]
        sx = sy
        if variant == "dogrudan":
            t = solve(lambda t: stem_n(InterGlyph("n").at(t, t), INTER_XH) * sy, stem_n(SenGlyph(sen, "n"), sen.info.xHeight))
            src = ig.at(t, t)
            i_ink = ink(src)
            lsb, rsb = i_ink[0] * sx, (ig.advance(t) - i_ink[2]) * sx
        else:
            t = solve(lambda t: _w(left_stem(ig.at(t, 0), INTER_XH * 0.2)) * sx, r_stem)
            src = ig.at(t, 0)
            i_ink, ir_lsb = ink(src), ink(iref.at(t, 0))[0]
            lsb = r_lsb * i_ink[0] / ir_lsb
            rsb = r_lsb * (ig.advance(t) - i_ink[2]) / ir_lsb
        lsb, rsb = round(lsb), round(rsb)
        shaped = transform(src, sx, sy, lambda y: y, 0)
        final = transform(shaped, 1, 1, lambda y: y, lsb - ink(shaped)[0])
        g = sen[name]
        oanch = {a.name: (a.x, a.y) for a in g.anchors}
        write_outline(g, final)
        nx0, _, nx1, _ = ink(final)
        g.width = round(nx1 + rsb)
        # çapalar gövdeye göre taşınır (eski ink kutusu serif/bayrak içerdiği için kullanılmaz)
        g.clearAnchors()
        for an, (ax, ay) in oanch.items():
            nx = nx0 + (ax - old_stem[0]) / _w(old_stem) * (nx1 - nx0)
            if an == "top":
                nx = (nx0 + nx1) / 2  # düz gövdede aksan tam ortaya
            g.appendAnchor({"name": an, "x": round(nx), "y": ay})
        log[name] = {"inter_weight": round(400 + t * 500), "scale": round(sx, 4),
                     "stem": round(nx1 - nx0), "lsb": lsb, "rsb": rsb, "width": g.width}
    # i: idotless + kendi noktası; nokta yeni gövdenin ortasına, genişlik ı'nınki
    i, base = sen["i"], sen["idotless"]
    for c in i.components:
        c.transformation = (1, 0, 0, 1, 0, 0)
    bx0, _, bx1, _ = ink(SenGlyph(sen, "idotless"))
    dot = i.contours[0]
    dxs = [p.x for p in dot.points if p.type]
    shift = round((bx0 + bx1) / 2 - (min(dxs) + max(dxs)) / 2)
    for p in dot.points:
        p.x += shift
    i.width = base.width
    i.clearAnchors()
    for a in base.anchors:
        i.appendAnchor({"name": a.name, "x": a.x, "y": a.y})
    log["i"] = {"dot_shift": shift, "width": i.width}
    fix_composites(sen, None, bases=("I", "idotless", "i"))
    return log


def remap_straight_kerning(font):
    """I/ı/i içeren çiftleri, aynı profildeki harfin (H, n, l) çiftine eşitler; yoksa siler."""
    changes = []
    for (left, right), v in list(font.kerning.items()):
        analog = (KERN_ANALOG_LEFT.get(left, left), KERN_ANALOG_RIGHT.get(right, right))
        if analog == (left, right):
            continue
        new = font.kerning.get(analog)
        if new is None:
            del font.kerning[(left, right)]
        else:
            font.kerning[(left, right)] = new
        changes.append({"pair": f"{left} {right}", "old": v, "new": new, "analog": " ".join(analog)})
    return changes


def harmonize(variant):
    inter = {n: InterGlyph(n) for n in "aeno"}
    log = {}
    fonts = {}
    term_rel = {}
    for m in MASTERS:
        sen = ufoLib2.Font.open(ROOT / f"sources/Sen-{m}.ufo")
        fonts[m] = sen
        straight_log = build_straight(sen, variant)
        cuts = sen_cut_lengths(sen)
        params = {}
        xh = sen.info.xHeight
        sy = xh / INTER_XH
        s_n, s_o, s_a, s_e = (SenGlyph(sen, n) for n in "noae")
        tgt = {
            "stem": stem_n(s_n, xh),
            "oside": o_side(s_o),
            "otop": o_top(s_o),
            "etop": o_top(s_e),  # Sen e'sinin üst çizgisi (o'dan ince)
            "n_ink": ink(s_n),
            "o_ink": ink(s_o),
            "e_ink": ink(s_e),
            "o_lsb": ink(s_o)[0],
            "o_rsb": sen["o"].width - ink(s_o)[2],
            "n_lsb": ink(s_n)[0],
        }
        o_bounds = ink(s_o)
        os_top, os_bot = o_bounds[3] - xh, o_bounds[1]
        old = {
            n: (ink(SenGlyph(sen, n)), sen[n].width, {a.name: (a.x, a.y) for a in sen[n].anchors})
            for n in ("a", "e", "ae")
        }
        log[m] = {"xHeight": xh, "targets": {k: round(v, 1) if isinstance(v, float) else v for k, v in tgt.items() if k in ("stem", "oside", "otop", "etop")}}
        log[m]["straight"] = straight_log

        for name in "ae":
            ig = inter[name]
            if variant == "dogrudan":
                sx = sy
                t = solve(lambda t: stem_n(inter["n"].at(t, t), INTER_XH) * sy, tgt["stem"])
                tx = ty = t
                ymap = lambda y: y  # noqa: E731
            else:
                # y: a için Inter o'sunun üst kalınlığı Sen o'sununkine; e için Inter e'sininki
                # Sen e'sininkine eşit olsun (Sen'in e'si o'sundan ince, yoksa e'nin ağzı kapanıyor)
                if name == "e":
                    ty = solve(lambda t: o_top(ig.at(0, t)) * sy, tgt["etop"])
                else:
                    ty = solve(lambda t: o_top(inter["o"].at(0, t)) * sy, tgt["otop"])
                # x: genişlik ve dikey kalınlık birlikte çözülür
                tx = 0.0
                for _ in range(6):
                    w_inter = ink(ig.at(tx, ty))
                    w_inter = w_inter[2] - w_inter[0]
                    if name == "a":
                        n_i = ink(inter["n"].at(tx, ty))
                        target_w = (tgt["n_ink"][2] - tgt["n_ink"][0]) * w_inter / (n_i[2] - n_i[0])
                    else:
                        target_w = tgt["e_ink"][2] - tgt["e_ink"][0]
                    sx = target_w / w_inter
                    if name == "a":
                        tx = solve(lambda t: stem_n(inter["n"].at(t, ty), INTER_XH) * sx, tgt["stem"])
                    else:
                        tx = solve(lambda t: o_side(inter["o"].at(t, ty)) * sx, tgt["oside"])
                io = ink(inter["o"].at(tx, ty))
                i_top, i_bot = io[3] * sy - xh, io[1] * sy

                def ymap(y, i_top=i_top, i_bot=i_bot):
                    if y > xh:
                        return xh + (y - xh) * os_top / i_top
                    if y < 0:
                        return y * os_bot / i_bot
                    return y

            src = ig.at(tx, ty)
            shaped = transform(src, sx, sy, ymap, 0)
            x0, _, x1, _ = ink(shaped)

            # boşluklar
            i_ink = ink(src)
            i_adv = ig.advance(tx)
            if variant == "dogrudan":
                lsb, rsb = i_ink[0] * sx, (i_adv - i_ink[2]) * sx
            else:
                io_ink = ink(inter["o"].at(tx, ty))
                io_lsb, io_rsb = io_ink[0], inter["o"].advance(tx) - io_ink[2]
                in_lsb = ink(inter["n"].at(tx, ty))[0]
                if name == "a":
                    lsb = tgt["o_lsb"] * i_ink[0] / io_lsb
                    rsb = tgt["n_lsb"] * (i_adv - i_ink[2]) / in_lsb
                else:
                    lsb = tgt["o_lsb"] * i_ink[0] / io_lsb
                    rsb = tgt["o_rsb"] * (i_adv - i_ink[2]) / io_rsb
            lsb, rsb = round(lsb), round(rsb)
            final = transform(shaped, 1, 1, lambda y: y, lsb - x0)
            nx0, ny0, nx1, ny1 = ink(final)
            width = round(nx1 + rsb)

            g = sen[name]
            write_outline(g, final)
            g.width = width
            params[name] = {"tx": tx, "ty": ty, "sx": sx, "sy": sy, "ymap": ymap, "lsb": lsb, "rsb": rsb}
            if variant == "uyarlanmis":
                apply_terminals(g, m, cuts, term_rel)
            (ox0, oy0, ox1, oy1), _, oanch = old[name]
            g.clearAnchors()
            for aname, (ax, ay) in oanch.items():
                if aname == "top":
                    nx, ny = round(top_extreme_x(final)), ay
                elif name == "a" and aname == "ogonek":
                    nx, ny = round(nx1 + (ax - ox1)), ay
                else:
                    nx, ny = round(nx0 + (ax - ox0) / (ox1 - ox0) * (nx1 - nx0)), ay
                g.appendAnchor({"name": aname, "x": nx, "y": ny})

            P = contours_of(SenGlyph(sen, name))
            log[m][name] = {
                "inter_weight_x": round(400 + tx * 500), "inter_weight_y": round(400 + ty * 500),
                "scale_x": round(sx, 4), "scale_y": round(sy, 4),
                "width": width, "lsb": lsb, "rsb": rsb,
                "bbox": [round(v) for v in ink(final)],
                "points": [len(c) for c in g.contours],
                "measured": {
                    "stem@0.4xh": [round(_w(r)) for r in runs_at_y(P, xh * 0.4)],
                    "vruns@center": [round(_w(r)) for r in runs_at_x(P, (nx0 + nx1) / 2)],
                },
            }

        if variant == "uyarlanmis":
            log[m]["ae"] = build_ae(sen, params, old["ae"], cuts, term_rel, m)
            log[m]["ordfeminine"] = build_ordfeminine(sen, cuts, term_rel, m)
            # a/e'nin boşluk ve kerning referansı: Sen'in eski a/e'si, ama yeni I/ı ile
            orig = ufoLib2.Font.open(ROOT / f"sources/Sen-{m}.ufo")
            build_straight(orig, variant)
            log[m]["straight_kerning"] = remap_straight_kerning(sen)
            remap_straight_kerning(orig)
            log[m]["spacing"] = respace(orig, sen, ("a", "e", "ae"))
        fix_composites(sen, old)
        if variant == "uyarlanmis":
            log[m]["kerning"] = adjust_kerning(orig, sen)
        sen.info.familyName = f"Sen Deneme {variant.capitalize()}"
    return fonts, log


def respace(orig, font, glyphs, min_shift=5):
    """Yeni glifin nötr harflerle optik boşluğunu, eski glifinkine eşitler (ortanca fark)."""
    out = {}
    for g in glyphs:
        def median(vals):
            vals = sorted(vals)
            return vals[len(vals) // 2]
        dl = median([optical_gap(orig, p, g, 0, {}) - optical_gap(font, p, g, 0, {}) for p in NEUTRAL_PARTNERS])
        dr = median([optical_gap(orig, g, p, 0, {}) - optical_gap(font, g, p, 0, {}) for p in NEUTRAL_PARTNERS])
        dl = round(dl) if abs(dl) >= min_shift else 0
        dr = round(dr) if abs(dr) >= min_shift else 0
        glyph = font[g]
        if dl:
            glyph.move((dl, 0))
        glyph.width += dl + dr
        out[g] = {"lsb": dl, "rsb": dr}
    _clear_profile_cache()
    return out


def _clear_profile_cache():
    import kerning
    kerning._PROFILE_CACHE.clear()


def _outer_tip_x(g, ci, i):
    pts = g.contours[ci].points
    N = len(pts)
    C_in = [(pts[(i - 3 + k) % N].x, pts[(i - 3 + k) % N].y) for k in range(4)]
    C_out = [(pts[(i + 1 + k) % N].x, pts[(i + 1 + k) % N].y) for k in range(4)]
    return C_in[3][0] if _outer_is_in(C_in, C_out) else C_out[0][0]


def apply_terminals(g, master, cuts, term_rel, scale=1.0):
    """Glifin açılı terminallerini Sen gibi dik keser (bkz. terminals.py).

    Kısa kesim konumu Regular'da k katsayısıyla bulunur; ExtraBold bu konumu göreli olarak alır.
    TERMINAL_LENGTH(_EXTRABOLD) kesimi bu konumdan Inter'in orijinal uç noktasına doğru kaydırır.
    """
    ys = [p.y for c in g.contours for p in c.points if p.type]
    xs = [p.x for c in g.contours for p in c.points if p.type]
    mid = (max(ys) + min(ys)) / 2
    x0, w = min(xs), max(xs) - min(xs)
    for k, (ci, i) in enumerate(find_terminals(g)):
        kind = "top" if g.contours[ci].points[i].y > mid else "bottom"
        if kind not in CUT_TERMINALS:
            continue
        key = (g.name, k)
        x_outer = _outer_tip_x(g, ci, i)
        if master == "Regular":
            x_trim, cut = make_vertical(copy.deepcopy(g), ci, i, TERMINAL_K_REGULAR * cuts[kind] * scale)
            term_rel[key] = (x_trim - x0) / w
            if TERMINAL_LENGTH:
                make_vertical_at(g, ci, i, x_trim + TERMINAL_LENGTH * (x_outer - x_trim), cut)
            else:
                make_vertical(g, ci, i, TERMINAL_K_REGULAR * cuts[kind] * scale)
        else:
            x_trim = x0 + term_rel[key] * w
            X = x_trim + TERMINAL_LENGTH_EXTRABOLD * (x_outer - x_trim)
            make_vertical_at(g, ci, i, X, round(TERMINAL_K_EXTRABOLD * cuts[kind] * scale))


def build_ae(sen, params, old_ae, cuts, term_rel, master):
    """Inter'in kendi æ'sini a ve e'nin parametreleriyle uyarlar (bileşik æ yerine)."""
    ig = InterGlyph("æ")
    pa, pe = params["a"], params["e"]
    tx, ty = (pa["tx"] + pe["tx"]) / 2, min(pa["ty"], AE_TY_CAP)
    sx = (pa["sx"] + pe["sx"]) / 2
    shaped = transform(ig.at(tx, ty), sx, pa["sy"], pa["ymap"], 0)
    x0 = ink(shaped)[0]
    final = transform(shaped, 1, 1, lambda y: y, pa["lsb"] - x0)
    nx0, _, nx1, _ = ink(final)
    g = sen["ae"]
    g.clearComponents()
    write_outline(g, final)
    g.width = round(nx1 + pe["rsb"])
    apply_terminals(g, master, cuts, term_rel)
    (ox0, _, ox1, _), _, oanch = old_ae
    g.clearAnchors()
    for aname, (ax, ay) in oanch.items():
        g.appendAnchor({"name": aname, "x": round(nx0 + (ax - ox0) / (ox1 - ox0) * (nx1 - nx0)), "y": ay})
    return {"inter_weight_x": round(400 + tx * 500), "inter_weight_y": round(400 + ty * 500),
            "scale_x": round(sx, 4), "width": g.width, "points": [len(c) for c in g.contours]}


def build_ordfeminine(sen, cuts, term_rel, master):
    """ª: Inter º → Sen º dönüşümünü bulup aynısını Inter ª'ya uygular."""
    io, ia = InterGlyph("º"), InterGlyph("ª")
    s_o = SenGlyph(sen, "ordmasculine")
    so = ink(s_o)
    s_top, s_side = o_top(s_o), o_side(s_o)
    i_h = ink(io.at(0, 0))
    sy = (so[3] - so[1]) / (i_h[3] - i_h[1])
    ty = solve(lambda t: o_top(io.at(0, t)) * sy, s_top)
    tx, sx = 0.0, sy
    for _ in range(6):
        iw = ink(io.at(tx, ty))
        sx = (so[2] - so[0]) / (iw[2] - iw[0])
        tx = solve(lambda t: o_side(io.at(t, ty)) * sx, s_side)
    dy = so[1] - ink(io.at(tx, ty))[1] * sy
    src = ia.at(tx, ty)
    shaped = transform(src, sx, sy, lambda y: y + dy, 0)
    # boşluk: Inter'deki ª/º oranları, Sen º'nun boşluklarına
    io_ink, ia_ink = ink(io.at(tx, ty)), ink(src)
    lsb = (so[0]) * ia_ink[0] / io_ink[0]
    rsb = (sen["ordmasculine"].width - so[2]) * (ia.advance(tx) - ia_ink[2]) / (io.advance(tx) - io_ink[2])
    x0 = ink(shaped)[0]
    final = transform(shaped, 1, 1, lambda y: y, round(lsb) - x0)
    g = sen["ordfeminine"]
    write_outline(g, final)
    g.width = round(ink(final)[2] + rsb)
    # küçük boyutta kesik uzunluğu: Sen º / o kalınlık oranıyla ölçeklenir
    apply_terminals(g, master, cuts, term_rel, scale=s_top / o_top(SenGlyph(sen, "o")))
    return {"inter_weight_x": round(400 + tx * 500), "inter_weight_y": round(400 + ty * 500),
            "scale": [round(sx, 4), round(sy, 4)], "width": g.width, "points": [len(c) for c in g.contours]}


def fix_composites(font, old, bases=("a", "e", "ae", "I", "idotless", "i")):
    """Değişen temel glifleri kullanan bileşikleri yeni çapalara ve genişliklere göre günceller."""
    # i önce: iogonek ve ij onun genişliğine bağlı
    order = sorted(font.keys(), key=lambda n: n != "i")
    for name in order:
        g = font[name]
        if g.name in ("ae", "oe", "IJ", "ij") or not g.components:
            continue
        base_c = next((c for c in g.components if c.baseGlyph in bases), None)
        if base_c is None:
            continue
        base = font[base_c.baseGlyph]
        base_c.transformation = (1, 0, 0, 1, 0, 0)
        marks = [c for c in g.components if c is not base_c]
        banch = {a.name: (a.x, a.y) for a in base.anchors}
        g.width = base.width
        for c in marks:
            manch = {a.name: (a.x, a.y) for a in font[c.baseGlyph].anchors}
            for an, (mx, my) in manch.items():
                if an.startswith("_") and an[1:] in banch:
                    # yatay konum çapadan; dikey konum Sen'deki gibi kalır (iogonek'te çapa y'si
                    # elle düzeltilmiş, çapaya uyunca kanca gövdeden kopuyor)
                    bx = banch[an[1:]][0]
                    c.transformation = (1, 0, 0, 1, bx - mx, c.transformation[5])
                    break
        new_anchors = dict(banch)
        for c in marks:
            dx, dy = c.transformation[4], c.transformation[5]
            for a in font[c.baseGlyph].anchors:
                if not a.name.startswith("_"):
                    new_anchors[a.name] = (a.x + dx, a.y + dy)
        g.clearAnchors()
        for an, (x, y) in new_anchors.items():
            g.appendAnchor({"name": an, "x": round(x), "y": round(y)})

    # IJ, ij: ikinci harf birincinin genişliği kadar sağda
    for name in ("IJ", "ij"):
        g = font[name]
        first, second = g.components
        off_old = second.transformation[4]
        off_new = font[first.baseGlyph].width
        second.transformation = (1, 0, 0, 1, off_new, 0)
        g.width = off_new + font[second.baseGlyph].width
        fanch = {a.name: a.x for a in font[first.baseGlyph].anchors}
        sanch = {a.name: a.x + off_new for a in font[second.baseGlyph].anchors}
        anchors = [(a.name, a.x, a.y) for a in g.anchors]
        g.clearAnchors()
        for an, x, y in anchors:
            # çapa ikinci harfte varsa ona, yoksa birinciye ait (ij'de top/bottom j'nin)
            x = sanch.get(an, fanch.get(an, x + off_new - off_old))
            g.appendAnchor({"name": an, "x": round(x), "y": y})

    if old is None:
        return
    new_a_ink, new_e_ink = ink(SenGlyph(font, "a")), ink(SenGlyph(font, "e"))
    (oa_ink, oa_w, _), (oe_ink, oe_w, _) = old["a"], old["e"]
    # æ (bileşikse): e'nin a'nın sağ gövdesine binme miktarını koru
    ae = font["ae"]
    if ae.components:
        ce = next(c for c in ae.components if c.baseGlyph == "e")
        off_old = ce.transformation[4]
        overlap = oa_ink[2] - (off_old + oe_ink[0])
        tail = ae.width - (off_old + oe_w)
        off_new = round(new_a_ink[2] - overlap - new_e_ink[0])
        ce.transformation = (1, 0, 0, 1, off_new, 0)
        ae.width = off_new + font["e"].width + tail
    # œ: e'nin mürekkep sol kenarını aynı yerde tut
    oe = font["oe"]
    ce = next(c for c in oe.components if c.baseGlyph == "e")
    off_old = ce.transformation[4]
    tail = oe.width - (off_old + oe_w)
    off_new = round(off_old + oe_ink[0] - new_e_ink[0])
    ce.transformation = (1, 0, 0, 1, off_new, 0)
    oe.width = off_new + font["e"].width + tail


if __name__ == "__main__":
    all_logs = {}
    for variant in ("dogrudan", "uyarlanmis"):
        fonts, log = harmonize(variant)
        out = ROOT / "variants" / variant
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        for m, f in fonts.items():
            f.save(out / f"Sen-{m}.ufo")
        shutil.copy(ROOT / "sources/Sen.designspace", out / "Sen.designspace")
        all_logs[variant] = log
    (ROOT / "build").mkdir(exist_ok=True)
    (ROOT / "build/olcumler.json").write_text(json.dumps(all_logs, indent=1, ensure_ascii=False))
    print(json.dumps(all_logs, indent=1, ensure_ascii=False))
