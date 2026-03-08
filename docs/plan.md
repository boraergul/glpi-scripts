# Teknik Tasarım: Dokümantasyon Konsolidasyonu ve README Güncellemesi

Bu plan, `MEMORY[user_global]` protokolüne uyum sağlamak için dokümantasyon dosyalarını konsolide etmeyi ve ana `README.md` dosyasını eksik modüllerle güncellemeyi amaçlar.

## Etkilenecek Dosyalar
- `docs/project_state.md` [NEW]: `project.md`, `memory.md` ve `logbook.md` dosyalarının birleşimi.
- `README.md` [MODIFIED]: Modül listesi ve güncel durum bilgisi eklenecek.
- `docs/plan.md` [MODIFIED]: Mevcut dokümantasyon görevine göre güncellenecek.

## Çözüm Adımları
1. **Konsolidasyon**: `project.md`, `memory.md` ve `logbook.md` içeriklerini `project_state.md` altında birleştir.
2. **Temizlik**: Eski dokümantasyon dosyalarını sil.
3. **README Güncellemesi**: Ana `README.md` dosyasına yeni eklenen veya eksik kalan modülleri (`create_ticket`, `glpi_backup`, `gui_customization`, `notifications`) ekle.
4. **Doğrulama**: Tüm linkleri ve bilgilerin doğruluğunu kontrol et.

## İş Kuralları
- `project_state.md` projenin "uzun vadeli hafızası" olarak işlev görmelidir.
- `README.md` projenin vitrini olmaya devam etmelidir.
