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
- Yatay kalınlık: `a` için Inter `o` üst kalınlığı Sen `o`'suna; `e` için Inter `e` üst kalınlığı Sen'in kendi
  `e`'sine eşitlenir (Sen'in ExtraBold `e`'si `o`'sundan ince: 142 / 165, aksi hâlde `e`'nin ağzı kapanıyor).
- Overshoot: Inter'in taşma payları Sen `o`'sununkilere eşlenir.
- Boşluk: Inter'in a/e ile o/n arasındaki oranları, Sen'in o/n değerlerine uygulanır.
- Aksanlı harfler ve `œ` yeni çapalara/genişliklere göre yeniden konumlandırılır.
- Terminaller (`scripts/terminals.py`): yalnızca üst uçlar (`a`, `æ`, `ª`'nın kemeri) Sen gibi dik kesilir;
  `e` Inter'in orijinal açılı ucuyla kalır (`CUT_TERMINALS`). Dik kesimde önce Sen'deki kadar kısa
  kesim konumu bulunur (kesik ≤ 1.25 × Sen'in `c`/`e` kesiği); `TERMINAL_LENGTH` (Regular 0.5,
  ExtraBold 0.25) kesimi bu konumdan Inter'in orijinal uç noktasına doğru kaydırır. İç kenar, dış
  kenarın yönü ile kendi yönünün ortasına göre yeniden kurulur.
- `æ` artık bileşik değil: Inter'in kendi `æ`'si a/e parametreleriyle uyarlanır (ExtraBold'da y
  ekstrapolasyonu 1.2 ile sınırlı, yoksa a ile e arasındaki boşluklar kapanıyor).
- `ª`: Inter `º` → Sen `º` dönüşümü bulunur, aynısı Inter `ª`'ya uygulanır.
- Boşluk düzeltmesi (`respace`): a/e/æ'nin nötr harflerle (`n o i l H O`) optik boşluğu, Sen'in
  eski a/e'sininkine eşitlenir (ortanca fark, ≥5 birimse).
- Kerning (`scripts/kerning.py`): x-height bölgesinde derinliği kırpılmış ortalama boşluk eski
  glifle eşitlenir. Sıkıştırma serbest; gevşetme yalnızca gerçek çarpışmada (en dar boşluk
  eskisinin %60'ının altına inerse) ve onu giderecek kadar. Yeni çift yalnızca |değer| ≥ 30 ise eklenir.
- PNG proof'ları HarfBuzz + FreeType ile dizilir (`scripts/hbrender.py`), yani kerning görünür.

## Açık konular

- **`e`'nin ağzı**: Sen'inkinden ~%25 kapalı (Regular 80 / 108, ExtraBold 47 / 66 birim). ExtraBold'da açılı
  kesik orta çizgiye paralel uzandığı için büyük boyutta yarık gibi görünüyor.
- **æ tepe birleşimi**: Inter'in tasarımından gelen küçük V çentiği ExtraBold'da belirgin.
- **ExtraBold yatay kalınlık**: Sen'e eşitlemek için Inter Black'in ötesine ~%45 ekstrapolasyon gerekti (y ağırlığı ≈1122).
  `a`'nın alt iç boşluğu bu yüzden dar.
- **Kerning gözden geçirme**: otomatik çiftler (`build/olcumler.json` → `kerning`)
  gerçek metinde kontrol edilmeli.
