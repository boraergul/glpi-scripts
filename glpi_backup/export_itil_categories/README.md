# GLPI ITIL Categories Export Scripti

Bu script, GLPI sunucusundan ITIL kategorilerini export eder ve CSV formatında kaydeder.

## Dosyalar

```
export_itil_categories/
├── config.json                    # GLPI bağlantı bilgileri
├── export_itil_categories.py      # Export scripti
└── glpi_itil_categories_v2.csv    # Export edilen kategoriler (çıktı)
```

## Kullanım

```bash
cd "c:\Users\maniac\Desktop\ITSM - GLPI\Script\glpi_backup\export_itil_categories"
python export_itil_categories.py
```

## Konfigürasyon

Script, üst dizindeki `config/config.json` dosyasını kullanır:

```json
{
    "GLPI_URL": "http://192.168.50.243/glpi/apirest.php/",
    "GLPI_APP_TOKEN": "your-app-token",
    "GLPI_USER_TOKEN": "your-user-token"
}
```

## Çıktı Formatı

Export edilen CSV dosyası (`glpi_itil_categories_v2.csv`) şu formatta olur:

```csv
name
01 - Cloud
01.01 - AWS
01.02 - Azure
02 - Network
02.01 - Firewall
```

**Format:** `Kod - Kategori Adı`
- Kodlar otomatik oluşturulur (01, 02, 01.01, vb.)
- Hiyerarşi korunur (parent-child ilişkileri)
- CSV delimiter: `;` (noktalı virgül)
- Encoding: UTF-8 with BOM

## Özellikler

### ✅ Otomatik Kod Oluşturma
- Root kategoriler: `01`, `02`, `03`, ...
- Alt kategoriler: `01.01`, `01.02`, `01.03`, ...
- Daha derin seviyeler: `01.01.01`, `01.01.02`, ...

### ✅ Hiyerarşi Koruması
- Kategoriler `completename` alanına göre sıralanır
- Parent-child ilişkileri korunur
- GLPI'daki hiyerarşi aynen yansıtılır

### ✅ HTML Entity Decode
- HTML karakterleri düzgün işlenir (örn: `&amp;` → `&`)

## Import İçin Kullanım

Export edilen CSV dosyası, `import_itil_categories` scripti ile başka bir GLPI sunucusuna aktarılabilir:

1. **Export:**
   ```bash
   cd export_itil_categories
   python export_itil_categories.py
   ```

2. **CSV'yi import dizinine kopyala:**
   ```bash
   copy glpi_itil_categories_v2.csv ..\import_itil_categories\itil_categories.csv
   ```

3. **Import:**
   ```bash
   cd ..\import_itil_categories
   python import_itil_categories.py
   ```

## Gereksinimler

- Python 3.x
- `requests` kütüphanesi
- GLPI API erişimi (App-Token ve User-Token)

## Notlar

- Script, GLPI REST API kullanır
- SSL doğrulaması devre dışıdır (`verify=False`)
- Tüm ITIL kategorileri export edilir
- Pagination otomatik yapılır (1000'er kayıt)
