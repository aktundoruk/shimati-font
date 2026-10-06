"""Gelinen noktanın Türkçe özet sayfası: başlıklar, paragraflar, arayüz örneği, karşılaştırma.

proof/ozet.html — fontlar sayfaya gömülü, tek dosya. Üstteki düğmeyle tüm sayfa Sen orijinal ile
yeni hâl arasında değişir; kaydırıcı ağırlığı (400–800) değiştirir.
"""

import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def face(name, file):
    data = base64.b64encode((ROOT / "build" / file).read_bytes()).decode()
    return (f"@font-face{{font-family:'{name}';src:url(data:font/ttf;base64,{data}) format('truetype');"
            "font-weight:400 800;}")


PARA_1 = (
    "İyi bir yazı karakteri, okuru yormadan geri çekilmeyi bilir. Arayüzde her gün binlerce kez "
    "görülecek harflerin tek tek ne kadar güzel olduğundan çok, birbirleriyle nasıl anlaştıkları önemlidir: "
    "a ile e aynı ritimde nefes almalı, ı ile i aynı sessizlikte durmalı, ş ile ç kuyruklarıyla satırın "
    "altına taşmadan Türkçeyi rahatça taşıyabilmeli."
)
PARA_2 = (
    "Pijamalı hasta yağız şoföre çabucak güvendi. Jale, Japonya’dan dönerken jöle ve reçel almıştı. Öğleden sonra İstanbul’da ılık bir rüzgâr esiyordu; "
    "Çağla ile Işıl, Üsküdar iskelesinde çaylarını içip şehrin ışıklarını izlediler. Saat 18.45’te "
    "vapur kalktığında, 2.350 ₺’lik hesabın 1.175 ₺’sini ödemişlerdi bile."
)
CHANGES = [
    ("a, e, æ, ª", "Inter’den; Sen’in genişlik, kalınlık ve boşluk sistemine uyarlandı. a’nın ucu Sen gibi dik kesik, e’ninki Inter’in açılı ucu."),
    ("I, ı, i", "Inter gibi düz çubuk: I’nın serifleri ve ı/i’nin bayrağı kalktı. ı’nın sağ boşluğu n’ninkine eşitlendi."),
    ("Ç ç Ş ş", "Sen’in C S c s’si korundu; çengel Inter’den, daha kısa (240 → 187 birim)."),
    ("J, j", "Inter’den: J taban çizgisine oturan çanaklı biçim, j bayraksız ve kuyruğu Sen’in alt uzantısına iniyor. Kerning Inter’in kendi J/j çiftlerinden."),
    ("i j İ noktası", "Inter’in oranında, daha küçük; Sen’deki iki farklı nokta tek noktaya indi."),
    ("Ğ ğ", "Kısa şapka Inter’den: daha ince ve narin."),
    ("Genişlik", "Tüm harfler gövde kalınlığı korunarak %8 daraltıldı; Regular’da aralık her yandan 8 birim sıkıştırıldı."),
]


def main():
    faces = face("Orijinal", "Sen-orijinal-VF.ttf") + face("Yeni", "Sen-uyarlanmis-VF.ttf")
    changes = "".join(f"<li><b>{k}</b><span>{v}</span></li>" for k, v in CHANGES)
    doc = f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sen Türevi Özet</title>
<style>
{faces}
:root{{--bg:#f7f5f0;--fg:#1b1a17;--muted:#77736a;--line:#e2ded4;--card:#fffefb;--accent:#c4451c;--accent-fg:#fff;--soft:#efe9dd;
  --font:'Yeni';--w:400}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#151513;--fg:#ecebe6;--muted:#9b978d;--line:#2d2c28;--card:#1d1d1a;--accent:#f0794f;--accent-fg:#1b1a17;--soft:#25241f}}}}
:root[data-theme="dark"]{{--bg:#151513;--fg:#ecebe6;--muted:#9b978d;--line:#2d2c28;--card:#1d1d1a;--accent:#f0794f;--accent-fg:#1b1a17;--soft:#25241f}}
*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:var(--bg);color:var(--fg);font-family:var(--font),system-ui,sans-serif;
  font-variation-settings:'wght' var(--w);line-height:1.5}}
.f{{font-family:var(--font)}}
.sys{{font-family:-apple-system,system-ui,sans-serif;font-variation-settings:normal}}
main{{max-width:1120px;margin:0 auto;padding:0 16px 96px}}
.bar{{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(8px);
  border-bottom:1px solid var(--line);margin:0 -16px;padding:10px 16px;display:flex;gap:14px;align-items:center;flex-wrap:wrap}}
.seg{{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:3px;background:var(--card)}}
.seg button{{border:0;background:transparent;color:var(--muted);padding:6px 14px;border-radius:999px;cursor:pointer;font:inherit;font-size:13px}}
.seg button[aria-pressed="true"]{{background:var(--fg);color:var(--bg)}}
.bar label{{font-size:13px;color:var(--muted)}}
.bar input[type=range]{{width:min(220px,40vw);accent-color:var(--accent)}}
.bar output{{font-size:13px;font-variant-numeric:tabular-nums;min-width:3ch}}
.hero{{padding:56px 0 32px;border-bottom:1px solid var(--line)}}
.eyebrow{{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin:0 0 12px}}
.hero h1{{font-size:clamp(44px,9vw,104px);line-height:1;margin:0;font-variation-settings:'wght' calc(var(--w) + 300);letter-spacing:-.01em}}
.hero p{{font-size:clamp(18px,2.4vw,24px);color:var(--muted);max-width:760px;margin:20px 0 0}}
section{{padding:44px 0;border-bottom:1px solid var(--line)}}
.sec-title{{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 22px}}
.scale>div{{display:grid;grid-template-columns:110px 1fr;gap:16px;align-items:baseline;padding:10px 0;border-top:1px dashed var(--line)}}
.scale>div:first-child{{border-top:0}}
.scale small{{color:var(--muted);font-size:12px}}
.scale .t1{{font-size:56px;line-height:1.08;font-variation-settings:'wght' calc(var(--w) + 300)}}
.scale .t2{{font-size:36px;line-height:1.15;font-variation-settings:'wght' calc(var(--w) + 200)}}
.scale .t3{{font-size:24px;line-height:1.25;font-variation-settings:'wght' calc(var(--w) + 100)}}
.scale .t4{{font-size:17px}} .scale .t5{{font-size:13px;color:var(--muted)}}
.article{{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:48px}}
.article h2{{font-size:clamp(30px,4.4vw,44px);line-height:1.12;margin:0 0 14px;font-variation-settings:'wght' calc(var(--w) + 300)}}
.article .lead{{font-size:21px;line-height:1.45;margin:0 0 18px;color:var(--fg)}}
.article p{{font-size:17px;margin:0 0 14px;max-width:66ch}}
.article b{{font-variation-settings:'wght' calc(var(--w) + 300);font-weight:normal}}
aside.note{{background:var(--soft);border-radius:14px;padding:20px;font-size:15px;align-self:start}}
aside.note h3{{margin:0 0 8px;font-size:18px;font-variation-settings:'wght' calc(var(--w) + 200)}}
.ui{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px}}
.card h4{{margin:0 0 4px;font-size:20px;font-variation-settings:'wght' calc(var(--w) + 200)}}
.card .sub{{color:var(--muted);font-size:14px;margin:0 0 18px}}
.field{{display:block;margin:0 0 14px}}
.field span{{display:block;font-size:13px;margin:0 0 6px;font-variation-settings:'wght' calc(var(--w) + 100)}}
.field input{{width:100%;font:inherit;font-family:var(--font);font-size:15px;padding:10px 12px;border-radius:10px;border:1px solid var(--line);
  background:var(--bg);color:var(--fg);font-variation-settings:'wght' var(--w)}}
.btns{{display:flex;gap:10px;flex-wrap:wrap;margin-top:6px}}
.btn{{font:inherit;font-family:var(--font);font-size:15px;padding:10px 18px;border-radius:10px;border:1px solid var(--line);background:transparent;color:var(--fg);
  cursor:pointer;font-variation-settings:'wght' calc(var(--w) + 200)}}
.btn.primary{{background:var(--accent);border-color:var(--accent);color:var(--accent-fg)}}
.list{{list-style:none;margin:0;padding:0}}
.list li{{display:flex;justify-content:space-between;gap:12px;padding:11px 0;border-top:1px solid var(--line);font-size:15px}}
.list li:first-child{{border-top:0}}
.num{{font-variant-numeric:tabular-nums;font-variation-settings:'wght' calc(var(--w) + 200)}}
.badge{{display:inline-block;font-size:12px;padding:2px 9px;border-radius:999px;background:var(--soft);color:var(--muted);margin-left:8px}}
.tabs{{display:flex;gap:18px;border-bottom:1px solid var(--line);margin:0 0 16px;font-size:15px;overflow-x:auto}}
.tabs span{{padding:0 0 10px;color:var(--muted);white-space:nowrap}}
.tabs span.on{{color:var(--fg);border-bottom:2px solid var(--accent);font-variation-settings:'wght' calc(var(--w) + 200)}}
.glyphs{{font-size:clamp(40px,8vw,88px);line-height:1.15;letter-spacing:.02em;word-break:break-word}}
.glyphs .lc{{display:block}}
.pangram{{font-size:clamp(22px,3.4vw,34px);margin:18px 0 0}}
.compare{{display:grid;grid-template-columns:1fr 1fr;gap:28px}}
.compare .col p{{font-size:17px;margin:8px 0 0}}
.compare .col h3{{font-size:30px;line-height:1.15;margin:6px 0 0;font-variation-settings:'wght' calc(var(--w) + 300)}}
.tag{{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}}
.o{{font-family:'Orijinal'}} .y{{font-family:'Yeni'}}
.changes{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px 28px}}
.changes li{{display:grid;grid-template-columns:120px 1fr;gap:12px;padding:12px 0;border-top:1px solid var(--line);font-size:15px}}
.changes b{{font-variation-settings:'wght' 700;font-weight:normal}}
.changes span{{color:var(--muted)}}
@media (max-width:760px){{.article,.compare{{grid-template-columns:1fr}}.scale>div{{grid-template-columns:1fr;gap:2px}}
  .scale .t1{{font-size:40px}}.changes li{{grid-template-columns:1fr;gap:2px}}}}
</style></head><body><main>
<div class="bar sys">
  <div class="seg" role="group" aria-label="Font">
    <button data-font="Yeni" aria-pressed="true">Yeni</button><button data-font="Orijinal" aria-pressed="false">Sen orijinal</button>
  </div>
  <label for="w">Ağırlık</label><input id="w" type="range" min="400" max="800" step="1" value="400"><output id="wv">400</output>
  <div class="seg" role="group" aria-label="Tema">
    <button data-theme="light" aria-pressed="false">Açık</button><button data-theme="dark" aria-pressed="false">Koyu</button>
  </div>
</div>

<header class="hero">
  <p class="eyebrow">Sen türevi · çalışma sürümü</p>
  <h1>Harfler artık aynı dili konuşuyor.</h1>
  <p>Sen’in karakterini koruyup Inter’den aldığımız harflerle yeniden dengelenmiş, Türkçe için ayarlanmış bir arayüz yazı karakteri.</p>
</header>

<section>
  <p class="sec-title">Başlık hiyerarşisi</p>
  <div class="scale">
    <div><small>Başlık 1 · 56</small><span class="t1">Güçlü ve sakin bir ses</span></div>
    <div><small>Başlık 2 · 36</small><span class="t2">Ürün ayarlarını düzenleyin</span></div>
    <div><small>Başlık 3 · 24</small><span class="t3">Ödeme yöntemi ve fatura bilgileri</span></div>
    <div><small>Gövde · 17</small><span class="t4">Değişiklikleriniz kaydedildi. Ekibinizdeki herkes yeni sürümü hemen görebilir.</span></div>
    <div><small>Açıklama · 13</small><span class="t5">Son güncelleme: 6 Ekim 2026, 21.08 · Çağrı Işık tarafından</span></div>
  </div>
</section>

<section>
  <p class="sec-title">Makale</p>
  <div class="article">
    <div>
      <h2>Yazı karakteri, arayüzün sesidir</h2>
      <p class="lead">Kullanıcı bir düğmeyi okumadan önce onun tonunu duyar. Harflerin genişliği, aralığı ve ritmi bu tonu belirler.</p>
      <p>{PARA_1}</p>
      <p>{PARA_2} <b>Kalın vurgular</b> da aynı ailenin içinden gelir; ağırlık kaydırıcısıyla deneyin.</p>
    </div>
    <aside class="note">
      <h3>Neden daralttık?</h3>
      <p>Sen geniş ve havadar bir yazı. Arayüzde, dar sütunlarda ve tablolarda daha fazla metin sığsın diye harfleri gövde kalınlığını bozmadan %8 daralttık.</p>
      <p style="margin:0">Satırlar kısaldı, ama ı ve i’nin çevresi hâlâ nefes alıyor.</p>
    </aside>
  </div>
</section>

<section>
  <p class="sec-title">Arayüz</p>
  <div class="ui">
    <div class="card">
      <div class="tabs"><span class="on">Genel</span><span>Güvenlik</span><span>Bildirimler</span><span>Faturalar</span></div>
      <h4>Hesap bilgileri</h4><p class="sub">Bu bilgiler yalnızca sizin ve yöneticinizin göreceği şekilde saklanır.</p>
      <label class="field"><span>Ad soyad</span><input value="Şükrü Ağaoğlu"></label>
      <label class="field"><span>E-posta adresi</span><input placeholder="ornek@sirket.com.tr"></label>
      <div class="btns"><button class="btn primary">Değişiklikleri kaydet</button><button class="btn">İptal</button></div>
    </div>
    <div class="card">
      <h4>Son işlemler <span class="badge">Bu ay</span></h4><p class="sub">Ekim 2026 · 4 işlem</p>
      <ul class="list">
        <li><span>Çiçekçi Gülşen</span><span class="num">−245,00 ₺</span></li>
        <li><span>Iğdır Kargo</span><span class="num">−1.180,50 ₺</span></li>
        <li><span>İade · Öğle yemeği</span><span class="num">+312,75 ₺</span></li>
        <li><span>Şişli Otopark</span><span class="num">−96,00 ₺</span></li>
      </ul>
    </div>
  </div>
</section>

<section>
  <p class="sec-title">Türkçe karakterler</p>
  <div class="glyphs"><span class="lc">ÇĞIİÖŞÜ</span><span class="lc">çğıiöşü</span></div>
  <p class="pangram">Pijamalı hasta yağız şoföre çabucak güvendi.</p>
</section>

<section>
  <p class="sec-title">Yan yana karşılaştırma</p>
  <div class="compare">
    <div class="col o"><span class="tag sys">Sen orijinal</span><h3>Işıklı İstanbul akşamı</h3><p>{PARA_2}</p></div>
    <div class="col y"><span class="tag sys">Yeni</span><h3>Işıklı İstanbul akşamı</h3><p>{PARA_2}</p></div>
  </div>
</section>

<section style="border-bottom:0">
  <p class="sec-title">Şimdiye kadar değişenler</p>
  <ul class="changes">{changes}</ul>
</section>
</main>
<script>
const root=document.documentElement,r=document.getElementById('w'),o=document.getElementById('wv');
r.addEventListener('input',e=>{{root.style.setProperty('--w',e.target.value);o.textContent=e.target.value}});
document.querySelectorAll('button[data-font]').forEach(b=>b.addEventListener('click',()=>{{
  root.style.setProperty('--font',"'"+b.dataset.font+"'");
  document.querySelectorAll('button[data-font]').forEach(x=>x.setAttribute('aria-pressed',x===b))}}));
document.querySelectorAll('button[data-theme]').forEach(b=>b.addEventListener('click',()=>{{
  const on=b.getAttribute('aria-pressed')!=='true';
  document.querySelectorAll('button[data-theme]').forEach(x=>x.setAttribute('aria-pressed','false'));
  if(on){{root.dataset.theme=b.dataset.theme;b.setAttribute('aria-pressed','true')}}else delete root.dataset.theme}}));
</script></body></html>"""
    (ROOT / "proof/ozet.html").write_text(doc)
    print("proof/ozet.html", len(doc) // 1024, "KB")


if __name__ == "__main__":
    main()
