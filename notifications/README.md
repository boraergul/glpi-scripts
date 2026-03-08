# GLPI Notification Export Tool

Bu script, GLPI sistemindeki tüm bildirimleri (notifications) detaylı bir şekilde CSV formatında dışa aktarır.

## 📋 Özellikler

- ✅ Tüm GLPI bildirimlerini otomatik olarak export eder
- ✅ Bildirim şablonları (templates) ve alıcıları (recipients) dahil
- ✅ Entity, grup, profil ve kullanıcı bilgilerini çözümler
- ✅ Sayfalama (pagination) desteği ile büyük veri setlerini işler
- ✅ Akıllı önbellek (cache) mekanizması ile performans optimizasyonu
- ✅ Detaylı log kaydı (`export_notifications.log`)
- ✅ UTF-8 BOM desteği ile Türkçe karakter uyumluluğu

## 📦 Gereksinimler

```bash
pip install requests urllib3
```

## ⚙️ Konfigürasyon

Script, `config.json` dosyasını şu konumlarda arar:
1. Script ile aynı dizin
2. Bir üst dizin (`../`)
3. `../config/` dizini
4. `../../Config/` dizini

### config.json Formatı

```json
{
  "GLPI_URL": "https://your-glpi-server/apirest.php",
  "GLPI_APP_TOKEN": "your_app_token_here",
  "GLPI_USER_TOKEN": "your_user_token_here"
}
```

> [!IMPORTANT]
> `config.json` dosyasını `.gitignore` dosyanıza eklemeyi unutmayın!

## 🚀 Kullanım

```bash
python export_notifications.py
```

Script çalıştırıldığında:
1. GLPI API'ye bağlanır
2. Tüm bildirimleri ve ilgili verileri çeker
3. `notifications_export_improved.csv` dosyasını oluşturur
4. İşlem loglarını `export_notifications.log` dosyasına kaydeder

## 📊 Çıktı Formatı

CSV dosyası aşağıdaki sütunları içerir:

| Sütun | Açıklama |
|-------|----------|
| **Notification ID** | Bildirimin benzersiz ID'si |
| **Notification Name** | Bildirimin adı |
| **Entity** | İlgili entity (kuruluş) |
| **Type** | Bildirim türü (Ticket, Problem, Change, vb.) |
| **Active** | Aktif durumu (Yes/No) |
| **Event Label** | Tetikleyici olay (New item, Update, Solved, vb.) |
| **Template** | Kullanılan bildirim şablonu ve modu |
| **Recipient Type** | Alıcı türü (User, Group, Profile) |
| **Recipient Name** | Alıcının adı veya rolü |

## 🎯 Event Etiketleri

Script, GLPI event kodlarını kullanıcı dostu etiketlere çevirir:

- `new` → "New item"
- `update` → "Update of an item"
- `solved` → "Item solved"
- `add_task` → "New task"
- `closed` → "Closing of the item"
- `validation` → "Validation request"
- `user_mention` → "User mentioned"
- `satisfaction` → "Satisfaction survey"

## 👥 Recipient Türleri

Script, dinamik alıcı rollerini tanır:

- **Requester** - Talep sahibi
- **Technician in charge of the ticket** - Atanan teknisyen
- **Group in charge of the ticket** - Atanan grup
- **Approver** - Onaylayıcı
- **Watcher** - İzleyici
- **Administrator** - Yönetici
- **Project Manager** - Proje yöneticisi

### Özel Modül Eşleştirmeleri (v2.1)

Domain ve Proje modülleri için aşağıdaki özel roller desteklenir:

- **Domain:** Group in charge of the domain, Technician in charge of the domain
- **Project:** Manager in charge of the project, Technician in charge of the project
- **Project Task:** Technician in charge of the project task

> **Not:** `Alert Tickets not closed` bildirimi için "Requester" (ID: 1) rolü otomatik olarak "Administrator" olarak eşleştirilir.

## 📝 Log Dosyası

Script, tüm işlemleri `export_notifications.log` dosyasına kaydeder:

```
2026-01-08 22:53:00 - INFO - Configuration loaded from: ../config.json
2026-01-08 22:53:01 - INFO - Initializing GLPI API session...
2026-01-08 22:53:02 - INFO - Session initialized successfully
2026-01-08 22:53:02 - INFO - Fetching NotificationTemplate...
2026-01-08 22:53:03 - INFO - Completed fetching NotificationTemplate: 45 items
```

## 🔧 Performans Optimizasyonları

1. **Önbellek Mekanizması**: User, Group, Profile ve Entity verileri önbelleğe alınır
2. **Toplu Veri Çekme**: Pagination ile 1000'er kayıt halinde veri çekilir
3. **Akıllı Entity Çözümleme**: Her entity sadece bir kez API'den çekilir
4. **Timeout Yönetimi**: API çağrılarında timeout koruması

## ⚠️ Bilinen Sınırlamalar

- SSL sertifika doğrulaması devre dışı (`verify=False`)
- Çok büyük GLPI kurulumlarında (10,000+ kullanıcı) ilk çalıştırma yavaş olabilir

## 🐛 Hata Ayıklama

Sorun yaşarsanız:

1. `export_notifications.log` dosyasını kontrol edin
2. GLPI API token'larınızın geçerli olduğundan emin olun
3. GLPI API'nin aktif olduğunu doğrulayın
4. Kullanıcınızın gerekli izinlere sahip olduğunu kontrol edin

## 📄 Lisans

Bu script, GLPI yönetimi için geliştirilmiş bir yardımcı araçtır.

## 🤝 Katkıda Bulunma

Önerileriniz ve geliştirmeleriniz için pull request gönderebilirsiniz.
