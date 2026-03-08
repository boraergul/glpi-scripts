# GLPI SLA ve Business Rule Entegrasyon Rehberi

Bu doküman, **Ultron Bilişim** standartlarında; Entity (Müşteri), Segment (Örn: SLA-PLATINUM-7X24) ve Priority (P1-P5) yapısına tam uyumlu GLPI kurallarının (script ile otomatik oluşturulan) çalışma mantığını ve yapılandırmasını açıklar.

## 1. Temel Yapı ve Öncelik (Priority) Mantığı

GLPI ticket öncelikleri (Urgency x Impact matrisi) ile SLA seviyeleri (P1-P5) arasındaki ilişki ITIL standartlarına uygun olarak yapılandırılmıştır.

**Priority Mapping:**
GLPI'da öncelik (Priority) 1'den 5'e kadar numaralandırılır, ancak ITIL SLA mantığında P1 en kritik (en kısa süre), P5 en düşük (en uzun süre) önceliktir. Script bu dönüşümü otomatik yapar.

| GLPI Priority | Tanım | Eşleşen SLA Seviyesi | Açıklama |
|---|---|---|---|
| **5** | Very High (Çok Yüksek) | **P1** | En Kritik (En kısa TTO/TTR) |
| **4** | High (Yüksek) | **P2** | Yüksek Öncelik |
| **3** | Medium (Orta) | **P3** | Orta Öncelik |
| **2** | Low (Düşük) | **P4** | Düşük Öncelik |
| **1** | Very Low (Çok Düşük) | **P5** | En Düşük (En uzun TTO/TTR) |

---

## 2. Business Rules Yapılandırması (Otomatik Oluşturulan)

Python scripti (`rules_business_sla.py`) tarafından oluşturulan kuralların standart yapısı aşağıdadır.

*Kural Yolu: Administration > Rules > Business rules for tickets*

### 2.1. Kural İsimlendirme Standardı
Kurallar okunabilirliği artırmak ve karışıklığı önlemek için şu formatı kullanır:

**Incident Kuralları (Priority-based):**
`Auto-SLA-[Entity-Adı]-Priority-P[1-5]-Incident`

**Request Kuralları (Sabit P3):**
`Auto-SLA-[Entity-Adı]-Request-P3`

Örnekler:
- `Auto-SLA-Prime-Sistem-Priority-P1-Incident` (Prime Sistem için En Kritik Incident Kuralı)
- `Auto-SLA-Merkez-Prime-Hastanesi-Priority-P3-Incident` (Orta Seviye Incident Kuralı)
- `Auto-SLA-Prime-Sistem-Request-P3` (Prime Sistem için Request Kuralı - tüm priority'ler için P3 SLA)

> **Not:** Entity adlarındaki boşluklar otomatik olarak tire ile değiştirilir.

### 2.2. Kriterler (Criteria)

**Incident Kuralları için 3 kriter (AND):**
1. **Type is Incident (1):** Sadece Incident tipindeki ticketlar
2. **Entity is [Müşteri Adı]:** İlgili müşteri entity'si
3. **Priority is [1-5]:** GLPI priority değeri (5=Very High → P1, 1=Very Low → P5)

**Request Kuralları için 2 kriter (AND):**
1. **Type is Request (2):** Sadece Request tipindeki ticketlar
2. **Entity is [Müşteri Adı]:** İlgili müşteri entity'si
   - **Not:** Request'lerde priority kontrolü YOK - tüm Request'ler P3 SLA alır

**Kural Özellikleri:**
- **is_active:** 1 (Aktif)
- **is_recursive:** 1 (Alt varlıklar dahil)
- **condition:** 3 (Add/Update - Hem ekleme hem güncelleme anında)
- **match:** AND
- **entities_id:** 0 (Root seviyesinde oluşturulur)

### 2.3. Aksiyonlar (Actions)
Kural eşleştiğinde 2 aksiyon tetiklenir:

1. **Assign TTO:** İlgili SLA'nın TTO (Time to Own) değerini atar
2. **Assign TTR:** İlgili SLA'nın TTR (Time to Resolve) değerini atar

> **Not:** "Stop Rules Processing" aksiyonu **KALDIRILDI**. Bu sayede SLA atamasından sonra kategori bazlı grup ataması yapan kurallar (Ranking 20) çalışabilir. Major Incident koruması ayrı bir script (Ranking 10) ile sağlanır.

---

## 3. SLA Veri Kaynağı ve Güncelleme (ÖNEMLİ)

Script, TTO/TTR sürelerini **kendi içinde saklamaz**. Bu verileri her çalıştırıldığında anlık olarak **GLPI**'dan çeker.

**Nasıl Çalışır?**
1. Script `entity_sla_map.json` dosyasından müşterinin SLA paket adını öğrenir (Örn: `SLA-SILVER-5X9`).
2. GLPI'a bağlanır ve **Setup > SLM > SLAs** altındaki tüm SLA tanımlarını tarar.
3. İsmi `SLA-SILVER-5X9` ve `P1` (veya P2, P3...) içeren SLA'yı bulur.
4. O SLA'nın **ID'sini** alıp kurala bağlar.

**Yönetim Senaryoları:**

*   **Senaryo 1: Süre Değişikliği (Örn: P1 TTO süresi 30dk yerine 15dk olacak)**
    *   **Ne Yapılmalı:** Sadece GLPI arayüzünden ilgili SLA'nın süresini değiştirin.
    *   **Script:** Scripti çalıştırmaya **GEREK YOKTUR**. Kural zaten o SLA ID'sine bağlıdır, süre değişince otomatik uyum sağlar.

*   **Senaryo 2: SLA Silinip Yeniden Oluşturuldu veya Yeni Kural Eklendi**
    *   **Ne Yapılmalı:** Script çalıştırılmalıdır.
    *   **Script:** Mevcut kuralları bulursa **GÜNCELLER (UPDATE)**. Kriterleri ve aksiyonları silip en baştan doğrusunu yazar. Kural ID'si değişmez.

---

## 4. Kurulum ve Konfigürasyon (Yeni)

Script artık merkezi bir yapılandırma sistemi kullanmaktadır.

### 4.1. Config Dosyası (`config.json`)
Script, GLPI bağlantı bilgilerini içeren `config.json` dosyasını sırasıyla şu lokasyonlarda arar:
1. Script ile aynı dizin
2. `../Config/` (Bir üst dizindeki Config klasörü)
3. `../../Config/` (İki üst dizindeki Config klasörü)

Bu sayede config dosyalarınızı merkezi bir yerde yönetebilirsiniz.

### 4.2. Ölçeklenebilirlik (Pagination)
Script, **1000'den fazla** Entity veya SLA olması durumunda verileri otomatik olarak sayfalayarak (batch fetch) çeker. Büyük GLPI ortamlarında sorunsuz çalışır.

### 4.3. Entity Haritası (`entity_sla_map.json`)
Müşteri - SLA eşleştirmeleri bu dosyada tutulur. Script ile aynı dizinde veya config arama yollarında bulunmalıdır.

Format:
```json
{
    "Müşteri Adı": "SLA-PAKET-ADI",
    "Prime Sistem": "SLA-PLATINUM-7X24"
}
```

### 4.4. Güvenlik ve Stabilite (v2.2 Özellikleri)
Script aşağıdaki güvenlik mekanizmalarıyla güçlendirilmiştir:
*   **Duplicate Detection (Kopya Kontrolü):** GLPI Search API kullanılarak mevcut kurallar "Auto-SLA" ismiyle taranır. Aynı isimli kural varsa **ID değişmeden güncellenir**. Asla duplicate kural oluşturmaz.
*   **Safe Updates (Güvenli Güncelleme):** Güncelleme sırasında, kuralın detayları (Criteria/Actions) silinirken **ID kontrolü** yapılır. Bu sayede script, yanlışlıkla başka kuralların (Business Rules, vb.) aksiyonlarını silme riskine karşı (GLPI API buglarına karşı) korumalıdır.
*   **Timeouts (Zaman Aşımı):** Tüm GLPI API sorgularına **30 saniyelik** zaman aşımı (timeout) eklenmiştir. Network takılmalarında scriptin asılı kalması (hang) engellenir.

---

## 5. Müşteri & SLA Segment Referans Tablosu

Scriptin `entity_sla_map.json` dosyasından okuyarak uyguladığı güncel eşleştirmeler:

| Müşteri Entitysi | SLA Segmenti & Takvimi |
|---|---|
| **Prime Sistem** | SLA-PLATINUM-7X24 |
| **Batıçim** | SLA-GOLD-5X9 |
| **Çiftay** | SLA-GOLD-5X9 |
| **Dorçe** | SLA-GOLD-5X9 |
| **Madalyon & OGM** | SLA-GOLD-7X9 |
| **Bakpiliç** | SLA-SILVER-7X24 |
| **Akfen Kadıköy Terminal AVM** | SLA-SILVER-7X12 |
| **Merkez Prime Hastanesi** | SLA-SILVER-5X9 |
| **Ankara Cerrahi Tıp Hastanesi** | SLA-SILVER-5X9 |
| **Özel Medsentez Polikliniği** | SLA-SILVER-5X9 |
| **Özel Eryaman Hastanesi** | SLA-SILVER-5X9 |
| **Elimko** | SLA-SILVER-5X9 |
| **Esila** | SLA-SILVER-5X9 |
| **Hayata Destek Derneği** | SLA-SILVER-5X9 |
| **İdak** | SLA-SILVER-5X9 |
| **Mervak** | SLA-SILVER-5X9 |
| **Nesibe Aydın** | SLA-SILVER-5X9 |
| **Netisa** | SLA-SILVER-5X9 |
| **Pfifner** | SLA-SILVER-5X9 |
| **Akfen Bodrum Loft** | SLA-BRONZE-7X24 |
| **Ankara Oto** | SLA-BRONZE-7X9 |
| **Ersen Ceran Öğrenci Yurdu** | SLA-BRONZE-7X9 |
| **Akfen Yenilenebilir Enerji** | SLA-BRONZE-5X9 |
| **Ankara Yem** | SLA-BRONZE-5X9 |
| **Karabük İl Özel İdaresi** | SLA-BRONZE-5X9 |

## 6. Script Kullanımı

Kuralları yeniden oluşturmak veya güncellemek gerekirse:

1. `entity_sla_map.json` dosyasını güncelleyin (yeni müşteri varsa).
2. Scripti `force` parametresiyle çalıştırın:
   
   ```bash
   python rules_business_sla.py --force
   ```

   **Parametresiz Çalıştırma (Dry-Run):**
   Sadece `python rules_business_sla.py` şeklinde çalıştırırsanız, yapılacak değişiklikleri ekrana yazar ancak GLPI'da değişiklik yapmaz.

---
**Son Güncelleme:** 7 Ocak 2026  
**Script Versiyonu:** v2.6 (Request SLA Support)

**Değişiklikler (v2.6):**
- ✅ **Request SLA Support:** Request tipindeki ticketlar için P3 SLA ataması eklendi
- ✅ **Dual Rule System:** Incident'ler için priority-based (P1-P5), Request'ler için sabit P3
- ✅ **Updated Naming:** Incident kurallarına `-Incident` suffix'i eklendi
- ✅ **Removed Stop Processing:** Kategori bazlı grup ataması için rule chain devam eder

**Değişiklikler (v2.5):**
- ✅ **Add/Update Trigger:** Condition 3 ile hem oluşturma hem güncelleme anında tetiklenir
- ✅ **Wipe & Rebuild:** Güncelleme sırasında kriter çakışmasını önlemek için güvenli temizlik
- ✅ **Safe Update:** Mevcut kuralları ID kontrolü ile günceller

**Değişiklikler (v2.4):**
- ✅ **Standardize Naming:** Hyphen-only format
- ✅ **Space Handling:** Entity adlarındaki boşluklar otomatik olarak tire ile değiştirilir
- ✅ **Timeout Koruması:** Tüm API çağrılarında 30sn timeout

Hazırlayan : Bora Ergül
