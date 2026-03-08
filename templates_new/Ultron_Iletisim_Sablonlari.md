**ULTRON BİLİŞİM A.Ş.**

**İLETİŞİM ŞABLONLARI KÜTÜPHANESİ**

_ITSM Süreçleri için Standart İletişim Şablonları_

Versiyon 1.0

08 Aralık 2024

# İÇERİK ÖZETİ

Bu doküman aşağıdaki iletişim şablonlarını içerir:

- Proaktif Incident Management Şablonları
- Reaktif Incident Management Şablonları
- Major Incident Management Şablonları
- Field Service Şablonları
- Problem Management Şablonları
- Change Management Şablonları
- Raporlama Şablonları
- Sözleşme Yönetimi Şablonları
- Eskalasyon Şablonları
- Müşteri Memnuniyeti Şablonları

**Her şablon aşağıdaki kanallar için hazırlanmıştır:**

- Email
- WhatsApp / Telegram
- SMS
- Telefon Görüşme Scriptleri

# 1\. PROAKTİF INCIDENT MANAGEMENT ŞABLONLARI

## 1.1. Proaktif Alarm Tespit - İlk Bildirim

### Email Şablonu

**Konu:** \[GLPI #{TICKET_ID}\] Proaktif Alarm: {ALARM_TYPE} - {AFFECTED_SYSTEM}

\---

Sayın {CUSTOMER_NAME},

Monitoring sistemlerimiz tarafından otomatik olarak tespit edilen bir alarm hakkında sizi bilgilendirmek isteriz.

**ALARM DETAYLARI:**

- Alarm Tipi: {ALARM_TYPE}
- Etkilenen Sistem: {AFFECTED_SYSTEM}
- Tespit Zamanı: {DETECTION_TIME}
- Öncelik Seviyesi: {PRIORITY}
- SLA Hedefi: {SLA_TARGET}

**ALARM AÇIKLAMASI:**

{ALARM_DESCRIPTION}

**ATILAN ADIMLAR:**

iNOC ekibimiz alarm üzerinde çalışmaya başlamıştır. İlk değerlendirme ve müdahale devam etmektedir.

**TAKİP:**

GLPI Ticket Numarası: {TICKET_ID}

Dashboard Erişimi: {DASHBOARD_URL}

Saygılarımızla,

Ultron Bilişim iNOC Ekibi

### WhatsApp / Telegram Şablonu

\---

🔔 \*ULTRON - PROAKTİF ALARM\*

📊 Ticket: #{TICKET_ID}

⚠️ {ALARM_TYPE}

🖥️ {AFFECTED_SYSTEM}

⏰ {DETECTION_TIME}

🎯 Öncelik: {PRIORITY}

✅ iNOC ekibimiz müdahale ediyor.

📈 Durum güncellemeleri takip edecektir.

### SMS Şablonu

\---

ULTRON ALARM: {ALARM_TYPE} - {AFFECTED_SYSTEM}. Ticket #{TICKET_ID}. iNOC ekibi mudahale ediyor. Guncellemeler GLPI'da.

## 1.2. Proaktif Alarm - Çözüm Bildirimi

### Email Şablonu

**Konu:** \[GLPI #{TICKET_ID}\] ÇÖZÜLDÜ - {ALARM_TYPE} - {AFFECTED_SYSTEM}

\---

Sayın {CUSTOMER_NAME},

Daha önce tarafınıza bildirilen alarm başarıyla çözülmüştür.

**ÇÖZÜM BİLGİLERİ:**

- Ticket Numarası: {TICKET_ID}
- Alarm Tipi: {ALARM_TYPE}
- Etkilenen Sistem: {AFFECTED_SYSTEM}
- Tespit Zamanı: {DETECTION_TIME}
- Çözüm Zamanı: {RESOLUTION_TIME}
- Toplam Süre: {TOTAL_DURATION}

**YAPILAN İŞLEMLER:**

{RESOLUTION_ACTIONS}

**KÖK NEDEN:**

{ROOT_CAUSE}

**ÖNLEYİCİ AKSIYONLAR:**

{PREVENTIVE_ACTIONS}

Sistem normal çalışma durumuna dönmüştür. Monitoring devam etmektedir.

Saygılarımızla,

Ultron Bilişim iNOC Ekibi

### WhatsApp / Telegram Şablonu

\---

✅ \*ULTRON - ALARM ÇÖZÜLDÜ\*

📊 Ticket: #{TICKET_ID}

🖥️ {AFFECTED_SYSTEM}

⏱️ Süre: {TOTAL_DURATION}

🔧 Çözüm: {RESOLUTION_SUMMARY}

✨ Sistem normale döndü.

📊 Monitoring devam ediyor.

# 2\. REAKTİF INCIDENT MANAGEMENT ŞABLONLARI

## 2.1. Ticket Açılış Onayı

### Email Şablonu

**Konu:** \[GLPI #{TICKET_ID}\] Destek Talebiniz Alındı - {SUBJECT}

\---

Sayın {CUSTOMER_NAME},

Destek talebiniz sistemimize kaydedilmiş ve ilgili ekibe atanmıştır.

**TICKET BİLGİLERİ:**

- Ticket Numarası: {TICKET_ID}
- Açılış Zamanı: {CREATED_TIME}
- Öncelik: {PRIORITY}
- Kategori: {CATEGORY}
- Atanan Ekip: {ASSIGNED_GROUP}
- Atanan Teknisyen: {ASSIGNED_TECHNICIAN}

**PROBLEM AÇIKLAMASI:**

{PROBLEM_DESCRIPTION}

**SLA TAAHHÜDÜMÜZ:**

- İlk Yanıt: {RESPONSE_SLA}
- Çözüm Hedefi: {RESOLUTION_SLA}

Ticket'ınızı takip etmek için: {GLPI_PORTAL_URL}

Saygılarımızla,

Ultron Bilişim Service Desk

### Telefon Görüşme Scripti

\---

**Açılış:**

Merhaba, Ultron Bilişim Service Desk, ben {AGENT_NAME}. Size nasıl yardımcı olabilirim?

**Bilgi Toplama:**

- Adınız ve soyadınız?
- Şirket/Departman?
- İrtibat telefonu/email?
- Probleminizi detaylı anlatır mısınız?
- Problem ne zaman başladı?
- Kaç kullanıcı etkilendi?

**Kapanış:**

Ticket numaranız {TICKET_ID}. Ekibimiz en kısa sürede size dönüş yapacaktır. Başka yardımcı olabileceğim bir konu var mı?

## 2.2. Durum Güncelleme

### Email Şablonu

**Konu:** \[GLPI #{TICKET_ID}\] Durum Güncellemesi - {SUBJECT}

\---

Sayın {CUSTOMER_NAME},

Ticket'ınız ile ilgili durum güncellemesini paylaşmak isteriz.

**GÜNCEL DURUM:**

{UPDATE_MESSAGE}

**YAPILAN İŞLEMLER:**

{ACTIONS_TAKEN}

**SONRAKI ADIMLAR:**

{NEXT_STEPS}

**TAHMİNİ ÇÖZÜM SÜRESİ:**

{ESTIMATED_RESOLUTION}

Ek bilgiye ihtiyacınız olursa lütfen bize ulaşın.

Saygılarımızla,

{TECHNICIAN_NAME}

Ultron Bilişim

# 3\. MAJOR INCIDENT MANAGEMENT ŞABLONLARI

## 3.1. Major Incident Duyurusu

### Email Şablonu

**Konu: \[MAJOR INCIDENT\] {INCIDENT_TITLE}**

\---

**MAJOR INCIDENT DUYURUSU**

Sayın {CUSTOMER_NAME},

Kritik bir olay tespit edilmiş ve Major Incident prosedürü başlatılmıştır.

**INCIDENT DETAYLARI:**

- Incident ID: {INCIDENT_ID}
- Başlangıç Zamanı: {START_TIME}
- Etkilenen Servisler: {AFFECTED_SERVICES}
- Etkilenen Kullanıcı Sayısı: {AFFECTED_USERS}
- İş Etkisi: {BUSINESS_IMPACT}

**GÜNCEL DURUM:**

{CURRENT_STATUS}

**ÇALIŞAN EKİP:**

- Major Incident Manager: {MIM_NAME} ({MIM_PHONE})
- Technical Lead: {TECH_LEAD_NAME}
- Communications Lead: {COMM_LEAD_NAME}

**GÜNCELLEME SIKLIĞI:**

15 dakikada bir güncelleme yapılacaktır.

**WAR ROOM:**

Teams War Room Linki: {TEAMS_LINK}

Bu kritik durumda sabır ve anlayışınız için teşekkür ederiz.

Ultron Bilişim Major Incident Ekibi

### WhatsApp / Telegram Şablonu

\---

🚨 \*MAJOR INCIDENT\* 🚨

ID: {INCIDENT_ID}

⚠️ {INCIDENT_TITLE}

🖥️ Etkilenen: {AFFECTED_SERVICES}

👥 Kullanıcı: {AFFECTED_USERS}

⏰ Başlangıç: {START_TIME}

🔧 Ekibimiz çalışıyor.

📢 15 dak. update

☎️ MIM: {MIM_NAME} {MIM_PHONE}

### SMS Şablonu

\---

MAJOR INCIDENT: {INCIDENT_TITLE}. Etkilenen: {AFFECTED_SERVICES}. Ekibimiz calisiyor. 15dk update. MIM: {MIM_NAME} {MIM_PHONE}

## 3.2. Major Incident Periyodik Güncelleme

### Email Şablonu

**Konu: \[MAJOR INCIDENT\] Güncelleme #{UPDATE_NUMBER} - {INCIDENT_TITLE}**

\---

Sayın {CUSTOMER_NAME},

Devam eden major incident hakkında #{UPDATE_NUMBER} numaralı güncelleme:

**GÜNCEL DURUM ({CURRENT_TIME}):**

{STATUS_UPDATE}

**SON 15 DAKİKADA YAPILAN İŞLEMLER:**

{RECENT_ACTIONS}

**SONRAKI ADIMLAR:**

{NEXT_ACTIONS}

**TAHMİNİ ÇÖZÜM SÜRESİ:**

{ETA}

Sonraki güncelleme: {NEXT_UPDATE_TIME}

Ultron Bilişim Major Incident Ekibi

### WhatsApp / Telegram Şablonu

\---

🔄 \*MAJOR INC UPDATE #{UPDATE_NUMBER}\*

⏰ {CURRENT_TIME}

📊 Durum: {STATUS_SUMMARY}

🔧 Yapılan: {ACTION_SUMMARY}

⏳ ETA: {ETA}

📢 Sonraki: {NEXT_UPDATE_TIME}

## 3.3. Major Incident Çözüm Bildirimi

### Email Şablonu

**Konu: \[MAJOR INCIDENT - ÇÖZÜLDÜ\] {INCIDENT_TITLE}**

\---

**MAJOR INCIDENT ÇÖZÜLDÜ**

Sayın {CUSTOMER_NAME},

Major incident başarıyla çözülmüş ve servisler normal duruma dönmüştür.

**ÖZET BİLGİLER:**

- Incident ID: {INCIDENT_ID}
- Başlangıç: {START_TIME}
- Çözüm: {END_TIME}
- Toplam Süre: {TOTAL_DURATION}
- Downtime: {DOWNTIME}

**ÇÖZÜM ÖZETİ:**

{RESOLUTION_SUMMARY}

**POST-INCIDENT REVIEW:**

Detaylı Post-Incident Review raporu 48 saat içinde paylaşılacaktır.

Gösterdiğiniz anlayış ve sabır için çok teşekkür ederiz.

Saygılarımızla,

Ultron Bilişim Major Incident Ekibi

### WhatsApp / Telegram Şablonu

\---

✅ \*MAJOR INCIDENT ÇÖZÜLDÜ\* ✅

ID: {INCIDENT_ID}

⏱️ Süre: {TOTAL_DURATION}

🖥️ {AFFECTED_SERVICES}

✨ Servisler normal.

📊 PIR raporu 48 saat içinde.

🙏 Anlayışınız için teşekkürler.

# 4\. FIELD SERVICE ŞABLONLARI

## 4.1. Saha Ziyareti Randevu Talebi

### Email Şablonu

**Konu:** \[GLPI #{TICKET_ID}\] Saha Ziyareti Randevu Talebi - {SUBJECT}

\---

Sayın {CUSTOMER_NAME},

Ticket'ınız için saha müdahalesi gerektiği tespit edilmiştir.

**SAHA ZİYARETİ DETAYLARI:**

- Ticket Numarası: {TICKET_ID}
- Müdahale Tipi: {INTERVENTION_TYPE}
- Atanan Teknisyen: {TECHNICIAN_NAME}
- Tahmini Süre: {ESTIMATED_DURATION}

**RANDEVU ÖNERİLERİ:**

- Seçenek 1: {OPTION_1}
- Seçenek 2: {OPTION_2}
- Seçenek 3: {OPTION_3}

**BİZE SAĞLAMANIZ GEREKENLER:**

- Lokasyon tam adresi ve yol tarifi
- İrtibat kişisi ve telefon
- Güvenlik/otopark prosedürleri
- Özel ekipman/araç gereç ihtiyacı

Lütfen size uygun olan randevu seçeneğini bu email'i yanıtlayarak bildiriniz.

Saygılarımızla,

Ultron Bilişim Field Service Coordinator

## 4.2. Teknisyen Yola Çıktı Bildirimi

### WhatsApp / Telegram Şablonu

\---

🚗 \*ULTRON - TEKNİSYEN YOLA ÇIKTI\*

📊 Ticket: #{TICKET_ID}

👨‍🔧 Teknisyen: {TECHNICIAN_NAME}

📞 Tel: {TECHNICIAN_PHONE}

⏰ Tahmini varış: {ETA}

📍 Adres: {LOCATION_ADDRESS}

👤 İrtibat: {CONTACT_PERSON}

### SMS Şablonu

\---

ULTRON: Teknisyenimiz {TECHNICIAN_NAME} yola cikti. Tel: {TECHNICIAN_PHONE}. Tahmini varis: {ETA}. Ticket #{TICKET_ID}

## 4.3. Saha Müdahalesi Tamamlandı

### Email Şablonu

**Konu:** \[GLPI #{TICKET_ID}\] Saha Müdahalesi Tamamlandı - {SUBJECT}

\---

Sayın {CUSTOMER_NAME},

Saha müdahalesimiz başarıyla tamamlanmıştır.

**MÜDAHALE BİLGİLERİ:**

- Ticket Numarası: {TICKET_ID}
- Teknisyen: {TECHNICIAN_NAME}
- Lokasyon: {LOCATION}
- Varış Zamanı: {ARRIVAL_TIME}
- Tamamlanma Zamanı: {COMPLETION_TIME}
- Toplam Süre: {TOTAL_DURATION}

**YAPILAN İŞLEMLER:**

{WORK_PERFORMED}

**DEĞİŞTİRİLEN PARÇALAR:**

{REPLACED_PARTS}

**TEST SONUÇLARI:**

{TEST_RESULTS}

**ÖNERİLER:**

{RECOMMENDATIONS}

İlgili dökümanlar ve fotoğraflar ticket'a eklenmiştir.

Saygılarımızla,

{TECHNICIAN_NAME}

Ultron Bilişim Field Service

# 5\. CHANGE MANAGEMENT ŞABLONLARI

## 5.1. Planlı Değişiklik Bildirimi

### Email Şablonu

**Konu:** \[CHANGE\] Planlı Bakım Bildirimi - {CHANGE_TITLE}

\---

Sayın {CUSTOMER_NAME},

Sistemlerinizde planlı bir değişiklik/bakım gerçekleştirilecektir.

**DEĞİŞİKLİK DETAYLARI:**

- Change ID: {CHANGE_ID}
- Change Türü: {CHANGE_TYPE}
- Başlangıç: {START_TIME}
- Bitiş: {END_TIME}
- Tahmini Süre: {DURATION}
- Etkilenen Sistemler: {AFFECTED_SYSTEMS}

**DEĞİŞİKLİĞİN AMACI:**

{CHANGE_REASON}

**BEKLENİLEN ETKİ:**

{EXPECTED_IMPACT}

**KULLANICILARA TAVSİYELER:**

- {RECOMMENDATION_1}
- {RECOMMENDATION_2}
- {RECOMMENDATION_3}

**GERİ ALMA PLANI:**

Beklenmedik bir sorun durumunda geri alma prosedürü mevcuttur.

Anlayışınız için teşekkür ederiz.

Saygılarımızla,

Ultron Bilişim Change Management

## 5.2. Emergency Change Bildirimi

### Email Şablonu

**Konu: \[EMERGENCY CHANGE\] Acil Değişiklik - {CHANGE_TITLE}**

\---

**ACİL DEĞİŞİKLİK BİLDİRİMİ**

Sayın {CUSTOMER_NAME},

Kritik bir durumu çözmek için acil bir değişiklik uygulanacaktır.

**ACİL DEĞİŞİKLİK DETAYLARI:**

- Emergency Change ID: {CHANGE_ID}
- İlgili Major Incident: {INCIDENT_ID}
- Uygulama Zamanı: {IMPLEMENTATION_TIME}
- Etkilenen Sistemler: {AFFECTED_SYSTEMS}

**ACİLİYET SEBEBİ:**

{URGENCY_REASON}

**YAPILACAK DEĞİŞİKLİK:**

{CHANGE_DESCRIPTION}

**ONAY:**

Bu emergency change {APPROVER_NAME} tarafından onaylanmıştır.

Anlayışınız için teşekkür ederiz.

Ultron Bilişim Change Management

# 6\. RAPORLAMA ŞABLONLARI

## 6.1. Günlük Rapor Özeti

### Email Şablonu

**Konu:** Günlük Operasyon Raporu - {DATE}

\---

Sayın {CUSTOMER_NAME},

{DATE} tarihli günlük operasyon raporumuzu paylaşmak isteriz.

**TICKET İSTATİSTİKLERİ:**

- Yeni Ticket: {NEW_TICKETS}
- Çözülen Ticket: {RESOLVED_TICKETS}
- Devam Eden: {OPEN_TICKETS}
- P1 Ticket: {P1_COUNT}
- P2 Ticket: {P2_COUNT}

**MONİTORİNG:**

- Proaktif Alarm: {PROACTIVE_ALARMS}
- Sistem Uptime: {UPTIME_PERCENTAGE}%
- False Positive: {FALSE_POSITIVE_COUNT}

**PERFORMANS METRİKLERİ:**

- Ortalama Yanıt Süresi: {AVG_RESPONSE}
- Ortalama Çözüm Süresi: {AVG_RESOLUTION}
- SLA Compliance: {SLA_COMPLIANCE}%

**ÖNEMLI OLAYLAR:**

{IMPORTANT_EVENTS}

Detaylı rapor ektedir.

Saygılarımızla,

Ultron Bilişim Operations Team

## 6.2. Aylık Performans Raporu

### Email Şablonu

**Konu:** Aylık Hizmet Performans Raporu - {MONTH} {YEAR}

\---

Sayın {CUSTOMER_NAME},

{MONTH} {YEAR} ayına ait hizmet performans raporumuzu sunmaktan memnuniyet duyarız.

**AYLIK ÖZET:**

- Toplam Ticket: {TOTAL_TICKETS}
- Çözüm Oranı: {RESOLUTION_RATE}%
- SLA Uyumu: {SLA_COMPLIANCE}%
- CSAT Skoru: {CSAT_SCORE}/5.0
- Sistem Uptime: {UPTIME}%

**KATEGORİ BAZLI DAĞILIM:**

- Network: {NETWORK_TICKETS}
- Server: {SERVER_TICKETS}
- Application: {APP_TICKETS}
- Field Service: {FIELD_TICKETS}

**TRENDLER:**

{MONTHLY_TRENDS}

**İYİLEŞTİRME ÖNERİLERİ:**

{IMPROVEMENT_SUGGESTIONS}

Detaylı rapor PDF formatında ektedir.

Saygılarımızla,

Ultron Bilişim Account Management

# 7\. SÖZLEŞME YÖNETİMİ ŞABLONLARI

## 7.1. Sözleşme Yenileme Hatırlatma (90 Gün Önce)

### Email Şablonu

**Konu:** Sözleşme Yenileme - 90 Gün Kaldı

\---

Sayın {CUSTOMER_NAME},

Mevcut hizmet sözleşmenizin bitiş tarihine 90 gün kaldı.

**SÖZLEŞME BİLGİLERİ:**

- Sözleşme No: {CONTRACT_NUMBER}
- Başlangıç: {START_DATE}
- Bitiş: {END_DATE}
- Kalan Süre: 90 gün

**KAPSANAN HİZMETLER:**

{SERVICES_LIST}

**YENİLEME TOPLANTISI:**

Yenileme koşullarını görüşmek ve ihtiyaçlarınızı değerlendirmek için bir toplantı planlamak isteriz.

Account Manager'ınız {ACCOUNT_MANAGER} en kısa sürede sizinle iletişime geçecektir.

Saygılarımızla,

Ultron Bilişim Account Management

## 7.2. Sözleşme Bitiş Bildirimi (30 Gün Önce)

### Email Şablonu

**Konu: ÖNEMLİ: Sözleşme Bitiş Bildirimi - 30 Gün**

\---

Sayın {CUSTOMER_NAME},

Mevcut hizmet sözleşmenizin bitiş tarihine 30 gün kaldı. Kesintisiz hizmet için acil karar beklenmektedir.

**SÖZLEŞME BİLGİLERİ:**

- Sözleşme No: {CONTRACT_NUMBER}
- Bitiş Tarihi: {END_DATE}
- Kalan Süre: 30 gün

**SÖZLEŞME BİTİMİNDE:**

- 7/24 monitoring hizmeti sona erecektir
- SLA taahhütleri geçerliliğini yitirecektir
- Field service hizmetleri durduracaktır
- GLPI portal erişimi kapatılacaktır

**YENİLEME İÇİN GEREKEN ADIMLAR:**

- Yenileme teklifimizi değerlendirin
- Nihai onayı 15 gün içinde verin
- Sözleşme imzalama işlemini tamamlayın

**ACİL İRTİBAT: {ACCOUNT_MANAGER} - {MANAGER_PHONE} - {MANAGER_EMAIL}**

Saygılarımızla,

Ultron Bilişim Account Management

# 8\. ESKALASYON ŞABLONLARI

## 8.1. SLA İhlali Uyarısı (İç Eskalasyon)

### Email Şablonu (İç)

**Konu: \[SLA ALERT\] Ticket #{TICKET_ID} - SLA İhlali Riski**

\---

Sayın {MANAGER_NAME},

Aşağıdaki ticket SLA ihlali riski taşımaktadır.

**TICKET DETAYLARI:**

- Ticket ID: {TICKET_ID}
- Müşteri: {CUSTOMER_NAME}
- Segment: {CUSTOMER_SEGMENT}
- Öncelik: {PRIORITY}
- Atanan: {ASSIGNED_TECH}

**SLA DURUMU:**

- Response SLA: {RESPONSE_SLA} (Kalan: {RESPONSE_REMAINING})
- Resolution SLA: {RESOLUTION_SLA} (Kalan: {RESOLUTION_REMAINING})
- **SLA İhlali Riski: {RISK_LEVEL}**

**GEREKLİ AKSIYON:**

Lütfen acil müdahale edin veya eskalasyon yapın.

GLPI Otomasyon

## 8.2. Müşteriye Eskalasyon Bildirimi

### Email Şablonu

**Konu:** \[GLPI #{TICKET_ID}\] Eskalasyon - {SUBJECT}

\---

Sayın {CUSTOMER_NAME},

Ticket'ınız üst yönetime eskaleedilmiştir.

**ESKALASYON SEBEBİ:**

{ESCALATION_REASON}

**YENİ ATAMA:**

- Seviye: {NEW_LEVEL}
- Sorumlu: {NEW_OWNER}
- İrtibat: {NEW_CONTACT}

**ATILAN ADIMLAR:**

{ACTIONS_TAKEN}

{NEW_OWNER} en kısa sürede sizinle iletişime geçecektir.

Saygılarımızla,

Ultron Bilişim Management

# 9\. MÜŞTERİ MEMNUNİYETİ ŞABLONLARI

## 9.1. CSAT Anketi - Ticket Çözümü

### Email Şablonu

**Konu:** Memnuniyet Anketi - Ticket #{TICKET_ID}

\---

Sayın {CUSTOMER_NAME},

Ticket #{TICKET_ID} çözümlendi. Hizmetimizi değerlendirmenizi rica ederiz.

**HİZMET KALİTESİNİ DEĞERLENDİRİN:**

1 = Çok Kötü | 5 = Mükemmel

**1\. Yanıt Süresi:**

☐ 1 ☐ 2 ☐ 3 ☐ 4 ☐ 5

**2\. Çözüm Kalitesi:**

☐ 1 ☐ 2 ☐ 3 ☐ 4 ☐ 5

**3\. İletişim:**

☐ 1 ☐ 2 ☐ 3 ☐ 4 ☐ 5

**4\. Teknik Yetkinlik:**

☐ 1 ☐ 2 ☐ 3 ☐ 4 ☐ 5

**EK YORUMLARINIZ:**

\_**\_**\_**\_**\_**\_**\_**\_**\_**\_**\_**\_**\___\__

Anketi tamamlamak için: {SURVEY_LINK}

Değerli görüşleriniz için teşekkür ederiz.

Ultron Bilişim

### WhatsApp / Telegram Şablonu

\---

📊 \*ULTRON - ANKET\*

Ticket #{TICKET_ID} çözüldü!

Hizmetimizi 1-5 arası değerlendirin:

1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣

Anket linki: {SURVEY_LINK}

🙏 Görüşleriniz bizim için değerli!

## 9.2. Düşük Puan Takip Görüşmesi

### Telefon Görüşme Scripti

\---

**Açılış:**

Merhaba, ben {AGENT_NAME}, Ultron Bilişim müşteri ilişkileri ekibinden arıyorum. {TICKET_ID} numaralı ticket için verdiğiniz geri bildirim ile ilgili görüşmek istiyorum. Şu an uygun musunuz?

**Durumu Anlama:**

- Yaşadığınız sıkıntıyı detaylı anlatır mısınız?
- Hangi konuda beklentileriniz karşılanmadı?
- Problem şu an çözülmüş durumda mı?

**Empati ve Özür:**

Yaşadığınız sıkıntı için çok üzgünüm. Bu durum kesinlikle olmamalıydı. Memnuniyetsizliğiniz için özür dilerim.

**Aksiy on Planı:**

- Bu konuda atacağımız adımlar:
- {ACTION_1}
- {ACTION_2}
- {ACTION_3}

**Kapanış:**

Geri bildiriminiz için teşekkür ederim. Konu ile ilgili takip için size {FOLLOWUP_DATE} tarihinde tekrar dönüş yapacağım. Başka eklemek istediğiniz bir şey var mı?

**DOKÜMAN SONU**

\---

Ultron Bilişim A.Ş.

İletişim Şablonları Kütüphanesi v1.0

_Tüm ITSM Süreçleri için Standart Şablonlar_

NOT: Bu şablonlar değişken alanlar içermektedir.

Kullanmadan önce {DEĞIŞKEN} alanlarını gerçek verilerle değiştirin.

GLPI otomasyon kuralları ile entegre edilebilir.