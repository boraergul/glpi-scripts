# GLPI Entity - Group Sync Automation

Bu script, GLPI üzerindeki Entity (Birim) yapısını Group (Grup) yapısına yansıtmak (senkronize etmek) amacıyla geliştirilmiştir. Özellikle Entity'lere karşılık gelen Müşteri Grupları oluşturarak, bilet süreçlerinde veya raporlamada Grupların kullanılmasına olanak sağlar.

## Amaç

GLPI'da tanımlı olan her 'Müşteri' (Entity), aynı zamanda bir 'Grup' olarak da sistemde bulunmalıdır. Bu script:
1.  Mevcut Entity'leri tarar.
2.  Belirlenen bir üst grup hiyerarşisi altında (`Ultron Bilişim` > `Müşteriler`) bu Entity isimleriyle birebir eşleşen Gruplar oluşturur.

## Özellikler

*   **Hiyerarşik Kontrol:** Öncelikle `Ultron Bilişim` ana grubunu ve onun altındaki `Müşteriler` alt grubunu bulur. Tüm senkronizasyon bu hiyerarşi altında gerçekleşir.
*   **Otomatik Grup Oluşturma:** Entity ismine sahip bir Grup, `Müşteriler` grubu altında yoksa otomatik oluşturur.
*   **Ölçeklenebilir (Pagination):** 1000'den fazla entity olması durumunda tüm kayıtları sayfalayarak eksiksiz işler.
*   **İstisnalar:** `Root Entity`, `Ultron Bilişim` ve `Müşteriler` gibi sistem veya yapısal isimleri senkronizasyondan hariç tutar.
*   **Recursive (Ardışık) Yapı:** Oluşturulan gruplar `is_recursive=1` olarak ayarlanır, yani alt öğeleri kapsayacak şekilde tanımlanır.
*   **Dry-Run (Test) Modu:** Varsayılan olarak değişiklik yapmaz, planlanan işlemleri listeler.

## Gereksinimler

*   Python 3.x
*   Kütüphaneler: `requests`, `urllib3`, `argparse`
*   Konfigürasyon: Script `config.json` dosyasını şu lokasyonlarda arar:
    1. Script ile aynı dizin
    2. `../Config/` (Bir üst dizindeki Config klasörü)
    3. `../../Config/` (İki üst dizindeki Config klasörü)

## Kurulum ve Konfigürasyon

`config.json` dosyasının formatı:
```json
{
    "GLPI_URL": "http://your-glpi-url/apirest.php",
    "GLPI_APP_TOKEN": "your_app_token",
    "GLPI_USER_TOKEN": "your_user_token"
}
```

## Kullanım

### Test Modu (Dry-Run)
Değişiklik yapmadan simülasyon yapmak için:
```bash
python sync_entity_groups.py
```

Örnek Çıktı:
```text
Found 'Ultron Bilişim': 55
Found 'Müşteriler': 56
Found 120 Entities.
PROPOSE: Create Group 'ABC Lojistik' under 'Müşteriler'
SKIP: Group 'XYZ Teknoloji' already exists (ID: 80)
```

### Değişiklikleri Uygulama (--force)
Grupları gerçekten oluşturmak için:
```bash
python sync_entity_groups.py --force
```

## Çalışma Mantığı

1.  **Grup Hiyerarşisi Kontrolü:**
    *   API üzerinden isme göre arama yaparak `Ultron Bilişim` grubunun ID'sini bulur (Güvenilir arama fonksiyonu `find_group_reliable` kullanılır).
    *   `Ultron Bilişim` altında `Müşteriler` grubunu arar.
2.  **Entity Taraması:** GLPI'daki tüm aktif Entity'leri çeker.
3.  **Senkronizasyon:**
    *   Her Entity için; eğer isim istisna listesinde değilse, `Müşteriler` grubu altında aynı isimde bir alt grup arar.
    *   Grup yoksa oluşturur (`entities_id=0` yani Root görünürlüğünde).

## Notlar
*   Script, grupları oluştururken `entities_id` değerini `0` (Root Entity) olarak ayarlar, böylece gruplar global olarak görünür olur.
*   Grup arama işleminde tam isim eşleşmesi (case-insensitive) kullanılır.

---

**Son Güncelleme:** 18 Aralık 2025  



Hazırlayan : Bora Ergül
