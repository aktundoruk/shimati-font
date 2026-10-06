# Shimati 1.000

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
body { font-family: "Shimati", system-ui, sans-serif; }
h1 { font-weight: 800; }
.serifli-i { font-feature-settings: "cv08"; } /* serifli I seçeneği */
```

Hızlı yükleme için `<head>` içine:

```html
<link rel="preload" href="/fonts/shimati/Shimati-Variable.woff2" as="font" type="font/woff2" crossorigin>
```
