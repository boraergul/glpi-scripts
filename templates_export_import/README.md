# templates_export_import

Bir GLPI sistemindeki **Notification Template**'lerini dışa aktarır (CSV) ve başka bir GLPI sistemine aktarır.

> **Amaç:** Sistem-A → CSV → Sistem-B template transferi.  
> `templates_import/` modülünden farkı: burada kaynak da GLPI API'sidir; `templates_new/` dizinindeki elle yazılmış şablonlara bağımlı değildir.

---

## 📂 Dosyalar

| Dosya | Açıklama |
|---|---|
| `export_templates.py` | Kaynak GLPI'den template'leri CSV'ye aktarır |
| `import_templates.py` | CSV'deki template'leri hedef GLPI'ye yükler |
| `Gui_templates_export_v2.py` | Export + Import için grafik arayüz (güncel) |
| `servers.json` | Kayıtlı sunucu profilleri (GUI tarafından kullanılır) |
| `export_templates.log` | Export çalışma logu (otomatik oluşturulur) |
| `import_templates.log` | Import çalışma logu (otomatik oluşturulur) |
| `templates_export_<tarih>.csv` | Export çıktısı (otomatik oluşturulur) |

---

## 🔄 Workflow

```
Kaynak GLPI  ──[export_templates.py]──▶  CSV Dosyası  ──[import_templates.py]──▶  Hedef GLPI
```

---

## 🚀 Kullanım

### Adım 1 — Export (Kaynak GLPI → CSV)

```bash
cd "\Projeler\Script\templates_export_import"
python export_templates.py
```

- `config.json`'daki bağlantı bilgilerini kullanır (kaynak sistem).
- Tüm template'leri, çevirilerini ve bağlı bildirim linklerini çeker.
- `templates_export_<YYYYMMDD_HHMMSS>.csv` dosyası oluşturur.

### Adım 2 — Import (CSV → Hedef GLPI)

```bash
python import_templates.py                            # En yeni CSV otomatik seçilir
python import_templates.py templates_export_X.csv     # Belirli bir CSV
python import_templates.py --dry-run                  # Test modu (değişiklik yapmaz)
```

- Çalışırken hedef GLPI URL ve token bilgileri **interaktif olarak** sorulur.
- Bağlantı testi yapılır, onay alındıktan sonra import başlar.
- Template varsa günceller, yoksa oluşturur (upsert).

### GUI ile Kullanım

```bash
python Gui_templates_export_v2.py
```

> **Not:** `Gui_templates_export_v2.py`, `export_templates.py` ve `import_templates.py` modüllerini direkt import eder. Bu iki script silinirse GUI çalışmaz.

- Kaynak ve hedef sunucu profillerini `servers.json`'dan okur.
- Export, Import ve Transfer (tek tıkla export+import) işlemlerini sunar.

---

## 📊 CSV Kolonları

| Kolon | Açıklama |
|---|---|
| `Template ID` | GLPI'daki şablon ID'si |
| `Name` | Şablon adı |
| `Item Type` | Bağlı nesne türü (Ticket, Problem, vb.) |
| `Comments` | Şablon açıklaması |
| `CSS` | Şablona ait CSS |
| `Date Modified` | Son değişiklik tarihi |
| `Date Creation` | Oluşturulma tarihi |
| `Translation Language` | Dil kodu (`tr_TR`, `en_GB`, vb.) |
| `Translation Subject` | E-posta konu satırı |
| `Translation Content HTML` | HTML içerik |
| `Translation Content Text` | Düz metin içerik |
| `Linked Notifications` | Bağlı bildirimler (`ad [mod]` formatında, `\|` ile ayrılmış) |

> Her template için birden fazla dil çevirisi varsa her dil **ayrı satır** olarak yazılır.

---

## ⚙️ Yapılandırma

### `config.json` (kaynak sistem)

```json
{
    "GLPI_URL": "https://kaynak-glpi.example.com/apirest.php",
    "GLPI_APP_TOKEN": "your_app_token_here",
    "GLPI_USER_TOKEN": "your_user_token_here"
}
```

Config dosyası şu sırayla aranır:
1. `templates_export_import/config.json`
2. `../config.json`
3. `../config/config.json`
4. `../../Config/config.json`

### `servers.json` (GUI için — opsiyonel)

```json
{
    "Kaynak": {
        "url": "https://kaynak.example.com/apirest.php",
        "app_token": "...",
        "user_token": "..."
    },
    "Hedef": {
        "url": "https://hedef.example.com/apirest.php",
        "app_token": "...",
        "user_token": "..."
    }
}
```

---

## 🔧 Teknik Detaylar

### Export — Kullanılan GLPI Endpoint'leri
- `GET /NotificationTemplate` — Tüm şablonları çeker
- `GET /NotificationTemplate/{id}/NotificationTemplateTranslation` — Çevirileri çeker
- `GET /Notification_NotificationTemplate` — Bildirim ↔ şablon linklerini çeker
- `GET /Notification` — Bildirim adlarını çeker

### Import — Kullanılan GLPI Endpoint'leri
- `GET /NotificationTemplate` — Mevcut şablonları kontrol eder
- `POST /NotificationTemplate` — Yeni şablon oluşturur
- `PUT /NotificationTemplate/{id}` — Mevcut şablonu günceller
- `GET /NotificationTemplate/{id}/NotificationTemplateTranslation` — Mevcut çevirileri kontrol eder
- `POST /NotificationTemplateTranslation` — Yeni çeviri ekler
- `PUT /NotificationTemplateTranslation/{id}` — Mevcut çeviriyi günceller

---

## 🔗 İlgili Modüller

| Modül | Fark |
|---|---|
| `templates_import/` | `templates_new/` dizinindeki Python/HTML kaynaklardan GLPI'ye yükler (tek sistem) |
| `notifications_export_import/` | Notification yapılandırmalarını (kural, alıcı) transfer eder; template içriklerini değil |

---

**Versiyon:** 1.0  
**Son Güncelleme:** 22 Şubat 2026  
**Hazırlayan:** Bora Ergül
