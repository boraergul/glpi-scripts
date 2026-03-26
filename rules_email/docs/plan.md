# rules_email.py İnceleme ve İyileştirme Planı

Bu plan, `rules_email.py` dosyasındaki olası sıkıntıları belirler ve bu sıkıntılar için çözüm önerileri sunar.

## İnceleme Sonuçları

Aşağıdaki noktalar, kodun çalışmasında olası sorunlar veya geliştirme alanları olarak belirlenmiştir:

1.  **Güvenlik (SSL/TLS):**
    *   `verify=False` ve `InsecureRequestWarning` uyarılarının kapatılması bir güvenlik riskidir.
2.  **Verimlilik (Gereksiz Silme ve Yeniden Oluşturma):**
    *   `create_or_update_rule` fonksiyonunda kural güncellenirken mevcut tüm kriter ve aksiyonlar silinip (Lines 139-151) yeniden ekleniyor. Bu, API'yi boş yere yorar ve işlem yarım kalırsa veri kaybına neden olabilir.
3.  **Hata Yönetimi ve Loglama:**
    *   Hata blokları (`try-except`) bazen çok geniş kapsamlı (`Exception as e`) ve sadece `print` kullanarak çıktı veriyor.
4.  **Konfigürasyon Esnekliği:**
    *   `config.json` dosya adı ve aranacak yollar (Lines 15-20) koda gömülü durumdadır.
5.  **Regex Escaping:**
    *   Sadece `.` karakteri (`mail_domain.replace('.', '\.')`) kaçış karakteri (escape) yapılıyor.
6.  **Domain Doğrulama:**
    *   `if '@' not in mail_domain:` kontrolü (Line 116), domain kısmında `@` içermeyen verileri (örneğin sadece `company.com`) atlamaya neden olur. README ise `@company.com` formatını öneriyor.
7.  **Ranking (Sıralama):**
    *   Tüm yeni kuralların `ranking: 1` ile yaratılması, kurallar arasındaki öncelik sırasını bozabilir.

## Önerilen Değişiklikler

### [Gelişmiş Hata Yönetimi & Loglama]
*   **Logging Modülü:** `print` ifadeleri yerine `logging` kütüphanesi kullanılacak. Loglar hem konsola hem de isteğe bağlı bir dosyaya (`rules_email.log`) yazılacak.
*   **Hata Yakalama:** API çağrıları `try...except requests.exceptions.RequestException` bloklarına alınacak.
*   **Session Koruması:** `init_session` başarılı olduktan sonra kodun geri kalanı `try...finally` bloğuna alınarak her durumda `kill_session` yapılması garanti altına alınacak.

### [Verimlilik & Akıllı Güncelleme]
*   **Smart Sync:** `create_or_update_rule` içinde kural mevcutsa:
    1.  Mevcut kriterler (`RuleCriteria`) API'den çekilecek.
    2.  Mevcut aksiyonlar (`RuleAction`) API'den çekilecek.
    3.  Eğer mevcut kriter ve aksiyonların değerleri (regex ve entity ID) hedef değerlerle birebir aynıysa, kural güncellenmeden atlanacak (LOG: "Rule '...' is already up to date. Skipping.").
    4.  Eğer fark varsa, güvenli bir şekilde temizlenip yeniden oluşturulacak.

### [Regex & Domain Kontrolü]
*   **Robust Regex:** `re.escape(mail_domain)` kullanılarak domain içindeki özel karakterler (nokta gibi) kaçırılacak.
*   **Domain Normalizasyonu:** Domain başında `@` varsa temizlenecek (internal logic için) ve regex her zaman `/@{escaped_domain}$/i` formatında oluşturulacak.
*   **Validation:** Geçersiz domain formatları loglarda uyarı olarak belirtilecek.

### [Güvenlik]
*   **SSL Configuration:** `verify_ssl` parametresi `config.json` dosyasına eklenecek (default: `false`).

## Doğrulama Planı

### Otomatik Testler
*   `test_rules_email_utils.py` dosyası oluşturulacak (Mock API kullanılarak):
    *   `init_session` ve `kill_session` akışının doğrulanması.
    *   "Smart Sync" mantığının (fark yoksa API çağrısı yapılmadığı) doğrulanması.
    *   Regex oluşturma fonksiyonunun farklı domain girişleri ile test edilmesi.

### Manuel Doğrulama
*   `python rules_email.py` (Dry-run) çalıştırılarak "PROPOSE" mesajları ve yeni log formatı kontrol edilecek.
*   `python rules_email.py --force` çalıştırılarak kuralların GLPI'da doğru oluştuğu teyit edilecek.
*   Bir kuralın domaini GLPI'dan manuel değiştirilip script tekrar çalıştırılarak sadece o kuralın güncellendiği (Smart Sync) görülecek.
