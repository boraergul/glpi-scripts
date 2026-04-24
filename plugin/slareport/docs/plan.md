# SLA Raporu Eklentisi İyileştirme Planı

Eklenti kodundaki hataları gidermek ve GLPI standartlarına uyumluluğu artırmak için aşağıdaki değişiklikler yapılacaktır.

## Tespit Edilen Hatalar ve Eksikler

1.  **Veritabanı Şeması Uyumsuzluğu**: `glpi_logs` tablosunda `ticket_id`, `newvalue`, `oldvalue` ve `date` sütunları bulunmamaktadır. GLPI 10+ standartlarına göre bunlar `items_id`, `new_value`, `old_value` ve `date_mod` şeklindedir.
2.  **Sıralama (Sorting) Hatası**: Kurum ismine göre sıralama yapıldığında `glpi_entities` tablosu ile JOIN yapılmadığı için SQL hatası alınacaktır.
3.  **PDF Dışa Aktarma Hatası**: `front/index.php` dosyasında PDF butonunda `entities_id` parametresi gönderilirken, `front/export_pdf.php` dosyasında `entity_id` parametresi beklenmektedir.
4.  **SQL Enjeksiyonu ve Güvenlik**: `calculateTotalPendingTime` metodunda SQL sorgusu manuel olarak oluşturulmaktadır. GLPI'nin `DB::request` metodunu kullanmak daha güvenlidir.
5.  **Performans**: `glpi_logs` tablosu çok büyük olabileceği için bekleyen süre hesaplaması optimize edilmelidir.

## Yapılacak Değişiklikler

### 1. `inc/report.class.php` Dosyası
- `calculateTotalPendingTime` metodu GLPI 10+ şemasına göre güncellenecek.
- `getSlaComplianceData` metoduna `glpi_entities` JOIN eklenecek.
- Sabit değerler yerine (örn: `4`) `CommonITILObject::PENDING` kullanılacak.

### 2. `front/index.php` Dosyası
- PDF butonundaki parametre ismi `entity_id` olarak düzeltilecek.
- Arayüzde ufak düzeltmeler yapılacak.

### 3. `front/export_pdf.php` Dosyası
- Parametre kontrolü ve hata yönetimi iyileştirilecek.

## Doğrulama Planı
- Raporun doğru verileri çektiği kontrol edilecek.
- Sıralama fonksiyonlarının (ID, Konu, Kurum, Tarih) çalıştığı teyit edilecek.
- CSV ve PDF dışa aktarma fonksiyonları test edilecek.
- Bekleyen süre (Pending Time) hesaplamasının doğruluğu örnek bir bilet üzerinden kontrol edilecek.
