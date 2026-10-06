# Deneme: Inter'den a, e, I, ı, çengel, nokta ve kısa şapka → Sen

Inter 4.1'in `a`, `e`, `I`, `ı` gliflerini, çengelini (`Ç ç Ş ş Ţ ţ`), noktasını (`i j İ ċ ė ġ ż`) ve kısa şapkasını (`Ğ ğ Ă ă Ŭ ŭ`) Sen'in iki masterına (Regular 400, ExtraBold) uyarlama denemesi.
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
- `I` ve `ı` (`build_straight`): Inter'de ikisi de düz dikdörtgen. Gövde Sen'in `H` / `n` gövdesine
  (90 / 187, 82 / 172), boşluklar `H` / `n`'nin sol boşluğuna eşitlenir (Inter'de oran 1:1). Sonuç: Sen'in
  `I` serifleri ve `ı` bayrağı kalkar; yeni `ı` Sen'in `l`'sinin x-height'te kesilmiş hâli olur.
  `i`, `ı` + nokta olduğu için o da bayraksız olur; nokta gövdenin ortasına alınır. `İ`, `í`, `į`, `Į`, `ij`,
  `IJ` vb. bileşikler çapalara göre yeniden kurulur (aksanların dikey konumu Sen'deki gibi kalır).
- `I`/`ı`/`i` içeren kerning çiftleri aynı profildeki harfin çiftine eşitlenir (`I` → `H`, sağda `ı`/`i` → `n`,
  solda → `l`); karşılığı yoksa silinir (`I C`, `I O`, ExtraBold `K i`). a/e kerning'i yeni `I`/`ı` ile ölçülür.
- Çengel (`build_cedilla`): Sen'in `C S c s T t` harfleri aynen kalır, yalnızca ortak `cedillacomb`
  Inter'in çengeliyle değişir. Inter'in şekli ve boyu (taban çizgisi altı 240 → 187 / 191), Sen'in kalınlığı
  (boyun genişliği x ağırlığıyla, kase alt kalınlığı y ağırlığıyla Sen'in çengeline eşitlenir) ve Sen'in
  bağlanma noktası (boyun ortası aynı `_bottom` çapasına). ExtraBold'da kase için Inter Black'in ötesine
  y ≈ 2.1 ekstrapolasyon gerekiyor (`CEDILLA_TY_CAP` = 2.2). Inter'in Regular'ında boyunda bir köşe
  noktası eksik; `_match_ops` doğruyu bölerek nokta yapısını Black'e eşitler.
- Nokta ve kısa şapka (`build_marks`): `dotaccentcomb`, `brevecomb` ve `i`/`j`'nin kendi noktaları
  Inter'den. Ağırlık, Inter `n` gövdesinin Sen `n` gövdesine eşit olduğu ağırlık (Inter'in harf/aksan oranı
  korunur, bu yüzden Sen'inkinden küçük/ince); x-height üstündeki boşluk Inter'deki gibi ölçeklenir; aksanlar
  eski çapanın üstüne ortalanır, `i`'nin noktası gövdenin ortasına. Sen'de `i`'nin noktası (136 / 215) ile
  nokta aksanı (126 / 152; Türkçe `i` ve `İ` bunu kullanıyor) farklıydı, artık tek nokta (112 / 174).
  ExtraBold'da `İ` noktası bu yüzden biraz büyüdü (152 → 174), `i`'ninki küçüldü (215 → 174).
- PNG proof'ları HarfBuzz + FreeType ile dizilir (`scripts/hbrender.py`), yani kerning görünür.

## Açık konular

- **`I` / `l` / `1` ayrımı**: `I` ve `l` artık ikisi de düz çubuk, yalnızca boyları farklı (670 / 720).
  Arayüzde (kodlar, şifreler, "Il") karışabilir. Inter bu yüzden serifli `I` seçeneği sunuyor (cv08).
- **`j` hâlâ bayraklı**: Sen'in `j`'si (ve `ij`'deki `j`) sol üst bayrağını koruyor; bayraksız `i` ile tutarlı
  olması için `j` de Inter'den alınabilir.

- **`e`'nin ağzı**: Sen'inkinden ~%25 kapalı (Regular 80 / 108, ExtraBold 47 / 66 birim). ExtraBold'da açılı
  kesik orta çizgiye paralel uzandığı için büyük boyutta yarık gibi görünüyor.
- **æ tepe birleşimi**: Inter'in tasarımından gelen küçük V çentiği ExtraBold'da belirgin.
- **ExtraBold yatay kalınlık**: Sen'e eşitlemek için Inter Black'in ötesine ~%45 ekstrapolasyon gerekti (y ağırlığı ≈1122).
  `a`'nın alt iç boşluğu bu yüzden dar.
- **Kerning gözden geçirme**: otomatik çiftler (`build/olcumler.json` → `kerning`)
  gerçek metinde kontrol edilmeli.
