# Modernizasyon: rules_unknowndomain.py (v2.0)

Bu çalışma, `rules_unknowndomain.py` scriptini modern standartlara (v3.0) yükseltmeyi, verimliliği artırmayı ve güvenliği sağlamayı amaçlar.

## Proposed Changes

### Core Enhancements
- **Smart Sync**: Mevcut kuralın kriterlerini ve aksiyonlarını API'den çekip, yeni değerlerle karşılaştıran bir mantık eklenecek. Değişiklik yoksa güncelleme atlanacak (LOG: SKIP).
- **Detailed Domain Logging**: Güncelleme sırasında hangi domainlerin eklendiği veya çıkarıldığı loglarda detaylı olarak (Detaylı Değişim Raporu) gösterilecek.
- **Professional Logging**: `logging` modülü entegre edilecek. Loglar hem konsola hem de `rules_unknowndomain.log` dosyasına yazılacak.
- **Secure Session Management**: `glpi_session` context manager'ı ile oturum yönetimi otomatikleştirilecek.
- **SSL Configuration**: `config.json`'dan `verify_ssl` parametresi okunacak (default: false) ve uygulanacak.

### [MODIFY] [rules_unknowndomain.py](file:///d:/Google%20Drive/Projeler/Script/rules_unknowndomain/rules_unknowndomain.py)
- `logging` yapılandırması eklenecek.
- `load_config` fonksiyonu `logger` kullanacak şekilde güncellenecek.
- `init_session` ve `kill_session` fonksiyonları `verify` parametresini destekleyecek şekilde güncellenecek.
- `@contextmanager` ile `glpi_session` eklenecek.
- `fetch_existing_rule_details` isminde yeni bir yardımcı fonksiyon eklenecek (Kriter ve aksiyonları çekmek için).
- `create_or_update_undefined_domain_rule` fonksiyonu "Smart Sync" mantığı ile baştan yazılacak:
    - Mevcut kuralı silmek yerine, içeriği (domains ve target_entity) karşılaştıracak.
    - Sadece değişiklik varsa kriterleri/aksiyonları temizleyip yeniden oluşturacak.
- `main` fonksiyonu, `rules_email.py`'daki gibi bir "Detaylı Özet Raporu" sunacak şekilde güncellenecek.

## Verification Plan

### Automated Tests (Dry-Run)
- Script `--force` parametresi olmadan çalıştırılarak log çıktısı kontrol edilecek.
- `python rules_unknowndomain.py`
- Beklenen: Mevcut kural bulunmalı, "PROPOSE" logları görülmeli, değişiklik yapılmamalı.

### Manual Verification
- `config.json` dosyasına `verify_ssl: true/false` eklenerek bağlantı test edilecek.
- Bir domain listeden çıkarılıp script çalıştırılarak "UPDATE" yaptığı doğrulanacak.
- İçerik aynıyken çalıştırılarak "SKIP" (Already up to date) logu doğrulanacak.
- Hata durumunda (yanlış URL vb.) session'ın düzgün kapatıldığı `logger.info("Session closed.")` mesajı ile teyit edilecek.
