import sys, ufoLib2
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
sys.path.insert(0, "scripts")
from geom import contours_of, runs_at_y, runs_at_x, bounds

class G:  # decomposing wrapper
    def __init__(self, g, gs): self.g, self.gs = g, gs
    def draw(self, pen):
        r = DecomposingRecordingPen(self.gs); self.g.draw(r); r.replay(pen)

def report(name, getg, width, xh):
    print(f"== {name}")
    for gn in ["n", "o", "a", "e"]:
        g, w = getg(gn)
        P = contours_of(g)
        x0, y0, x1, y1 = bounds(P)
        line = f"  {gn}: adv={w:.0f} bbox=({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f}) lsb={x0:.0f} rsb={w-x1:.0f}"
        if gn == "n":
            r = runs_at_y(P, xh * 0.4); line += f" vstem={[round(b-a) for a,b in r]}"
        if gn == "o":
            cx = (x0 + x1) / 2; r = runs_at_x(P, cx); line += f" hthick={[round(b-a) for a,b in r]}"
            r = runs_at_y(P, (y0 + y1) / 2); line += f" side={[round(b-a) for a,b in r]}"
        if gn in "ae":
            cx = (x0 + x1) / 2; r = runs_at_x(P, cx); line += f" vruns@cx={[(round(a),round(b)) for a,b in r]}"
            r = runs_at_y(P, xh * 0.3); line += f" hruns@.3={[(round(a),round(b)) for a,b in r]}"
            r = runs_at_y(P, xh * 0.75); line += f" hruns@.75={[(round(a),round(b)) for a,b in r]}"
        print(line)

for m in ["Regular", "ExtraBold"]:
    f = ufoLib2.Font.open(f"sources/Sen-{m}.ufo")
    xh = f.info.xHeight
    print(f"Sen {m}: upm={f.info.unitsPerEm} xh={xh} cap={f.info.capHeight} asc={f.info.ascender}")
    report(f"Sen {m}", lambda gn: (G(f[gn], f), f[gn].width), None, xh)
    for gn in "ae":
        g = f[gn]
        print(f"  {gn}: contours={len(g.contours)} pts={[len(c) for c in g.contours]} comps={[c.baseGlyph for c in g.components]} anchors={[(a.name,a.x,a.y) for a in g.anchors]}")

for w in ["Regular", "Bold", "ExtraBold", "Black"]:
    t = TTFont(f"upstream/inter/Inter-{w}.otf"); gs = t.getGlyphSet(); hm = t["hmtx"]
    xh = t["OS/2"].sxHeight
    print(f"Inter {w}: upm={t['head'].unitsPerEm} xh={xh} cap={t['OS/2'].sCapHeight}")
    cmap = t.getBestCmap()
    report(f"Inter {w}", lambda gn: (gs[cmap[ord(gn)]], hm[cmap[ord(gn)]][0]), None, xh)
    for gn in "ae":
        r = DecomposingRecordingPen(gs); gs[cmap[ord(gn)]].draw(r)
        print(f"  {gn}: glyph={cmap[ord(gn)]} ops={[op for op,_ in r.value].count('moveTo')} contours, segs={len(r.value)}")
