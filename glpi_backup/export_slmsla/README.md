# GLPI SLM/SLA Export ve Import Scriptleri

Bu scriptler, GLPI sunucuları arasında SLM (Service Level Management) ve SLA (Service Level Agreement) verilerini taşımak için kullanılır.

## Dizin Yapısı

```
glpi_backup/
├── export_slmsla/          # Kaynak sunucudan veri çekme
│   ├── config.json         # Kaynak GLPI bağlantı bilgileri
│   ├── export_slmsla.py    # Export scripti
│   ├── calendars_export.json    # Export edilen takvimler
│   └── slms_export.json    # Export edilen SLM/SLA'lar
│
└── import_slmsla/          # Hedef sunucuya veri aktarma
    ├── config.json         # Hedef GLPI bağlantı bilgileri
    ├── import_slmsla.py    # Import scripti
    ├── calendars_export.json    # İçe aktarılacak takvimler
    └── slms_export.json    # İçe aktarılacak SLM/SLA'lar
```

## Kullanım

### 1. Export (Veri Çekme)

Kaynak GLPI sunucusundan SLM/SLA verilerini export etmek için:

```bash
cd "c:\Users\maniac\Desktop\ITSM - GLPI\Script\glpi_backup\export_slmsla"
python export_slmsla.py
```

**Çıktı:**
- `calendars_export.json` - Takvim tanımları
- `slms_export.json` - SLM konteynerleri ve SLA kuralları

### 2. Import (Veri Aktarma)

Export edilen verileri hedef GLPI sunucusuna aktarmak için:

```bash
cd "c:\Users\maniac\Desktop\ITSM - GLPI\Script\glpi_backup\import_slmsla"
python import_slmsla.py
```

**İşlem Sırası:**
1. **Takvimler** oluşturulur/eşleştirilir
2. **SLM konteynerleri** oluşturulur/eşleştirilir
3. **SLA kuralları** oluşturulur/eşleştirilir

## Konfigürasyon

Her iki dizinde de `config.json` dosyası bulunur:

```json
{
    "GLPI_URL": "http://192.168.50.243/glpi/apirest.php/",
    "GLPI_APP_TOKEN": "your-app-token",
    "GLPI_USER_TOKEN": "your-user-token"
}
```

**Önemli:** Export ve import için farklı `config.json` dosyaları kullanılır:
- `export_slmsla/config.json` → Kaynak sunucu bilgileri
- `import_slmsla/config.json` → Hedef sunucu bilgileri

## Özellikler

### ✅ Duplicate Check
Script, mevcut kayıtları tespit eder ve tekrar oluşturmaz:
- Aynı isimde Calendar varsa → Mevcut ID kullanılır
- Aynı isimde SLM varsa → Mevcut ID kullanılır
- Aynı isimde SLA varsa → Atlanır

### ✅ ID Mapping
Kaynak ve hedef sunuculardaki farklı ID'ler otomatik eşleştirilir:
- Calendar ID'leri eşleştirilir
- SLM ID'leri eşleştirilir
- SLA'lar doğru parent SLM'ye bağlanır

### ✅ İlişki Koruması
Tüm parent-child ilişkileri korunur:
- SLA → SLM bağlantısı
- SLA → Calendar bağlantısı
- SLM → Calendar bağlantısı

## GLPI Yapısı

GLPI'da SLM/SLA hiyerarşisi şu şekildedir:

```
SLM (Service Level Management)
└── SLA (Service Level Agreement)
    ├── number_time: 5
    ├── definition_time: "minute"
    ├── type: 1 (TTO) veya 0 (TTR)
    └── calendars_id: X
```

- **SLM**: Ana konteyner (ör: "SLA-PLATINUM-7X24")
- **SLA**: İçindeki kurallar (ör: "PLAT-7x24-P1-TTO-5m")

## Örnek Kullanım Senaryosu

1. **Kaynak sunucudan export:**
   ```bash
   cd export_slmsla
   python export_slmsla.py
   ```
   → `calendars_export.json` ve `slms_export.json` oluşturulur

2. **Dosyaları hedef sunucuya kopyala:**
   ```bash
   copy calendars_export.json ..\import_slmsla\
   copy slms_export.json ..\import_slmsla\
   ```

3. **Hedef sunucuya import:**
   ```bash
   cd ..\import_slmsla
   python import_slmsla.py
   ```

4. **Tekrar çalıştırma güvenli:**
   ```bash
   python import_slmsla.py  # Duplicate oluşturmaz
   ```

## Gereksinimler

- Python 3.x
- `requests` kütüphanesi
- GLPI API erişimi (App-Token ve User-Token)
- Super-Admin yetkisi (SLM/SLA oluşturma için)

## Notlar

- Script, GLPI REST API kullanır
- SSL doğrulaması devre dışıdır (`verify=False`)
- Export edilen dosyalar UTF-8 formatındadır
- Script idempotent'tir (tekrar çalıştırılabilir)
