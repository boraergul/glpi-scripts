# GLPI ITIL Kategori İçe Aktarma Aracı (Python)

Bu script, hazırlanan bir CSV dosyasındaki ITIL kategorilerini (Incident/Request) hiyerarşik bir yapıda GLPI'ya otomatik olarak aktarır.

## 1. Ön Gereksinimler

*   **Python 3.x:** Yüklü olmalıdır.
*   **Requests Kütüphanesi:**
    ```bash
    pip install requests
    ```
*   **Network Erişimi:** Scriptin çalıştığı makine, GLPI sunucusuna HTTPS üzerinden erişebilmelidir.

## 2. Kurulum ve Yapılandırma

### A. config.json
Scriptin bulunduğu dizinde `config.json` adında bir dosya oluşturun ve aşağıdaki bilgileri girin. Bu dosya GitHub'a **gönderilmemelidir**.

```json
{
    "GLPI_URL": "https://glpi.domain.com/apirest.php",
    "GLPI_APP_TOKEN": "SIZIN_APP_TOKEN_DEGERINIZ",
    "GLPI_USER_TOKEN": "SIZIN_USER_TOKEN_DEGERINIZ"
}
```

*   **GLPI_URL:** GLPI API adresi (genellikle `/apirest.php` ile biter).
*   **App-Token:** `Setup > General > API` menüsünden oluşturulur.
*   **User-Token:** Yetkili bir kullanıcının (Super-Admin önerilir) API token'ı (`Administration > Users > [User] > API Token`).

### B. itil_categories.csv
Kategorilerin bulunduğu dosya script ile aynı dizinde olmalıdır.
*   **Format:** `Code - Name` yapısında olmalıdır (Örn: `01.01 - Firewall`).
*   **Ayrıraç (Delimiter):** Noktalı virgül (`;`) kullanılmalıdır.
*   **Kodlama:** `UTF-8` (veya `UTF-8-SIG`) olmalıdır.

**Örnek CSV İçeriği:**
```csv
name;
01 - Network;
01.01 - Firewall;
01.02 - Switch;
02 - Sistem;
02.01 - Sunucular;
```

**Mantık:**
*   Script ismin başındaki numarayı "Code" (Kod) olarak alır.
*   Nokta ile ayrılmış yapıyı analiz ederek hiyerarşiyi kurar (Örn: `01.01` kategorisi, `01` kodlu kategorinin altına eklenir).

## 3. Kullanım

Scripti terminal veya komut satırından çalıştırın:

```bash
python import_itil_categories.py
```

### Beklenen Çıktılar:
*   **CREATED:** Kategori başarıyla oluşturulduğunda ve ID'si döndüğünde.
*   **Warning:** Üst kategori (Parent) bulunamadığında kök dizine ekler.
*   **FAILED:** Bir hata oluştuğunda (Örn: Yetki hatası, API hatası).

## 4. Sorun Giderme
*   `Error loading config.json`: JSON formatını kontrol edin.
*   `Session initialization failed`: Token'larınızı ve GLPI URL'sini kontrol edin.
*   Kategoriler iç içe geçmiyorsa: CSV dosyasındaki sıralamaya dikkat edin. Üst kategoriler (01), alt kategorilerden (01.01) **önce** gelmelidir.
