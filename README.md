# GLPI Automation & Integration Scripts

Bu proje, **GLPI** (Gestionnaire Libre de Parc Informatique) ITSM yazılımı için geliştirilmiş otomasyon scriptlerini, entegrasyon araçlarını ve iş kuralı yönetim araçlarını içerir.

Amaç; GLPI yönetimini basitleştirmek, insan hatasını azaltmak ve dış sistemlerle (Zabbix vb.) entegrasyonu sağlamaktır.

## 📂 Proje Yapısı ve Modüller

Proje, işlevlerine göre ayrılmış modüllerden oluşur:

### 1. 🔧 Config (Yapılandırma)
* **Dizin:** `/config`
* **Amaç:** Tüm scriptlerin kullandığı ortak yapılandırma ayarlarını (API URL, Tokenlar, Veritabanı bilgileri) merkezi olarak yönetir.
* **Önemli:** `config.json` dosyasını kendi ortamınıza göre düzenlemelisiniz.

### 2. 🚨 Zabbix Webhook Entegrasyonu
* **Dizin:** `/zabbix_webhook`
* **Amaç:** Zabbix monitoring sisteminden gelen alarmları otomatik olarak GLPI'da bilete (Incident) dönüştürür.
* **Özellikler:**
  * Major incident yönetimi.
  * İyileşme (Recovery) durumunda bileti otomatik kapatma.
  * Öncelik ve aciliyet belirleme.

### 3. 📧 Email Kuralları (Email Rules)
* **Dizin:** `/rules_email`
* **Amaç:** E-posta yoluyla gelen biletleri gönderen alan adına (domain) göre doğru Entity'ye (Birim) yönlendirir.
* **Özellikler:**
  * Bilinmeyen domainleri yakalama.
  * Otomatik kategori atama (Generic).

### 4. ⏱️ SLA ve İş Kuralları (SLA Rules)
* **Dizin:** `/rules_business_sla` & `/rules_business`
* **Amaç:** Açılan biletlere, Entity ve Öncelik seviyesine göre otomatik SLA (TTO/TTR - Çözüm ve Müdahale süreleri) atar.
* **Özellikler:**
  * Entity bazlı özelleştirilmiş SLA tanımları.
  * İş kurallarının toplu oluşturulması ve güncellenmesi.

### 5. 👥 Entity & Grup Senkronizasyonu
* **Dizin:** `/entity_group_sync`
* **Amaç:** GLPI içerisindeki Entity ve Grupların hiyerarşik yapısının korunması ve senkronize edilmesini sağlar.

### 6. 🚀 Onboarding (Yeni Kurulum)
* **Dizin:** `/onboarding`
* **Amaç:** Yeni bir GLPI kurulumu veya yeni bir Entity eklendiğinde gerekli standart tanımların (Kurallar, Ayarlar) otomatik olarak yapılmasını sağlar.

### 7. ❓ Bilinmeyen Domain Yönetimi
* **Dizin:** `/rules_unknownDomain`
* **Amaç:** Tanımsız domainlerden gelen mailler için özel kurallar işletir ve yöneticiye raporlar.

### 8. 📧 Notification Templates (Bildirim Şablonları)
* **Dizinler:** `/templates_new`, `/templates_import` & `/templates_export_import`
* **Amaç:** Modern, optimize edilmiş, çok dilli (TR/EN) GLPI notification template'leri sağlar ve bunların yönetimini otomatize eder.
* **Modüller:**
  * **templates_new:** Şablon motoru. `generate_email_templates.py` ile tek bir kaynaktan onlarca HTML/TXT şablonu üretir.
  * **templates_import:** Otomasyon aracı. `templates_new/` dizinindeki Python/HTML kaynaklardan şablonları GLPI'ye yükler ve bildirimlerle ilişkilendirir.
  * **templates_export_import:** Transfer aracı. Bir GLPI sisteminden tüm template'leri CSV olarak dışa aktarır ve başka bir GLPI sistemine aktarır. Grafik arayüzü (`Gui_templates_export_v2.py`) ile Export, Import ve tek tıkla Transfer desteklenir.
* **Özellikler:**
  * **Dinamik İçerik:** Foreach döngüleri ile timeline, envanter listesi gibi dinamik veriler.
  * **Otomatik Dağıtım:** Tek komutla tüm sisteme şablon dağıtımı.
  * **Kapsamlı:** 50+ farklı bildirim senaryosu için hazır şablon.
  * **Modern Tasarım:** Ticket durumuna göre değişen renk kodları, net aksiyon butonları ve standardize edilmiş tablo yapısı.
* **Son Güncelleme:** 2026-02-22

### 9. 📊 SLA Compliance & Dashboard (SLA Raporlama)
* **Dizin:** `/reports_sla`
* **Amaç:** GLPI verilerini analiz ederek detaylı SLA uyum raporları ve interaktif web dashboard sunar.
* **Özellikler:**
  * **v3.1 Web Dashboard:** Modern, Flask tabanlı görsel arayüz.
  * **Gerçek İhlal Analizi:** TTR ve TTO sürelerini (Active/Pending dahil) hassas analiz eder.
  * **Detaylı Raporlar:** CSV/Excel formatında entity ve ticket bazlı kırılım.

### 10. 🔔 Notification Transfer (Bildirim Aktarımı)
* **Dizin:** `/notifications_export_import`
* **Amaç:** Bir GLPI sistemindeki notification yapılandırmalarını (hangi olayda, kime, hangi şablonla bildirim) başka bir GLPI sistemine aktarır.
* **Modüller:**
  * **export_notifications.py:** Kaynak GLPI'den notification'ları CSV'ye aktarır.
  * **import_notifications.py:** CSV'deki notification'ları hedef GLPI'ye yükler.
  * **gui_notifications_import_v2.py:** Grafik arayüz. Export Kaynak, Export Hedef ve tek tıkla Transfer işlemlerini sunar.
* **Özellikler:**
  * GUI üzerinden sunucu profili yönetimi (`servers.json`).
  * Dry-Run modu ile güvenli test imkânı.
  * `templates_export_import/` ile aynı `servers.json` profillerini paylaşabilir.

### 11. 🔔 SLA Eskalasyon (Proaktif Uyarı)
* **Dizin:** `/sla_escalation`
* **Amaç:** Açık ticket'ların TTR tüketim yüzdesini izler ve SLA ihlali olmadan önce otomatik aksiyon alır.
* **Eskalasyon Adımları:**
  * **%75:** Ticket'a followup uyarısı eklenir.
  * **%90:** Priority +1 yükseltilir + followup eklenir.
  * **%100+:** Priority = Major (6) atanır (cezai yaptırım).
* **Cron:** Her 15 dakikada bir çalıştırılması önerilir.

### 12. 📊 SLA Breach Report (GLPI Plugin)
* **Dizin:** `/plugin/slareport`
* **Amaç:** GLPI arayüzüne entegre, gerçek zamanlı SLA ihlal raporu sunan bir eklentidir.
* **Özellikler:**
  * **İstatistiksel Analiz**: TTR (Çözüm) ve TTO (Sahiplenme) sürelerini GLPI veritabanı istatistikleri üzerinden saniye hassasiyetinde analiz eder.
  * **Dashboard**: İhlal dağılımını gösteren interaktif grafikler.
  * **Detaylı Tablo**: Çözüm hedefi, gerçekleşen süre ve gecikme bilgilerini içeren detaylı liste.
  * **Dışa Aktarma**: Tek tıkla CSV formatında rapor alma.
  * **PHP 8.1+ Uyumluluğu**: Modern PHP sürümleriyle tam uyumlu.

---

## 🚀 Kurulum ve Kullanım

1.  **Gereksinimler:**
    * Python 3.x
    * Gerekli kütüphaneler: `requests`, `mysql-connector-python` (kullanılan scriptlere göre değişebilir).

2.  **Yapılandırma:**
    * `config/config_loader_template.py` yapısını inceleyin.
    * `config/config.json` dosyasını oluşturun ve GLPI API bilgilerinizi girin.

3.  **Çalıştırma:**
    * İlgili modülün klasörüne giderek scriptleri çalıştırabilirsiniz. Çoğu script `--dry-run` modunu destekler (değişiklik yapmadan test etmek için).
    * Örnek: `python rules_email/rules_email.py --dry-run`

## 📝 Versiyon Kontrolü

Bu proje Git ile takip edilmektedir. Değişikliklerinizi göndermeden önce mutlaka test ediniz.

```bash
git add .
git commit -m "Yeni özellik eklendi"
git push origin main
```
