# SLA Breach Report Eklentisi İnceleme Raporu

**Tarih:** 16 Nisan 2026
**Eklenti:** slareport (GLPI Plugin)

Genel mimari, Chart.js entegrasyonu ve kullanılan UI paleti modern bir yapı sunmaktadır. Ancak arka plandaki veri doğruluğu, performans ve güvenlik açısından aşağıdaki kritik noktaların iyileştirilmesi gerekmektedir.

## 1. 🚨 Kritik Güvenlik Açığı: SQL Injection Riski (ORDER BY)
`front/index.php` dosyasında URL'den gelen `sort` ve `order` değişkenleri doğrudan `$_GET` ile alınıp, `inc/report.class.php` sınıfına aktarılıyor ve doğrudan SQL sorgusunun `ORDER` cümlesine string olarak yerleştiriliyor:

```php
// index.php içindeki kullanım
$sort = isset($_GET['sort']) ? $_GET['sort'] : 'glpi_tickets.date';
$order = isset($_GET['order']) ? $_GET['order'] : 'DESC';

// report.class.php içerisindeki SQL sorgusunda kullanım
'ORDER' => "$sort $order"
```
**Risk:** Kötü niyetli bir kullanıcı URL üzerinden `?sort=glpi_tickets.id; UPDATE ...` gibi bir değer enjekte edebilir. Bu parametreler hiçbir filtreleme yapılmadan SQL sorgusuna dahil edilmemelidir.

## 2. ⚠️ Mantıksal Hata: SLA İhlali Hesaplama Yöntemi (Kritik)
SLA sürelerinin `convertToSeconds` ile direkt çarpılıp saniye cinsinden `solve_delay_stat` ile kıyaslanması yapısal olarak yanlıştır:

```php
// Mevcut hesplama:
$limit = self::convertToSeconds($sla['number_time'], $sla['definition_time']);
if ($delay > 0 && $delay > $limit) {
    $ttr_violated = true; 
}
```
**Neden Hatalı?:** GLPI'da bir SLA (örneğin "2 gün" limiti), **Takvim (Mesai Saatleri)** kuralına bağlı olabilir (Örn. günde 8 saat mesai = 2 gün 16 saat demektir). `convertToSeconds` metodu günü daima 24 saat ile çarptığından, birçok ihlal edilen bilet raporda geçerli (compliant) olarak görünecektir.
**Çözüm:** GLPI'nin core mantığı kullanılarak direkt `solvedate` ile `time_to_resolve` (Son Çözüm Tarihi) kıyaslanmalıdır.

## 3. 🐛 Bug (Veri Çakışması): Entity İsimlerinin Sadeleştirilmesi
Entity çeken sorguda isimlerin sadece en alt kırılımı alınıyor:
```php
$name_parts = explode(' > ', $data['completename']);
$entities[$data['id']] = end($name_parts);
```
**Sorun:** `Holding > IT` ve `Fabrika > IT` şeklinde iki farklı varlık varsa, ikisi de "IT" adını alacak ve dizi gruplamasında SLA istatistikleri birbirine karışacaktır.
**Çözüm:** Veri gruplaması Entity ismi (`entity_name`) üzerinden değil, tekil ID (`entities_id`) üzerinden yapılmalıdır.

## 4. 🛡️ Güvenlik Zafiyeti: Eksik CSRF Kontrolü
Toplu dışa aktarım (CSV Export) gibi form işlemlerinde CSRF Token doğrulaması yapılmamaktadır.
`Html::printCSRFToken()` HTML içine gömülmüş olsa da POST isteği alındığında `Session::checkCSRF();` çağrılarak doğrulama eksik bırakılmıştır. Form sömürüsüne yol açabilir.

## 5. 🚀 Memory (Bellek) Ölçeklenebilirliği Durumu
Sorgu limitsiz çalışarak seçilen aralıktaki tüm verileri tek bir PHP dizisine (`$tickets[]`) aktarıyor. Müşteride on binlerce bilet olması durumunda "Memory Limit" (PHP Bellek Aşımları) yaşatacaktır. Gelecekte Pagination (Sayfalama) yapısına geçilmesi elzemdir.
