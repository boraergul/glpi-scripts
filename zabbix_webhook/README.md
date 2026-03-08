# Zabbix - GLPI Entegrasyonu (v2.2) Kurulum Kılavuzu

Bu belge, Zabbix alarmlarının otomatik olarak GLPI üzerinde **Incident (Arıza Kaydı)** oluşturmasını ve Zabbix üzerinde problem çözüldüğünde GLPI ticket'ının otomatik olarak **Solved (Çözüldü)** statüsüne çekilmesini sağlayan entegrasyonun kurulum adımlarını içerir.

## 1. Ön Hazırlıklar (Prerequisites)

*   **Zabbix Sunucusu:** JavaScript webhook desteği olan bir sürüm (Zabbix 5.x, 6.x, 7.x).
*   **GLPI Sunucusu:** REST API eklentisi aktif edilmiş olmalı.
*   **Ağ Erişimi:** Zabbix sunucusu, GLPI sunucusunun API portuna (Genellikle 80 veya 443) erişebilmelidir.

---

## 2. GLPI Tarafı Yapılandırması

### 2.1. API'yi Aktif Etme
1.  GLPI'da **Setup** > **General** > **API** sekmesine gidin.
2.  **Enable Rest API**: `Yes`
3.  **Enable login with external token**: `Yes`
4.  **Enable login with credentials**: `Yes` (Opsiyonel ama test için iyi olur).
5.  **API URL**: Genellikle `https://glpi-adresiniz/apirest.php/` şeklindedir.

### 2.2. API Kullanıcısı ve Token Oluşturma
1.  **Administration** > **Users** menüsünden Zabbix için özel bir kullanıcı oluşturun (örn: `zabbix_api`).
2.  Bu kullanıcıya **Self-Service** veya **Technician** profilini atayın.
3.  Kullanıcının detaylarına girip **API Token** sekmesinden bir **User Token** oluşturun ve kaydedin.
    *   *Bu token Zabbix Media Type ayarlarında `glpi_user_token` olarak kullanılacak.*

### 2.3. Yetkiler
Kullanıcının profilinde şu yetkilerin olduğundan emin olun:
*   Ticket oluşturma (Create).
*   Ticket güncelleme (Update).
*   Ticket kapatma/çözme (Update Status to Solved).
*   Followup (Yorum) ekleme.

---

## 3. Zabbix Tarafı Yapılandırması

### 3.1. Webhook Scriptini Hazırlama
Proje klasöründeki veya `zabbixhook_v2.js` dosyasının içeriğini bir metin editörüyle açıp kopyalayın.

### 3.2. Media Type (Ortam Türü) Oluşturma
1.  Zabbix arayüzünde **Administration** > **Media types** menüsüne gidin.
2.  Sağ üstten **Create media type** butonuna tıklayın.
3.  **Name**: `GLPi Webhook v2`
4.  **Type**: `Webhook`
5.  **Parameters** kısmına aşağıdaki listeyi **EKSİKSİZ** ekleyin:

| Name | Value | Açıklama |
| :--- | :--- | :--- |
| `alert_message` | `{ALERT.MESSAGE}` | Alarm mesajı |
| `alert_subject` | `{ALERT.SUBJECT}` | Alarm başlığı |
| `event_id` | `{EVENT.ID}` | Olay ID'si |
| `event_nseverity` | `{EVENT.NSEVERITY}` | Önem derecesi (Sayısal) |
| `event_severity` | `{EVENT.SEVERITY}` | Önem derecesi (Yazı) |
| `event_source` | `{EVENT.SOURCE}` | Kaynak (Trigger vs) |
| `event_update_status` | `{EVENT.UPDATE.STATUS}` | Güncelleme durumu |
| `event_value` | `{EVENT.VALUE}` | Olay durumu (Problem/Resolve) |
| `glpi_app_token` | `(Varsa Uygulama Tokeni)` | Opsiyonel |
| `glpi_ticket_id` | `{EVENT.TAGS.__zbx_glpi_ticket_id}` | **KRİTİK:** Ticket ID'yi geri okumak için |
| `glpi_url` | `https://itsm.ultron.com.tr` | GLPI Adresiniz (Sonunda slash olmasın) |
| `glpi_user_token` | `(GLPI'dan aldığınız User Token)` | Auth Token |
| `host` | `{HOST.HOST}` | **KRİTİK:** Varlık eşleştirmesi için Hostname |
| `trigger_id` | `{TRIGGER.ID}` | Tetikleyici ID'si |
| `zabbix_url` | `YOUR_ZABBIX_URL` | Zabbix sunucu adresi |

6.  **Script** alanına kopyaladığınız `zabbixhook_v2.js` içeriğini yapıştırın.
7.  **Message templates** sekmesinde varsayılan şablonları (Problem, Recovery vb.) ekleyin.
8.  **Add** diyerek kaydedin.

### 3.3. Action (Aksiyon) Oluşturma
1.  **Configuration** > **Actions** > **Trigger actions** menüsüne gidin.
2.  **Create action** butonuna tıklayın.
3.  **Action** sekmesinde bir isim verin ve koşulları (Conditions) belirleyin (örn: `Trigger severity >= Average`).
4.  **Operations** sekmesinde:
    *   **Add** deyin.
    *   **Send to users**: İlgili yönetici grubunu seçin.
    *   **Send only to**: `GLPi Webhook v2` seçin.
5.  **Recovery operations** sekmesinde:
    *   **Add** deyin.
    *   **Send to users**: İlgili yönetici grubunu seçin.
    *   **Send only to**: `GLPi Webhook v2` seçin. (Bu adım Ticket'ın kapanması için şarttır).

---

## 4. Sorun Giderme (Troubleshooting)

### Ticket Açılmıyor
*   **Action Log:** Reports -> Action log kısmına bakın. "Failed" yazıyorsa hatayı okuyun.
*   **Varlık Bulunamadı:** Logda "Asset not found" yazıyorsa, Script Hostname ile GLPI'da eşleşen bir cihaz (Bilgisayar veya Ağ Cihazı) bulamıyordur. Cihaz isminin GLPI ile birebir aynı olduğundan veya `host` parametresinin `{HOST.HOST}` olduğundan emin olun.

### Ticket Kapanmıyor (Status "İşlemde" kalıyor)
*   **Parametre Hatası:** Media Type parametrelerinde `glpi_ticket_id` parametresinin değeri kesinlikle `{EVENT.TAGS.__zbx_glpi_ticket_id}` olmalıdır. Eğer `{EVENT.TAGS.__zbx_glpi_problem_id}` kalmışsa düzeltin.
*   **Eski Ticketlar:** Script veya ayar değişikliğinden ÖNCE açılmış ticketlar, gerekli "Tag" bilgisine sahip olmadığı için otomatik kapanmaz. Manuel kapatılmalıdır. Sadece yeni alarmlar otomatik kapanır.
*   **Yetki:** GLPI API loglarında "Permission denied" görürseniz, kullanıcının "Update Ticket" ve "Solve Ticket" yetkisini kontrol edin.

---

**Not:** Bu Script, ID `228` (ITIL Category), ID `7` (Assigned Group) ve ID `8` (Request Source - Monitoring) gibi değerleri kod içinde sabit (hardcoded) kullanmaktadır. GLPI ID'leriniz farklıysa `zabbixhook_v2.js` dosyasındaki `createTicket` fonksiyonunu düzenlemelisiniz.

---

## 5. Teknik Detaylar (Kod Mantığı)

Scriptin arkaplanında çalışan önemli mantıksal süreçler şunlardır:

### 5.1. Önem Derecesi (Severity) Eşleştirmesi
Zabbix alarm seviyeleri, GLPI ticket önceliklerine (Urgency, Impact, Priority) şöyle dönüştürülür:

| Zabbix Severity | Urgency | Impact | Priority (Sonuç) |
| :--- | :--- | :--- | :--- |
| **Disaster** | 5 (Very High) | 5 (Very High) | **5 (Major)** |
| **High** | 4 (High) | 4 (High) | **4 (High)** |
| **Average** | 3 (Medium) | 3 (Medium) | **3 (Medium)** |
| **Warning** | 3 (Medium) | 2 (Low) | **2 (Low)** |
| **Information** | 2 (Low) | 1 (Very Low) | **1 (Very Low)** |

### 5.2. Varlık (Asset) Arama ve Entity Takibi
Script, Zabbix'ten gelen `{HOST.HOST}` bilgisini kullanarak GLPI'da otomatik varlık eşleştirmesi yapar. Arama sırası şöyledir:

1.  **Computer (Bilgisayar/Sunucu):** İsim "contains" mantığıyla aranır.
2.  **NetworkEquipment (Ağ Cihazı):** Bilgisayar bulunamazsa ağ cihazlarında aranır.

**Entity Takibi:**
*   Varlık bulunduğunda, script otomatik olarak varlığın detaylarını çeker ve `entities_id` bilgisini alır.
*   Ticket, bulunan varlığın bağlı olduğu **Entity'ye** otomatik olarak atanır (örn: Ultron Bilişim).
*   Varlık ticket'a `items_id` parametresi ile bağlanır (Computer veya NetworkEquipment olarak).
*   Varlık bulunamazsa ticket Root Entity (ID: 0) altında oluşturulur.

### 5.3. Otomatik Kapanma (Recovery)
Zabbix'ten "Recovery" (Resolve) sinyali geldiğinde:
1.  Script önce mevcut ticket'a **"Zabbix Recovery"** başlıklı bir **Followup (Yorum)** ekler.
2.  Ardından ticket statüsünü **Solved (Çözüldü)** olarak günceller.
3.  Çözüm (Solution) sekmesi yerine, işlemin hızlı olması için statü değişikliği tercih edilmiştir.

---

**Son Güncelleme:** 29 Aralık 2025  



Hazırlayan : Bora Ergül
