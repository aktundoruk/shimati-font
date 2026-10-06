"""Shimati dağıtım paketi: masaüstü (OTF, TTF, değişken TTF) ve web (WOFF2 + CSS) dosyaları.

variants/uyarlanmis kaynakları build/shimati-src'ye kopyalanır, ad ve telif bilgileri değiştirilir,
fontmake ile derlenir. Çıktı dist/Shimati/ ve dist/Shimati-<sürüm>.zip.

OFL 4. ve 2. madde: türev font özgün telif satırlarını ve lisansı taşımak zorunda; bunlar font
dosyalarının name tablosunda (ID 0) ve OFL.txt'de durur. Tanıtım sayfası ad vermez.
"""

import plistlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.ttLib.woff2 import compress

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "variants" / "uyarlanmis"
WORK = ROOT / "build" / "shimati-src"
DIST = ROOT / "dist"
OUT = DIST / "Shimati"
VENV = ROOT / ".venv" / "bin"

FAMILY = "Shimati"
VERSION = (1, 0)
VERSION_STR = f"{VERSION[0]}.{VERSION[1]:03d}"
AUTHOR = "Doruk Aktun"
COPYRIGHT = (
    f"Copyright 2026 {AUTHOR}. "
    "Contains glyphs from fonts Copyright 2015 The Sen Project Authors (https://github.com/philatype/Sen/) "
    "and Copyright 2016 The Inter Project Authors (https://github.com/rsms/inter)."
)
LICENSE = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
           "This license is available with a FAQ at: https://openfontlicense.org")
LICENSE_URL = "https://openfontlicense.org"
# Ağırlık ekseni: kullanıcı değeri → tasarım değeri (kaynak designspace'teki eşleme)
STYLES = [("Regular", 400, 400), ("Medium", 500, 500), ("SemiBold", 600, 600),
          ("Bold", 700, 650), ("ExtraBold", 800, 900)]
# cv08 için uygulamalarda görünen ad
CV08_LABEL = "Serifli I"


def set_info(ufo, style):
    p = ufo / "fontinfo.plist"
    info = plistlib.load(p.open("rb"))
    for k in ("openTypeNameDesignerURL", "openTypeNameManufacturerURL", "trademark",
              "openTypeNameUniqueID", "openTypeNameVersion", "styleMapFamilyName",
              "openTypeNamePreferredFamilyName", "openTypeNamePreferredSubfamilyName",
              "openTypeNameDescription", "openTypeNameRecords", "postscriptFullName",
              "macintoshFONDName", "openTypeHeadCreated"):
        info.pop(k, None)
    info.update(
        familyName=FAMILY, styleName=style, postscriptFontName=f"{FAMILY}-{style}",
        copyright=COPYRIGHT, openTypeNameDesigner=AUTHOR, openTypeNameManufacturer=AUTHOR,
        openTypeNameLicense=LICENSE, openTypeNameLicenseURL=LICENSE_URL,
        openTypeOS2VendorID="NONE", versionMajor=VERSION[0], versionMinor=VERSION[1],
    )
    plistlib.dump(info, p.open("wb"))


def label_cv08(ufo):
    fea = ufo / "features.fea"
    text = fea.read_text()
    if "cvParameters" not in text:
        text = text.replace("feature cv08 {\n",
                            "feature cv08 {\n  cvParameters {\n    FeatUILabelNameID {\n"
                            f'      name "{CV08_LABEL}";\n      name 3 1 0x041F "{CV08_LABEL}";\n'
                            "    };\n  };\n", 1)
        fea.write_text(text)


def designspace():
    labels = "\n".join(
        f'        <label uservalue="{u}" name="{s}"' + (' elidable="true"' if s == "Regular" else "") + "/>"
        for s, u, _ in STYLES)
    maps = "\n".join(f'      <map input="{u}" output="{d}"/>' for _, u, d in STYLES)
    instances = "\n".join(
        f'    <instance name="{FAMILY} {s}" familyname="{FAMILY}" stylename="{s}" '
        f'postscriptfontname="{FAMILY}-{s}" filename="instances/{FAMILY}-{s}.ufo"'
        + (f' stylemapfamilyname="{FAMILY}" stylemapstylename="{s.lower()}"' if s in ("Regular", "Bold") else "")
        + ">\n"
        f'      <location><dimension name="Weight" xvalue="{d}"/></location>\n    </instance>'
        for s, _, d in STYLES)
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<designspace format="5.0">
  <axes>
    <axis tag="wght" name="Weight" minimum="400" maximum="800" default="400">
{maps}
      <labels>
{labels}
      </labels>
    </axis>
  </axes>
  <sources>
    <source filename="{FAMILY}-Regular.ufo" name="{FAMILY} Regular" familyname="{FAMILY}" stylename="Regular">
      <location><dimension name="Weight" xvalue="400"/></location>
    </source>
    <source filename="{FAMILY}-ExtraBold.ufo" name="{FAMILY} ExtraBold" familyname="{FAMILY}" stylename="ExtraBold">
      <location><dimension name="Weight" xvalue="900"/></location>
    </source>
  </sources>
  <instances>
{instances}
  </instances>
</designspace>
"""


def fontmake(*args):
    subprocess.run([str(VENV / "fontmake"), "-m", str(WORK / f"{FAMILY}.designspace"), *args],
                   check=True, cwd=WORK)


def fix_regular_instance(path):
    """Elidable "Regular" etiketi fvar'daki Regular örneğinin adını boş bırakıyor; ID 2'yi kullan."""
    f = TTFont(path)
    name = f["name"]
    for inst in f["fvar"].instances:
        if not name.getDebugName(inst.subfamilyNameID):
            name.removeNames(nameID=inst.subfamilyNameID)
            inst.subfamilyNameID = 2
    f.save(path)


def woff2(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    compress(str(src), str(dst))


def check_names(path):
    """Ad tablosunda Shimati dışında aile adı kalmamalı (telif satırı hariç)."""
    f = TTFont(path)
    for n in f["name"].names:
        s = str(n)
        if n.nameID != 0 and ("Sen" in s.split() or "Inter" in s or "Deneme" in s or "Philatype" in s):
            sys.exit(f"{path.name}: name {n.nameID} hâlâ eski ad içeriyor: {s}")


CSS_VAR = """/* Shimati — değişken font (400–800). Bu dosyayı ve woff2'leri aynı klasöre koyun. */
@font-face {
  font-family: "Shimati";
  src: url("Shimati-Variable.woff2") format("woff2-variations"),
       url("Shimati-Variable.woff2") format("woff2");
  font-weight: 400 800;
  font-style: normal;
  font-display: swap;
}
"""


def css_static():
    out = ["/* Shimati — sabit ağırlıklar. Değişken font desteklenmeyen ortamlar için. */"]
    for s, u, _ in STYLES:
        out.append(f"""@font-face {{
  font-family: "Shimati";
  src: url("static/{FAMILY}-{s}.woff2") format("woff2");
  font-weight: {u};
  font-style: normal;
  font-display: swap;
}}""")
    return "\n".join(out) + "\n"


def ofl():
    body = (ROOT / "upstream" / "sen" / "OFL.txt").read_text()
    body = body[body.index("This Font Software is licensed"):]
    head = ("Copyright 2026 Doruk Aktun\n"
            "Copyright 2015 The Sen Project Authors (https://github.com/philatype/Sen/)\n"
            "Copyright 2016 The Inter Project Authors (https://github.com/rsms/inter)\n\n")
    return head + body


KURULUM = f"""# Shimati {VERSION_STR}

Made by Doruk Aktun. SIL Open Font License 1.1 (`OFL.txt`).

## Bilgisayara kurulum

- **macOS:** `desktop/` içindeki dosyaya çift tıklayın → *Yükle* (Font Book). Tüm ağırlıklar için
  `desktop/Shimati-Variable.ttf` yeterli; değişken fontu desteklemeyen uygulamalar için `desktop/otf/`.
- **Windows:** dosyaya sağ tıklayın → *Yükle* (ya da *Tüm kullanıcılar için yükle*).
- **Figma / tasarım araçları:** değişken TTF'i ya da `otf/` klasöründeki beş ağırlığı kurun.
- Aynı anda hem değişken hem sabit sürümü kurmayın; uygulamalar ikisini karıştırabilir.

| Dosya | Ne için |
| --- | --- |
| `desktop/Shimati-Variable.ttf` | Tek dosyada 400–800 arası tüm ağırlıklar |
| `desktop/otf/*.otf` | Regular, Medium, SemiBold, Bold, ExtraBold (baskı, eski uygulamalar) |
| `desktop/ttf/*.ttf` | Aynı beş ağırlık, TrueType (Windows ofis uygulamaları) |
| `web/Shimati-Variable.woff2` + `web/shimati.css` | Web sitesi, değişken |
| `web/static/*.woff2` + `web/shimati-static.css` | Web sitesi, sabit ağırlıklar |

## Web sitesine kurulum

`web/` klasörünü sitenize kopyalayın ve CSS'i bağlayın:

```html
<link rel="stylesheet" href="/fonts/shimati/shimati.css">
```

```css
body {{ font-family: "Shimati", system-ui, sans-serif; }}
h1 {{ font-weight: 800; }}
.serifli-i {{ font-feature-settings: "cv08"; }} /* serifli I seçeneği */
```

Hızlı yükleme için `<head>` içine:

```html
<link rel="preload" href="/fonts/shimati/Shimati-Variable.woff2" as="font" type="font/woff2" crossorigin>
```
"""


def main():
    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)
    for style in ("Regular", "ExtraBold"):
        dst = WORK / f"{FAMILY}-{style}.ufo"
        shutil.copytree(SRC / f"Sen-{style}.ufo", dst)
        set_info(dst, style)
        label_cv08(dst)
    (WORK / f"{FAMILY}.designspace").write_text(designspace())

    fontmake("-o", "variable", "--output-path", str(WORK / "out" / f"{FAMILY}-Variable.ttf"))
    fontmake("-i", "-o", "otf", "ttf", "--output-dir", str(WORK / "out" / "static"))

    shutil.rmtree(OUT, ignore_errors=True)
    (OUT / "desktop" / "otf").mkdir(parents=True)
    (OUT / "desktop" / "ttf").mkdir(parents=True)
    vf = OUT / "desktop" / f"{FAMILY}-Variable.ttf"
    shutil.copy(WORK / "out" / f"{FAMILY}-Variable.ttf", vf)
    fix_regular_instance(vf)
    for s, _, _ in STYLES:
        for ext in ("otf", "ttf"):
            shutil.copy(WORK / "out" / "static" / f"{FAMILY}-{s}.{ext}", OUT / "desktop" / ext)
        woff2(OUT / "desktop" / "ttf" / f"{FAMILY}-{s}.ttf", OUT / "web" / "static" / f"{FAMILY}-{s}.woff2")
    woff2(vf, OUT / "web" / f"{FAMILY}-Variable.woff2")
    (OUT / "web" / "shimati.css").write_text(CSS_VAR)
    (OUT / "web" / "shimati-static.css").write_text(css_static())
    (OUT / "OFL.txt").write_text(ofl())
    (OUT / "KURULUM.md").write_text(KURULUM)

    for p in sorted(OUT.rglob("*")):
        if p.suffix in (".ttf", ".otf"):
            check_names(p)

    z = DIST / f"{FAMILY}-{VERSION_STR}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(OUT.rglob("*")):
            if p.is_file() and p.name != ".DS_Store":
                zf.write(p, Path(FAMILY) / p.relative_to(OUT))
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            print(f"{p.stat().st_size:>8}  {p.relative_to(DIST)}")
    print(f"{z.stat().st_size:>8}  {z.relative_to(DIST)}")


if __name__ == "__main__":
    main()
