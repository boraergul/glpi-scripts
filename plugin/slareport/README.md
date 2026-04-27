# GLPI SLA Breach Report Plugin

Bu eklenti, GLPI 10 ve 11 sürümleri için geliştirilmiş, SLA ihlallerini denetleyen ve detaylı raporlayan profesyonel bir araçtır.

## 🚀 Öne Çıkan Özellikler

- **Gelişmiş Dashboard:** Toplam ticketlar, SLA uyum oranı ve ihlal sayılarını içeren dinamik görsel panel.
- **SLA Audit (Denetim):** Ticketlar üzerindeki olası SLA manipülasyonlarını (gereksiz beklemeye alma, son dakika işlemleri vb.) tespit eden akıllı denetim sistemi.
- **Özel Çeviri Motoru:** GLPI'nin standart dil sisteminden bağımsız, hızlı ve stabil çalışan dahili çeviri altyapısı (Türkçe ve İngilizce tam destek).
- **Premium PDF Raporu:** Kapak sayfası, yönetici özeti ve detaylı ihlal listesi içeren kurumsal PDF çıktısı.
- **Excel Dışa Aktar:** Analizler için UTF-8 BOM destekli CSV çıktısı.
- **Detaylı Filtreleme:** Tarih aralığı ve Birim (Entity) bazlı raporlama.

## 🛠 Kurulum ve Güncelleme

Eklentiyi kurmak veya güncellemek için aşağıdaki adımları takip edin:

1.  Dosyaları `/plugins/slareport` dizinine kopyalayın.
2.  GLPI arayüzünden **Kurulum > Eklentiler** sayfasına gidin.
3.  Eklentiyi **Kur** ve **Etkinleştir** yapın.

## 📦 Yayına Alma (Deployment)

Geliştirme ortamından sunuculara hızlı gönderim için iki adet betik mevcuttur:

### Test Ortamı (DEV)
```bash
bash deploy.sh
```
Hedef: `10.42.2.146` (ITSM-DEV)

### Canlı Ortam (PROD)
```bash
bash deploy_prod.sh
```
Hedef: `10.42.2.149` (ITSM-PROD) - Kullanıcı: `bora`

## 📂 Dosya Yapısı

- `inc/report.class.php`: Ana mantık, veritabanı sorguları ve çeviri motoru.
- `front/index.php`: Dashboard ve ana arayüz.
- `front/export_pdf.php`: Gelişmiş PDF raporlama motoru.
- `locales/`: Türkçe (`tr_TR.php`) ve İngilizce (`en_GB.php`) dil dosyaları.
- `setup.php`: Eklenti tanımı ve GLPI entegrasyonu.

## ⚖️ Lisans

Bu eklenti Bora Ergül tarafından geliştirilmiştir ve GPLv2+ lisansı altındadır.
