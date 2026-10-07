# Shimati

Doruk Aktun'un ilk yazı karakteri: arayüzler ve uzun metinler için değişken ağırlıklı (400–800), Türkçeye
özenle çizilmiş bir grotesk. Sürüm 1.000, SIL Open Font License 1.1.

- Kurulum dosyaları: [`dist/Shimati/`](dist/Shimati/KURULUM.md) — masaüstü (değişken TTF, 5 ağırlık OTF/TTF),
  web (WOFF2 + CSS); tek paket: `dist/Shimati-1.000.zip`
- Tanıtım sayfası: [`specimen/index.html`](specimen/index.html)
- Ad: Akkadca *šīmāti*, "kaderler"; Mezopotamya mitolojisindeki Kader Tableti'nden (*ṭuppi šīmāti*).

Aşağısı geliştirme notları: font, iki OFL fontun (Sen ve Inter) birleştirilip uyumlu hâle getirilmesiyle
betiklerle üretiliyor.

---

## Başlangıç: Inter'den a, e, I, ı, çengel, nokta ve kısa şapka → Sen

Inter 4.1'in `a`, `e`, `I`, `ı` gliflerini, çengelini (`Ç ç Ş ş Ţ ţ`), noktasını (`i j İ ċ ė ġ ż`) ve kısa şapkasını (`Ğ ğ Ă ă Ŭ ŭ`) Sen'in iki masterına (Regular 400, ExtraBold) uyarlama denemesi.
Her iki font da OFL-1.1, ayrılmış font adı yok; sonuç da OFL kalır.

## Çalıştırma

```bash
.venv/bin/python scripts/harmonize.py      # variants/dogrudan, variants/uyarlanmis + build/olcumler.json
.venv/bin/fontmake -m variants/uyarlanmis/Sen.designspace -o variable --output-path build/Sen-uyarlanmis-VF.ttf
.venv/bin/python scripts/proof.py          # proof/proof.html
.venv/bin/python scripts/ozet.py           # proof/ozet.html — Türkçe özet sayfası (başlık, paragraf, arayüz)
.venv/bin/python scripts/render_png.py "metin 1" "metin 2"   # proof/karsilastirma.png
```

## Shimati: dağıtım paketi ve tanıtım sayfası

Fontun çalışma adı **Shimati** (sürüm 1.000, Made by Doruk Aktun).

```bash
.venv/bin/python scripts/harmonize.py      # kaynakları üret (yukarıdaki gibi)
.venv/bin/python scripts/release.py        # dist/Shimati/ + dist/Shimati-1.000.zip
.venv/bin/python scripts/specimen.py       # specimen/index.html (tanıtım sayfası, font gömülü)
```

- `release.py`: `variants/uyarlanmis` → `build/shimati-src` (ad, telif, tasarımcı, sürüm, `cv08` için
  "Serifli I" etiketi, STAT etiketleri, Regular/Bold stil bağlantısı) → fontmake.
  Çıktı: `desktop/` (değişken TTF, 5 ağırlık OTF ve TTF), `web/` (WOFF2 + `shimati.css`,
  `shimati-static.css`), `OFL.txt`, `KURULUM.md`. Sabit dosyalar değişken fonttan en fazla 1 birim farklı.
- OFL gereği font dosyalarının telif satırı (name ID 0) ve `OFL.txt` kaynak fontların telif satırlarını
  taşır; ayrılmış font adı olmadığı için yeni ad serbest. Tanıtım sayfasında kaynak font adı geçmez
  (`specimen.py` bunu denetler).
- `specimen.py` + `specimen_template.html`: kahraman, karakter, deneme alanı, ağırlıklar, yapı çizimleri
  (ölçü çizgileri, noktalar, tutamaçlar, gövde/taşma/çengel ölçüleri, iki master arasında interpole eden
  ağırlık kaydırıcısı), ağırlık ekseni çizimi, ölçü tablosu, glif inceleyici, Türkçe, ölçek, arayüz,
  OpenType (cv08, frac, sups), indirme. Açık/koyu tema; mobilde yatay taşma yok.
- Proje hafızasının yedeği: `docs/hafiza/`.

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
  (90 / 187, 82 / 172), sol boşluk `H` / `n`'nin sol boşluğuna, sağ boşluk sağ boşluğuna eşitlenir
  (Inter'de oran 1:1; Sen `n`'nin sağı solundan dar, 70 / 85, bu yüzden "ın" artık "nn" kadar sıkı). Sonuç: Sen'in
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
- `J` ve `j` (`build_j`): `J` Inter'in taban çizgisine oturan çanaklı biçimi; gövde ve alt kalınlık Sen `U`'suna,
  genişlik Sen `U` × (Inter `J`/`U`), boşluklar Inter'deki `J`/`U` oranıyla. `ȷ` gövde ve boşlukta Sen `n`'sine
  (`ı` gibi bayraksız), kuyruk kalınlığı `a` ile aynı kuralla; taban altı noktalar topluca Sen `p`'nin alt ucuna
  (−240) kaydırılır, aradaki düz gövde uzar. `Ŋ` eski `J`'yi kanca olarak kullandığı için önce konturlara
  çevrilir (Sen'in kancası kalır). `j`'nin noktası gövdenin ortasına alınır.
- `J`/`j` kerning'i: Sen'in eski `J`'si bambaşka bir şekil olduğu için referans olamaz; Inter'in kendi çiftleri
  HarfBuzz ile ölçülüp `J`'nin x ağırlığına interpole edilir ve ölçeklenir (`kerning.inter_pairs`). Sen'in
  harflerine karşı çarpışma kontrolü `U` / `ı` çiftlerine göre (ör. ExtraBold `P J` −95 → −35).
- Daraltma (`scripts/condense.py`, en sonda): her masterın x koordinatları Regular–ExtraBold arasında
  biraz daha kalın bir ağırlıktan alınıp ölçeklenir, y'ler aynı kalır. Ağırlık ve ölçek, `n` gövdesi aynı
  kalacak ve küçük harflerin ortalama genişliği Sen'in orijinaline göre `CONDENSE` (0.92) oranına inecek
  şekilde çözülür (referans sabit, tek bir harf değişince oran kaymaz)
  (Regular: x ağırlığı ≈ 443, ölçek 0.915; ExtraBold: ≈ 996 yani ExtraBold'un %19 ötesi, ölçek 0.908).
  Bileşen ofsetleri, çapalar ve kerning de aynı dönüşümle; bağımsız noktalar (i, j, ., ¨, ˙, ÷) yuvarlak
  kalsın diye yalnızca taşınır.
  Kaynak masterda aynı x'te duran ardışık noktalar (dikey kenarlar, dikey teğetler) daraltmadan sonra
  yeniden hizalanır (`_keep_verticals`): hiza, iki master arasında en az yer değiştiren noktaya (gerçek kenar)
  yapılır, ortalamaya değil (ortalama G'nin gövdesini inceltip kuyruktaki içe dönüşü kaybettiriyordu); yoksa ExtraBold'un ötesine taşan x ağırlığında, iki masterda farklı
  dizilmiş noktalar ayrışıp ExtraBold `G`'nin kolunda basamak açıyordu (etkilenen: `G`, `d`, `q`).
- Aralık (`TRACKING`): Regular'da her yan boşluktan 8 birim çıkarılır; ExtraBold'da daraltma aralığı
  zaten yeterince kıstığı için 0.
- PNG proof'ları HarfBuzz + FreeType ile dizilir (`scripts/hbrender.py`), yani kerning görünür.

## Çözülen açık konular (6 Ekim 2026)

- **`₺`** eklendi (`build_lira`): Inter'den; gövde Sen `L`'sine, alt kavis `U`'suna; ölçek Sen/Inter rakam
  oranından; genişlik Sen'in tablo rakamlarınınki (550 / 600), mürekkep ortalı.
- **`I` / `l` / `1` ayrımı**: varsayılan düz `I` kalır; Sen'in orijinal serifli `I`'sı (ve `Í Î Ï İ Ì Ī Į`)
  `.cv08` olarak eklendi, `cv08` özelliğiyle açılır (Inter'deki gibi). CSS: `font-feature-settings: 'cv08'`.
- **`Ŋ ŋ`** (`build_eng_tails`): Sen'in `N`/`n` gövdesi korunur, kanca yeni `j`'nin kuyruğu (Inter `ȷ`), aynı
  gövde genişliği ve alt uzantı. (Inter'in kendi `Ŋ`'si Regular/Black arasında nokta-uyumsuz.)
- **`e` / `æ` kuyruğu (ExtraBold)**: kesik çok yatıktı (8.6° / 0.7°), kuyruğun üstü çubuğun altında uzun bir
  yarık yapıyordu. İç uç sabit, dış kenar kısaltılarak kesik 30°'ye dikleştirildi (`steepen_terminal`).
  Regular'a (14.7°) dokunulmadı.
- **`æ` tepe çentiği**: Regular 81, ExtraBold 46 birim derinlikteki V, 25 birime indirildi (yalnızca çukur
  noktası kalkar, kontrol noktaları yerinde; yoksa tepe çizgisini aşan tümsek oluşuyor).
- **ExtraBold `a`'nın alt kasesi**: yatay çizgiler Sen `o`'su (165) yerine Sen `e`'sine (142) eşitlendi;
  Inter y ağırlığı 1122 → 940, kasenin içi ~68 → ~91 birim. Regular değişmedi (o ve e aynı: 80).
- **Kerning denetimi** (`scripts/kern_audit.py`): Regular'daki aralık sıkıştırma çapraz harfleri (AA, vv, XX)
  değecek kadar yaklaştırıyordu; ExtraBold'da `c a`, `s a`, `Q j` çarpışıyordu. Son adımda çarpışma koruması
  (`kerning.collision_guard`): en dar boşluk Sen'dekinin %60'ının altına inerse yalnızca o kadar pozitif
  kerning (çoğu +5/+10). Şekli değişen `I ı i J j` için eski boşluk referans olamaz, mutlak alt sınır 0.03 em.

## Açık konular

- Gerçek arayüz metinlerinde (küçük boyut, ekran) gözle kontrol.
- Karar: varsayılan düz `I`/`ı` kalacak (konu kapandı).
