# notifications_export_import

Bir GLPI sistemindeki **Notification** yapılandırmalarını dışa aktarır (CSV) ve başka bir GLPI sistemine aktarır.

> **Amaç:** Sistem-A → CSV → Sistem-B notification transferi.  
> `templates_export_import/` modülünden farkı: burada notification template içerikleri değil, notification *yapılandırmaları* (hangi olayda, hangi alıcıya, hangi şablonla bildirim gönderileceği) aktarılır.

---

## 📂 Dosyalar

| Dosya | Açıklama |
|---|---|
| `export_notifications.py` | Kaynak GLPI'den notification'ları CSV'ye aktarır |
| `import_notifications.py` | CSV'deki notification'ları hedef GLPI'ye yükler |
| `gui_notifications_import_v2.py` | Export + Import + Transfer için grafik arayüz (güncel) |
| `export_notifications.log` | Export çalışma logu (otomatik oluşturulur) |
| `import_notifications.log` | Import çalışma logu (otomatik oluşturulur) |
| `notifications_<profil>_<tarih>.csv` | Export çıktısı (otomatik oluşturulur) |

> **Not:** `gui_notifications_import_v2.py`, `export_notifications.py` ve `import_notifications.py` modüllerini direkt import eder. Bu iki script silinirse GUI çalışmaz.

---

## 🔄 Workflow

```
Kaynak GLPI  ──[export_notifications.py]──▶  CSV Dosyası  ──[import_notifications.py]──▶  Hedef GLPI
```

---

## 🚀 Kullanım

### GUI ile Kullanım (Önerilen)

```bash
python gui_notifications_import_v2.py
```

GUI üç işlem sunar:

| Buton | Açıklama |
|---|---|
| 📤 **Export Kaynak** | Seçili kaynak sunucudan CSV oluşturur |
| 📥 **Export Hedef** | Seçili hedef sunucudan CSV oluşturur (karşılaştırma için) |
| ⚡ **Transfer** | Kaynaktan export edip otomatik olarak Hedefe import eder (tek tıkla) |

### CLI ile Kullanım

**Export:**
```bash
cd "\Projeler\Script\notifications_export_import"
python export_notifications.py
```

**Import:**
```bash
python import_notifications.py                               # En yeni CSV otomatik seçilir
python import_notifications.py notifications_X.csv           # Belirli bir CSV
python import_notifications.py --dry-run                     # Test modu (değişiklik yapmaz)
```

---

## ⚙️ Yapılandırma

### `servers.json`

GUI'nin kullandığı sunucu profil dosyasıdır. Aynı `servers.json` dosyası `templates_export_import/` modülüyle paylaşılabilir.

```json
{
    "servers": {
        "ITSM": {
            "url": "https://itsm.example.com/apirest.php",
            "app_token": "...",
            "user_token": "...",
            "description": "Ana ITSM sistemi"
        },
        "GLPI11L": {
            "url": "https://glpi11.example.com/apirest.php",
            "app_token": "...",
            "user_token": "...",
            "description": "Test ortamı"
        }
    }
}
```

> `servers.json` mevcut değilse GUI üzerinden profil eklenebilir.

### CLI için `config.json`

CLI scriptleri şu sırayla config arar:
1. `notifications_export_import/config.json`
2. `../config.json`
3. `../../Config/config.json`

---

## 📊 CSV Kolonları

| Kolon | Açıklama |
|---|---|
| `Name` | Notification adı |
| `Active` | Aktif mi? (0/1) |
| `Entity` | Bağlı entity adı |
| `Item Type` | İlgili nesne türü (Ticket, Problem, vb.) |
| `Event` | Tetikleyen olay (new_ticket, update, vb.) |
| `Mode` | İletim modu (mailing, ajax, vb.) |
| `Template Name` | Bağlı notification template adı |
| `Recipients` | Bildirim alıcıları (`;` ile ayrılmış) |

---

## 🔧 Teknik Detaylar

### Export — Kullanılan GLPI Endpoint'leri
- `GET /Notification` — Tüm notification'ları çeker
- `GET /Notification/{id}/Notification_NotificationTemplate` — Bağlı şablonları çeker
- `GET /NotificationTarget` veya sub-resource — Alıcıları çeker

### Import — Kullanılan GLPI Endpoint'leri
- `GET /Notification` — Mevcut notification'ları kontrol eder
- `POST /Notification` — Yeni notification oluşturur
- `PUT /Notification/{id}` — Mevcut notification'ı günceller

---

## 🔗 İlgili Modüller

| Modül | Fark |
|---|---|
| `templates_export_import/` | Notification *template içeriklerini* (konu, HTML, metin) aktarır |
| `notifications/` | Notification ayarlarını tek sistem üzerinde yönetir |

---

**Versiyon:** 1.0  
**Son Güncelleme:** 22 Şubat 2026  
**Hazırlayan:** Bora Ergül
