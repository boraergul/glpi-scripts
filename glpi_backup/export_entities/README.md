# GLPI Entity Export ve Import Scriptleri

Bu scriptler, GLPI sunucuları arasında Entity (Birim) yapısını hiyerarşik olarak taşımak için kullanılır.

## Dizin Yapısı

```
glpi_backup/
├── export_entities/          # Kaynak sunucudan entity çekme
│   ├── config_source.json    # Kaynak GLPI bağlantı bilgileri
│   ├── export_entities.py    # Export scripti
│   └── entities_export.json  # Export edilen entity'ler (çıktı)
│
└── import_entities/          # Hedef sunucuya entity aktarma
    ├── config_target.json    # Hedef GLPI bağlantı bilgileri
    ├── import_entities.py    # Import scripti
    └── entities_export.json  # İçe aktarılacak entity'ler (kopyalanır)
```

## Kullanım

### 1. Export (Veri Çekme)

Kaynak GLPI sunucusundan entity'leri export etmek için:

```bash
cd "d:\Google Drive\Projeler\Script\glpi_backup\export_entities"
python export_entities.py
```

**Çıktı:**
- `entities_export.json` - Tüm entity'ler hiyerarşik sırada

### 2. Import (Veri Aktarma)

Export edilen verileri hedef GLPI sunucusuna aktarmak için:

```bash
cd "c:\Users\maniac\Desktop\ITSM - GLPI\Script\glpi_backup\import_entities"
python import_entities.py
```

**İşlem Sırası:**
1. Mevcut entity'ler kontrol edilir
2. Her entity için:
   - İsim bazlı duplicate check yapılır
   - **Varsa ve farklıysa**: Güncellenir
   - **Varsa ve aynıysa**: Atlanır
   - **Yoksa**: Yeni oluşturulur
3. Parent-child ilişkileri korunur

## Konfigürasyon

### Export için: `config_source.json`

```json
{
    "GLPI_URL": "http://192.168.50.243/glpi/apirest.php/",
    "GLPI_APP_TOKEN": "your-app-token",
    "GLPI_USER_TOKEN": "your-user-token"
}
```

### Import için: `config_target.json`

```json
{
    "GLPI_URL": "http://192.168.50.243/glpi/apirest.php/",
    "GLPI_APP_TOKEN": "your-app-token",
    "GLPI_USER_TOKEN": "your-user-token"
}
```

## Özellikler

### ✅ Hiyerarşik Yapı Koruması
- Entity'ler `completename` alanına göre sıralanır
- Parent entity'ler önce işlenir
- Child entity'ler parent ID'leri ile doğru bağlanır

### ✅ Duplicate Check
- İsim bazlı duplicate kontrolü
- Mevcut entity'ler tespit edilir ve atlanır

### ✅ Güncelleme Desteği
Aşağıdaki alanlar karşılaştırılır ve farklıysa güncellenir:
- `comment` - Açıklama
- `address` - Adres
- `postcode` - Posta kodu
- `town` - Şehir
- `state` - Eyalet/İl
- `country` - Ülke
- `website` - Website
- `phonenumber` - Telefon
- `fax` - Faks
- `email` - E-posta

### ✅ ID Mapping
- Kaynak ve hedef sunuculardaki farklı ID'ler otomatik eşleştirilir
- Parent-child ilişkileri korunur

## Örnek Kullanım Senaryosu

1. **Kaynak sunucudan export:**
   ```bash
   cd export_entities
   python export_entities.py
   ```
   → `entities_export.json` oluşturulur

2. **Dosyayı hedef sunucuya kopyala:**
   ```bash
   copy entities_export.json ..\import_entities\
   ```

3. **Hedef sunucuya import:**
   ```bash
   cd ..\import_entities
   python import_entities.py
   ```

4. **Güncelleme testi (tekrar çalıştırma):**
   ```bash
   python import_entities.py  # Mevcut entity'ler atlanır veya güncellenir
   ```

## Export Dosyası Formatı

```json
{
    "entities": [
        {
            "id": 0,
            "name": "Kök birim",
            "completename": "Kök birim",
            "entities_id": -1,
            "comment": "",
            "address": "",
            ...
        }
    ],
    "total_count": 1
}
```

## Gereksinimler

- Python 3.x
- `requests` kütüphanesi
- GLPI API erişimi (App-Token ve User-Token)
- Entity oluşturma/güncelleme yetkisi

## Notlar

- Script, GLPI REST API kullanır
- SSL doğrulaması devre dışıdır (`verify=False`)
- Hiyerarşik sıralama otomatik yapılır
- Script idempotent'tir (tekrar çalıştırılabilir)
- Güncelleme sadece belirtilen alanlarda yapılır
