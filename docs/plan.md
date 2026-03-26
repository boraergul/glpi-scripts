# Teknik Tasarım: Etiket Doğrulama Düzeltmesi

Bu plan, `validate_tags.py` betiğindeki hatalı geçersiz etiket raporlarını düzeltmeyi amaçlar.

## Etkilenecek Dosyalar
- `templates_new/validate_tags.py` [MODIFIED]: Tag yükleme mantığı geliştirilecek.

## Çözüm Adımları
1. `validate_tags.py` içindeki `load_valid_tags` fonksiyonunu, CSV'deki tum etiketleri eksiksiz yukleyecek şekilde güncelle.
2. Hatalı pozitif raporları doğrula ve temizle.
