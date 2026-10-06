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
- Aksanlı harfler ve `æ`, `œ` yeni çapalara/genişliklere göre yeniden konumlandırılır.

## Açık konular

- **æ**: bileşik (a + e) yapı çift katlı `a` ile çalışmıyor; `a`'nın gövde ucu taban çizgisinde görünüyor. Elle çizilmeli.
- **Terminaller**: Inter'in `a`/`e` uçları açılı kesik, Sen'in uçları dik kesik. Karakter farkının çoğu buradan geliyor.
- **ExtraBold yatay kalınlık**: Sen'e eşitlemek için Inter Black'in ötesine ~%45 ekstrapolasyon gerekti (y ağırlığı ≈1122).
  `a`'nın alt iç boşluğu bu yüzden dar.
- **ª** (ordfeminine) ayrı çizilmiş, hâlâ eski tek katlı `a`.
- **Kerning**: `R a`, `v a`, `k e` gibi glife özel çiftler eski şekillere göre; gözden geçirilmeli.
