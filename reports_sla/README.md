# GLPI SLA Uyum Raporu

Bu script, GLPI'daki SLA (Service Level Agreement) uyumunu **gerçek verilerle** analiz eder ve entity bazlı kırılım sağlar.

## 📊 Ne Yapar?

- Belirtilen tarih aralığındaki tüm SLA'lı ticketları çeker
- **120 SLA tanımını** GLPI'dan otomatik çeker (TTO ve TTR)
- **Gerçek SLA ihlallerini** tespit eder (`solve_delay_stat` kullanarak)
- Entity bazlı SLA uyum/ihlal istatistiklerini hesaplar
- **2 ayrı CSV raporu** oluşturur: Özet + Detaylı
- Konsol çıktısı, CSV veya Excel formatında rapor oluşturur

## ✨ Yeni Özellikler (v2.1)

- ✅ **Gerçek SLA İhlal Hesaplaması**: `solve_delay_stat` ve `time_to_own` alanlarını kullanarak gerçek ihlalleri tespit eder
- ✅ **SLA Tanımlarını Otomatik Çekme**: GLPI'dan TTO/TTR SLA'larını otomatik çeker
- ✅ **TTR ve TTO Ayrı Kontrol**: Time To Resolve ve Time To Own ayrı ayrı analiz edilir
- ✅ **Toplam vs SLA Ayrımı**: Tüm ticketlar ile SLA'lı ticketlar ayrı ayrı raporlanır
- ✅ **Aktif Ticket Desteği**: Henüz çözülmemiş ancak süresi dolmamış ticketlar "SLA Devam" olarak raporlanır
- ✅ **Detaylı CSV Raporu**: Her ticket için TTR/TTO ihlal detaylarını gösterir
- ✅ **Okunabilir Süre Formatı**: Gecikmeleri "1g 2s 30d" formatında gösterir

## 🚀 Kullanım

### Temel Kullanım

```bash
python sla_compliance_report.py --start-date 2024-12-24 --end-date 2025-12-24
```

### CSV Export (Özet + Detaylı)

```bash
python sla_compliance_report.py --start-date 2024-12-24 --end-date 2025-12-24 --export csv
```

**Oluşturulan Dosyalar:**
- `sla_report_summary_2024-12-24_2025-12-24.csv` - Entity bazlı özet
- `sla_report_detailed_2024-12-24_2025-12-24.csv` - Ticket bazlı detay

### Excel Export

```bash
python sla_compliance_report.py --start-date 2024-12-24 --end-date 2025-12-24 --export excel
```

## 📋 Gereksinimler

### Python Kütüphaneleri

```bash
pip install requests urllib3
```

### Excel Export için (Opsiyonel)

```bash
pip install openpyxl
```

### Config Dosyası

Script, merkezi `config.json` dosyasını kullanır:
- `./config.json`
- `../config/config.json`
- `../../config/config.json`

## 📈 Rapor Örnekleri

### 1. Konsol Çıktısı (Özet)

```
============================================================================================================================================
SLA UYUM RAPORU - ENTITY BAZLI KIRILIM
============================================================================================================================================
Entity                                   Toplam     SLA'lı     SLA Uygun    SLA İhlal    SLA Devam    İhlal Oranı
--------------------------------------------------------------------------------------------------------------------------------------------
Merkez Prime Hastanesi                   5          3          0            2            1            66.67%
Genel destek                             10         4          3            1            0            25.00%
Elimko                                   8          5          4            1            0            20.00%
Dorçe                                    3          0          0            0            0             0.00%
--------------------------------------------------------------------------------------------------------------------------------------------
TOPLAM                                   26         12         7            4            1            33.33%
============================================================================================================================================
```

### 2. Özet CSV Raporu

| Entity | Toplam Ticket | SLA'lı Ticket | SLA Uygun | SLA İhlal | SLA Devam (Aktif) | İhlal Oranı % |
|--------|---------------|---------------|-----------|-----------|-------------------|---------------|
| Merkez Prime Hastanesi | 5 | 3 | 0 | 2 | 1 | 66.67 |
| Genel destek | 10 | 4 | 3 | 1 | 0 | 25.00 |
| Elimko | 8 | 5 | 4 | 1 | 0 | 20.00 |

### 3. Detaylı CSV Raporu

| Entity | Ticket ID | SLA Durumu | TTR İhlal | TTR Limit | TTR Gerçek | TTR Gecikme | TTO İhlal |
|--------|-----------|------------|-----------|-----------|------------|-------------|-----------|
| Merkez Prime | 137 | İHLAL | EVET | 4s | 18s 35d | 14s 35d | HAYIR |
| Elimko | 167 | İHLAL | EVET | 8s | 9s 12d | 1s 12d | HAYIR |
| Genel destek | 246 | İHLAL | EVET | 8s | 1g 2s 11d | 18s 11d | HAYIR |

**Süre Formatı:**
- `g` = gün
- `s` = saat  
- `d` = dakika
- Örnek: `1g 2s 30d` = 1 gün 2 saat 30 dakika

## 📊 Çıktı Formatları

### 1. Konsol Çıktısı
- Tablo formatında entity bazlı özet
- Toplam istatistikler

### 2. CSV Export
- Excel'de açılabilir
- Pivot table için uygun
- UTF-8 BOM ile Türkçe karakter desteği

### 3. Excel Export
- Formatlı tablo
- Renkli başlıklar
- Otomatik sütun genişlikleri

## 🔧 Parametreler

| Parametre | Zorunlu | Açıklama | Örnek |
|-----------|---------|----------|-------|
| `--start-date` | ✅ | Başlangıç tarihi | `2024-01-01` |
| `--end-date` | ✅ | Bitiş tarihi | `2024-12-31` |
| `--export` | ❌ | Export formatı (csv/excel) | `csv` |

## 🔍 Teknik Detaylar

### SLA İhlal Tespiti

Script, **gerçek GLPI verilerini** kullanarak SLA ihlallerini tespit eder:

#### TTR (Time To Resolve) Kontrolü
```python
if solve_delay_stat > sla_limit_seconds:
    # İhlal var!
```
- `solve_delay_stat`: Ticket'ın gerçek çözüm süresi (saniye)
- `sla_limit_seconds`: SLA'da tanımlı limit (saniye)

#### TTO (Time To Own) Kontrolü
```python
if time_to_own > sla_limit_seconds:
    # İhlal var!
```
- `time_to_own`: Ticket'ın gerçek atama süresi (saniye)
- `sla_limit_seconds`: SLA'da tanımlı limit (saniye)

### SLA Tanımları

Script, GLPI'dan SLA tanımlarını otomatik çeker:
- **Type 0**: TTR (Time To Resolve)
- **Type 1**: TTO (Time To Own)
- **definition_time**: day, hour, minute
- **number_time**: Süre değeri

Örnek SLA:
- `SILV-5x9-P1-TTR-4h` → 4 saat TTR limiti
- `GOLD-5x9-P2-TTO-1h` → 1 saat TTO limiti

### Süre Dönüşümü

Script, tüm süreleri saniyeye çevirir:
- **1 dakika** = 60 saniye
- **1 saat** = 3,600 saniye
- **1 gün** = 86,400 saniye

Raporda ise okunabilir formata çevirir:
- `1g 2s 30d` = 1 gün 2 saat 30 dakika

## 📝 Notlar

### Önemli Bilgiler

1. **Gerçek Veri Kullanımı**: Script, GLPI'nın `solve_delay_stat` ve `time_to_own` alanlarını kullanır
2. **120 SLA Tanımı**: Sistemde tanımlı tüm SLA'lar otomatik çekilir
3. **Çift Kontrol**: Hem TTR hem TTO ayrı ayrı kontrol edilir
4. **Detaylı Raporlama**: Her ticket için hangi SLA'nın ihlal edildiği gösterilir
5. **İhlal Miktarı**: Gecikme süresi hesaplanır ve raporlanır

### CSV Dosyaları

**Özet Rapor:**
- Entity bazlı toplam istatistikler
- Genel ihlal oranları
- Pivot table için uygun

**Detaylı Rapor:**
- Ticket bazlı detaylar
- TTR/TTO ayrımı
- SLA isimleri ve limitler
- Gerçek süreler ve gecikmeler
- Filtreleme ve analiz için ideal

## 🎯 Kullanım Senaryoları

### 1. Yıllık SLA Raporu
```bash
python sla_compliance_report.py --start-date 2024-01-01 --end-date 2024-12-31 --export excel
```

### 2. Aylık SLA Takibi
```bash
python sla_compliance_report.py --start-date 2024-11-01 --end-date 2024-11-30 --export csv
```

### 3. Çeyrek Dönem Analizi
```bash
python sla_compliance_report.py --start-date 2024-10-01 --end-date 2024-12-31
```

## 🔍 Sorun Giderme

### "config.json bulunamadı" Hatası
**Çözüm**: Config dosyasının doğru konumda olduğundan emin olun.

### "Session başlatılamadı" Hatası
**Çözüm**: GLPI API token'larını kontrol edin.

### Excel Export Çalışmıyor
**Çözüm**: `pip install openpyxl` komutunu çalıştırın.

## 🌐 Web Dashboard (YENİ!)

### Kurulum

1. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

2. **Dashboard sunucusunu başlatın:**
```bash
python sla_dashboard_api.py
```

3. **Tarayıcınızda açın:**
```
http://localhost:5000
```

### Özellikler

#### 📊 İnteraktif Grafikler
- **SLA Uyum Pasta Grafiği**: Genel uyum/ihlal oranı
- **En Çok İhlal Olan Entity'ler**: Top 10 bar grafiği
- **Entity Bazlı Kırılım**: Stacked horizontal bar chart

#### 🎨 Modern UI/UX
- **Glassmorphism Tasarım**: Modern, şık arayüz
- **Dark Mode**: Göz yormayan karanlık tema
- **Responsive**: Mobil, tablet ve desktop uyumlu
- **Smooth Animasyonlar**: Akıcı geçişler ve hover efektleri

#### 🔧 Kontroller
- **Tarih Aralığı Seçici**: Başlangıç ve bitiş tarihi
- **Entity Filtresi**: Belirli entity'lere odaklanma
- **Gerçek Zamanlı Yenileme**: Tek tıkla veri güncelleme
- **CSV Export**: Doğrudan tarayıcıdan export

#### 📈 Özet Kartlar
- Toplam Ticket Sayısı
- SLA Uygun Ticket Sayısı
- SLA İhlal Edilen Ticket Sayısı
- Genel Uyum Oranı (%)

#### 📋 Detaylı Tablo
- Son 100 SLA ihlali
- Entity, Ticket ID, İhlal Tipi
- Filtrelenebilir ve sıralanabilir

### API Endpoints

Dashboard, Flask tabanlı REST API kullanır:

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/` | GET | Dashboard ana sayfa |
| `/api/entities` | GET | Entity listesi |
| `/api/compliance-data` | GET | SLA uyum verileri |
| `/api/export/csv` | GET | CSV export |

**Örnek API Kullanımı:**
```bash
# Entity listesi
curl http://localhost:5000/api/entities

# SLA uyum verileri
curl "http://localhost:5000/api/compliance-data?start_date=2024-01-01&end_date=2024-12-31"

# Belirli entity için
curl "http://localhost:5000/api/compliance-data?start_date=2024-01-01&end_date=2024-12-31&entity_id=17"
```

### Teknik Detaylar

**Backend:**
- Flask 3.0.0
- Flask-CORS (CORS desteği)
- 5 dakikalık cache mekanizması
- Session yönetimi

**Frontend:**
- Vanilla JavaScript (framework yok)
- Chart.js 4.4.1 (grafikler)
- CSS Variables (tema desteği)
- LocalStorage (tema tercihi)

**Performans:**
- Cache ile hızlı veri erişimi
- Lazy loading
- Optimize edilmiş API çağrıları
- Minimal bundle size

### Ekran Görüntüleri

Dashboard aşağıdaki bileşenleri içerir:
1. **Header**: Logo, başlık, dark mode toggle
2. **Kontrol Paneli**: Tarih seçici, entity filtresi, butonlar
3. **Özet Kartlar**: 4 adet KPI kartı
4. **Grafikler**: 3 farklı interaktif grafik
5. **Tablo**: Detaylı ihlal listesi
6. **Footer**: Son güncelleme zamanı

## 🚧 Gelecek Geliştirmeler

- [x] ~~Gerçek SLA ihlal hesaplaması (solve_delay_stat kullanarak)~~ ✅ v2.0
- [x] ~~SLA TTO (Time To Own) analizi~~ ✅ v2.0
- [x] ~~Grafik/chart oluşturma~~ ✅ v3.0 (Web Dashboard)
- [ ] Kategori bazlı kırılım
- [ ] Öncelik bazlı kırılım
- [ ] PDF export
- [ ] Otomatik e-posta gönderimi
- [ ] Trend analizi (zaman serisi)
- [ ] SLA tahmin modeli (ML)

## 📞 Destek

Sorun yaşarsanız:
1. Script çıktısını kontrol edin
2. GLPI API erişimini test edin
3. Tarih formatını kontrol edin (YYYY-MM-DD)

---

**Versiyon**: 3.1
**Son Güncelleme**: 12 Ocak 2026

**Değişiklik Geçmişi:**
- **v3.1**: Toplam/SLA'lı ticket ayrımı, Aktif (Süresi Dolmamış) SLA desteği
- **v3.0**: Web Dashboard eklendi (Flask API + Modern UI), interaktif grafikler, dark mode
- **v2.0**: Gerçek SLA ihlal hesaplaması, TTR/TTO ayrı kontrol, detaylı CSV raporu
- **v1.0**: İlk versiyon, temel entity bazlı rapor

Hazırlayan: Bora Ergül
