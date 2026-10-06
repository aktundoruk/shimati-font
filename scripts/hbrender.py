"""HarfBuzz ile dizip (kerning, özellikler dahil) PIL'e çizen yardımcı."""
import freetype
import uharfbuzz as hb
from fontTools.pens.recordingPen import RecordingPen
from PIL import Image, ImageChops, ImageDraw


def _flatten(ops):
    polys, cur = [], []
    for op, args in ops:
        if op == "moveTo":
            cur = [args[0]]
        elif op == "lineTo":
            cur.append(args[0])
        elif op == "qCurveTo":
            p0 = cur[-1]
            pts = list(args)
            # TrueType ardışık off-curve noktalarını ayır
            segs = []
            for i in range(len(pts) - 1):
                c = pts[i]
                e = pts[i + 1] if i == len(pts) - 2 else ((pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2)
                segs.append((c, e))
            for c, e in segs:
                for k in range(1, 17):
                    t = k / 16
                    cur.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * e[0],
                                (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * e[1]))
                p0 = e
        elif op == "curveTo":
            p0 = cur[-1]
            p1, p2, p3 = args
            for k in range(1, 25):
                t = k / 24
                mt = 1 - t
                cur.append((mt**3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t**3 * p3[0],
                            mt**3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t**3 * p3[1]))
        elif op in ("closePath", "endPath"):
            if cur:
                polys.append(cur)
            cur = []
    return polys


class HBFont:
    """Konumlar HarfBuzz'dan (kerning dahil), glif rasterı FreeType'tan (nonzero dolgu)."""

    def __init__(self, path, wght=None):
        self.face = hb.Face(hb.Blob.from_file_path(path))
        self.font = hb.Font(self.face)
        self.ft = freetype.Face(path)
        if wght is not None:
            self.font.set_variations({"wght": wght})
            self.ft.set_var_design_coords((wght,))
        self.upem = self.face.upem

    def shape(self, text, kern=True):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.font, buf, {"kern": kern})
        return buf.glyph_infos, buf.glyph_positions

    def draw(self, img, text, x, y, size, fill=0, kern=True):
        """(x, y) taban çizgisi başlangıcı; tek renkli metni img'ye çizer."""
        scale = size / self.upem
        self.ft.set_char_size(int(size * 64))
        infos, poss = self.shape(text, kern)
        pen_x = 0
        ink = Image.new(img.mode, img.size, fill)
        for info, pos in zip(infos, poss):
            self.ft.load_glyph(info.codepoint, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
            gs = self.ft.glyph
            bm = gs.bitmap
            if bm.width and bm.rows:
                mask = Image.frombytes("L", (bm.width, bm.rows), bytes(bm.buffer))
                gx = x + (pen_x + pos.x_offset) * scale + gs.bitmap_left
                gy = y - pos.y_offset * scale - gs.bitmap_top
                img.paste(ink.crop((0, 0, bm.width, bm.rows)), (round(gx), round(gy)), mask)
            pen_x += pos.x_advance
        return pen_x * scale
