# Tanımsız Domain Email Rule Script

Bu script, GLPI'da tanımlı olmayan (bilinmeyen) domain'lerden gelen e-postaları otomatik olarak belirli bir entity'ye yönlendiren "Tanımsız domain" kuralını oluşturur.

## 📋 Genel Bakış

Script, GLPI API'sinden tüm entity'lerin mail domain bilgilerini çeker ve bu domainlerden **gelmeyen** e-postaları yakalamak için bir catch-all (yakalama) kuralı oluşturur. Bu sayede:

- ✅ Tanımlı müşteri domainlerinden gelen e-postalar kendi entity'lerine gider
- ✅ Tanımsız/bilinmeyen domainlerden gelen e-postalar "Genel destek" entity'sine yönlendirilir
- ✅ Hiçbir e-posta kaybolmaz veya yanlış yere atanmaz

## 🎯 Kural Mantığı

Kural şu şekilde çalışır:

```
EĞER e-posta gönderen adresi:
  - @ultron.com.tr DEĞİLSE VE
  - @merkezprime.com.tr DEĞİLSE VE
  - @ankaraoto.com DEĞİLSE VE
  - ... (diğer 14 domain)
O ZAMAN:
  → Entity'yi "Genel destek" (ID: 32) olarak ata
```

## 🚀 Kullanım

### Önkoşullar

- Python 3.x
- `requests` kütüphanesi (`pip install requests`)
- GLPI API erişimi (config.json dosyası gerekli)

### Dry-Run Modu (Önerilen İlk Adım)

Önce değişiklik yapmadan ne yapılacağını görmek için:

```powershell
cd "c:\Users\Super\Desktop\ITSM - GLPI\Script\Unknown domain"
python rules_unknowndomain.py
```

**Çıktı Örneği:**
```
Found 17 entities with valid mail domains.
Target entity 'Root Entity > Ultron Bilişim > Internal IT > Genel destek' found with ID: 32

PROPOSE: CREATE rule 'Tanımsız-Domain'
Number of domains to exclude: 17

Domains that will be EXCLUDED:
  - @ultron.com.tr
  - @merkezprime.com.tr
  - @ankaraoto.com
  ...

DRY-RUN MODE: No changes will be made. Use --force to execute.
```

### Kuralı Oluşturma (Gerçek Çalıştırma)

Dry-run çıktısını kontrol ettikten sonra, kuralı oluşturmak için:

```powershell
python rules_unknowndomain.py --force
```

### Özel Entity Belirtme

Farklı bir entity'ye yönlendirmek isterseniz:

```powershell
python rules_unknowndomain.py --target-entity "Root Entity > Başka Entity" --force
```

## 📊 Kural Detayları

| Özellik | Değer |
|---------|-------|
| **Kural Adı** | Tanımsız-Domain |
| **Tip** | RuleMailCollector |
| **Ranking** | 2 |
| **Durum** | Aktif |
| **Kriter Sayısı** | 17 (her domain için bir kriter) |
| **Kriter Koşulu** | "is not" (değilse) |
| **Aksiyon** | Entity ataması → Genel destek (ID: 32) |

## 🔍 GLPI'da Doğrulama

Kural oluşturulduktan sonra GLPI arayüzünden kontrol edin:

1. **Setup** > **Automatic actions** > **Rules for assigning a ticket created through a mail collector**
2. "**Tanımsız-Domain**" kuralını bulun
3. Kontrol edin:
   - ✅ Ranking: 2
   - ✅ Durum: Aktif
   - ✅ 17 kriter var (her biri "from" field, "is not" condition)
   - ✅ 1 aksiyon var (entities_id = 32)

## 🧪 Test Senaryoları

### Test 1: Tanımlı Domain
```
Gönderen: destek@ultron.com.tr
Beklenen: Bu kural tetiklenmez (domain listede olduğu için)
Sonuç: E-posta kendi entity kuralına göre işlenir
```

### Test 2: Tanımsız Domain
```
Gönderen: kullanici@gmail.com
Beklenen: Bu kural tetiklenir
Sonuç: Ticket "Genel destek" entity'sine atanır
```

## 📁 Dosya Yapısı

```
Unknown domain/
├── rules_unknowndomain.py            # Ana script
├── README.md                         # Bu dosya
├── debug_entities.py                 # Debug helper (opsiyonel, silinebilir)
└── list_entities_temp.py            # Debug helper (opsiyonel, silinebilir)
```

## ⚙️ Teknik Detaylar

### Script Akışı

1. **Config Yükleme**: `../Config/config.json` dosyasından GLPI credentials
2. **Session Başlatma**: GLPI API session token alma
3. **Entity Fetching**: Tüm entity'leri çekme (33 entity)
4. **Domain Extraction**: Valid mail domain'leri filtreleme (17 domain)
5. **Path Traversal**: Target entity'yi hiyerarşik path ile bulma
6. **Rule Check**: Mevcut "Tanımsız-Domain" kuralını kontrol
7. **Rule Creation/Update**: 
   - Varsa: Eski kriterleri ve aksiyonları sil, yenilerini ekle
   - Yoksa: Yeni kural oluştur
8. **Criteria Addition**: Her domain için "is not" kriteri ekle
9. **Action Addition**: Entity ataması aksiyonu ekle
10. **Session Kapatma**: GLPI session'ı sonlandır

### API Endpoints Kullanımı

| Endpoint | Method | Amaç |
|----------|--------|------|
| `/initSession` | GET | Session token alma |
| `/Entity` | GET | Tüm entity'leri listeleme |
| `/search/RuleMailCollector` | GET | Mevcut kuralları arama |
| `/RuleMailCollector` | POST | Yeni kural oluşturma |
| `/RuleMailCollector/{id}/RuleCriteria` | GET/POST/DELETE | Kriter yönetimi |
| `/RuleMailCollector/{id}/RuleAction` | GET/POST/DELETE | Aksiyon yönetimi |
| `/killSession` | GET | Session sonlandırma |

### Önemli Notlar

⚠️ **expand_dropdowns Kullanımı**: Script, entity'leri çekerken `expand_dropdowns` parametresini **kullanmaz**. Çünkü bu parametre `entities_id` değerini sayısal ID yerine full path string'e çevirir, bu da hiyerarşi traversal'ını bozar.

⚠️ **Root Entity Handling**: "Root Entity" GLPI'da gerçek bir entity değildir (ID=0). Script, path'in başındaki "Root Entity" ifadesini otomatik olarak atlar.

⚠️ **None Handling**: Bazı entity'lerin `mail_domain` değeri `None` olabilir. Script bunu handle eder.

## 🔧 Sorun Giderme

### Hata: "Could not find entity with path"

**Sebep**: Belirtilen entity path'i bulunamadı.

**Çözüm**: Script otomatik olarak mevcut entity'leri listeler. Doğru path'i `--target-entity` ile belirtin:

```powershell
python rules_unknowndomain.py --target-entity "Doğru > Path > Buraya"
```

### Hata: "No valid mail domains found"

**Sebep**: Hiçbir entity'de geçerli mail domain tanımlı değil.

**Çözüm**: GLPI'da entity'lere mail domain ekleyin (format: `@domain.com`)

### Hata: "Failed to initialize session"

**Sebep**: GLPI API credentials hatalı veya GLPI erişilemiyor.

**Çözüm**: 
1. `../Config/config.json` dosyasını kontrol edin
2. GLPI URL'inin doğru olduğundan emin olun
3. App Token ve User Token'ın geçerli olduğunu doğrulayın

## 📝 Güncelleme ve Bakım

### Kural Güncelleme

Script, mevcut "Tanımsız domain" kuralını bulursa otomatik olarak günceller:
- Eski kriterler ve aksiyonlar silinir
- Yeni domain listesi ile kriterler yeniden oluşturulur

### Yeni Entity Eklendiğinde

Yeni bir müşteri entity'si eklendiğinde ve mail domain tanımlandığında:

```powershell
python rules_unknowndomain.py --force
```

Script otomatik olarak yeni domain'i algılar ve kuralı günceller.

## 📄 Lisans

Bu script, GLPI ITSM projesi için geliştirilmiştir.

## 👤 Geliştirici Notları

- **Kural Ranking**: 2 olarak ayarlanmıştır (backup XML'den alınmıştır)
- **Kriter Condition**: 3 = "is not" / "does not equal"
- **Match Type**: AND (tüm kriterler sağlanmalı)
- **Recursive**: Hayır (sadece belirtilen entity)

## Özellikler (v2.4)
- ✅ **Timeout Koruması:** Tüm API çağrılarında 30sn timeout
- ✅ **Duplicate Prevention:** Range parametresi (0-5000) ile güvenli silme
- ✅ **Güvenli Güncelleme:** Mevcut kuralları ID kontrolü ile günceller
- ✅ **Standardize Naming:** Hyphen-only format (`Tanımsız-Domain`)

---
**Versiyon:** 2.4  
**Son Güncelleme:** 25 Aralık 2024


Hazırlayan : Bora Ergül
