# ATLAS — Yerel C++ & Tersine Mühendislik AI Ajanı

Tamamen senin bilgisayarında (offline) çalışan, projeni ve seni **kalıcı olarak hatırlayan** kodlama ajanı.
**Uygulama sürümü: v0.3.2** (ATLAS → sürüm; build parmak izi uygulama durumunda görünür).
Donanımına göre ayarlandı: **RTX 4060 8 GB · 32 GB RAM · Ryzen 7 5700X · Windows 10**.

## 🚀 Kurulum (tek tık)

1. Klasörü bir yere çıkar (ör. `C:\AtlasAgent`). Yolda Türkçe karakter/boşluk olmaması önerilir.
2. **`KUR.bat`**'a çift tıkla. Şunları otomatik yapar:
   - Python 3.12 (uyumlu sürüm yoksa) ve Ollama'yı kurar (winget, olmazsa resmi kurulum dosyası)
   - Masaüstü arayüz motoru **Microsoft Edge WebView2**'yi kontrol eder / kurar
   - Ollama performans ayarlarını kalıcı olarak yazar
   - Sanal ortam + paketleri kurar
   - Ajan takımının 3 benzersiz modelini indirir (~43 GB; ana ve kodlama/görsel rolleri aynı 35B modelini paylaşır) — ilerleme çubuklu
   - Masaüstüne ve Başlat menüsüne **ATLAS** kısayolu ekler (kendi ikonuyla)
3. Sonra her seferinde **ATLAS** kısayolu veya **`BASLAT.bat`** → native Windows uygulaması açılır (konsol penceresi yok, tarayıcı yok).

| Dosya | Ne işe yarar |
|---|---|
| `KUR.bat` | Tek seferlik kurulum |
| `BASLAT.bat` | Uygulamayı açar (konsolsuz) |
| `SORUN_GIDER.bat` | Konsol + geliştirici araçlarıyla açar; hata olursa buradan görürsün |
| `MODELLERI_GUNCELLE.bat` | Modelleri yeniden indirir/günceller |
| `BUILD_EXE.bat` | İstersen tek klasörlük `ATLAS.exe` derler (PyInstaller) |

## 🖥 Masaüstü uygulaması

Claude Desktop tarzı, üç bölmeli native pencere:

- **Sol kenar çubuğu:** projeler, tarihe göre gruplanmış sohbetler (Bugün / Dün / Son 7 gün…), sabitleme, yeniden adlandırma, Markdown dışa aktarma (sağ tık menüsü)
- **Orta:** sohbet. Düşünme süreci, her araç adımı (açılır detay), dosya değişiklikleri **renkli diff** olarak, ajan soru sorarsa **seçenek kartları**, komut onayı kartları
- **Sağ çalışma paneli (Ctrl+J):**
  - **Plan** — çok adımlı görevlerde otomatik oluşturulan canlı TODO listesi; araç sonuçlarına göre tamamlanan ve sıradaki adımlar güncellenir, sohbet bazında SQLite'a kaydedilir.
  - **Dosyalar** — proje dosya gezgini + sözdizimi renkli görüntüleyici, "@ Sohbete ekle"
  - **Değişiklikler** — ajanın yaptığı her dosya değişikliği; **tek tıkla turu geri al**
  - **Terminal** — çalıştırılan komutlar, derleme ve Python çıktıları; `git commit` komutu, kullanıcı mevcut işi açıkça başarılı diye doğrulayana kadar araç düzeyinde engellenir (test/build başarısı tek başına yetmez). İzin verilen başarılı commit'ler proje içindeki `.atlas/commit-log.md` dosyasına hash, mesaj, dal, yazar ve değişen dosyalarla otomatik kaydedilir.
- **Besteci:** `/` komutları, `@dosya` bahsetme (dosya içeriği otomatik bağlama eklenir), sürükle-bırak dosya, Ctrl+V görsel, model seçici (Ajan Takımı / Mimar / Uygulayıcı / Görsel), Düşün ve Web anahtarları
- **Mesaj işlemleri:** kopyala, **düzenle** (o noktadan yeniden yanıtlar), **yeniden oluştur**, bu yanıttan davranış dersi çıkar (**Öğret**), değişiklikleri geri al, tok/s istatistiği
- **Sohbet navigasyonu:** yukarı kaydırıldığında sağ altta görünen aşağı ok, tek tıkla konuşmanın en altına götürür.
- **Komut paleti (Ctrl+K):** tüm sohbetlerde ve mesajlarda arama + tüm komutlar
- **Sistem tepsisi:** pencereyi kapatınca arka planda çalışır; sağ tık → yeni sohbet, ekran görüntüsüyle sor, her zaman üstte, çıkış
- **Global kısayollar** (uygulama arkadayken bile): **Ctrl+Alt+Space** göster/gizle · **Ctrl+Alt+S** ekran görüntüsü al ve sor
- **Windows bildirimleri:** pencere arkadayken yanıt bitince / onay veya cevap gerektiğinde
- Koyu/açık/sistem teması, koyu başlık çubuğu, Windows ile başlatma, yakınlaştırma (Ctrl + / −)

### Klavye kısayolları
| Kısayol | İşlev |
|---|---|
| Ctrl+N | Yeni sohbet |
| Ctrl+K | Arama / komut paleti |
| Ctrl+B / Ctrl+J | Kenar çubuğu / çalışma paneli |
| Ctrl+, | Ayarlar |
| Ctrl+1…4 | Model: Ajan Takımı / Mimar / Uygulayıcı / Görsel |
| Ctrl+T | Düşünmeyi aç/kapat |
| Ctrl+Shift+S | Ekran görüntüsü ekle |
| Ctrl+Shift+O | Ollama paneli |
| ↑ (boş kutuda) | Son mesajı düzenle |
| Esc | Durdur / kapat |

## 🧠 Modeller ve otomatik yönlendirme

| Rol | Model | Yaklaşık boyut | Görev |
|---|---|---:|---|
| Mimar / uygulayıcı / görsel | `huihui_ai/Qwen3.6-abliterated:35b-a3b` | 24 GB | İsteği anlama, plan, kodlama ve görseller — ana ağır model |
| Bağımsız reviewer | `orcarouter/Qwen3.8-27B-Uncensored:q4_K_M` | 18 GB | Farklı model ailesiyle değişiklikleri ve test kanıtlarını denetler |
| Hafıza | `qwen3-embedding:0.6b` | 0.6 GB | Yerel anlamsal hafıza araması (CPU) |

**Ajan takımı:** 35B mimar isteği/planı çıkarır → 35B uygulayıcı kodu değiştirir → ilk build/compile çağrısından önce Qwen3.8 27B diff'i inceler. Kritik/major bulgu varsa build bloke edilir; 35B bulguyu doğrular, düzeltir ve yeni diff yeniden 27B ön incelemesinden geçer. Ön inceleme PASS olunca gerçek build/test çalışır; ardından 27B çıktıları da denetler. Build sonrası reviewer bulguları coder'a geri döner (en fazla iki review turu). Büyük modeller sırayla yüklenir, aynı anda değil.

### Modeller ve disk bakımı
- Aktif görev rolleri yalnızca Qwen3.6 35B ve bağımsız Qwen3.8 27B takımını kullanır; düşük parametreli 0.6B embedding sadece yerel hafıza aramasıdır. Ana, uygulayıcı ve görsel roller 35B'yi paylaşır. İnference yavaş olabilir; kalite önceliğidir.
- Bağımsız reviewer, Qwen3.8 27B Uncensored Q4_K_M'dir. Yaklaşık 18 GB indirilir; farklı aileden ikinci görüş verir. Modelin ürettiği bulgu kanıtla desteklenmiyorsa coder'a körü körüne uygulatılmaz.
- Toplam model indirmesi yaklaşık **42.6 GB** (+ varsa Ollama cache). Uygulama açıldığında eksikler arka planda iner, durum çubuğunda ilerleme görünür.
- Uygulama güncellenince eski 9B/Qwen3 rol atamaları yeni takım varsayılanlarına taşınır. Yeni rol modelleri kuruluysa ve eski model hiçbir rolde kullanılmıyorsa 9B/Qwen3-Coder/Qwen3-VL modelleri açılışta temizlenir; Ayarlar → Modeller → **Eski 9B / Qwen3 modellerini temizle** ile elle de başlatılabilir. Başka model ailelerine dokunulmaz. Eski modelin silinmesi için güncel rol modelinin kurulu olması gerekir.
- `Qwen3.6 35B` Ollama kütüphanesinde 24 GB Q4_K_M, MoE'de 3B aktif parametre ve native tools/thinking/vision olarak listelenir ([model kartı](https://ollama.com/huihui_ai/Qwen3.6-abliterated:35b-a3b)). Qwen3.8 reviewer'ın Q4_K_M etiketi 18 GB, native tools/thinking/vision ve uncensored kartıyla listelenir ([model kartı](https://ollama.com/orcarouter/Qwen3.8-27B-Uncensored:q4_K_M)). Bu boyutlar RAM gereksinimini ortadan kaldırmaz; 32 GB sistem belleğinde iki model asla eşzamanlı yüklenmez.


**İstenen modeli doğrudan seçme:** Sohbet üstündeki model menüsü artık ATLAS'ın sabit modlarına ek olarak Ollama'da kurulu tüm modelleri listeler. Bir modeli seçince VRAM'de değilse yükler ve bu sohbet seçimi sonraki açılışlar için saklanır. Kurulu olmayan bir model için Ollama paneli → Modeller bölümünden Ollama model adını girip indir; sonra sohbet menüsünden seç. Seçili model, Mimar rolü için ayarlanan güvenli bağlam/sıcaklık değerleriyle çalışır; ATLAS rol model atamalarını değiştirmez.

### Araç kullanımı: iki mod
- **Ana model (Qwen3.6 35B)** Ollama'nın **yerel araç çağrısını** kullanır (model sayfasında `tools` yeteneği var).
- **Ağır iş modeli (Qwen3.6)** de yerel araç çağrısı kullanır.
- Şablonunda araç desteği **olmayan** bir model seçersen (ör. eski `qwen3-coder-abliterated`) ATLAS bunu otomatik algılar ve **metin tabanlı araç moduna** geçer: araç listesi sistem istemine Qwen3-Coder'ın eğitildiği
  XML biçiminde yazılır, modelin `<tool_call><function=…>` çıktısı araç şemasına göre ayrıştırılır (dosya içeriği her zaman metin
  olarak korunur), sonuçlar `<tool_response>` bloklarıyla geri verilir. Böylece Coder da dosya yazar, düzenler, derler ve komut çalıştırır.
  Arayüzde bu mod için ham XML görünmez; adımlar normal araç kartları olarak gösterilir.

### Agent Skills ve MCP
- **Agent Skills** standardındaki `SKILL.md` dosyaları görev bağlamına göre yüklenir. ATLAS `~/.agents/skills/<skill>/SKILL.md` ve `~/.claude/skills/<skill>/SKILL.md` kullanıcı klasörlerini; proje içinde `.agents/skills/` ve `.claude/skills/` klasörlerini tarar. `name` ve `description` YAML frontmatter alanları zorunludur. Model önce katalogdaki açıklamaları görür, ilgili skill'i `load_skill` ile açar; referans metinleri `read_skill_resource` ile okuyabilir. Skill dosyaları çalıştırılmaz ve içerikleri sistem/kullanıcı talimatlarının üstüne çıkamaz.
- **MCP istemcisi** stdio, Streamable HTTP (`streamable_http`) ve eski SSE (`sse`) sunucularını destekler. Ayarlar → **Skills & MCP** bölümünde etkinleştir, sunucu JSON'unu düzenle ve isteğe bağlı olarak bağlantıyı test et. Sunucular varsayılan olarak kapalı ve güvenilmeyen durumdadır. Her MCP tool çağrısı, sunucuya ve argümanlara özel ayrı bir onay ister; Ajan → Komutları otomatik onayla ayarı bu kontrolü aşamaz.
- Yalnızca denetlediğin sunucuyu `"trusted": true` yap. Bu, o sunucunun araç çağrıları için kalıcı onay muafiyetidir; sunucu kapatılıp yeniden açıldığında da ayarda kalır. stdio sunucuları bilgisayarında komut çalıştırır, HTTP sunucuları ise ağa erişir.
- Kimlik bilgilerini yapılandırmaya düz metin olarak koyma. Ortam değişkeni referansı kullan: `"env":{"API_TOKEN":"${API_TOKEN}"}` veya `"headers":{"Authorization":"Bearer ${API_TOKEN}"}`; gerçek değer ATLAS çalıştığı sürecin ortamında tanımlı olmalıdır. MCP örneği:
  ```json
  {"id":"files","name":"Local files","transport":"stdio","command":"npx","args":["-y","@modelcontextprotocol/server-filesystem","C:/Projects"],"env":{},"enabled":true,"trusted":false}
  ```
  Streamable HTTP/SSE örneklerinde `command`/`args` yerine `url` ve isteğe bağlı `headers` kullanılır. MCP Python SDK bağımlılığı ilk kurulumda yüklenir.

### Ollama sürümü
Qwen3.6 35B ve Qwen3.8 27B için güncel Ollama gerekir; kurulum betikleri Ollama'yı günceller.
`KUR.bat` ve `MODELLERI_GUNCELLE.bat` Ollama'yı otomatik günceller; eski sürüm tespit edilirse sol altta ve Ayarlar → Modeller'de uyarı çıkar.

### Bozuk araç çağrılarına dayanıklılık
Küçük/abliterated modeller zaman zaman hatalı araç çağrısı üretir. ATLAS bunları **çalıştırmadan önce onarır**
(Ayarlar → Ajan → *Bozuk araç çağrılarını onar*, varsayılan açık):

| Sorun | ATLAS ne yapar |
|---|---|
| Geçersiz JSON (tek tırnak, tırnaksız anahtar, sondaki virgül, yorum, `True/None`, kaçışsız satır sonu) | Hoşgörülü ayrıştırıcıyla düzeltir |
| Yarım kalan JSON (kapanmayan parantez/tırnak) | Kapatır; dosya yazma gibi riskli çağrılar kesikse **çalıştırmaz**, modelden küçük parçalarla tekrar ister |
| Yanlış araç adı (`readFile`, `functions.read_file`, `ls`, yazım hatası) | En yakın gerçek araca eşler |
| Yanlış parametre adı (`file_path`, `filename`, `cmd`…) / yanlış tip (`"1"` → 1, `"true"` → true) | Şemaya göre düzeltir, bilinmeyenleri atar |
| Çağrının metne (`<tool_call>`, ```json bloğu, `<function=…>`, `read_file(path="…")`) ya da düşünce bölümüne yazılması | Metinden çıkarıp çalıştırır, ham metni göstermez |
| Ollama'nın `error parsing tool call` hatası | Ham çağrıyı hatadan kurtarır; 2 kez üst üste olursa o tur için metin tabanlı araç moduna geçer |
| Aynı başarısız çağrıyı tekrar tekrar deneme / art arda bozuk çağrılar | Döngüyü keser; gerekirse araçları kapatıp doğrudan cevap ister |
| Araçtan sonra boş cevap | Bir kez dürter, özet cevap ister |
| Onarılamayan çağrı | Modele *neyin yanlış olduğunu ve doğru biçimi* örnekle bildirir |

Onarılan adımlar sohbette turuncu **onarıldı** rozetiyle işaretlenir; adıma tıklayınca yapılan düzeltmeler görünür.

## 🖥️ Ollama paneli
Sol menüdeki **Ollama** (ya da sol alttaki durum yazısı, Ctrl+Shift+O, komut paleti, tepsi menüsü) Ollama sunucusunu uygulamadan yönetir:

- **Genel bakış:** durum, sürüm, PID, çalışma süresi; GPU/VRAM; VRAM'deki modeller (GPU/CPU yerleşim oranı, bağlam,
  bellekte kalma süresi, *Boşalt*); çalışan Ollama süreçleri; etkin ortam değişkenleri.
- **Başlat / Durdur / Yeniden başlat:** ajan çalışırken durdurmaya kalkarsan önce sorar.
- **Modeller:** adını yazarak herhangi bir modeli indir (ilerleme çubuklu), yükle/boşalt, ayrıntıları gör (yetenekler, bağlam,
  şablon), **ATLAS rolü ata** (Ana / Coder / Görsel / Embedding), sil (rolde kullanılan model için ek onay ister).
- **Sunucu ayarları:** Flash Attention, KV önbellek tipi (f16/q8_0/q4_0), aynı anda yüklü model, paralel istek, varsayılan bağlam,
  GPU'da boş bırakılacak bellek, bellekte kalma süresi, **model klasörü** (başka diske taşımak için), ek ortam değişkenleri.
  *Kaydet ve yeniden başlat* ile hemen uygulanır; ayarlar değişip uygulanmadıysa panel uyarır.
- **Log:** Ollama sunucu logu canlı akar; hata/uyarı satırları renklenir, filtrelenebilir, kopyalanabilir.

Ollama ATLAS dışında başlatılmışsa (ör. Ollama'nın kendi tepsi uygulaması) panel bunu gösterir ve tek tıkla ATLAS ayarlarıyla
yeniden başlatmayı önerir. ATLAS'ın Ollama'ya hiç dokunmamasını istersen *Ollama'yı ATLAS yönetsin* anahtarını kapat.

## 🧬 IDA Pro ile tersine mühendislik
ATLAS, kurulu IDA Pro'yu (8.x / 9.x, ör. **9.3**) arka planda metin modunda (`idat.exe -A`) kendisi çalıştırır.
Sohbette şunu demen yeterli:

> *IDA ile şu dosyayı incele ve ne yaptığını açıkla: C:\Samples\crackme.exe*

ya da komut paletinde (**Ctrl+K**) **"Bir exe/dll'i IDA ile incele"** ile dosyayı seç.

**Ajan şu iş akışını izler:** genel bakış (tür, mimari, derleyici, bölümler, importlar, şüpheli API'ler, dizeler) →
ipucu toplama (dizeler/importlar + çapraz referanslar) → Hex-Rays pseudo-kodu okuma → anladığı fonksiyonları
**IDB'de yeniden adlandırma / yorumlama** → bulguları proje notlarına yazma → adres göstererek raporlama.

| `ida` aracının eylemleri | |
|---|---|
| `overview` | dosya özeti, bölümler, giriş noktaları, import modülleri, anti-debug/injection/crypto/network API'leri, dizeler |
| `functions` | fonksiyon listesi (filtre, boyuta göre sıralama, sayfalama) |
| `decompile` | Hex-Rays pseudo-kodu (birden fazla hedef), çağıran/çağrılan listesi; decompiler yoksa disasm |
| `disasm` · `xrefs` · `strings` · `imports` | assembly, çapraz referanslar, dizeler (regex) ve importlar |
| `rename` · `comment` | IDB'ye kalıcı ad ve yorum yazar (IDA'da açınca sen de görürsün) |
| `script` | IDAPython çalıştırır (onay ister) |

- Analiz veritabanı (`.i64`) proje klasöründe `.atlas\ida\` altında tutulur: ilk sorgu analiz yapar
  (büyük dosyada birkaç dakika), sonraki sorgular saniyeler sürer. Orijinal dosyaya dokunulmaz.
- Kendi `.i64` dosyanı da verebilirsin (o sırada IDA'da kapalı olmalı).
- **İlk kurulum:** Ayarlar → **Tersine müh.** → IDA otomatik bulunur (bulunamazsa `idat.exe`'yi Gözat ile seç) →
  **IDA'yı test et**. Test başarısız olursa: IDA'yı bir kez normal açıp lisans/EULA'yı onayla; IDAPython hatasında
  IDA klasöründeki `idapyswitch.exe` ile Python sürümünü seç.
- İnceleme görevleri yerel araç çağrısı destekleyen **ana modelde** çalışır (hızlı, tamamen GPU); hook/loader/yama
  kodu yazma istekleri Coder'a gider.

### Kayıtlı IDA betikleri
Ajanın yazdığı IDAPython betikleri projeye kaydedilebilir ve tekrar kullanılır:
- `ida action=script code=… save_as=vtable_tarayici description="…"` → `<proje>\.atlas\ida\scripts\vtable_tarayici.py`
- `ida action=script script_name=vtable_tarayici args={"n": 50}` → kayıtlı betiği yeniden çalıştırır (`ARGS` sözlüğü)
- `ida action=scripts` → listeler. Kayıtlı betikler ajanın bağlamına da eklenir; aynı betiği tekrar yazmaz.
- Her dosyada küçük bir uyumluluk katmanı vardır: IDA arayüzünde **File → Script file** ile de doğrudan çalışır.
- Bu klasöre kendi `.py` betiklerini de koyabilirsin; ilk yorum satırı/docstring açıklama olarak görünür.
- Çalıştırılan geçici betiklerin kopyası `scripts\_gecmis\` altına yazılır; iş %100 bitince otomatik silinir, iş yarım kaldıysa
  neyin çalıştığını görebilmen için durur (hata verenler `_HATA` ekiyle). `save_as` ile kaydedilenlere dokunulmaz.
- Hata veren betik `save_as` verilse bile kaydedilmez.

### Diğer programlar
Ayarlar → Tersine müh. → **Kullanabileceği programlar** listesine eklediğin her programı (x64dbg, Ghidra
`analyzeHeadless`, Detect It Easy `diec`, `cdb`, radare2, UPX…) ATLAS tanır ve gerektiğinde `run_command` ile
çalıştırır (her komutta onay ister). **Yeniden algıla** bilgisayarındaki bilinen RE araçlarını bulup tek tıkla ekler.
Biçim: `Ad = yol | ne işe yarar / nasıl kullanılır`.

### "Projeyi incele" = oku, özetle, komut bekle
- **Proje inceleme modu:** "projeyi incele / özetle / kavra / tanı" gibi (düzelt, ekle, derle gibi bir iş istemeyen)
  mesajlarda ATLAS yalnızca okuma araçlarını görür (list_dir, read_file, search_code, notlar). Yapıyı, build
  dosyalarını ve ana kaynakları okur, proje notlarına kaydeder, özet verir ve "ne yapmamı istersin?" diye bekler.
  Kod yazma, komut, derleme ve IDA bu turda kapalıdır.
- **IDA / ikili analiz yalnızca açık istekle:** mesajında exe/dll, IDA, decompile, tersine mühendislik gibi açık bir
  ifade yoksa analiz araçları ve IDA yolu modele hiç gösterilmez. Önceki mesajlar sayılmaz; yalnızca kısa bir
  "devam et / evet" önceki analiz isteğini sürdürür. idat.exe'nin `run_command` ile elle çağrılması da engellenir.

## 📁 Projeler ve çalışma alanları
- **Mevcut klasör:** Sol menü → PROJELER **＋** → *Mevcut klasör* → Gözat → klasörün proje (çalışma alanı) olur.
- **Yeni klasör:** *Yeni klasör oluştur* → konum (varsayılan `Belgeler\ATLAS Projeler`) + proje adı → klasör oluşturulur.
- **Sohbetten:** *"C:\Projeler\Oyun klasöründe yeni bir proje aç"* → ajan `set_workspace` ile klasörü oluşturur/bağlar,
  sohbet o projeye taşınır ve kenar çubuğu güncellenir.
- Yol yazarken pencere anında kontrol eder (klasör var mı, kaç öğe içeriyor, başka proje kullanıyor mu).

## 🧠 Deneyimden öğrenme ve uzun işler
- **Dersler:** Sen ATLAS'ı düzelttiğinde ("öyle demedim", "neden … yaptın") ya da bir araç hatasını başka yolla
  çözdüğünde, arka planda genel bir **davranış kuralı** çıkarılır ve Hafıza → **DERS** olarak kaydedilir. Her asistan
  yanıtındaki **🧠 Öğret** düğmesiyle de açık bir düzeltmeyi global davranış dersi veya seçili projeye özel ders olarak
  ekleyebilirsin. Dersler sonraki isteklerde bağlama alınır; bu, model ağırlıklarını eğitmez. Hafıza panelinden dersleri
  inceleyebilir, düzenleyebilir veya silebilirsin.
- **Uzun işlerde sessiz devam:** Her 24 adımda (Ayarlar → Ara kontrol aralığı) ATLAS sessizce durumunu değerlendirir;
  ilerliyorsa kendiliğinden sürer, döngüye girdiyse yaklaşım değiştirir ya da elindekiyle nihai cevabı yazar.
  Normal turlarda kesin üst sınır 150 adım (`agent.hard_max_steps`). "Maksimum adım" yazısıyla durmaz.
- **Watchdog’lu çözene-kadar modu:** İsteğine açıkça "test ederek çöz, çözene kadar durma" / "başarılı olana kadar devam et" gibi bir talimat eklediğinde ATLAS önce plan ve ölçülebilir bitti kriterleri çıkarır; test/build–hata inceleme–düzeltme döngüsünü, tamamlanma denetçisini ve takılınca 27B devrini kullanır. Tek oturum en fazla **4 saat** veya 24 devam aşaması sürer; başarı ölçütleri kanıtlanmazsa başarı diye işaretlemez, checkpoint bırakır. Durdur düğmesi her zaman çalışır. Yalnızca aktif proje içindeki tanınan test/build komutları otomatik onaylanır; diğer komutlar mevcut izin/onay kapısından geçer. Proje dışı dosya değişikliği, paket/ağ işlemi, hassas onay, kimlik bilgisi veya OS ayarı için durur.
- **Computer use:** Bu modda yalnızca görev mesajında hedef başlığı açıkça yazılmış Windows penceresinde ekranı gözleyip tekil tıklama/tuş/yazma/kaydırma yapabilir. Her eylem öncesi/sonrası ekranı kontrol etmesi istenir; beklenmeyen pencere veya hassas giriş görünürse durur. Normal görevlerde fare/klavye otomasyonu devre dışıdır.

### Kendini doğrulama, proje dersleri, iş akışları
- **Otomatik derleme doğrulaması:** Bir turda C/C++ dosyası değiştirildiyse ve derlenmediyse ATLAS bitirmeden önce
  derler (proje build sistemi → yoksa compile_cpp; DLL/başlık için yalnızca derleme), hata varsa düzeltir. Her
  değişiklik grubu için bir kez sorulur, döngüye girmez (`agent.auto_verify`, `agent.verify_rounds`).
- **Projeye özel dersler:** Yalnızca o projede geçerli kurallar (ör. "bu projede build.bat kullan") ayrı tutulur ve
  sadece o projede uygulanır. Hafıza panelinde **PROJE DERSİ** etiketiyle görünür.
- **İş akışları:** Hafıza → **İş akışları** sekmesinde sık yapılan işler için tarifler var (derleme/link hatası,
  CMake projesi, DLL iskeleti, ImGui girdi sorunları, performans, IDA raporu, crash analizi). Mesajın anahtar
  kelimelerle eşleşirse tarif o tura eklenir ("📘 İş akışı uygulanıyor"). ATLAS başarılı yöntemleri `save_playbook`
  ile kendisi kaydeder; sen de ekleyip düzenleyebilirsin.
- **Tekrar koruması:** Model aynı metni adım adım yeniden yazarsa tekrar gösterilmez; yalnızca yeni satırlar görünür.
- **Döngü koruması (tek cevap / düşünce içinde):** Model aynı bloğu ya da aynı düşünceyi sonsuz yazmaya başlarsa ATLAS akışı anında keser (Ollama üretimi de durur), ekranda tekrar eden kısmı geri alır ve tek kopyayı bırakır. Düşünce döngüsünde adım düşünmeden yeniden denenir; cevap çok erken döngüye girdiyse bir kez, düşünmeden ve biraz daha yüksek sıcaklıkla tamamlatılır. Geçmişteki döngülü eski cevaplar bağlama tekrarsız girer. Kapatmak için `agent.loop_guard: false`. Not: Ollama'nın yeni motoru `repeat/presence_penalty` değerlerini yok sayabildiği için koruma uygulama tarafında yapılır; ana model varsayılanları Qwen3.6 önerisine göre `temperature 0.8`, `presence_penalty 1.5` olarak güncellendi (eski 0.6 kaydı otomatik taşınır, elle değiştirdiğin değerlere dokunulmaz).
- **Geçici betik temizliği:** Ajanın tek seferlik yardımcı betikleri (`write_file temporary=true`, `tmp_*.py`/`temp_*.ps1`/`deneme_*.bat` gibi yeni dosyalar, `.atlas\tmp\` altı, IDA geçmiş kopyaları) tur sonunda **iş %100 bittiyse** silinir. Bitmediyse (hata veren son komut/derleme, derlenmemiş C++ değişikliği, planda açık adım, adım sınırı, durdurma, sana soru) korunur; aynı sohbette iş bitince ya da en geç 3 gün sonra silinir. Yalnızca ATLAS'ın oluşturduğu ve sonradan değiştirilmemiş dosyalar silinir; senin dosyalarına, adını verdiğin betiklere ve kalıcı IDA betiklerine dokunulmaz. `.atlas\backups` dosya başına son 5 yedekle sınırlanır (14 günden eskiler silinir). Ayarlar: `agent.auto_cleanup`, `cleanup_max_days`, `backups_keep`.
- **Boş yanıt kurtarma:** Model yalnızca düşünüp araç çağırmadan / cevap yazmadan durursa tur kesilmez: önce düşüncesinde planladığı adım hatırlatılarak düşünmeden devam ettirilir, üst üste ikinci kez olursa araçsız nihai cevap istenir (turda en fazla 6 deneme). Düşünce uzunluk sınırına takılırsa adım düşünmeden yeniden denenir. Model yine de hiçbir şey yazmazsa ATLAS yapılan adımları listeleyip "devam et" önerir — tur asla boş bitmez.
- **İsteği önce anlama:** İş isteklerinde ATLAS işe başlamadan mesajını yüklü modelle (düşünmeden, birkaç saniye) amaç / teslimatlar / kısıtlar / bitti kriterine çevirir ve "🎯 Anladığım: …" diye gösterir; model tur boyunca buna göre çalışır. "devam et" aynı görevi sürdürür (inceleme görevi incelemede kalır). İstek iki farklı şekilde anlaşılabiliyorsa işe başlamadan seçenekli tek soru sorar. Kısa sorularda ve "projemi incele"de bu adım atlanır. (Ayarlar → Ajan → İsteği önce anla / Kritik belirsizlikte sor)
- **Hedeften sapmama:** Uzun turlarda her 8 adımda bir (ve bağlam kısaltıldığında) asıl istek, kısıtlar, bitti kriteri ve plan durumu modele sessizce hatırlatılır.
- **Takılınca 27B görevi devralır:** 35B art arda 4 adım ilerleme sağlayamazsa, aynı derleme hatasında takılırsa veya açıkça çözemediğini söylerse 27B bir kez otomatik devreye girer. 27B yalnızca review önermez; mevcut araç/geçmiş bağlamını devralır, farklı çözüm yolunu uygular ve doğrular. Build öncesi güvenlik review kapısı ayrıca korunur. Bu bir model ağırlığı eğitimi değil, çalışma anında model devridir.
- **Düzeltmeyi anlama:** "hayır öyle demedim / neden sildin" → yanlış anladığını kabul edip istenen şekilde yapar ve kalıcı ders olarak kaydeder. "hâlâ çalışmıyor / yine olmadı" → aynı çözümü tekrarlamaz, neden tutmadığını araçlarla doğrulayıp farklı çözüm uygular.
- **Komut koruması:** ATLAS projedeki .bat/.cmd/.ps1 betiklerini içeriklerine göre DERLEME (cmake/msbuild/cl/g++ …) ve BAŞLATMA (start, .exe çalıştıran) olarak ayırır ve modele bildirir — "derle" denince başlatma betiği (ör. start.bat) çalıştırılmaz, doğru derleme betiği önerilir. Program/oyun başlatma ve taskkill yalnızca mesajında "çalıştır / başlat / test et" gibi açık bir istek varsa yapılır; izin olsa bile aynı programı en fazla 2 kez başlatır / 2 kez kapatır, aynı komutu en fazla 3 kez çalıştırır (başlat-öldür döngüsü kesilir). (Ayarlar → Ajan → Komut koruması)
- **Yarım kalan iş koruması:** Model bir sonraki adımı duyurup ("…içeriğini görmek gerek:", "şimdi derleyelim") aracı çağırmadan durursa ya da planında bitmemiş adımlar varken bitirirse tur sonlanmaz; sessizce aracı çağırması istenir (en fazla 2 + 1 hatırlatma). Uzunluk sınırındaki otomatik devam hakkı her araç adımından sonra yenilenir; hak biterse metin sessizce ve öz biçimde tamamlatılır. Model önceki metnini tekrar ederken sınıra takılırsa tekrar devam ettirilmez, metni kesip sıradaki adıma geçmesi istenir.
- **Güncellemeler:** Şu an yeni sürüm ZIP olarak indirilip uygulama klasörüne elle çıkarılır; güncellenen kodun yüklenmesi için ATLAS yeniden başlatılır. Otomatik ZIP güncellemesi henüz bu pakette etkin değildir.

## 💾 Hafıza — neden unutmaz?

1. **Käyttäjämuisti** — käyttäjää koskevat pysyvät tiedot (lisätään jokaiseen tehtäväkontekstiin).
2. **AGENTS.md proje yönergeleri** — Aktif projedeki `AGENTS.md`/`agents.md` (ve yazım hatası `agenst.md`) dosyaları kökten ve alt klasörlerden otomatik okunur, içerik proje hafızasında saklanır ve her görevde kullanılır. Dosya ancak kullanıcı işi “oldu/çözüldü/başarılı” gibi bir ifadeyle onayladıktan sonra güncellenebilir; o durumda da yalnızca doğrulanmış, tekrar kullanılabilir yöntem eklenir ve mevcut içerik korunur. Bağımlılık/build klasörleri atlanır; talimatlar sistem ve kullanıcı talimatlarından öncelikli değildir.
3. **Projektiomuistiinpanot** — ajantasainen projektidokumentti (arkkitehtuuri, päätökset, tehtävät).
4. **Projektikartta** — kansion tiedostot ja C++-luokka-/funktiosymbolit (indeksoidaan automaattisesti).
5. **Koodi-indeksi** — viestin projektisymboli (esim. `DrawFrame`) liittää asiaankuuluvan koodin kontekstiin.
6. **Hybridihaku** — SQLite FTS5 (BM25) ja vektorisamankaltaisuus yhdistetään RRF:llä.
7. **Automaattinen tiedon poiminta** — pysyviä tietoja opitaan vastauksen jälkeen taustalla. Kun käyttäjä vahvistaa työn onnistuneeksi (esim. "oldu", "başarılı", "çözdük", "çalıştı"), ATLAS poimii edellisen pyynnön, suoritetut työkaluvaiheet ja tulokset sekä tallentaa todennetun ratkaisun projektimuistiin (ilman aktiivista projektia vain yleishyödyllisen tiedon käyttäjämuistiin). Salaisuudet redaktoidaan.
8. **Kokemuspäiväkirja** — työkalua käyttävät tehtävät kirjataan SQLiteen redaktoiduilla vaiheilla ja tuloksilla. Derleme çıktıları merkitään varmennetuiksi vain onnistuneella tuloksella; epäonnistuneet/korjatut yritykset erotellaan, eikä epäonnistumista esitetä toimivana ohjeena. Käyttäjän myöhempi selkeä palaute merkitsee viimeisimmän yrityksen onnistuneeksi tai epäonnistuneeksi. Vain tehtävään liittyviä aiempia epäonnistumisia tuodaan kontekstiin, jotta samaa lähestymistapaa ei toisteta. Tämä parantaa orkestrointia ja muistia — mallin painoja ei kouluteta.
9. **Liukuva yhteenveto** — vanhoja viestejä tiivistetään keskustelun kasvaessa.

Hepsi `data/atlas.db` dosyasında. **🧠 Hafıza** panelinden görüntüle/düzenle/sil.

## 🛠 Ajan araçları

- **Dosya:** `list_dir`, `read_file`, `write_file`, `edit_file` (otomatik yedek: `.atlas/backups`), `search_code`
- **Derleme:** `compile_cpp` — g++ / clang++ / MSVC'yi otomatik bulur (Visual Studio'yu `vswhere` ile bulup `vcvars64` yükler), hataları okuyup düzeltir
- **Komut:** `run_command` — cmake, git, msbuild… (varsayılan olarak **senin onayınla** çalışır)
- **Tersine mühendislik:** `analyze_binary` (PE/ELF başlık, bölüm entropisi, import/export, ASLR/DEP/CFG, packer/.NET tespiti), `disassemble` (capstone x86/x64, VA/RVA/export adı), `extract_strings` (ASCII + UTF-16), `hexdump`
- **Hafıza:** `remember`, `recall`, `update_project_notes`
- **Planlama ve etkileşim:** `update_plan` (canlı yapılacaklar listesi), `ask_user` (belirsizlikte sana seçenekli soru sorar)
- **Python:** `run_python` — hesaplama, veri işleme, hızlı script (onaylı)
- **Ekran:** `take_screenshot` — ajan gerektiğinde ekranına kendisi bakar (pencere otomatik gizlenir) ve görsel modelle analiz eder
- **Web:** `web_search`, `fetch_url` — dokümantasyon/hata araştırması (Web anahtarıyla kapatılabilir)
- Her `write_file`/`edit_file` değişikliği diff olarak veritabanına kaydedilir ve arayüzden geri alınabilir

## ⚡ Performans optimizasyonları

| Optimizasyon | Etki |
|---|---|
| `OLLAMA_FLASH_ATTENTION=1` | Uzun bağlamda daha hızlı + daha az VRAM |
| `OLLAMA_KV_CACHE_TYPE=q8_0` | KV önbelleği belleği ~%50 azalır → daha uzun bağlam GPU'ya sığar |
| `OLLAMA_NUM_PARALLEL=1` | Tek kullanıcı: paralel slotlara VRAM harcanmaz |
| `OLLAMA_MAX_LOADED_MODELS=2` | LLM (GPU) + embedding (CPU) birlikte durur, gidip gelmez |
| `keep_alive=30m` + açılışta ön yükleme | İlk mesajda model yükleme beklemesi yok |
| `num_thread=8` | 5700X'in 8 fiziksel çekirdeği (SMT thread'leri llama.cpp'yi yavaşlatır) |
| KV-cache dostu istem yapısı | Sabit sistem istemi önde, değişken hafıza son mesajda → Ollama önceki ön eki tekrar hesaplamaz |
| Yapışkan yönlendirme | Coder'dayken devam sorularında modeli değiştirmez → 19 GB yeniden yükleme yok |
| Arka plan işleri aynı modeli kullanır | Hafıza/özet için model değiştirilmez |
| Bağlam bütçesi | Mesajlar `num_ctx`'e göre kırpılır; Ollama'nın sessiz kesmesiyle sistem istemi kaybolmaz |
| Tur içi bağlam koruması | Her adımdan önce istem (araç şemaları dahil) ölçülür, Ollama'nın gerçek token sayısıyla kalibre edilir; eski araç sonuçları kısaltılır, `num_predict` kalan alana göre ayarlanır |
| Otomatik devam | Cevap uzunluk sınırına takılırsa (`done_reason=length`) kaldığı yerden tekrarsız sürdürülür (`agent.auto_continue`, varsayılan 3) |
| SQLite WAL + mmap | Hafıza sorguları milisaniye düzeyinde |

**Hız notu:** 35B ve 27B modeller bu 8 GB VRAM / 32 GB RAM makinede ağırlıklı CPU+GPU hibrit çalışabilir ve yavaş olacaktır. Öncelik bilinçli olarak kod kalitesi; büyük modeller ajan takımı içinde sırayla yüklenir.

### Otomatik bağlam (VRAM'e göre num_ctx)
ATLAS her modeli farklı bağlam değerleriyle yükleyip Ollama'nın kendi yerleşimini (`/api/ps` → GPU/CPU payı) ölçer ve
modelin **tamamen GPU'da** kaldığı en büyük bağlamı ikili aramayla bulur (12.288–32.768, bir adım güvenlik payıyla).
- İlk açılışta bir kez yapılır (birkaç saniye–1 dk); sonuç `data\ctxfit.json`'a yazılır, ana model ölçülen bağlamla yüklü kalır.
- Model, KV önbellek tipi, flash attention, num_gpu/num_batch değişince kendiliğinden yeniden ölçülür.
- 12.288'e bile tam sığmayan modellerde (ör. 30B coder, 8 GB kart) ayardaki `num_ctx` kullanılır — zorla küçültmez.
- Ollama paneli → Genel bakış → **Bağlam — VRAM'e göre otomatik**: sonuçlar, aç/kapa, **Şimdi ölç**.
- Ayarlar: `performance.auto_ctx`, `auto_ctx_min`, `auto_ctx_max`, `auto_ctx_margin`. Oyun açıkken VRAM azalır; ölçümü
  oyun kapalıyken yapmak ya da `ollama_server.gpu_overhead_mb` ile pay bırakmak iyi olur.

### Elle yapabileceğin ek ayarlar
- **NVIDIA Denetim Masası → 3D Ayarları → "CUDA - Sysmem Fallback Policy" → "Prefer No Sysmem Fallback"**: VRAM taşınca sürücünün yavaş paylaşılan belleğe sessizce kaçmasını engeller.
- Ağır iş modeli daha hızlı olsun istersen Ollama panelinden `richardyoung/gemma-4-12b-coder-abliterated:IQ4_XS` (6.7 GB, tamamen GPU'da) indirip "Ağır iş" rolüne ata.
- Ana modelde bağlamı 32768'e çıkarabilirsin (Ayarlar → num_ctx); VRAM taşarsa katmanların bir kısmı CPU'ya geçer, yavaşlar.
- Modelleri başka diske koymak için: **Ollama paneli → Sunucu ayarları → Model klasörü**.
- Tüm bu sunucu ayarları Ollama panelinden değiştirilebilir (ör. VRAM yetmezse KV önbelleği `q4_0`).

## 📁 Kullanım ipuçları
- Sol üstte **PROJELER ＋** → ad + klasör (**Gözat** ile seç) + proje talimatları → ajan dosyaları okur, düzenler, derler.
- İlk iş: *"Proje klasörünü incele, mimariyi özetle ve proje notlarını oluştur."*
- Ekran görüntüsü: **Ctrl+Alt+S** (her yerden) veya besteci **＋ → Ekran görüntüsü / Bölge seç**, ya da Win+Shift+S → Ctrl+V.
- `@src/main.cpp` yazarak dosyayı doğrudan bağlama ekle.
- **Ayarlar → Kişiselleştirme → Özel talimatlar:** ATLAS'ın her sohbette uyacağı kuralların.
- Bağlam halkası (üst çubuk) dolunca tıkla → sohbet özetlenir, hiçbir şey unutulmaz.
- Bir sorun olursa: `SORUN_GIDER.bat` ve `data\atlas.log`.

## Dosya yapısı
```
AtlasAgent/
├─ KUR.bat / BASLAT.bat / SORUN_GIDER.bat / BUILD_EXE.bat / MODELLERI_GUNCELLE.bat
├─ desktop.py           native pencere (WebView2), tepsi, global kısayollar, bildirimler
├─ launcher.py          Ollama'yı optimize ayarlarla başlatır (+ --setup model kurulumu)
├─ assets/              uygulama ikonu
├─ atlas/
│  ├─ agent.py          yönlendirme, bağlam, araç döngüsü, özet, hafıza çıkarımı
│  ├─ tools.py          dosya / derleme / komut / RE / plan / soru / python / ekran / web araçları
│  ├─ store.py          SQLite + FTS5 + vektör hafıza + dosya değişikliği geçmişi
│  ├─ screen.py         ekran görüntüsü (mss) ve bölge seçimi
│  ├─ indexer.py        proje haritası + kod indeksi
│  ├─ ollama.py         asenkron Ollama istemcisi
│  ├─ ollama_ctl.py     Ollama sunucusunu başlatma/durdurma/ayar/log (panel + başlatıcı)
│  ├─ ctxfit.py         Bağlamı VRAM'e göre ölçerek otomatik ayarlama
│  ├─ cleanup.py        Geçici betik temizliği (iş bitince) + yedek sınırı
│  ├─ repair.py         bozuk araç çağrısı onarım motoru
│  ├─ ida.py            IDA Pro (idat.exe) çalıştırıcı + RE program algılama
│  ├─ ida_script.py     IDA içinde çalışan IDAPython köprüsü
│  ├─ playbooks.py      İş akışları: hazır tarifler + anahtar kelime eşleştirme
│  └─ core.py           ajan çekirdeği — süreç içi köprü (ağ sunucusu / port yok)
├─ static/index.html    arayüz (tamamen offline)
└─ data/                config.json, atlas.db, görseller, loglar (EXE sürümünde %APPDATA%\ATLAS)
```

> **Web arayüzü yok:** ATLAS bir web sitesi değildir; hiçbir web sunucusu çalıştırmaz, **hiçbir port açmaz** ve tarayıcıdan açılamaz.
> Pencere, uygulama klasöründeki yerel `static/index.html` dosyasını gömülü WebView2 motoruyla çizer (Tauri ve Claude Desktop ile aynı yöntem).
> Arayüz Python çekirdeğiyle (`atlas/core.py`) **süreç içi köprüyle** (pywebview `js_api`) konuşur; yanıt akışı pencereye doğrudan iletilir.
> Tek ağ trafiği, bilgisayarındaki Ollama motoruna (`127.0.0.1:11434`) giden istektir. İsteğe bağlı web arama araçlarını Ayarlar → Ajan bölümünden kapatabilirsin.
> ATLAS'tan çıktığında Ollama arka planda çalışmaya devam eder (bir sonraki açılış anında olsun diye); modeller `keep_alive` süresi sonunda VRAM'den kendiliğinden boşalır.
