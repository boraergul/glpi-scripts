**ULTRON BİLİŞİM A.Ş.**

**İletişim Şablonları Kılavuzu**

_ITSM Süreçleri için Standart İletişim Dokümanları_

Versiyon: 1.0

Tarih: Aralık 2024

# İÇİNDEKİLER

1\. Incident Management İletişim Şablonları

2\. Problem Management İletişim Şablonları

3\. Change Management İletişim Şablonları

4\. Raporlama Şablonları

5\. Sözleşme ve İdari Bildirimler

6\. Kanallarına Göre Şablon Kullanımı

7\. Değişken Listesi ve Kullanım Kuralları

# 1\. INCIDENT MANAGEMENT İLETİŞİM ŞABLONLARI

## 1.1. Proaktif Incident Management (iNOC Monitoring)

### 1.1.1. Alarm Tespiti - İlk Bildirim

**📧 EMAIL ŞABLONU**

**Konu:** \[P{PRIORITY}\] Proaktif Alarm - {SISTEM_ADI} - {ALARM_TIPI}

Sayın {MUSTERI_IRTIBAT}, iNOC monitoring sistemimiz tarafından aşağıdaki alarm tespit edilmiştir: Ticket No: {TICKET_NO} Priority: {PRIORITY_LEVEL} Sistem: {SISTEM_ADI} Alarm: {ALARM_DETAY} Tespit Zamanı: {ALARM_ZAMANI} Durum: Analiz ediliyor Teknik ekibimiz alarımın geçerliliğini kontrol etmektedir. Gerçek bir problem olması durumunda hemen müdahale başlatılacaktır. Tahmini yanıt süresi: {RESPONSE_TIME} Saygılarımızla, Ultron Bilişim iNOC Ekibi {OPERATOR_ADI} Tel: +90 XXX XXX XXXX

**📱 WHATSAPP/TELEGRAM ŞABLONU**

🔴 Proaktif Alarm Tespiti 📋 Ticket: {TICKET_NO} ⚠️ Priority: {PRIORITY} 🖥️ Sistem: {SISTEM_ADI} ⏰ Zaman: {ALARM_ZAMANI} Teknik ekibimiz inceliyor. Response time: {RESPONSE_TIME} Detaylı bilgi: {GLPI_LINK}

### 1.1.2. Doğrulama Sonrası - Müdahale Başlatıldı

**📧 EMAIL ŞABLONU**

**Konu:** \[P{PRIORITY}\] Müdahale Başladı - {TICKET_NO} - {SISTEM_ADI}

Sayın {MUSTERI_IRTIBAT}, Ticket No: {TICKET_NO} için müdahale başlatılmıştır. Problem Tanımı: {PROBLEM_TANIM} Etkilenen Sistem: {SISTEM_ADI} Etki Alanı: {ETKI_ALANI} Atanan Teknik: {TEKNISYEN_ADI} Yapılan/Yapılacak İşlemler: {ISLEM_LISTESI} Tahmini çözüm süresi: {RESOLUTION_TIME} Durumunuz hakkında {UPDATE_FREQUENCY} güncelleme alacaksınız. Saygılarımızla, Ultron Bilişim iNOC Ekibi

**💬 SMS ŞABLONU (160 karakter)**

Ultron: Ticket {TICKET_NO} mudahale basladi. {SISTEM_ADI} - {KISA_ACIKLAMA}. Cozum suresi: {SURE}. Detay: {LINK}

### 1.1.3. Çözüm Bildirimi

**📧 EMAIL ŞABLONU**

**Konu:** \[ÇÖZÜLDİ\] {TICKET_NO} - {SISTEM_ADI}

Sayın {MUSTERI_IRTIBAT}, Ticket No: {TICKET_NO} başarıyla çözüme kavuşturulmuştur. Problem: {PROBLEM_TANIM} Kök Neden: {ROOT_CAUSE} Uygulanan Çözüm: {COZUM_DETAY} Çözüm Zamanı: {COZUM_ZAMANI} Toplam Süre: {TOPLAM_SURE} SLA Durumu: {SLA_MET} ✅ Sistemleriniz normal çalışmaya devam etmektedir. Herhangi bir sorun olması durumunda lütfen bizimle iletişime geçin. Hizmet kalitemizi değerlendirmek için lütfen anketi doldurun: {ANKET_LINKI} Saygılarımızla, Ultron Bilişim {OPERATOR_ADI}

**📱 WHATSAPP/TELEGRAM ŞABLONU**

✅ Ticket Çözüldü 📋 {TICKET_NO} 🖥️ {SISTEM_ADI} ✔️ {COZUM_OZET} ⏱️ Süre: {TOPLAM_SURE} Sisteminiz normal çalışıyor. Memnuniyet anketi: {ANKET_LINKI} Teşekkürler! 🙏

## 1.2. Reaktif Incident Management (Kullanıcı Bildirimleri)

### 1.2.1. Ticket Açılış Onayı

**📧 EMAIL ŞABLONU**

**Konu:** Ticket Oluşturuldu - {TICKET_NO} - {KONU}

Sayın {KULLANICI_ADI}, Talebiniz başarıyla kaydedilmiştir. Ticket No: {TICKET_NO} Konu: {KONU} Priority: {PRIORITY} Açılış Zamanı: {ACILIS_ZAMANI} Atanan Grup: {GRUP_ADI} Talebiniz {RESPONSE_TIME} içinde yanıtlanacaktır. Ticket durumunuzu takip etmek için: {GLPI_PORTAL_LINK} İhtiyacınız olması durumunda bizimle iletişime geçebilirsiniz: Email: <support@ultron.com.tr> Tel: 0XXX XXX XX XX Saygılarımızla, Ultron Bilişim Service Desk

**☎️ TELEFON SCRIPT ŞABLONU**

**Giriş:**

"Ultron Bilişim Service Desk, {OPERATOR_ADI}, size nasıl yardımcı olabilirim?" \[Müşteri sorunu anlatır\] "Anladım, {PROBLEM_OZET}. Hemen sizin için bir ticket oluşturuyorum." \[Ticket açılır\] "Ticket numaranız {TICKET_NO}. Bu numarayı not alabilir misiniz?" "Talebiniz {PRIORITY} öncelikte kaydedildi. {RESPONSE_TIME} içinde size dönüş yapılacak." "Size email ile onay gönderilecek. Başka yardımcı olabileceğim bir konu var mı?" "İyi günler dilerim, en kısa sürede geri dönüş yapacağız."

### 1.2.2. Eskalasyon Bildirimi (SLA Risk)

**📧 EMAIL ŞABLONU (Müşteriye)**

**Konu:** \[DİKKAT\] {TICKET_NO} - SLA Riski

Sayın {MUSTERI_IRTIBAT}, Ticket No: {TICKET_NO} için bildirimdeyiz. Mevcut Durum: Çözüm süreci devam ediyor SLA Hedefi: {SLA_HEDEF} Kalan Süre: {KALAN_SURE} Problem karmaşık olduğu için çözüm beklenenden uzun sürüyor. Ekibimiz yoğun şekilde çalışmaktadır. Yapılanlar: {YAPILAN_ISLEMLER} Sonraki Adımlar: {SONRAKI_ADIMLAR} Güncellemeler {UPDATE_FREQUENCY} verilecektir. İletişim: {TEKNISYEN_ADI} - {TEKNISYEN_TEL} Saygılarımızla, Ultron Bilişim

**📧 EMAIL ŞABLONU (İç Eskalasyon)**

**Konu:** \[ESKALASYON\] {TICKET_NO} - {MUSTERI_ADI}

Sayın {MANAGER_ADI}, Aşağıdaki ticket SLA riski taşımaktadır ve eskalasyon gerekiyor: Ticket: {TICKET_NO} Müşteri: {MUSTERI_ADI} ({SEGMENT}) Priority: {PRIORITY} SLA Hedefi: {SLA_HEDEF} Kalan Süre: {KALAN_SURE} Atanan: {TEKNISYEN_ADI} Problem: {PROBLEM_DETAY} Yapılanlar: {YAPILAN_ISLEMLER} Engeller: {ENGELLER} Önerilen Aksiyon: {ONERILEN_AKSIYON} Acil müdahale gerekiyor. {OPERATOR_ADI} Ultron Bilişim Service Desk

## 1.3. Major Incident Management

### 1.3.1. Major Incident Duyurusu

**📧 EMAIL ŞABLONU**

**Konu:** \[MAJOR INCIDENT\] {SISTEM_ADI} Kesintisi

Sayın {MUSTERI_IRTIBAT}, ÖNEMLİ BİLGİLENDİRME: Sistemlerinizde kritik bir kesinti tespit edilmiştir. Incident No: {INCIDENT_NO} Başlangıç: {BASLANGIC_ZAMANI} Etkilenen Sistem: {SISTEM_ADI} Etki: {ETKI_TANIMI} Etkilenen Kullanıcı: {KULLANICI_SAYISI} War Room Aktivasyonu: Major Incident Manager: {MANAGER_ADI} - {MANAGER_TEL} Technical Lead: {TECH_LEAD} - {TECH_TEL} İlk Değerlendirme: {ILK_DEGERLENDIRME} Şu anda tüm ekipler sorunun çözümü için çalışmaktadır. Güncelleme Sıklığı: Her 15 dakika Sonraki Güncelleme: {SONRAKI_GUNCELLEME} Bu kritik bir durumdur. War room konferans bilgileri: {CONFERENCE_LINK} Saygılarımızla, Ultron Bilişim Major Incident Team

**📱 WHATSAPP/TELEGRAM ŞABLONU**

🚨 MAJOR INCIDENT ALERT 📋 {INCIDENT_NO} ⚠️ {SISTEM_ADI} KESİNTİSİ 👥 Etkilenen: {KULLANICI_SAYISI} ⏰ {BASLANGIC_ZAMANI} War Room aktif! Manager: {MANAGER_ADI} Tel: {MANAGER_TEL} Her 15 dk güncelleme yapılacak. Conference: {LINK}

**💬 SMS ŞABLONU**

ULTRON - MAJOR INCIDENT: {SISTEM_ADI} kesinti. {INCIDENT_NO}. War Room: {TEL}. Her 15dk guncelleme.

### 1.3.2. Major Incident - İlerleme Güncellemesi

**📧 EMAIL ŞABLONU**

**Konu:** \[MAJOR\] Güncelleme #{UPDATE_NO} - {INCIDENT_NO}

Sayın {MUSTERI_IRTIBAT}, Güncelleme #{UPDATE_NO} - {GUNCELLEME_ZAMANI} Incident: {INCIDENT_NO} Geçen Süre: {GECEN_SURE} Durum: {DURUM_ACIKLAMA} Son 15 Dakikada Yapılanlar: • {ISLEM_1} • {ISLEM_2} • {ISLEM_3} Mevcut Durum: {MEVCUT_DURUM} Sonraki Adımlar: • {ADIM_1} • {ADIM_2} Tahmini Çözüm: {TAHMINI_COZUM} Sonraki güncelleme 15 dakika içinde gönderilecektir. War Room: {CONFERENCE_LINK} Ultron Bilişim Major Incident Team

**📱 WHATSAPP/TELEGRAM - KISA GÜNCELLEME**

🔄 Güncelleme #{UPDATE_NO} 📋 {INCIDENT_NO} ⏱️ Süre: {GECEN_SURE} Son Durum: {KISA_DURUM} İlerleme: {ILERLEME_YUZDESI}% 15dk sonra yeni güncelleme.

### 1.3.3. Major Incident - Çözüm Duyurusu

**📧 EMAIL ŞABLONU**

**Konu:** \[ÇÖZÜLDÜ\] Major Incident {INCIDENT_NO}

Sayın {MUSTERI_IRTIBAT}, Major Incident {INCIDENT_NO} başarıyla çözülmüştür. Özet: Başlangıç: {BASLANGIC_ZAMANI} Bitiş: {BITIS_ZAMANI} Toplam Süre: {TOPLAM_SURE} Sistem: {SISTEM_ADI} Kök Neden: {ROOT_CAUSE_DETAY} Uygulanan Çözüm: {COZUM_DETAY} Etki Analizi: • Etkilenen Kullanıcı: {KULLANICI_SAYISI} • Downtime: {DOWNTIME} • Kayıp İşlem: {KAYIP_ISLEM} Tüm sistemleriniz normal çalışmaya döndü. Post-Incident Review: 48 saat içinde detaylı RCA raporu paylaşılacaktır. Toplantı: {PIR_TARIH} - {PIR_SAAT} Önleyici Aksiyonlar: • {AKSIYON_1} • {AKSIYON_2} • {AKSIYON_3} Verdiğimiz rahatsızlıktan dolayı özür dileriz. Saygılarımızla, Ultron Bilişim {MANAGER_ADI} Major Incident Manager

## 1.4. Field Service Incident Management

### 1.4.1. Saha Ziyareti Planlaması

**📧 EMAIL ŞABLONU**

**Konu:** Saha Ziyareti Planlandı - {TICKET_NO}

Sayın {MUSTERI_IRTIBAT}, Ticket No {TICKET_NO} için saha ziyareti planlanmıştır. Randevu Bilgileri: Tarih: {RANDEVU_TARIHI} Saat: {RANDEVU_SAATI} Lokasyon: {LOKASYON_ADRESI} Teknisyen Bilgileri: Ad: {TEKNISYEN_ADI} Tel: {TEKNISYEN_TEL} Uzmanlık: {UZMANLIK} Yapılacak İşlem: {ISLEM_TANIM} Gerekli Hazırlıklar: • {HAZIRLIK_1} • {HAZIRLIK_2} • {HAZIRLIK_3} Teknisyenimiz randevu saatinden önce size ulaşacaktır. Randevu değişikliği için: Tel: {KOORDINATOR_TEL} Email: {KOORDINATOR_EMAIL} Saygılarımızla, Ultron Bilişim Field Service {KOORDINATOR_ADI}

**☎️ TELEFON SCRIPT - RANDEVU ONAY**

"Merhaba, Ultron Bilişim Field Service, {OPERATOR_ADI}." "Ticket {TICKET_NO} için yarın saat {SAAT}'te saha ziyareti planladık." "Size uygun mu?" \[Evet ise\] "Harika. Teknisyenimiz {TEKNISYEN_ADI} yarın {SAAT} civarında lokasyonunuzda olacak." "İrtibat numarası {TEKNISYEN_TEL}. Not alabilir misiniz?" "Yapılacak işlem {ISLEM_OZET}." "Hazırlık olarak {HAZIRLIK_LISTESI} gerekiyor." "Başka bilgi ister misiniz?" \[Hayır ise\] "Hangi tarih/saat size uygun?" \[Yeni randevu belirle\] "Teşekkür ederim, iyi günler."

### 1.4.2. Saha Öncesi Hatırlatma

**📱 WHATSAPP/TELEGRAM ŞABLONU**

🔧 Saha Ziyareti Hatırlatma Yarın randevunuz var! 📅 📋 Ticket: {TICKET_NO} ⏰ Saat: {RANDEVU_SAATI} 📍 Lokasyon: {LOKASYON} 👨‍🔧 Teknisyen: {TEKNISYEN_ADI} 📞 Tel: {TEKNISYEN_TEL} Hazırlıklar: ✓ {HAZIRLIK_1} ✓ {HAZIRLIK_2} Görüşmek üzere! 👋

**💬 SMS ŞABLONU**

Ultron: Yarin {SAAT} saha ziyareti. Teknisyen: {TEKNISYEN_ADI}, Tel:{TEL}. Ticket:{TICKET_NO}

### 1.4.3. Lokasyona Varış Bildirimi

**📱 WHATSAPP/TELEGRAM (Teknisyenden)**

Merhaba, Ultron Bilişim teknisyeni {TEKNISYEN_ADI}. {LOKASYON} lokasyonunuza ulaştım. Güvenlik/Karşılama için kimle görüşmeliyim? Ticket: {TICKET_NO} Teşekkürler.

**☎️ TELEFON SCRIPT**

"Merhaba, Ultron Bilişim teknisyeni {TEKNISYEN_ADI}." "Ticket {TICKET_NO} için randevumuz vardı." "{LOKASYON} lokasyonunuza ulaştım." "Hangi katta/bölümde görüşebiliriz?" "Yaklaşık {SURE} dakika içinde sizinle olacağım." "Görüşmek üzere."

### 1.4.4. Müdahale Tamamlandı - Onay

**📧 EMAIL ŞABLONU**

**Konu:** Saha Müdahalesi Tamamlandı - {TICKET_NO}

Sayın {MUSTERI_IRTIBAT}, Ticket No {TICKET_NO} için saha müdahalesi başarıyla tamamlanmıştır. Müdahale Özeti: Tarih: {MUDAHALE_TARIHI} Teknisyen: {TEKNISYEN_ADI} Başlangıç: {BASLANGIC_SAAT} Bitiş: {BITIS_SAAT} Süre: {TOPLAM_SURE} Problem: {PROBLEM_DETAY} Yapılan İşlemler: • {ISLEM_1} • {ISLEM_2} • {ISLEM_3} Değiştirilen Parçalar: • {PARCA_1} - S/N: {SERI_NO_1} • {PARCA_2} - S/N: {SERI_NO_2} Test Sonuçları: ✅ {TEST_1} ✅ {TEST_2} Müşteri Onayı: {ONAY_DURUM} İmza: {IMZA_ALINDI} Sistem normal çalışmaya devam etmektedir. Ekli Dosyalar: • Müdahale öncesi fotoğraflar • Müdahale sonrası fotoğraflar • İmza formu Saygılarımızla, Ultron Bilişim Field Service {KOORDINATOR_ADI}

# 2\. PROBLEM MANAGEMENT İLETİŞİM ŞABLONLARI

## 2.1. Problem Kaydı Oluşturuldu

**📧 EMAIL ŞABLONU**

**Konu:** Problem Kaydı Oluşturuldu - {PROBLEM_NO}

Sayın {MUSTERI_IRTIBAT}, Sistemlerinizde tespit edilen tekrarlayan sorun için bir Problem kaydı oluşturulmuştur. Problem No: {PROBLEM_NO} Açılış Tarihi: {ACILIS_TARIHI} Öncelik: {PRIORITY} İlişkili Incident'ler: • {INCIDENT_1} - {TARIH_1} • {INCIDENT_2} - {TARIH_2} • {INCIDENT_3} - {TARIH_3} Problem Tanımı: {PROBLEM_TANIMI} Etki: {ETKI_TANIMI} Atanan: {PROBLEM_MANAGER} Hedef RCA Tarihi: {RCA_HEDEF_TARIH} Kök neden analizimiz başlamıştır. Çözüm bulunana kadar workaround: {WORKAROUND} İki haftada bir ilerleme raporu gönderilecektir. Saygılarımızla, Ultron Bilişim Problem Management {PROBLEM_MANAGER}

## 2.2. RCA Tamamlandı

**📧 EMAIL ŞABLONU**

**Konu:** RCA Raporu Hazır - {PROBLEM_NO}

Sayın {MUSTERI_IRTIBAT}, Problem No {PROBLEM_NO} için Root Cause Analysis tamamlanmıştır. Kök Neden: {ROOT_CAUSE_DETAY} Analiz Metodolojisi: {METODOLOJI} (5 Whys / Fishbone / Timeline) Katkıda Bulunan Faktörler: • {FAKTOR_1} • {FAKTOR_2} • {FAKTOR_3} Kalıcı Çözüm Önerisi: {COZUM_ONERISI} Gerekli Change: Change No: {CHANGE_NO} Planlı Tarih: {CHANGE_TARIH} Downtime: {DOWNTIME_IHTIYAC} Change başarılı olduktan sonra problem kapatılacaktır. Detaylı RCA raporu ektedir. Saygılarımızla, Ultron Bilişim {PROBLEM_MANAGER}

## 2.3. Problem Kapatıldı

**📧 EMAIL ŞABLONU**

**Konu:** Problem Kapatıldı - {PROBLEM_NO}

Sayın {MUSTERI_IRTIBAT}, Problem No {PROBLEM_NO} başarıyla kapatılmıştır. Özet: Başlangıç: {ACILIS_TARIHI} Kapanış: {KAPANIS_TARIHI} Süre: {TOPLAM_SURE} Uygulanan Çözüm: {COZUM_DETAY} Change Başarı Durumu: Change No: {CHANGE_NO} Uygulama: {CHANGE_TARIH} Sonuç: ✅ Başarılı Verification: Son 30 gün: {INCIDENT_SAYISI} tekrar eden incident Known Error Database: Problem ve çözümü KEDB'ye kaydedildi. Referans: {KEDB_NO} Önleyici Aksiyonlar: • {AKSIYON_1} • {AKSIYON_2} Sorun kalıcı olarak çözülmüştür. Saygılarımızla, Ultron Bilişim {PROBLEM_MANAGER}

# 3\. CHANGE MANAGEMENT İLETİŞİM ŞABLONLARI

## 3.1. Change Request Oluşturuldu

**📧 EMAIL ŞABLONU**

**Konu:** Change Request - {CHANGE_NO} - {CHANGE_BASLIK}

Sayın {MUSTERI_IRTIBAT}, Sistemlerinizde bir değişiklik planlanmıştır. Change No: {CHANGE_NO} Tür: {CHANGE_TYPE} (Standard/Normal/Emergency) Başlık: {CHANGE_BASLIK} Öncelik: {PRIORITY} Değişiklik Nedeni: {DEGISIKLIK_NEDENI} Kapsam: • Etkilenen Sistem: {SISTEM_ADI} • Etkilenen Kullanıcı: {KULLANICI_SAYISI} • Lokasyon: {LOKASYON} Planlı Tarih/Saat: Başlangıç: {BASLANGIC_TARIH} {BASLANGIC_SAAT} Bitiş: {BITIS_TARIH} {BITIS_SAAT} Tahmini Süre: {TAHMINI_SURE} Downtime: {DOWNTIME_VAR_MI} Etki: {ETKI_TANIMI} Risk Değerlendirmesi: Risk Seviyesi: {RISK_LEVEL} Rollback Plan: {ROLLBACK_VAR_MI} CAB Toplantısı: Tarih: {CAB_TARIH} Onay Durumu: {ONAY_DURUM} Lütfen {CAB_TARIH} tarihine kadar onayınızı bildirin. Saygılarımızla, Ultron Bilişim Change Management {CHANGE_MANAGER}

## 3.2. Planlı Bakım Bildirimi (7 gün önce)

**📧 EMAIL ŞABLONU**

**Konu:** \[PLANLI BAKIM\] {SISTEM_ADI} - {BAKIM_TARIHI}

Sayın {MUSTERI_IRTIBAT}, HATIRLATMA: 7 gün sonra planlı bakım yapılacaktır. Change No: {CHANGE_NO} Sistem: {SISTEM_ADI} Bakım Tarihi: {BAKIM_TARIHI} Bakım Saati: {BASLANGIC_SAAT} - {BITIS_SAAT} Süre: {TAHMINI_SURE} Yapılacak İşlemler: • {ISLEM_1} • {ISLEM_2} • {ISLEM_3} Etki: {ETKI_TANIMI} Kesinti Süresi: Tam Kesinti: {KESINTI_SURE} Etkilenen Servisler: {SERVIS_LISTESI} Kullanıcılar İçin: • {KULLANICI_BILGI_1} • {KULLANICI_BILGI_2} Backup planı hazırlandı ✅ Rollback planı hazır ✅ Test ortamında başarılı ✅ Sorularınız için: {CHANGE_MANAGER} Tel: {MANAGER_TEL} Email: {MANAGER_EMAIL} Saygılarımızla, Ultron Bilişim

## 3.3. Bakım Başlangıç Bildirimi

**📧 EMAIL ŞABLONU**

**Konu:** \[BAŞLADI\] Planlı Bakım - {SISTEM_ADI}

Sayın {MUSTERI_IRTIBAT}, Change No {CHANGE_NO} için planlı bakım başlamıştır. Başlangıç: {BASLANGIC_SAAT} Tahmini Bitiş: {BITIS_SAAT} Mevcut Durum: Sistemler bakım modunda Adımlar: ☑ Backup alındı ☐ Konfigürasyon değişikliği ☐ Test ☐ Doğrulama Güncelleme: Her 30 dakika Acil iletişim: {CHANGE_MANAGER} - {MANAGER_TEL} Saygılarımızla, Ultron Bilişim

**📱 WHATSAPP/TELEGRAM**

🔧 Bakım Başladı Change: {CHANGE_NO} Sistem: {SISTEM_ADI} Başlangıç: {SAAT} Tahmini süre: {SURE} Her 30dk güncelleme yapılacak. Acil: {TEL}

## 3.4. Bakım Tamamlandı

**📧 EMAIL ŞABLONU**

**Konu:** \[TAMAMLANDI\] Planlı Bakım - {SISTEM_ADI}

Sayın {MUSTERI_IRTIBAT}, Change No {CHANGE_NO} başarıyla tamamlanmıştır. Başlangıç: {BASLANGIC_SAAT} Bitiş: {BITIS_SAAT} Gerçek Süre: {GERCEK_SURE} Tamamlanan İşlemler: ✅ {ISLEM_1} ✅ {ISLEM_2} ✅ {ISLEM_3} Test Sonuçları: ✅ Fonksiyonellik testi: Başarılı ✅ Performans testi: Başarılı ✅ Kullanıcı erişimi: Başarılı Sistemleriniz normal çalışmaya döndü. Post Implementation Review: {PIR_TARIH} tarihinde değerlendirme yapılacak. Herhangi bir sorun fark ederseniz lütfen bildiriniz: Tel: {SUPPORT_TEL} Email: {SUPPORT_EMAIL} Saygılarımızla, Ultron Bilişim {CHANGE_MANAGER}

**📱 WHATSAPP/TELEGRAM**

✅ Bakım Tamamlandı Change: {CHANGE_NO} Sistem: {SISTEM_ADI} Başarıyla tamamlandı! ✨ Süre: {SURE} Sistemler aktif. Sorun olursa: {TEL} Teşekkürler! 🙏

## 3.5. Emergency Change Bildirimi

**📧 EMAIL ŞABLONU**

**Konu:** \[ACİL\] Emergency Change - {SISTEM_ADI}

Sayın {MUSTERI_IRTIBAT}, ÖNEMLİ: Acil bir değişiklik yapılması gerekmektedir. Emergency Change No: {CHANGE_NO} İlişkili Incident: {INCIDENT_NO} Aciliyet Nedeni: {ACILIYET_NEDENI} Planlanmamış Müdahale: Tarih: {TARIH} Başlangıç: {BASLANGIC_SAAT} (30 dakika içinde) Tahmini Süre: {TAHMINI_SURE} Etki: {ETKI_TANIMI} Yetkilendirme: {YETKILI_ADI} tarafından onaylandı Risk: Bu acil bir müdahaledir. Normal CAB süreci atlanmıştır. Post-implementation review yapılacaktır. Gerçek zamanlı güncelleme: Her 15 dakika durum bildirimi yapılacak. Acil İletişim: {CHANGE_MANAGER} - {TEL} Saygılarımızla, Ultron Bilişim

# 4\. RAPORLAMA ŞABLONLARI

## 4.1. Günlük Operasyon Raporu

**📧 EMAIL ŞABLONU**

**Konu:** Günlük Operasyon Raporu - {TARIH}

Sayın {MUSTERI_IRTIBAT}, {TARIH} Günlük Operasyon Özeti 📊 GENEL DURUM • Toplam Ticket: {TOPLAM_TICKET} • Açık Ticket: {ACIK_TICKET} • Kapatılan: {KAPATILAN_TICKET} • SLA Met: {SLA_MET_ORAN}% 🔴 KRİTİK OLAYLAR (P1) • Yeni: {P1_YENI} • Devam Eden: {P1_DEVAM} • Çözülen: {P1_COZULEN} 📈 PROAKTİF MONİTORİNG • Toplam Alarm: {ALARM_SAYISI} • Auto-Ticket: {AUTO_TICKET} • False Positive: {FALSE_POSITIVE}% 🔧 FIELD SERVICE • Saha Ziyareti: {SAHA_ZIYARET} • Tamamlanan: {TAMAMLANAN} • Bekleyen: {BEKLEYEN} 💡 ÖNEMLİ NOTLAR {ONEMLI_NOT_1} {ONEMLI_NOT_2} 📅 YARIN PLANLANAN • Change: {PLANLANAN_CHANGE} • Bakım: {PLANLANAN_BAKIM} Detaylı rapor ektedir. Saygılarımızla, Ultron Bilişim Operations {OPERATOR_ADI}

## 4.2. Haftalık Performans Raporu

**📧 EMAIL ŞABLONU**

**Konu:** Haftalık Performans Raporu - Hafta {HAFTA_NO}

Sayın {MUSTERI_IRTIBAT}, HAFTALIK PERFORMANS RAPORU {BASLANGIC_TARIH} - {BITIS_TARIH} 📊 TICKET İSTATİSTİKLERİ • Toplam Ticket: {TOPLAM_TICKET} ({ONCEKI_HAFTA_KIYASLAMA}) • P1: {P1_SAYI} • P2: {P2_SAYI} • P3: {P3_SAYI} • P4: {P4_SAYI} ⏱ PERFORMANS METRİKLERİ • SLA Compliance: {SLA_ORAN}% (Hedef: ≥95%) • MTTR: {MTTR} saat (Hedef: <4 saat) • First Contact Resolution: {FCR}% (Hedef: ≥75%) • Customer Satisfaction: {CSAT}/5.0 (Hedef: ≥4.2) 🎯 SLA DETAY • Met: {SLA_MET} • Missed: {SLA_MISSED} • At Risk: {SLA_RISK} 📈 TREND ANALİZİ • Ticket Artış/Azalış: {TREND_ORAN}% • En Çok Sorun: {TOP_KATEGORI} • Peak Saat: {PEAK_SAAT} 🔧 FIELD SERVICE • Tamamlanan Ziyaret: {ZIYARET_SAYI} • First Time Fix: {FTF_ORAN}% • Avg. On-Site Time: {ONSITE_TIME} saat ⚠️ MAJOR INCIDENT • Sayı: {MI_SAYI} • Avg. Resolution: {MI_AVG_TIME} • RCA Tamamlanan: {RCA_SAYI} 💡 ÖNERİLER {ONERI_1} {ONERI_2} {ONERI_3} Detaylı dashboard: {DASHBOARD_LINK} Saygılarımızla, Ultron Bilişim {ACCOUNT_MANAGER}

## 4.3. Aylık Yönetici Raporu

**📧 EMAIL ŞABLONU**

**Konu:** Aylık Yönetici Raporu - {AY} {YIL}

Sayın {MUSTERI_YONETİCİ}, AYLIK YÖNETİCİ RAPORU {AY} {YIL} 🎯 EXECUTIVE SUMMARY Bu ay toplam {TOPLAM_TICKET} ticket işlendi. SLA compliance %{SLA_ORAN} ile hedefin {HEDEF_KIYASLAMA}. Müşteri memnuniyeti {CSAT}/5.0 seviyesinde. 📊 HİZMET PERFORMANSI SLA Compliance: {SLA_GRAFIK} MTTR Trend: {MTTR_GRAFIK} Ticket Volume: {VOLUME_GRAFIK} 🔴 KRİTİK OLAYLAR • Major Incident: {MI_SAYI} • Total Downtime: {DOWNTIME_TOTAL} saat • Business Impact: {BUSINESS_IMPACT} 💰 SLA PERFORMANSI • Met: {SLA_MET} ({SLA_MET_ORAN}%) • Missed: {SLA_MISSED} ({SLA_MISSED_ORAN}%) • Penalty/Credit: {PENALTY_MIKTAR} TL 🔧 PROBLEM MANAGEMENT • Açılan Problem: {PROBLEM_ACILAN} • Kapatılan Problem: {PROBLEM_KAPATILAN} • RCA Tamamlanan: {RCA_SAYI} 🔄 CHANGE MANAGEMENT • Başarılı Change: {CHANGE_BASARILI} • Failed/Rollback: {CHANGE_FAILED} • Emergency: {EMERGENCY_CHANGE} 📈 TREND ve TAHMİN • Gelecek Ay Tahmin: {TAHMIN_TICKET} • Capacity Durumu: {CAPACITY_DURUM} • Risk Alanları: {RISK_ALANLARI} 💡 ÖNERİLER ve EYLEM PLANLARI 1. {ONERI_1} 2. {ONERI_2} 3. {ONERI_3} 📅 GELECEKTEKİ PLANLAR {PLANLANAN_AKTIVITELER} Detaylı rapor ve grafikler ektedir. Görüşmek için: {MEETING_LINK} Saygılarımızla, Ultron Bilişim {SERVICE_DELIVERY_MANAGER}

# 5\. SÖZLEŞME VE İDARİ BİLDİRİMLER

## 5.1. Sözleşme Yenileme (90 gün önce)

**📧 EMAIL ŞABLONU**

**Konu:** Sözleşme Yenileme Bildirimi - {MUSTERI_ADI}

Sayın {MUSTERI_YONETİCİ}, Sizinle olan hizmet sözleşmemiz yakında sona erecektir. Mevcut Sözleşme: Başlangıç: {SOZLESME_BASLANGIC} Bitiş: {SOZLESME_BITIS} Kalan Süre: {KALAN_GUN} gün Hizmet Kapsamı: {HIZMET_LISTESI} Bu Dönem Performans: • SLA Compliance: {SLA_ORAN}% • CSAT: {CSAT}/5.0 • Toplam Ticket: {TOPLAM_TICKET} • Major Incident: {MI_SAYI} Yenileme Seçenekleri: 1. Mevcut koşullarla yenileme 2. Hizmet kapsamı genişletme 3. Özelleştirilmiş paket Görüşme talebi için: {SALES_MANAGER} Tel: {SALES_TEL} Email: {SALES_EMAIL} Sürekliliği sağlamak için {DEADLINE_TARIH} tarihine kadar karar vermenizi rica ederiz. Saygılarımızla, Ultron Bilişim {ACCOUNT_MANAGER}

## 5.2. Sözleşme Yenileme (30 gün önce - Son Hatırlatma)

**📧 EMAIL ŞABLONU**

**Konu:** \[ÖNEMLİ\] Sözleşme Bitimine 30 Gün

Sayın {MUSTERI_YONETİCİ}, ÖNEMLİ HATIRLATMA Sözleşme bitiş tarihi: {SOZLESME_BITIS} Kalan süre: 30 gün Henüz yenileme konusunda bir karar almadınız. Sözleşme yenilenmezse: • Hizmet sona erecektir • Sistem erişimleri kaldırılacaktır • Monitoring durdurulacaktır • Data retention süresi: 30 gün Kesintisiz hizmet için lütfen en kısa sürede bizimle iletişime geçin. Acil İletişim: {ACCOUNT_MANAGER} Tel: {MANAGER_TEL} Email: {MANAGER_EMAIL} Saygılarımızla, Ultron Bilişim

## 5.3. Fiyat Güncellemesi Bildirimi

**📧 EMAIL ŞABLONU**

**Konu:** Hizmet Ücretlendirmesi Güncellemesi

Sayın {MUSTERI_YONETİCİ}, Sizinle olan sözleşmemiz kapsamında ücretlendirme güncellemesi yapmak istiyoruz. Güncel Durum: Aylık Ücret: {MEVCUT_UCRET} TL Hizmet Kapsamı: {HIZMET_LISTESI} Yeni Fiyatlandırma: Aylık Ücret: {YENI_UCRET} TL Artış Oranı: %{ARTIS_ORANI} Geçerlilik: {GECERLILIK_TARIHI} Artış Gerekçesi: {ARTIS_GEREKCE} Ek Avantajlar: {EK_AVANTAJLAR} Görüşmek için: {ACCOUNT_MANAGER} Tel: {TEL} {YANIT_DEADLINE} tarihine kadar görüşlerinizi bekliyoruz. Saygılarımızla, Ultron Bilişim

# 6\. KANALLARA GÖRE ŞABLON KULLANIMI

## 6.1. Email Kuralları

**✅ İYİ UYGULAMALAR**

- Konu satırında mutlaka ticket/problem/change numarası olsun
- Priority belirteci kullanın \[P1\], \[P2\], vb.
- Önemli bildirimler için \[ÖNEMLİ\], \[ACİL\] etiketi
- Her email'de ticket numarası, durum, sonraki adım net olmalı
- İrtibat bilgileri her zaman en altta
- Bullet point'lerle okunabilirliği artırın

**❌ KAÇINILMASI GEREKENLER**

- Uzun paragraflar yazmayın
- Teknik jargon kullanmayın (müşteri anlamıyorsa)
- Gereksiz CC kullanımı
- Emoji kullanmayın (profesyonel olmayan)

## 6.2. WhatsApp/Telegram Kuralları

**✅ İYİ UYGULAMALAR**

- Kısa ve öz mesajlar (maksimum 10 satır)
- Emoji kullanımı UYGUN (dikkat çekmek için): 🔴⚠️✅🔧
- Ticket numarası mutlaka olsun
- Detaylı bilgi için link verin
- Bold kullanın önemli bilgiler için
- Hızlı yanıt gereken durumlarda kullanın

**📝 ÖRNEK YAPILAR**

İyi Örnek: 🔴 P1 Alert 📋 T-12345 🖥️ Mail Server Down ⏰ 14:30 Ekip müdahale ediyor. ETA: 30 dakika Kötü Örnek: Merhaba, sistemlerinizde bir sorun tespit ettik ve şu anda ekibimiz inceliyor, yaklaşık olarak yarım saat içinde çözüm bekliyoruz, herhangi bir gelişme olursa size tekrar mesaj atacağız... (çok uzun, yapılandırılmamış)

## 6.3. SMS Kuralları

**✅ İYİ UYGULAMALAR**

- 160 karakter limiti - kısaltmalar kullanın
- Ultron prefix ile başlayın
- Sadece kritik durumlar (P1/P2)
- Ticket numarası mutlaka
- Detay için link ekleyin (bit.ly gibi kısa link)
- Türkçe karakter kullanmayın (karakter sayısı azalır)

**📝 KISALTMA TABLOSU**

mudahale = müdahale basladi = başladı tamamlandi = tamamlandı cozum = çözüm suresi = süresi bilgi = bilgi detay = detay link = link tel = telefon acil = acil

## 6.4. Telefon Script Kuralları

**✅ İYİ UYGULAMALAR**

- Her zaman kendinizi ve şirketi tanıtın
- Ticket numarasını tekrar ettirin
- Müşterinin anlayabileceği dil kullanın
- Sonraki adımları net açıklayın
- Nezaket her zaman ön planda
- Empati gösterin

**📞 TELEFON ETİKETİ**

- Gülümseyin (ses tonuna yansır)
- Müşteriyi dinleyin, sözünü kesmeyin
- Hızlı konuşmayın, anlaşılır olun
- Sessiz ortamda arayın
- Not alın

# 7\. DEĞİŞKEN LİSTESİ VE KULLANIM KURALLARI

## 7.1. Müşteri Bilgileri

| **Değişken** | **Açıklama** |
| --- | --- |
| {MUSTERI_ADI} | Müşteri şirket adı |
| {MUSTERI_IRTIBAT} | İrtibat kişisi adı (örn: Ahmet Yılmaz) |
| {MUSTERI_YONETICI} | Üst düzey yönetici (BT Direktörü, Genel Müdür) |
| {KULLANICI_ADI} | Son kullanıcı adı (ticket açan kişi) |
| {SEGMENT} | Platinum/Gold/Silver/Bronze |

## 7.2. Ticket/Incident Bilgileri

| **Değişken** | **Açıklama** |
| --- | --- |
| {TICKET_NO} | Ticket numarası (örn: T-12345) |
| {INCIDENT_NO} | Major incident numarası (örn: MI-001) |
| {PRIORITY} | P1/P2/P3/P4 |
| {PRIORITY_LEVEL} | P1 - Critical / P2 - High / vb. (açıklamalı) |
| {SISTEM_ADI} | Etkilenen sistem (örn: Mail Server, SAP) |
| {PROBLEM_TANIM} | Kısa problem tanımı |
| {RESPONSE_TIME} | Yanıt süresi (örn: 15 dakika) |
| {RESOLUTION_TIME} | Çözüm süresi (örn: 4 saat) |
| {SLA_MET} | SLA karşılandı mı (Evet/Hayır) |
| {GLPI_LINK} | GLPI ticket linki |

## 7.3. Ekip ve İletişim

| **Değişken** | **Açıklama** |
| --- | --- |
| {OPERATOR_ADI} | Service Desk operatörü |
| {TEKNISYEN_ADI} | Atanan teknisyen |
| {TEKNISYEN_TEL} | Teknisyen telefon numarası |
| {MANAGER_ADI} | Major Incident Manager/Problem Manager |
| {MANAGER_TEL} | Manager telefon |
| {CHANGE_MANAGER} | Change Manager adı |
| {ACCOUNT_MANAGER} | Hesap yöneticisi |

## 7.4. Kullanım Kuralları

**✅ DOĞRU KULLANIM**

- Her şablonu kullanmadan önce değişkenleri doldurun
- Boş değişken bırakmayın (N/A yazın gerekirse)
- Müşteri segmentine göre ton ayarlayın
- GLPI'dan otomatik doldurma yapın (mümkünse)
- İmla kontrol yapın
- Link'lerin çalıştığından emin olun

**💡 GLPI OTOMASYON ÖNERİSİ**

Bu şablonları GLPI'da template notification olarak yapılandırabilirsiniz:

- Setup → Notifications → Templates
- Her şablon için ayrı template oluşturun
- ##ticket.id##, ##ticket.priority## gibi GLPI tag'leri kullanın
- Trigger'larla otomatik gönderim ayarlayın

**Ultron Bilişim A.Ş.**

_Bu doküman düzenli olarak güncellenecektir._

Son Güncelleme: Aralık 2024

<www.ultron.com.tr>