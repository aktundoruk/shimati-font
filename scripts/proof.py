"""Üç fontu (orijinal, dogrudan, uyarlanmis) karşılaştıran tek dosyalık HTML proof üretir."""

import base64
import html
import json
from pathlib import Path

import ufoLib2
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parent.parent
VARIANTS = [
    ("orijinal", "Sen (orijinal)"),
    ("dogrudan", "Doğrudan aktarım"),
    ("uyarlanmis", "Uyarlanmış"),
]
SAMPLES = [
    ("hamburgefonstiv", 96),
    ("aeaeae nanene ooaa", 72),
    ("ra fa va ka Pa Fa Va Ya av ay ex", 64),
    ("Değerlendirme yarın akşam", 56),
    ("Işık İzmir ılık IŞIK İNCİ HIH nın lil", 56),
    ("Çiçek Şeker çay şiş ÇAĞ ŞİŞ", 56),
    ("İğne bilgi ığdır DOĞU İNCİ iyi", 56),
    ("ä â á à ã å ā ą æ é è ê ë ē ė ę ě œ", 44),
]
PARAGRAPH = (
    "Tasarım sisteminin temel yazı karakteri, arayüzde her gün binlerce kez okunacak. "
    "Bu yüzden harflerin birbirine ne kadar uyduğu, tek tek ne kadar güzel olduklarından "
    "daha önemlidir. Ağaç, gece, çay, şeker, kalem, mavi; İstanbul’da ılık bir öğleden sonra."
)


def font_face(variant):
    data = base64.b64encode((ROOT / f"build/Sen-{variant}-VF.ttf").read_bytes()).decode()
    return (
        f"@font-face{{font-family:'P-{variant}';src:url(data:font/ttf;base64,{data}) format('truetype');"
        "font-weight:400 800;}"
    )


def glyph_svg(font, names, ghost=None, label=""):
    """Glifleri yan yana, düğüm noktaları ve metrik çizgileriyle çizer."""
    xh = font.info.xHeight
    asc, desc = 760, -200
    x = 0
    parts, nodes = [], []
    for name in names:
        g = font[name]
        rec = DecomposingRecordingPen(font)
        g.draw(rec)
        pen = SVGPathPen(font)
        rec.replay(pen)
        parts.append(f'<path class="ink" transform="translate({x} 0)" d="{pen.getCommands()}"/>')
        if ghost is not None and name in ghost:
            gp = SVGPathPen(ghost)
            gr = DecomposingRecordingPen(ghost)
            ghost[name].draw(gr)
            gr.replay(gp)
            parts.append(
                f'<path class="ghost" transform="translate({x + (g.width - ghost[name].width) / 2} 0)" '
                f'd="{gp.getCommands()}"/>'
            )
        for c in g.contours:
            for p in c.points:
                cls = "on" if p.type else "off"
                r = 6 if p.type else 4
                nodes.append(f'<circle class="{cls}" cx="{p.x + x}" cy="{p.y}" r="{r}"/>')
        parts.append(f'<rect class="adv" x="{x}" y="{desc}" width="{g.width}" height="{asc - desc}"/>')
        x += g.width
    lines = "".join(
        f'<line class="metric" x1="-40" x2="{x + 40}" y1="{y}" y2="{y}"/>' for y in (0, xh, font.info.capHeight)
    )
    return (
        f'<figure class="outline"><svg viewBox="-40 {-asc} {x + 80} {asc - desc}" role="img" '
        f'aria-label="{html.escape(label)}"><g transform="scale(1 -1)">{lines}{"".join(parts)}'
        f'{"".join(nodes)}</g></svg><figcaption>{html.escape(label)}</figcaption></figure>'
    )


def measurements_table(log):
    rows = []
    for variant, title in VARIANTS[1:]:
        for m in ("Regular", "ExtraBold"):
            t = log[variant][m]["targets"]
            for g in "ae":
                d = log[variant][m][g]
                stem = d["measured"]["stem@0.4xh"][-1]
                vr = d["measured"]["vruns@center"]
                rows.append(
                    f"<tr><td>{title}</td><td>{m}</td><td>{g}</td>"
                    f"<td>{d['inter_weight_x']} / {d['inter_weight_y']}</td>"
                    f"<td>{d['scale_x']:.3f} / {d['scale_y']:.3f}</td>"
                    f"<td>{stem} <span class=muted>({t['stem'] if g == 'a' else t['oside']:.0f})</span></td>"
                    f"<td>{vr[-1]} <span class=muted>({t['otop']:.0f})</span></td>"
                    f"<td>{d['lsb']} / {d['rsb']}</td></tr>"
                )
    return (
        "<table><thead><tr><th>Varyant</th><th>Master</th><th>Glif</th>"
        "<th>Inter ağırlığı x / y</th><th>Ölçek x / y</th><th>Dikey kalınlık (hedef)</th>"
        "<th>Üst çizgi kalınlığı (hedef)</th><th>Sol / sağ boşluk</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def main():
    log = json.loads((ROOT / "build/olcumler.json").read_text())
    faces = "".join(font_face(v) for v, _ in VARIANTS)

    specimens = []
    for text, size in SAMPLES:
        rows = "".join(
            f'<div class="row"><span class="tag">{t}</span>'
            f'<span class="spec" style="font-family:\'P-{v}\';font-size:{size}px">{html.escape(text)}</span></div>'
            for v, t in VARIANTS
        )
        specimens.append(f'<section class="block">{rows}</section>')
    paras = "".join(
        f'<div class="pcol"><span class="tag">{t}</span><p class="spec para" style="font-family:\'P-{v}\'">'
        f"{html.escape(PARAGRAPH)}</p></div>"
        for v, t in VARIANTS
    )

    outlines = []
    for m in ("Regular", "ExtraBold"):
        orig = ufoLib2.Font.open(ROOT / f"sources/Sen-{m}.ufo")
        new = ufoLib2.Font.open(ROOT / f"variants/uyarlanmis/Sen-{m}.ufo")
        direct = ufoLib2.Font.open(ROOT / f"variants/dogrudan/Sen-{m}.ufo")
        outlines.append(glyph_svg(orig, list("naoe"), label=f"{m} — Sen orijinal"))
        outlines.append(
            glyph_svg(new, list("naoe"), ghost=direct,
                      label=f"{m} — Uyarlanmış (kesikli çizgi: doğrudan aktarım)")
        )
    for m in ("Regular", "ExtraBold"):
        orig = ufoLib2.Font.open(ROOT / f"sources/Sen-{m}.ufo")
        new = ufoLib2.Font.open(ROOT / f"variants/uyarlanmis/Sen-{m}.ufo")
        names = ["H", "I", "l", "idotless", "i", "n"]
        outlines.append(glyph_svg(orig, names, label=f"{m} — Sen orijinal: H I l ı i n"))
        outlines.append(glyph_svg(new, names, label=f"{m} — Uyarlanmış: H I l ı i n"))

    doc = f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Inter Harf Denemesi</title>
<style>
{faces}
:root{{--bg:#fbfaf7;--fg:#1d1c1a;--muted:#7a776f;--line:#e4e1d8;--accent:#c4451c;--ghost:#2f6fd6;--card:#fff}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--fg:#ecebe6;--muted:#9a978e;--line:#2e2d29;--accent:#f0794f;--ghost:#79a8ff;--card:#1e1e1b}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,system-ui,sans-serif}}
main{{max-width:1180px;margin:0 auto;padding:32px 16px 80px}}
h1{{font-size:28px;margin:0 0 6px}} h2{{font-size:18px;margin:48px 0 12px}}
.lede{{color:var(--muted);max-width:760px;margin:0}}
.controls{{position:sticky;top:0;z-index:2;background:var(--bg);border-bottom:1px solid var(--line);
  padding:12px 0;margin:24px 0 8px;display:flex;gap:16px;align-items:center;flex-wrap:wrap}}
.controls input{{width:min(360px,60vw)}} .controls output{{font-variant-numeric:tabular-nums;min-width:3ch}}
.controls button{{background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}}
.block{{border-top:1px solid var(--line);padding:14px 0}}
.row{{display:grid;grid-template-columns:150px 1fr;align-items:baseline;gap:12px;overflow:hidden}}
.tag{{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em}}
.spec{{font-variation-settings:'wght' var(--w,400);white-space:nowrap;line-height:1.25}}
.paras{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}}
.para{{white-space:normal;font-size:18px;line-height:1.5;margin:6px 0 0}}
.outline{{margin:0 0 20px;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px}}
.outline svg{{width:100%;height:auto;display:block}}
figcaption{{color:var(--muted);font-size:12px;padding:4px 6px}}
.ink{{fill:var(--fg);fill-opacity:.12;stroke:var(--fg);stroke-width:2}}
.ghost{{fill:none;stroke:var(--ghost);stroke-width:3;stroke-dasharray:10 8}}
.on{{fill:var(--accent)}} .off{{fill:none;stroke:var(--accent);stroke-width:2}}
.metric{{stroke:var(--line);stroke-width:2}} .adv{{fill:none;stroke:var(--line);stroke-width:2}}
table{{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}}
th,td{{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line)}} th{{color:var(--muted);font-weight:500}}
.tablewrap{{overflow-x:auto}} .muted{{color:var(--muted)}}
ul.notes li{{margin:6px 0;max-width:820px}}
@media (max-width:640px){{.row{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>Inter’den a, e, I, ı, çengel, nokta ve kısa şapka → Sen</h1>
<p class="lede">Aynı metin üç fontla: Sen’in kendisi, Inter’in a, e, I ve ı’sının yalnızca ölçeklenip konmuş hâli
ve Sen’in genişlik, kalınlık, overshoot ve boşluk sistemine göre uyarlanmış hâli. Ağırlığı kaydırıcıyla değiştirin.</p>
<div class="controls"><label for="w">Ağırlık</label>
<input id="w" type="range" min="400" max="800" value="400" step="1"><output id="wv">400</output>
<button data-w="400">Regular</button><button data-w="600">SemiBold</button><button data-w="800">ExtraBold</button></div>
{''.join(specimens)}
<h2>Paragraf</h2><div class="paras">{paras}</div>
<h2>Konturlar</h2>
<p class="lede">Turuncu noktalar düğümler, içi boş olanlar kontrol noktaları. Yatay çizgiler: taban çizgisi, x-height, büyük harf yüksekliği.</p>
{''.join(outlines)}
<h2>Ölçümler</h2>
<p class="lede">Font birimi (UPM 1024). “Inter ağırlığı x / y”: konturun yatay ve dikey koordinatlarının alındığı Inter ağırlığı;
900’ün üzeri Black’in ötesine ekstrapolasyon demek.</p>
<div class="tablewrap">{measurements_table(log)}</div>
</main>
<script>
const r=document.getElementById('w'),o=document.getElementById('wv');
function set(v){{r.value=v;o.textContent=v;document.documentElement.style.setProperty('--w',v)}}
r.addEventListener('input',e=>set(e.target.value));
document.querySelectorAll('button[data-w]').forEach(b=>b.addEventListener('click',()=>set(b.dataset.w)));
</script></body></html>"""
    (ROOT / "proof").mkdir(exist_ok=True)
    (ROOT / "proof/proof.html").write_text(doc)
    print("proof/proof.html", len(doc) // 1024, "KB")


if __name__ == "__main__":
    main()
