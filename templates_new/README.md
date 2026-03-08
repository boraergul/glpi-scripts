# Modern GLPI Email Templates Pack

Bu paket, GLPI ITSM yazılımı için hazırlanmış modern, mobil uyumlu ve kurumsal e-posta bildirim şablonlarını içerir. 
2026 Ocak güncellemesi ile tüm ana bildirimler (Ticket, Alarm, Saha, Değişiklik) **tablo tabanlı (table-based)** yapıya geçirilerek okunabilirlik artırılmıştır.

## 📂 Klasör Yapısı

*   `html/`
    *   `tr/`: Türkçe HTML şablonlar
    *   `en/`: İngilizce HTML şablonlar
*   `text/`
    *   `tr/`: Türkçe Düz Metin (Plain Text) şablonlar
    *   `en/`: İngilizce Düz Metin (Plain Text) şablonlar
*   `generate_email_templates.py`: Şablonları yeniden oluşturmak için kullanılan Python betiği.
*   `glpi_notifications.md`: Hangi GLPI bildirimine hangi şablonun bağlanacağını gösteren **REFERANS** dosyasıdır.
*   `docs/`: Teknik tasarım, proje detayları ve çalışma günlüklerinin bulunduğu klasör.

## 📖 Dokümantasyon
Proje ile ilgili daha detaylı teknik bilgilere `docs/` klasöründen ulaşabilirsiniz:
- [Proje Detayları](file:///d:/Google%20Drive/Projeler/Script/templates_new/docs/project.md)
- [Teknik Tasarım](file:///d:/Google%20Drive/Projeler/Script/templates_new/docs/plan.md)
- [Çalışma Günlüğü (Logbook)](file:///d:/Google%20Drive/Projeler/Script/templates_new/docs/logbook.md)
- [Teknik Borç ve Notlar (Memory)](file:///d:/Google%20Drive/Projeler/Script/templates_new/docs/memory.md)

## 🚀 Kurulum ve Kullanım

1.  **Şablonu Seçin:** GLPI panelinde değiştirmek istediğiniz bildirim için `glpi_notifications.md` dosyasındaki eşleşmeye bakın (Örn: *New Ticket* -> *ticket_opening_confirmation*).
2.  **Kodu Kopyalayın:** İlgili şablonun `.html` dosyasını (Notepad++ veya VS Code ile) açın ve içeriği kopyalayın.
3.  **Otomatik Yükleme (Önerilen):** 
    *   `../templates_import` klasörüne gidin.
    *   `python import_templates.py` komutunu çalıştırın.
    *   Bu script, tüm şablonları GLPI'a otomatik olarak yükleyecek ve ilgili bildirimlerle ilişkilendirecektir.

4.  **Manuel Yükleme (Alternatif):**
    *   GLPI menüsünden `Kurulum > Bildirimler > Bildirim Şablonları` yoluna gidin.
    *   Yeni bir şablon oluşturun veya var olanı düzenleyin.
    *   HTML içeriği "HTML Gövdesi" alanına yapıştırın.
    *   Metin içeriği (.txt dosyası) "Metin Gövdesi" alanına yapıştırın.

## 🛠️ Düzenleme

Eğer şablonlarda toplu bir değişiklik (renk, logo, imza vb.) yapmak isterseniz:
1.  `generate_email_templates.py` dosyasını açın.
2.  `TEMPLATES` sözlüğündeki ilgili kısımları düzenleyin.
3.  Scripti çalıştırarak (`python generate_email_templates.py`) tüm dosyaları saniyeler içinde yeniden oluşturun.

## 📋 Kapsayicilik

Bu paket GLPI'daki **Tüm** bildirim türlerini (Ticket, Problem, Change, Project, Reservation, User Actions, System Alerts vb.) kapsayacak şekilde hazırlanmıştır. Detaylar için `glpi_notifications.md` dosyasındaki "Recommended Template" sütununa bakınız.
