# GLPI Category-Based Group Assignment Rules

Bu script, GLPI'de ITIL kategorisine göre otomatik olarak teknisyen grubu ataması yapan business rule'ları oluşturur.

## 🎯 Amaç

Kullanıcılar ticket açarken kategori seçtiğinde, ticket otomatik olarak o kategoriye özel teknisyen grubuna atanır:

- **Server & Storage** (221) → Sistem ve Yedekleme Ekibi (3)
- **Security** (222) → Güvenlik Ekibi (2)
- **Network & Firewall** (223) → Network & Firewall Ekibi (1)
- **Endpoint & End-User** (225) → Endpoint & Enduser Ekibi (18)
- **Cloud** (226) → Bulut Ekibi (17)
- **Genel Destek** (227) → Genel Destek Ekibi (16)
- **Monitoring Alerts** (228) → İzleme Ekibi (7)

## 📋 Özellikler

- ✅ **Kategori Bazlı Atama**: Her kategori için özel ekip ataması
- ✅ **Otomatik Kural Oluşturma**: 7 kategori için otomatik rule oluşturur
- ✅ **Güncelleme Desteği**: Mevcut kuralları güvenli şekilde günceller
- ✅ **Duplicate Önleme**: Aynı isimli kural varsa günceller
- ✅ **Timeout Koruması**: Tüm API çağrılarında 30sn timeout
- ✅ **Dry-Run Modu**: Varsayılan olarak test modunda çalışır
- ✅ **Session Yönetimi**: Otomatik GLPI API session yönetimi
- ✅ **Pagination**: Büyük veri setleri için pagination desteği

## 🚀 Kullanım

### 1. Dry-Run (Test Modu)

Varsayılan olarak test modunda çalışır. Hiçbir değişiklik yapmaz, sadece oluşturulacak kuralları listeler.

```bash
cd rules_itilcategory_assign
python rules_itilcategory_assign.py
```

**Örnek Çıktı:**
```
======================================================================
GLPI Category-Based Group Assignment Rule Creator
======================================================================
Mode: DRY-RUN (simulation only)
======================================================================

✓ Session initialized: abc123...
Fetching ITIL Categories...
✓ Loaded 9 categories
Fetching Groups...
✓ Loaded 41 groups
Fetching existing rules...
✓ Found 0 existing rules

======================================================================
SUMMARY
======================================================================
Categories: 9
Groups: 41
Existing Rules: 0
Rules to Create/Update: 7
======================================================================

======================================================================
PROPOSE: CREATE rule 'Auto-Category-Group-221'
  Category: Server & Storage (ID: 221)
  Assign Group: Sistem ve Yedekleme Ekibi (ID: 3)
  Criteria:
    - ITIL Category = Server & Storage (ID: 221)
  Actions:
    - Assign Technician Group → Sistem ve Yedekleme Ekibi (ID: 3)
  [DRY RUN] No changes made
======================================================================
...
```

### 2. Gerçek Çalıştırma (--force)

Kuralları gerçekten oluşturmak için `--force` parametresini kullanın.

```bash
python rules_itilcategory_assign.py --force
```

> ⚠️ **ÖNEMLİ: Manuel Düzeltme Gerekli!**
> 
> GLPI API limitasyonu nedeniyle, script criteria'ları "does not exist" yerine "exists" olarak oluşturur.
> 
> **Script çalıştıktan sonra, her rule'u GLPI UI'de manuel olarak düzeltmelisiniz:**
> 
> 1. GLPI'de Setup > Rules > Business rules for tickets
> 2. Oluşturulan rule'u açın (örn: "Auto-Category-Security")
> 3. Criteria sekmesine gidin
> 4. **"Technician exists"** → Dropdown'dan **"does not exist"** seçin
> 5. **"Technician group exists"** → Dropdown'dan **"does not exist"** seçin
> 6. Save/Update butonuna tıklayın
> 7. Tüm 7 rule için tekrarlayın
> 
> Bu, GLPI API'sinin condition code 8 ile boş pattern kullanıldığında "does not exist" yerine "exists" oluşturmasından kaynaklanır.

### 3. Manuel Düzeltme Adımları (Detaylı)

**Her rule için (toplam 7 rule):**

| Rule Name | Düzeltilecek Criteria |
|-----------|----------------------|
| Auto-Category-Server-And-Storage | Technician + Group |
| Auto-Category-Security | Technician + Group |
| Auto-Category-Network-And-Firewall | Technician + Group |
| Auto-Category-Endpoint-And-End-User | Technician + Group |
| Auto-Category-Cloud | Technician + Group |
| Auto-Category-Genel-Destek | Technician + Group |
| Auto-Category-Monitoring-Alerts | Technician + Group |

**Düzeltme Süreci:**
- Her rule için ~30 saniye
- Toplam süre: ~3,5 dakika (7 rule)

## 🎯 Kural Yapısı

Her oluşturulan kural şu özelliklere sahiptir:

### Kural İsmi
**Format:** `Auto-Category-{KategoriAdı}`

**Örnekler:**
- `Auto-Category-Server-And-Storage`
- `Auto-Category-Security`
- `Auto-Category-Network-And-Firewall`

### Kriterler
1. **ITIL Category** = Belirli bir kategori (örn: Security)

### Aksiyonlar
1. **Technician Group** → Kategoriye özel ekip

### Kural Özellikleri
- **is_active:** 1 (Aktif)
- **is_recursive:** 1 (Alt varlıklar dahil)
- **condition:** 3 (GLPI kural motoru için)
- **match:** AND
- **ranking:** 20 (SLA rule'larından sonra, diğer rule'lardan önce)

## 📊 Kategori-Grup Eşleştirmesi

| Kategori ID | Kategori Adı | Grup ID | Grup Adı |
|-------------|--------------|---------|----------|
| 221 | Server & Storage | 3 | Sistem ve Yedekleme Ekibi |
| 222 | Security | 2 | Güvenlik Ekibi |
| 223 | Network & Firewall | 1 | Network & Firewall Ekibi |
| 225 | Endpoint & End-User | 18 | Endpoint & Enduser Ekibi |
| 226 | Cloud | 17 | Bulut Ekibi |
| 227 | Genel Destek | 16 | Genel Destek Ekibi |
| 228 | Monitoring Alerts | 7 | İzleme Ekibi |

**Not:**
- Kategori 224 (Field Service) ve Saha Ekibi sistemden kaldırılmıştır
- Kategori 229 (Major Incident) için kural oluşturulmaz (`rules_business_incident_major.py` tarafından yönetilir)
- Toplam 7 kategori için otomatik grup ataması yapılır

## 🔍 Teknik Detaylar

### GLPI API Endpoint'leri
- `/ITILCategory` - Kategorileri çeker
- `/Group` - Grupları çeker
- `/search/RuleTicket` - Mevcut kuralları çeker
- `/RuleTicket` - Kural oluşturur
- `/RuleTicket/{id}/RuleCriteria` - Kriter ekler
- `/RuleTicket/{id}/RuleAction` - Aksiyon ekler

### Kural Kriterleri - Condition Kodları
- **0** = is (eşittir)

### Kural Aksiyonları - Field Kodları
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

Config dosyası şu lokasyonlarda aranır:
1. Mevcut dizin (`config.json`)
2. `../config/config.json`
3. `../Config/config.json`
4. `../../config/config.json`
5. `../../Config/config.json`

## 🎬 Çalışma Senaryosu

### Örnek: Security Ticket

**Kullanıcı Aksiyonu:**
```
Ticket Type: Incident
Category: Security (222)
Entity: Dorçe
```

**Rule Execution:**
1. ✅ `Auto-Category-Group-222` çalışır
2. ✅ Ticket → Güvenlik Ekibi (2) atanır

**Sonuç:** Security ticket'ı otomatik olarak Güvenlik Ekibi'ne gider! ✅

### Örnek: Network Ticket

**Kullanıcı Aksiyonu:**
```
Ticket Type: Request
Category: Network & Firewall (223)
Entity: Ultron Bilişim
```

**Rule Execution:**
1. ✅ `Auto-Category-Group-223` çalışır
2. ✅ Ticket → Network & Firewall Ekibi (1) atanır

**Sonuç:** Network ticket'ı otomatik olarak Network & Firewall Ekibi'ne gider! ✅

## 🔗 İlgili Scriptler

1. **rules_email.py** - E-posta kuralları (Entity ataması)
2. **rules_business_sla.py** - SLA kuralları (Incident için)
3. **rules_business_incident_major.py** - Major Incident kuralları
4. **rules_business.py** - Business rules (Request için)
5. **rules_itilcategory_assign.py** - Kategori bazlı grup ataması (bu script)

## 📝 Notlar

### Önemli Bilgiler
1. **Ranking 20**: SLA rule'larından (15) sonra, diğer rule'lardan önce çalışır
2. **Stop Processing Yok**: Diğer rule'ların da çalışmasına izin verir
3. **Recursive**: Tüm kurallar alt varlıklara da uygulanır
4. **Kategori Kontrolü**: Sadece kategori seçilmişse çalışır
5. **Mevcut Kurallar**: Aynı isimli kural varsa günceller, yoksa oluşturur

### Avantajlar
- ✅ Doğru ekibe otomatik atama
- ✅ Manuel atama hatalarını önler
- ✅ Ticket çözüm süresini kısaltır
- ✅ Ekip iş yükünü dengeler

## 🐛 Sorun Giderme

### GLPI API Limitation: "exists" vs "does not exist"

**Sorun:** Script ile oluşturulan rule'larda criteria "exists" olarak görünüyor, "does not exist" olarak değil.

**Neden:** GLPI API'si condition code 8 ile boş pattern kullanıldığında "does not exist" yerine "exists" oluşturuyor. Bu bilinen bir GLPI API limitasyonudur.

**Çözüm:** Manuel düzeltme gerekli (yukarıdaki adımları takip edin).

**Alternatif:** Gelecekte GLPI API güncellenirse, script otomatik olarak doğru criteria oluşturabilir.

### Grup Bulunamıyor
**Sorun:** "Unknown (ID)" mesajı alıyorsunuz.

**Çözüm:**
- GLPI'de ilgili grubun mevcut olduğundan emin olun
- Grup ID'lerini kontrol edin
- Script'teki `CATEGORY_GROUP_MAP` değerlerini güncelleyin

### Kategori Bulunamıyor
**Sorun:** "Unknown (ID)" mesajı alıyorsunuz.

**Çözüm:**
- GLPI'de ilgili kategorinin mevcut olduğundan emin olun
- Kategori ID'lerini kontrol edin

### API Bağlantı Hatası
**Sorun:** "Failed to initialize session" hatası alıyorsunuz.

**Çözüm:**
1. `config.json` dosyasının doğru konumda olduğundan emin olun
2. API token'larının geçerli olduğunu kontrol edin
3. GLPI URL'inin doğru olduğunu kontrol edin

## 📄 Lisans

Bu script GLPI otomasyonu için geliştirilmiştir.

---

**Versiyon:** 1.2  
**Son Güncelleme:** 22 Şubat 2026  

**Değişiklikler (v1.2):**
- 🗑️ **Field Service kaldırıldı:** Kategori 224 (Field Service) ve Saha Ekibi (19) sistemden kaldırıldı
- ✅ Kategori sayısı 8 → 7 olarak güncellendi

**Değişiklikler (v1.1):**
- ✅ **Add/Update Trigger:** Condition 3 ile güncelleme desteği eklendi
- ✅ **Safe Update:** Wipe & Rebuild mantığı ile duplicate önleme  

**Değişiklik Notları:**

**v1.0 (25 Aralık 2024):**
- ✅ İlk versiyon
- ✅ 7 kategori için otomatik grup ataması
- ✅ Dry-run modu
- ✅ Güncelleme desteği
- ✅ Timeout koruması
- ✅ Pagination desteği

---

Hazırlayan: Bora Ergül
