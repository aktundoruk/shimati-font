# Deneme: Inter'in a ve e'si → Sen

Inter 4.1'in küçük `a` ve `e` gliflerini Sen'in iki masterına (Regular 400, ExtraBold) uyarlama denemesi.
Her iki font da OFL-1.1, ayrılmış font adı yok; sonuç da OFL kalır.

## Çalıştırma

```bash
.venv/bin/python scripts/harmonize.py      # variants/dogrudan, variants/uyarlanmis + build/olcumler.json
.venv/bin/fontmake -m variants/uyarlanmis/Sen.designspace -o variable --output-path build/Sen-uyarlanmis-VF.ttf
.venv/bin/python scripts/proof.py          # proof/proof.html
.venv/bin/python scripts/render_png.py "metin 1" "metin 2"   # proof/karsilastirma.png
```

## Yöntem (uyarlanmış varyant)

- Inter Regular→Black aralığı nokta nokta doğrusal (sapma < 2/2048), bu yüzden x ve y koordinatları
  ayrı ağırlıklardan alınabiliyor (anizotropik interpolasyon).
- Dikey ölçek: Inter x-height'i (1118) Sen x-height'ine (500 / 510).
- Genişlik: `e` → Sen'in kendi `e` genişliği; `a` → Sen `n` genişliği × Inter'deki a/n oranı.
- Dikey kalınlık: `a` gövdesi Sen `n` gövdesine, `e` yan kalınlığı Sen `o` yanına eşit.
- Yatay kalınlık: Inter `o` üst kalınlığı Sen `o` üst kalınlığına eşit; a/e Inter'in kendi oranlarını korur.
- Overshoot: Inter'in taşma payları Sen `o`'sununkilere eşlenir.
- Boşluk: Inter'in a/e ile o/n arasındaki oranları, Sen'in o/n değerlerine uygulanır.
- Aksanlı harfler ve `œ` yeni çapalara/genişliklere göre yeniden konumlandırılır.
- Terminaller Sen gibi dik kesilir (`scripts/terminals.py`). Regular'da kesik uzunluğu Sen'in `c`/`e`
  kesiğinin en fazla 1.25 katı; ExtraBold'da kesim yeri Regular'daki göreli konumdan alınır, iç kenar
  dış kenara paralel uzatılır.
- `æ` artık bileşik değil: Inter'in kendi `æ`'si a/e parametreleriyle uyarlanır (ExtraBold'da y
  ekstrapolasyonu 1.2 ile sınırlı, yoksa a ile e arasındaki boşluklar kapanıyor).
- `ª`: Inter `º` → Sen `º` dönüşümü bulunur, aynısı Inter `ª`'ya uygulanır.

## Açık konular

- **ExtraBold terminal iç kenarı**: `a` ve `e`'de dik kesiğin hemen içinde hafif düz bir bölge var; büyük boyutta göz ayarı gerekebilir.
- **æ tepe birleşimi**: Inter'in tasarımından gelen küçük V çentiği ExtraBold'da belirgin.
- **ExtraBold yatay kalınlık**: Sen'e eşitlemek için Inter Black'in ötesine ~%45 ekstrapolasyon gerekti (y ağırlığı ≈1122).
  `a`'nın alt iç boşluğu bu yüzden dar.
- **Kerning**: `R a`, `v a`, `k e` gibi glife özel çiftler eski şekillere göre; gözden geçirilmeli.
