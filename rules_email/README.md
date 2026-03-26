# GLPI Email Rules Automation (v3.0)

Bu script, GLPI üzerindeki Entity'ler (Birimler) için otomatik olarak e-posta kuralları oluşturur. Her bir Entity'nin `mail_domain` (e-posta alan adı) bilgisini kullanarak, o alan adından gelen e-postaların otomatik olarak ilgili Entity'ye atanmasını sağlar.

## Özellikler (v3.0)

*   **Akıllı Senkronizasyon (Smart Sync):** Mevcut kuralları kontrol eder; eğer kural zaten doğruysa (regex ve entity ID aynıysa) API çağrısı yapmadan atlar.
*   **Profesyonel Loglama:** Tüm işlemler hem konsola hem de `rules_email.log` dosyasına kaydedilir.
*   **Detaylı Özet Raporu:** İşlem sonunda oluşturulan, güncellenen ve atlanan birimleri listeleyen kapsamlı bir rapor sunar.
*   **Dayanıklı Regex:** `re.escape()` kullanarak domain isimlerindeki özel karakterleri (nokta vb.) güvenli bir şekilde işler.
*   **Güvenli Oturum Yönetimi:** `glpi_session` context manager ile session token'ın her durumda (hata olsa bile) kapatılması garanti edilir.
*   **SSL Konfigürasyonu:** `config.json` üzerinden `verify_ssl: true/false` ayarı yapılabilir.
*   **Pagination Desteği:** Büyük veri setleri (1000+ Entity) için otomatik sayfalama yapar.

## Kurulum

1.  Gerekli kütüphaneleri yükleyin:
    ```bash
    pip install requests
    ```

2.  Config dosyası merkezi `../Config/config.json` veya yerel dizinde olmalıdır:
    ```json
    {
        "GLPI_URL": "https://glpi.firma.com/apirest.php",
        "GLPI_APP_TOKEN": "your_app_token",
        "GLPI_USER_TOKEN": "your_user_token",
        "verify_ssl": false
    }
    ```

## Kullanım

### Dry-Run (Test Modu)
Varsayılan olarak script hiçbir değişiklik yapmaz, sadece rapor sunar:
```bash
python rules_email.py
```

### Değişiklikleri Uygulama (--force)
Kuralları gerçekten oluşturmak veya güncellemek için:
```bash
python rules_email.py --force
```

## Örnek Rapor Çıktısı
```text
DETAILED EXECUTION SUMMARY REPORT
------------------------------------------------------------
NEW RULES CREATED (1):
  + Assan Group
ALREADY UP-TO-DATE (28):
  - Ultron Bilişim
  ...
SKIPPED - MISSING MAIL DOMAIN (28):
  ? Müşteriler
------------------------------------------------------------
Total Processed: 57 entities.
```

## Çalışma Mantığı

1.  **Konfigürasyon:** `config.json` yüklenir ve GLPI oturumu açılır.
2.  **Veri Toplama:** Tüm Entity'ler ve mevcut `RuleMailCollector` kuralları çekilir.
3.  **Karşılaştırma:** Her birim için kuralın varlığı ve içeriği (regex) kontrol edilir.
4.  **İşlem:** 
    - Kural yoksa veya farklıysa: CREATE/UPDATE işlemi yapılır.
    - Kural aynıysa: Atlanır (SKIP).
5.  **Raporlama:** İşlem sonunda detaylı özet raporu loglanır.
6.  **Kapatma:** Oturum güvenli bir şekilde kapatılır.

## Önemli Notlar
*   **Mail Domain:** GLPI tarafında Birim (Entity) tanımında **"Mail domain surrogates entity"** alanının dolu olması gerekir. Boş olan birimler otomatik olarak atlanır.
*   **Kural İsimlendirme:** Kurallar `Auto-Email-{Birim-Adı}` formatında oluşturulur.

---
**Versiyon:** 3.0  
**Son Güncelleme:** 25 Mart 2026  
**Hazırlayan:** Bora Ergül  
