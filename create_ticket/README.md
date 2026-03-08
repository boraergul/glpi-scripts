# GLPI Test Ticket Creator by Category

Bu script, seçilen bir entity için tüm ITIL kategorilerine ait test ticketları otomatik olarak oluşturur.

## 🎯 Amaç

- Test ve demo amaçlı gerçekçi ticketlar oluşturmak
- Her ITIL kategorisi için örnek senaryo üretmek
- Yeni GLPI kurulumlarında örnek veri sağlamak
- Kategori bazlı raporlama testleri yapmak

## ✨ Özellikler

- **Otomatik Kategori Tespiti**: ITIL kategorilerini otomatik çeker
- **Gerçekçi Senaryolar**: 5 farklı kategori tipi için önceden hazırlanmış senaryolar
- **Akıllı Kategorizasyon**: Kategori adına göre uygun senaryo seçimi
- **Dry-Run Modu**: Değişiklik yapmadan test etme imkanı
- **İnteraktif Entity Seçimi**: Komut satırı veya interaktif seçim

## 📋 Senaryo Kategorileri

Script, ITIL kategorilerini otomatik olarak şu tiplere ayırır:

1. **Hardware (Donanım)**: Laptop, monitör, klavye arızaları
2. **Software (Yazılım)**: Lisans, kurulum, güncelleme sorunları
3. **Network (Ağ)**: İnternet, VPN, ağ yazıcı problemleri
4. **Access (Erişim)**: Şifre, yetki, erişim talepleri
5. **Support (Destek)**: Genel destek, eğitim, performans

Her kategori için 3 farklı senaryo şablonu mevcuttur.

## 🚀 Kullanım

### Temel Kullanım (İnteraktif)

```bash
python create_ticket_by_category.py
```

Script size entity listesi gösterecek ve seçim yapmanızı isteyecektir.

### Entity ID ile Kullanım

```bash
python create_ticket_by_category.py --entity-id 17
```

### Dry-Run Modu (Test)

```bash
python create_ticket_by_category.py --entity-id 17 --dry-run
```

Bu modda hiçbir ticket oluşturulmaz, sadece ne yapılacağı gösterilir.

## 📊 Örnek Çıktı

```
✓ GLPI session başlatıldı

Entity'ler çekiliyor...
✓ 25 entity bulundu

✓ Seçilen Entity: Merkez Prime Hastanesi (ID: 17)

ITIL kategorileri çekiliyor...
✓ 45 aktif kategori bulundu

================================================================================
Ticket Oluşturma Başlıyor
================================================================================

📋 Kategori: Hardware > Laptop
  ✓ Ticket #1234 oluşturuldu: Hardware > Laptop - Laptop Ekran Arızası

📋 Kategori: Software > Microsoft Office
  ✓ Ticket #1235 oluşturuldu: Software > Microsoft Office - Microsoft Office Lisans Hatası

...

================================================================================
ÖZET
================================================================================
Toplam Kategori: 45
Başarılı: 45
Başarısız: 0
================================================================================
```

## 🔧 Gereksinimler

### Python Kütüphaneleri

```bash
pip install requests urllib3
```

### Config Dosyası

Script, merkezi `config.json` dosyasını kullanır:
- `./config.json`
- `../config/config.json`
- `../../config/config.json`

Örnek `config.json`:
```json
{
  "GLPI_URL": "https://your-glpi-instance.com/apirest.php",
  "GLPI_APP_TOKEN": "your_app_token_here",
  "GLPI_USER_TOKEN": "your_user_token_here"
}
```

## 📝 Senaryo Örnekleri

### Hardware Senaryosu
```
Başlık: Hardware > Laptop - Laptop Ekran Arızası
İçerik: 
Merhaba,

Kullandığım dizüstü bilgisayarın ekranında dikey çizgiler belirmeye başladı. 
Özellikle sabah ilk açılışta bu durum daha belirgin oluyor.
Ekran parlaklığını ayarladığımda çizgiler artıyor.
Cihazın garanti süresi henüz dolmadı, kontrol edilmesini rica ederim.

Teşekkürler.
```

### Software Senaryosu
```
Başlık: Software > Office - Microsoft Office Lisans Hatası
İçerik:
Merhaba,

Bilgisayarımda Microsoft Office uygulamaları lisans hatası veriyor.
"Ürününüz lisanslanamadı" mesajı alıyorum.
Excel ve Word kullanmam gerekiyor ancak açılmıyor.
Lisans yenileme veya aktivasyon desteği bekliyorum.

Teşekkürler.
```

## ⚠️ Önemli Notlar

1. **Test Ortamı**: Bu script test amaçlıdır, production ortamında dikkatli kullanın
2. **Toplu Ticket**: Tüm kategoriler için ticket oluşturur, sayı fazla olabilir
3. **Rastgele Senaryo**: Her çalıştırmada farklı senaryolar seçilir
4. **Dry-Run Öncelikli**: İlk kullanımda mutlaka `--dry-run` ile test edin

## 🔍 Sorun Giderme

### "config.json bulunamadı" Hatası
**Çözüm**: Config dosyasının doğru konumda olduğundan emin olun.

### "Entity ID bulunamadı" Hatası
**Çözüm**: Geçerli bir entity ID kullanın veya interaktif modda seçim yapın.

### API Bağlantı Hatası
**Çözüm**: GLPI API token'larını ve URL'yi kontrol edin.

## 📞 Destek

Sorun yaşarsanız:
1. Dry-run modu ile test edin
2. GLPI API erişimini kontrol edin
3. Config dosyasını doğrulayın

---

**Versiyon**: 1.0  
**Son Güncelleme**: 14 Ocak 2026  
**Hazırlayan**: Bora Ergül
