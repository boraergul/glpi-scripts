# GLPI Group Export ve Import Scriptleri

Bu scriptler, GLPI sunucuları arasında Group (Grup) yapısını hiyerarşik olarak taşımak için kullanılır.

## Dizin Yapısı

```
glpi_backup/
├── export_groups/            # Kaynak sunucudan group çekme
│   ├── config_source.json    # Kaynak GLPI bağlantı bilgileri
│   ├── export_groups.py      # Export scripti
│   └── groups_export.json    # Export edilen gruplar (çıktı)
│
└── import_groups/            # Hedef sunucuya group aktarma
    ├── config_target.json    # Hedef GLPI bağlantı bilgileri
    ├── import_groups.py      # Import scripti
    └── groups_export.json    # İçe aktarılacak gruplar (kopyalanır)
```

## Kullanım

### 1. Export (Veri Çekme)

Kaynak GLPI sunucusundan grupları export etmek için:

```bash
cd "c:\Users\maniac\Desktop\ITSM - GLPI\Script\glpi_backup\export_groups"
python export_groups.py
```

**Çıktı:**
- `groups_export.json` - Tüm gruplar hiyerarşik sırada

### 2. Import (Veri Aktarma)

Export edilen verileri hedef GLPI sunucusuna aktarmak için:

```bash
cd "c:\Users\maniac\Desktop\ITSM - GLPI\Script\glpi_backup\import_groups"
python import_groups.py
```

**İşlem Sırası:**
1. Mevcut gruplar kontrol edilir
2. Her grup için:
   - İsim bazlı duplicate check yapılır
   - **Varsa ve farklıysa**: Güncellenir
   - **Varsa ve aynıysa**: Atlanır
   - **Yoksa**: Yeni oluşturulur
3. Parent-child ilişkileri korunur

## Konfigürasyon

### Export için: `config_source.json`

```json
{
    "GLPI_URL": "https://itsm.ultron.com.tr/apirest.php/",
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
- Gruplar `completename` alanına göre sıralanır
- Parent gruplar önce işlenir
- Child gruplar parent ID'leri ile doğru bağlanır

### ✅ Duplicate Check
- İsim bazlı duplicate kontrolü
- Mevcut gruplar tespit edilir ve atlanır

### ✅ Güncelleme Desteği
Aşağıdaki alanlar karşılaştırılır ve farklıysa güncellenir:
- `comment` - Açıklama
- `ldap_field` - LDAP alan adı
- `ldap_value` - LDAP değeri
- `ldap_group_dn` - LDAP grup DN

### ✅ ID Mapping
- Kaynak ve hedef sunuculardaki farklı ID'ler otomatik eşleştirilir
- Parent-child ilişkileri korunur

## Örnek Kullanım Senaryosu

1. **Kaynak sunucudan export:**
   ```bash
   cd export_groups
   python export_groups.py
   ```
   → `groups_export.json` oluşturulur

2. **Dosyayı hedef sunucuya kopyala:**
   ```bash
   copy groups_export.json ..\import_groups\
   ```

3. **Hedef sunucuya import:**
   ```bash
   cd ..\import_groups
   python import_groups.py
   ```

4. **Güncelleme testi (tekrar çalıştırma):**
   ```bash
   python import_groups.py  # Mevcut gruplar atlanır veya güncellenir
   ```

## Export Dosyası Formatı

```json
{
    "groups": [
        {
            "id": 15,
            "name": "Ultron Bilişim",
            "completename": "Ultron Bilişim",
            "groups_id": 0,
            "comment": "",
            "ldap_field": "",
            "ldap_value": "",
            ...
        }
    ],
    "total_count": 42
}
```

## Gereksinimler

- Python 3.x
- `requests` kütüphanesi
- GLPI API erişimi (App-Token ve User-Token)
- Group oluşturma/güncelleme yetkisi

## Notlar

- Script, GLPI REST API kullanır
- SSL doğrulaması devre dışıdır (`verify=False`)
- Hiyerarşik sıralama otomatik yapılır
- Script idempotent'tir (tekrar çalıştırılabilir)
- Güncelleme sadece belirtilen alanlarda yapılır
