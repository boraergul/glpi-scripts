# SLA Raporu - Bekleme ve Risk Analizi Geliştirme Planı

Eklentiye "SLA Manipülasyon Analizi" ve gelişmiş bekleme takibi özelliklerini eklemek için aşağıdaki adımlar izlenecektir.

## Yapılacak Değişiklikler

### 1. `inc/report.class.php` (Mantık Katmanı)
- **Veri Toplama**: `glpi_pendingreasons` ve `glpi_pendingreasons_items` tabloları bilet sorgusuna (LEFT JOIN) eklenecek.
- **İstatistik Hesaplama**: `calculateTotalPendingTime` metodu `calculatePendingStats` olarak genişletilecek:
    - Toplam bekleme süresi hesaplanacak.
    - Bekleme (Pending) statüsüne kaç kez geçildiği sayılacak (`status_toggles`).
    - İlk bekleme başlangıç zamanı kaydedilecek.
- **Risk Analizi**: Her bilet için bir `risk_score` ve `risk_flags` hesaplanacak:
    - **Stagnant**: Bekleme Süresi > TTR Süresi.
    - **Last Minute**: SLA'in son %10'luk diliminde beklemete alınma.
    - **Excessive Toggling**: 3 kereden fazla beklemete alınma.

### 2. `front/index.php` (Sunum Katmanı)
- **KPI Kartları**: "Pending Tickets" kartı eklenecek.
- **Bilet Listesi**:
    - "Pending Reason" (Bekleme Nedeni) sütunu eklenecek.
    - "SLA Audit" (Risk Analizi) sütunu eklenecek.
    - Risk durumuna göre ikonlar ve renkli uyarılar (Badge) eklenecek:
        - 🔴 **Yüksek Risk**: Manipülasyon belirtileri (Son dakika, aşırı git-gel).
        - 🟡 **Şüpheli**: Çok uzun süreli bekleme (Stagnant).
        - 🟢 **Normal**: Kurallara uygun bekleme.
- **Grafik**: "SLA Status Distribution" pasta grafiğine "Pending" dilimi eklenecek.

## Doğrulama Planı
- Bekleme nedenlerinin doğru çekildiği kontrol edilecek.
- Manipülasyon tespit kriterlerinin (Son dakika, git-gel sayısı) bilet loglarıyla tutarlılığı test edilecek.
- Arayüzde risk durumlarının görsel olarak netliği kontrol edilecek.
