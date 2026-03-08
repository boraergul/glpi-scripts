# GLPI Business Rules Otomasyonu

Bu script, GLPI'deki Entity'ler (Birimler) için otomatik olarak **Business Rules** (İş Kuralları) oluşturur. E-posta ile gelen ticket'lar için kategori, öncelik, SLA ve teknik grup ataması yapar.

## 📋 Ne Yapar?

Script, **"Müşteriler" entity'si altındaki** tüm birimler için e-posta yoluyla gelen ticket'lar için otomatik atama kuralları oluşturur:

1. **Entity Ataması:** Ticket'ı doğru birime atar
2. **Kategori Ataması:** Varsayılan kategori (Genel Destek) atar
3. **Öncelik Ataması:** Varsayılan öncelik (P3) atar
4. **SLA Ataması:** Entity'nin service level'ına göre TTO ve TTR SLA'larını atar
5. **Grup Ataması:** Entity'ye uygun teknik grubu atar

> **ÖNEMLİ:** Script sadece "Müşteriler" parent entity'si altındaki entity'ler için kural oluşturur. Internal IT, Monitoring alerts gibi sistem entity'leri için kural oluşturulmaz.

## 🎯 Neden Gerekli?

GLPI'de e-posta ile ticket oluşturulduğunda:
1. **Email Rule** → Entity'yi atar
2. **Business Rule** → Kategori, SLA, Grup atar ← **Bu script bunu otomatikleştirir**

Manuel olarak her entity için kural oluşturmak yerine, bu script "Müşteriler" altındaki tüm entity'ler için otomatik kural oluşturur.

## 🔧 Özellikler

- ✅ **Otomatik Entity Filtreleme:** Sadece "Müşteriler" altındaki entity'ler için kural oluşturur
- ✅ **Otomatik Kural Oluşturma:** Filtrelenmiş entity'ler için business rule oluşturur
- ✅ **Güncelleme Desteği:** Mevcut kuralları güvenli şekilde günceller (v2.3)
- ✅ **Duplicate Önleme:** Search API ve geniş range ile çift kayıt önler (v2.3)
- ✅ **Timeout Koruması:** Tüm API çağrılarında 30sn timeout (v2.3)
- ✅ **E-posta Filtreleme:** Sadece e-posta ile gelen ticket'ları hedefler
- ✅ **Tip Kontrolü:** "Incident" dışındaki tipleri işler (Request, Problem, Change vb.)
- ✅ **SLA Eşleştirme:** Entity'nin service level'ına göre otomatik SLA atar
- ✅ **Kategori Ataması:** Varsayılan veya özel kategori atar
- ✅ **Grup Ataması:** Entity'ye uygun teknik grubu atar
- ✅ **Recursive (Alt Varlıklar Dahil):** Kurallar alt entity'lere de uygulanır
- ✅ **Dry-Run Modu:** Varsayılan olarak test modunda çalışır
- ✅ **Session Yönetimi:** Otomatik GLPI API session yönetimi
- ✅ **Pagination:** Büyük veri setleri için pagination desteği

## 📦 Gereksinimler

### Python Kütüphaneleri
```bash
pip install requests urllib3
```

### Gerekli Dosyalar
1. **config.json** - GLPI API bağlantı bilgileri
2. **entity_sla_map.json** - Entity-SLA service level eşleştirmesi (opsiyonel)

## 📁 Dosya Yapısı

```
Business Rules/
├── rules_business.py           # Ana script
├── entity_sla_map.json         # Entity-SLA mapping (opsiyonel)
└── README.md                    # Bu dosya
```

## 🚀 Kullanım

### 1. Dry-Run (Test Modu)
Varsayılan olarak test modunda çalışır. Hiçbir değişiklik yapmaz, sadece oluşturulacak kuralları listeler.

```bash
python rules_business.py
```

**Çıktı Örneği:**
```
======================================================================
SUMMARY
======================================================================
Entities: 33
Existing Business Rules: 261
SLA TTO: 59
SLA TTR: 61
Categories: 8
Groups: 41
Default Category: Genel Destek (ID: 227)
Default Priority: P3
Mode: DRY-RUN (simulation only)
======================================================================

======================================================================
FILTERING ENTITIES
======================================================================
Found 'Müşteriler' entity: ID=2
Total entities: 33
Entities under 'Müşteriler': 26
======================================================================

PROPOSE: CREATE business rule 'Auto-BR-Ankara-Oto'
  Entity: 'Ankara Oto' (ID: 14)
  Criteria:
    - Entity is 'Ankara Oto' (ID: 14)
    - Request source is 'E-Mail' (ID: 2)
    - Type is not 'Incident' (ID: 1)
  Actions:
    - Assign Category (ID: 227)
    - Assign Priority: P3
    - Assign SLA TTO: BRNZ-5x9-P3-TTO-1d (ID: 53)
    - Assign SLA TTR: BRNZ-5x9-P3-TTR-3d (ID: 58)

======================================================================
RESULTS
======================================================================
Rules to create: 26
Rules skipped (already exist): 0
======================================================================
```

### 2. Gerçek Çalıştırma (--force)
Kuralları gerçekten oluşturmak için `--force` parametresini kullanın.

```bash
python rules_business.py --force
```

**Çıktı Örneği:**
```
PROPOSE: CREATE business rule 'Auto-BR-Dorçe'
  Entity: 'Dorçe' (ID: 8)
  Criteria:
    - Entity is 'Dorçe' (ID: 8)
    - Request source is 'E-Mail' (ID: 2)
    - Type is not 'Incident' (ID: 1)
  Actions:
    - Assign Category (ID: 227)
    - Assign Priority: P3
    - Assign SLA TTO: GOLD-5x9-P3-TTO-30m (ID: 33)
    - Assign SLA TTR: GOLD-5x9-P3-TTR-1d (ID: 38)
  ✓ CREATED Rule ID: 1517
```

### 3. Özel Öncelik Belirtme
Varsayılan öncelik P3'tür. Farklı bir öncelik için:

```bash
python rules_business.py --priority P1
python rules_business.py --priority P2 --force
```

**Öncelik Seviyeleri:**
- P1: Very High (En yüksek)
- P2: High
- P3: Medium (Varsayılan)
- P4: Low
- P5: Very Low

### 4. Özel Kategori Belirtme
Varsayılan kategori "Genel Destek"tir. Farklı bir kategori için:

```bash
python rules_business.py --category "Teknik Destek"
python rules_business.py --category "Network" --force
```

## 🎯 Kural Yapısı

Her oluşturulan kural şu özelliklere sahiptir:

### Kural İsmi
**Format:** `Auto-BR-{Entity-Name}` (entity adlarındaki boşluklar tire ile değiştirilir)

**Örnekler:**
- `Auto-BR-Ultron-Bilişim`
- `Auto-BR-Ankara-Oto`
- `Auto-BR-Dorçe`

### Kriterler (AND mantığı ile)
1. **Entity** = Belirli bir entity (örn: Ankara Oto)
2. **Request Source** = E-Mail (ID: 2)
3. **Type** ≠ Incident (ID: 1)

### Aksiyonlar
1. **Category** → Genel Destek (veya belirtilen kategori)
2. **Priority** → P3 (veya belirtilen öncelik)
3. **SLA TTO** → Entity'nin service level'ına göre
4. **SLA TTR** → Entity'nin service level'ına göre
5. **Technician Group** → Entity'ye uygun grup (opsiyonel)

### Kural Özellikleri
- **is_active:** 1 (Aktif)
- **is_recursive:** 1 (Alt varlıklar dahil)
- **condition:** 3 (GLPI kural motoru için)
- **match:** AND (Tüm kriterler eşleşmeli)

## 📊 SLA Eşleştirme

Script, SLA'ları iki yöntemle bulur:

### 1. Service Level Bazlı (Önerilen)
`entity_sla_map.json` dosyasını kullanarak entity'leri service level'lara eşleştirir.

**entity_sla_map.json Örneği:**
```json
{
    "Ankara Oto": "SLA-BRONZE-5X9",
    "Dorçe": "SLA-GOLD-5X9",
    "Prime Sistem": "SLA-PLATINUM-7X24",
    "Ankara Cerrahi Tıp Hastanesi": "SLA-SILVER-5X9"
}
```

**SLA İsimlendirme Formatı:**
- `PLAT-7x24-P3-TTO-15m` → Platinum, 7x24, Priority 3, Time To Own: 15 dakika
- `GOLD-5x9-P3-TTR-1d` → Gold, 5x9, Priority 3, Time To Resolve: 1 gün
- `SILV-5x9-P3-TTO-4h` → Silver, 5x9, Priority 3, Time To Own: 4 saat
- `BRNZ-5x9-P3-TTR-3d` → Bronze, 5x9, Priority 3, Time To Resolve: 3 gün

### 2. Entity Adı Bazlı (Fallback)
Eğer `entity_sla_map.json` yoksa veya entity bulunamazsa, SLA adında entity adını arar:
- `Auto SLA - Ankara Oto - Priority P3`

### SLA Bulunamazsa
SLA bulunamayan entity'ler için kural yine oluşturulur, ancak SLA ataması yapılmaz:
```
PROPOSE: CREATE business rule 'Auto-BR-Internal-IT'
  ...
  Actions:
    - Assign Category (ID: 227)
    - Assign Priority: P3
    - WARNING: SLA TTO not found for Internal IT - P3
    - WARNING: SLA TTR not found for Internal IT - P3
  ✓ CREATED Rule ID: 1539
```

## 🔍 Teknik Detaylar

### GLPI API Endpoint'leri
- `/Entity` - Entity'leri çeker
- `/SLA` - SLA'ları çeker (Type 0=TTR, Type 1=TTO)
- `/ITILCategory` - Kategorileri çeker
- `/Group` - Grupları çeker
- `/search/RuleTicket` - Mevcut kuralları çeker
- `/RuleTicket` - Kural oluşturur
- `/RuleTicket/{id}/RuleCriteria` - Kriter ekler
- `/RuleTicket/{id}/RuleAction` - Aksiyon ekler

### SLA Type Mapping (GLPI Standart)
- **Type 0** = TTR (Time To Resolve)
- **Type 1** = TTO (Time To Own)

### Kural Kriterleri - Condition Kodları
- **0** = is (eşittir)
- **1** = is not (eşit değildir)

### Kural Aksiyonları - Field Kodları
- `itilcategories_id` = Kategori
- `priority` = Öncelik (5=Very High, 4=High, 3=Medium, 2=Low, 1=Very Low)
- `slas_id_tto` = SLA Time To Own
- `slas_id_ttr` = SLA Time To Resolve
- `_groups_id_assign` = Teknik Grup

## ⚙️ Yapılandırma

### config.json
```json
{
    "GLPI_URL": "https://itsm.example.com/apirest.php",
    "GLPI_APP_TOKEN": "your_app_token_here",
    "GLPI_USER_TOKEN": "your_user_token_here"
}
```

### entity_sla_map.json (Opsiyonel)
```json
{
    "Entity Adı": "SLA-SERVICE_LEVEL-HOURS",
    "Ankara Oto": "SLA-BRONZE-5X9",
    "Dorçe": "SLA-GOLD-5X9",
    "Prime Sistem": "SLA-PLATINUM-7X24"
}
```

**Service Level Formatı:**
- `SLA-PLATINUM-7X24` → Platinum seviye, 7 gün 24 saat
- `SLA-GOLD-5X9` → Gold seviye, 5 gün 9 saat
- `SLA-SILVER-5X9` → Silver seviye, 5 gün 9 saat
- `SLA-BRONZE-5X9` → Bronze seviye, 5 gün 9 saat

## 📈 Çıktı Örnekleri

### Başarılı Kural Oluşturma
```
✓ CREATED Rule ID: 1517

PROPOSE: CREATE business rule 'Auto-BR-Dorçe'
  Entity: 'Dorçe' (ID: 8)
  Criteria:
    - Entity is 'Dorçe' (ID: 8)
    - Request source is 'E-Mail' (ID: 2)
    - Type is not 'Incident' (ID: 1)
  Actions:
    - Assign Category (ID: 227)
    - Assign Priority: P3
    - Assign SLA TTO: GOLD-5x9-P3-TTO-30m (ID: 33)
    - Assign SLA TTR: GOLD-5x9-P3-TTR-1d (ID: 38)
```

### SLA Bulunamadı Uyarısı
```
PROPOSE: CREATE business rule 'Auto-BR-Internal-IT'
  Entity: 'Internal IT' (ID: 31)
  Criteria:
    - Entity is 'Internal IT' (ID: 31)
    - Request source is 'E-Mail' (ID: 2)
    - Type is not 'Incident' (ID: 1)
  Actions:
    - Assign Category (ID: 227)
    - Assign Priority: P3
    - WARNING: SLA TTO not found for Internal IT - P3
    - WARNING: SLA TTR not found for Internal IT - P3
  ✓ CREATED Rule ID: 1539
```

### Mevcut Kural Atlandı
```
SKIP: Rule 'Auto-BR-Ultron-Bilişim' already exists (ID: 1511)
```

## 🐛 Sorun Giderme

### SLA Bulunamıyor
**Sorun:** "WARNING: SLA TTO/TTR not found" mesajı alıyorsunuz.

**Çözüm:**
1. `entity_sla_map.json` dosyasını oluşturun
2. Entity'yi doğru service level ile eşleştirin
3. SLA'ların GLPI'de mevcut olduğundan emin olun
4. SLA isimlendirmesinin doğru olduğunu kontrol edin (PLAT/GOLD/SILV/BRNZ)

### Kategori Bulunamıyor
**Sorun:** "Category not found" uyarısı alıyorsunuz.

**Çözüm:**
- `--category` parametresi ile mevcut bir kategori adı verin
- Veya GLPI'de "Genel Destek" kategorisini oluşturun

### Grup Bulunamıyor
**Sorun:** Grup ataması yapılmıyor.

**Çözüm:**
- GLPI'de entity adını içeren ve "Genel Destek" kelimesini içeren bir grup oluşturun
- Örnek: "Ultron Bilişim > Teknik Ekipler > Genel Destek Ekibi"

### API Bağlantı Hatası
**Sorun:** "Failed to initialize session" hatası alıyorsunuz.

**Çözüm:**
1. `config.json` dosyasının doğru konumda olduğundan emin olun
2. API token'larının geçerli olduğunu kontrol edin
3. GLPI URL'inin doğru olduğunu kontrol edin
4. API'nin aktif olduğundan emin olun

### Kurallar GLPI'de Görünmüyor
**Sorun:** Kurallar oluşturuldu ama GLPI arayüzünde görünmüyor.

**Çözüm:**
1. GLPI'de doğru entity'yi seçtiğinizden emin olun (Root Entity)
2. "Administration > Rules > Business rules for tickets" menüsüne gidin
3. Kuralların `is_recursive: 1` olduğundan emin olun (alt varlıklar dahil)
4. Tarayıcı cache'ini temizleyin

## 📝 Notlar

### Önemli Bilgiler
1. **Sadece "Müşteriler" altındaki entity'ler** işlenir
2. **Root Entity (ID: 0)** otomatik olarak atlanır
3. **"Müşteriler" entity'sinin kendisi** atlanır
4. **Sistem entity'leri** (Internal IT, Monitoring alerts, vb.) işlenmez
5. **Mevcut kurallar** tekrar oluşturulmaz (isim kontrolü ile atlanır)
6. **SLA eşleştirme** önce service level, sonra entity adına göre yapılır
7. **Grup eşleştirme** entity adı + "Genel Destek" içeren grupları arar
8. **Request Source ID:** E-Mail = 2 (GLPI standart)
9. **Type ID:** Incident = 1 (GLPI standart)
10. **Recursive:** Tüm kurallar alt varlıklara da uygulanır

### Entity Filtreleme Detayları
Script, `completename` alanında "Müşteriler" kelimesini arayarak filtreleme yapar:
- ✅ `Root Entity > Ultron Bilişim > Müşteriler > Ankara Oto` → İşlenir
- ✅ `Root Entity > Ultron Bilişim > Müşteriler > Dorçe` → İşlenir
- ❌ `Root Entity > Ultron Bilişim` → İşlenmez
- ❌ `Root Entity > Ultron Bilişim > Internal IT` → İşlenmez

### Güvenlik
- Script `verify=False` kullanır (SSL sertifika kontrolü kapalı)
- Üretim ortamında SSL doğrulaması önerilir
- API token'larını güvenli tutun

### Performans
- Pagination desteği sayesinde büyük veri setleri ile çalışabilir
- Her entity için ayrı API çağrısı yapılır
- Ortalama 32 entity için ~30 saniye sürer

## 🔗 İlgili Scriptler

1. **rules_email.py** - E-posta kuralları oluşturur (Entity ataması)
2. **rules_business_sla.py** - SLA kuralları oluşturur
3. **rules_business.py** - Business rules oluşturur (bu script)

## 📖 Çalışma Akışı

### Genel Akış
1. **E-posta gelir** → Email Rule çalışır → Entity atar
2. **Ticket oluşur** → Business Rule çalışır → Kategori, SLA, Grup atar
3. **Ticket hazır** → Teknik ekibe atanmış, SLA'lı ticket

### Script Akışı
1. GLPI API'ye bağlan
2. Entity'leri çek
3. **"Müşteriler" entity'sini bul ve altındaki entity'leri filtrele**
4. Mevcut business rule'ları çek
5. SLA'ları çek (TTO ve TTR)
6. Kategorileri çek
7. Grupları çek
8. Entity-SLA mapping'i yükle
9. Her **filtrelenmiş** entity için:
   - Kural adını oluştur (`Auto-BR-{Entity}`)
   - Mevcut kural kontrolü yap
   - Varsa atla, yoksa devam et
   - SLA'ları bul (service level veya entity adına göre)
   - Grubu bul
   - Kuralı oluştur (dry-run veya force)
10. Sonuçları göster
11. Session'ı kapat

## 💡 İpuçları

1. **İlk çalıştırmada** `--force` kullanmayın, önce dry-run ile kontrol edin
2. **Farklı öncelikler** için ayrı ayrı çalıştırın (P1, P2, P3, vb.)
3. **Mevcut kuralları silmek** yerine script'i tekrar çalıştırın (otomatik atlar)
4. **SLA mapping** için `entity_sla_map.json` kullanın (daha güvenilir)
5. **Test ortamında** önce test edin, sonra production'a geçin
6. **Recursive özelliği** sayesinde alt entity'ler için ayrı kural oluşturmaya gerek yok

## 📞 Destek

Sorun yaşarsanız:
1. Dry-run çıktısını kontrol edin
2. GLPI log'larını inceleyin
3. API token'larının yetkilerini kontrol edin
4. Script çıktısındaki WARNING mesajlarına dikkat edin

## 📜 Lisans

Bu script GLPI otomasyonu için geliştirilmiştir.

---

**Son Güncelleme:** 26 Aralık 2024  
**Versiyon:** 2.5  

**Değişiklikler (v2.5):**
- ✅ **Add/Update Trigger:** Condition 3 ile hem oluşturma hem güncelleme anında tetiklenir
- ✅ **Wipe & Rebuild:** Güncelleme sırasında kriter çakışmasını önlemek için güvenli temizlik
- ✅ **Safe Update:** Mevcut kuralları ID kontrolü ile günceller

**Değişiklik Notları:**

**v2.4 (25 Aralık 2024):**
- ✅ **Standardize Naming:** Hyphen-only format (`Auto-BR-Entity-Name`)
- ✅ **Space Handling:** Entity adlarındaki boşluklar otomatik olarak tire ile değiştirilir

**v2.3 (22 Aralık 2025):**
- ✅ Timeout koruması eklendi (30sn tüm API çağrılarında)
- ✅ Duplicate prevention: Range parametresi (0-5000) ile güvenli silme
- ✅ Search API kullanımı ile geliştirilmiş duplicate detection
- ✅ Güncelleme modu: Mevcut kuralları güvenli şekilde günceller

**v2.1 (18 Aralık 2025):**
- Entity filtreleme eklendi: Sadece "Müşteriler" altındaki entity'ler için kural oluşturulur
- Sistem entity'leri (Internal IT, Monitoring alerts, vb.) artık işlenmez
- Filtreleme sonuçları çıktıda gösterilir



Hazırlayan : Bora Ergül
