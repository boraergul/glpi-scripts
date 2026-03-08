# GLPI Email Rules Automation

Bu script, GLPI üzerindeki Entity'ler (Birimler) için otomatik olarak e-posta kuralları oluşturur. Her bir Entity'nin `mail_domain` (e-posta alan adı) bilgisini kullanarak, o alan adından gelen e-postaların otomatik olarak ilgili Entity'ye atanmasını sağlayan kuralları GLPI'da tanımlar.

## Özellikler

*   **Otomatik Kural Oluşturma/Güncelleme:** GLPI'daki tüm Entity'leri tarar ve `mail_domain` bilgisi olanlar için kural oluşturur veya günceller.
*   **Regex Eşleştirme:** E-postaların "Kimden" (From) bilgisini kontrol eder ve belirtilen alan adı ile bitip bitmediğini kontrol eden bir Regex (Düzenli İfade) kuralı oluşturur (condition: 6 = Regex match).
*   **Entity Ataması:** Eşleşen e-postaları ilgili Entity'ye atayan bir aksiyon ekler.
*   **Akıllı Güncelleme:** Mevcut kuralları siler ve yeniden oluşturarak güncel tutar.
*   **Dry-Run (Test) Modu:** Varsayılan olarak değişiklik yapmaz, sadece ne yapacağını ekrana basar.
*   **Pagination Desteği:** Büyük veri setlerini (1000+ Entity, 100+ kural) otomatik olarak parçalayarak çeker.
*   **Session Yönetimi:** API session'ı otomatik olarak başlatılır ve script sonunda güvenli şekilde kapatılır.
*   **Merkezi Config:** Config dosyalarını merkezi `Config/` dizininden okur.

## Gereksinimler

*   Python 3.x
*   Gerekli Python kütüphaneleri:
    *   `requests`
    *   `urllib3`
    *   `argparse` (Python standart kütüphanesi)
    *   `json` (Python standart kütüphanesi)

## Kurulum

1.  Gerekli kütüphaneleri yükleyin:
    ```bash
    pip install requests urllib3
    ```

2.  Config dosyası merkezi `../Config/config.json` konumunda olmalıdır:
    ```json
    {
        "GLPI_URL": "https://your-glpi-url/apirest.php",
        "GLPI_APP_TOKEN": "your_app_token",
        "GLPI_USER_TOKEN": "your_user_token"
    }
    ```
    
    > **Not:** Script config dosyasını şu sırayla arar:
    > 1. Mevcut dizin (`config.json`)
    > 2. `../Config/config.json`
    > 3. `../../Config/config.json`

## Kullanım

### Dry-Run (Test Modu)
Varsayılan olarak script test modunda çalışır. Hiçbir değişiklik yapmaz, sadece oluşturulacak kuralları listeler.

```bash
python rules_email.py
```

Örnek Çıktı:
```text
Connecting to https://your-glpi-url/apirest.php...
Fetching Entities...
Fetching existing Mail Rules...
Found 33 entities and 261 existing rules.
------------------------------------------------------------
PROPOSE: CREATE rule 'Auto-Email-IT-Department' for Entity 'IT Department' (ID: 5)
  Criteria: From email header (name) REGEX MATCHES '/@company\.com$/i'
  Action 1: Assign Entity -> IT Department (ID: 5)
PROPOSE: UPDATE rule 'Auto-Email-Finance' for Entity 'Finance' (ID: 6)
  Criteria: From email header (name) REGEX MATCHES '/@finance\.com$/i'
  Action 1: Assign Entity -> Finance (ID: 6)
------------------------------------------------------------
Session closed.
```

### Değişiklikleri Uygulama (--force)
Kuralları gerçekten oluşturmak için `--force` parametresini kullanın.

```bash
python rules_email.py --force
```

Örnek Çıktı (--force ile):
```text
PROPOSE: CREATE rule 'Auto-Email-IT-Department' for Entity 'IT Department' (ID: 5)
  Criteria: From email header (name) REGEX MATCHES '/@company\.com$/i'
  Action 1: Assign Entity -> IT Department (ID: 5)
  ✓ CREATED Rule ID: 1461

PROPOSE: UPDATE rule 'Auto-Email-Finance' for Entity 'Finance' (ID: 6)
  Criteria: From email header (name) REGEX MATCHES '/@finance\.com$/i'
  Action 1: Assign Entity -> Finance (ID: 6)
  Purging existing criteria and actions for Rule ID: 1462
  ✓ UPDATED Rule ID: 1462
```

## Çalışma Mantığı

1.  **Konfigürasyon Yükleme:** `config.json` dosyasından GLPI bağlantı bilgileri okunur.
2.  **Session Başlatma:** GLPI API'ye `initSession` ile bağlanır ve session token alınır.
3.  **Veri Toplama:**
    *   `fetch_all_entities()`: Tüm Entity'leri pagination ile çeker (1000'er kayıt).
    *   `fetch_existing_rules()`: Mevcut `RuleMailCollector` kurallarını pagination ile çeker (100'er kayıt).
4.  **Kural Oluşturma İşlemi:**
    *   Her Entity için `mail_domain` alanı kontrol edilir.
    *   Root entity (ID: 0) atlanır.
    *   `mail_domain` boş veya geçersiz olan Entity'ler atlanır.
    *   Kural adı: `Auto-Email-{Entity-Adı}` formatında oluşturulur (boşluklar tire ile değiştirilir).
    *   **Mevcut kural varsa:** Eski criteria/action'lar silinir ve yenileri eklenir (UPDATE).
    *   **Mevcut kural yoksa:** Yeni kural oluşturulur (CREATE).
    *   **Regex Pattern:** `/@domain\.com$/i` formatında oluşturulur (domain sonunda eşleşme).
    *   **Dry-run modunda:** Sadece ekrana yazdırılır.
    *   **Force modunda:**
        *   Kural oluşturulur (`RuleMailCollector` endpoint'i).
        *   Kriter eklenir (`RuleCriteria` - from header, regex match).
        *   Aksiyon eklenir (`RuleAction` - entities_id assign).
5.  **Session Kapatma:** `killSession` ile API session'ı güvenli şekilde kapatılır.

## Script Yapısı

### Fonksiyonlar

*   `load_config()`: config.json dosyasını yükler.
*   `init_session()`: GLPI API session'ı başlatır.
*   `kill_session()`: GLPI API session'ı kapatır.
*   `fetch_all_entities()`: Tüm Entity'leri pagination ile çeker.
*   `fetch_existing_rules()`: Mevcut mail collector kurallarını çeker.
*   `create_rule()`: Yeni kural oluşturur (dry-run veya gerçek).

### Kural Detayları

Her oluşturulan kural şu özelliklere sahiptir:

*   **Name:** `Auto-Email-{Entity-Name}` (entity adındaki boşluklar tire ile değiştirilir)
*   **Match:** AND (tüm kriterler eşleşmeli)
*   **Active:** Evet (is_active: 1)
*   **Sub Type:** RuleMailCollector
*   **Ranking:** 1
*   **Criteria:**
    *   Field: `from` (Gönderen e-posta adresi)
    *   Condition: 6 (Regex match)
    *   Pattern: `/@domain\.com$/i` (büyük/küçük harf duyarsız, satır sonu eşleşmesi)
*   **Action:**
    *   Type: assign
    *   Field: `entities_id`
    *   Value: Entity ID

> [!NOTE]
> Script, "Stop processing on this rule" aksiyonunu **eklemez**. Bu sayede aynı e-posta için birden fazla kural çalışabilir.

## Notlar ve Önemli Bilgiler

*   **Root Entity:** Root entity (ID: 0) otomatik olarak atlanır.
*   **Mail Domain Kontrolü:** `mail_domain` alanı boş olan veya `@` karakteri içermeyen Entity'ler sessizce atlanır.
*   **Kural İsimlendirme:** Kurallar `Auto-Email-{Entity-Name}` formatında isimlendirilir (hyphen-only format). Entity adındaki boşluklar otomatik olarak tire ile değiştirilir. Bu format değiştirilirse, çift kayıt önleme çalışmaz.
*   **SSL Sertifika Uyarıları:** InsecureRequestWarning uyarıları bastırılmıştır (`verify=False` kullanıldığı için). Üretim ortamında SSL sertifikası doğrulaması önerilir.
*   **API Yetkileri:** Script'in çalışması için kullanılan API token'ının `RuleMailCollector`, `RuleCriteria`, `RuleAction` ve `Entity` endpoint'lerine okuma/yazma yetkisi olmalıdır.

> [!IMPORTANT]
> Scriptin çalışması için GLPI üzerinde Entity (Birim) tanımlarken **"Mail domain surrogates entity"** (E-posta etki alanı vekili) alanının doldurulması zorunludur. Script bu alanı (`mail_domain`) referans alır.

## Sorun Giderme

*   **"config.json not found" hatası:** Script ile aynı dizinde `config.json` dosyası olduğundan emin olun.
*   **"Failed to initialize session" hatası:** GLPI URL, App Token ve User Token bilgilerini kontrol edin.
*   **Kurallar oluşturulmuyor:** `--force` parametresini kullandığınızdan emin olun. Dry-run modunda hiçbir değişiklik yapılmaz.
*   **Bazı Entity'ler atlanıyor:** Entity'nin `mail_domain` alanının dolu ve geçerli bir e-posta domain'i içerdiğinden emin olun (örn: `@company.com`).

---

## Özellikler (v2.4)
- ✅ **Timeout Koruması:** Tüm API çağrılarında 30sn timeout
- ✅ **Duplicate Prevention:** Range parametresi (0-5000) ile güvenli silme
- ✅ **Güvenli Güncelleme:** Mevcut kuralları ID kontrolü ile günceller
- ✅ **Standardize Naming:** Hyphen-only format (`Auto-Email-Entity-Name`)
- ✅ **Space Handling:** Entity adlarındaki boşluklar otomatik olarak tire ile değiştirilir

---
**Versiyon:** 2.4  
**Son Güncelleme:** 25 Aralık 2024  



Hazırlayan : Bora Ergül
