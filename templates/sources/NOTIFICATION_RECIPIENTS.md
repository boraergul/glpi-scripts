# GLPI Notification Template Recipients (Alıcılar) Rehberi

## 📧 Her Template için Önerilen Alıcılar

Bu rehber, her notification template'inin hangi kullanıcı gruplarına gönderilmesi gerektiğini gösterir.

---

## 📊 Alıcı Tablosu

| # | Template | Requester | Observer | Assigned Technician | Assigned Group | Supervisor | Admin | Supplier | Açıklama |
|---|----------|-----------|----------|---------------------|----------------|------------|-------|----------|----------|
| 1 | **New Ticket** | ✅ | ✅ | ✅ | ✅ | ⚠️ | ❌ | ❌ | Yeni ticket oluşturulduğunda tüm ilgili taraflar bilgilendirilir |
| 2 | **Transfer** | ✅ | ✅ | ✅ | ✅ | ⚠️ | ❌ | ❌ | Ticket başka gruba transfer edildiğinde eski ve yeni grup bilgilendirilir |
| 3 | **Resolution** | ✅ | ✅ | ✅ | ⚠️ | ❌ | ❌ | ❌ | Ticket çözüldüğünde talep eden ve çözümü yapan bilgilendirilir |
| 4 | **Followup** | ✅ | ✅ | ✅ | ✅ | ⚠️ | ❌ | ❌ | Yeni yorum eklendiğinde tüm takip edenler bilgilendirilir |
| 5 | **Assignment** | ✅ | ✅ | ✅ | ✅ | ⚠️ | ❌ | ✅ | Atama yapıldığında yeni atanan kişi/grup bilgilendirilir |
| 6 | **Task** | ❌ | ⚠️ | ✅ | ✅ | ⚠️ | ❌ | ❌ | Görev oluşturulduğunda sadece teknik ekip bilgilendirilir |
| 7 | **SLA Warning** | ⚠️ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | SLA ihlali yaklaştığında yönetim ve teknik ekip uyarılır |
| 8 | **Deletion** | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ | ❌ | Ticket silindiğinde tüm ilgili taraflar bilgilendirilir |

**Lejant:**
- ✅ **Kesinlikle Gönder** - Bu alıcı grubuna mutlaka gönderilmeli
- ⚠️ **İsteğe Bağlı** - Organizasyon politikasına göre eklenebilir
- ❌ **Gönderme** - Bu alıcı grubuna gönderilmemeli

---

## 📋 Detaylı Alıcı Açıklamaları

### 1. New Ticket (Yeni Ticket)

**Kimler Almalı:**
- ✅ **Requester (Talep Eden)** - Ticket'ın oluşturulduğunu onaylamak için
- ✅ **Observer (Gözlemci)** - Ticket'tan haberdar olmaları için
- ✅ **Assigned Technician (Atanan Teknisyen)** - Yeni iş bildirimi
- ✅ **Assigned Group (Atanan Grup)** - Grup üyeleri bilgilendirilir
- ⚠️ **Supervisor (Süpervizör)** - Sadece kritik ticket'lar için

**GLPI Ayarı:**
```
Setup > Notifications > Notifications > New Ticket
Recipients:
- Requester
- Observer  
- Assigned Technician
- Assigned Group
```

---

### 2. Transfer (Transfer)

**Kimler Almalı:**
- ✅ **Requester** - Ticket'ın başka gruba gittiğini bilmeli
- ✅ **Observer** - Değişiklikten haberdar olmalı
- ✅ **Assigned Technician (Yeni)** - Yeni sorumlu bilgilendirilir
- ✅ **Assigned Group (Yeni)** - Yeni grup bilgilendirilir
- ⚠️ **Supervisor** - Önemli transfer'ler için

**GLPI Ayarı:**
```
Setup > Notifications > Notifications > Transfer Ticket
Recipients:
- Requester
- Observer
- Assigned Technician
- Assigned Group
```

**Not:** Eski grup/teknisyen otomatik olarak bilgilendirilmez, gerekirse manuel ekleyin.

---

### 3. Resolution (Çözüm)

**Kimler Almalı:**
- ✅ **Requester** - Çözümü görmeli ve onaylamalı
- ✅ **Observer** - Sonuçtan haberdar olmalı
- ✅ **Assigned Technician** - Çözümü yapan teknisyen
- ⚠️ **Assigned Group** - Sadece grup metrikleri için gerekirse

**GLPI Ayarı:**
```
Setup > Notifications > Notifications > Resolve Ticket
Recipients:
- Requester
- Observer
- Assigned Technician
```

---

### 4. Followup (Yorum/Takip)

**Kimler Almalı:**
- ✅ **Requester** - Yeni gelişmelerden haberdar olmalı
- ✅ **Observer** - Takip ettikleri ticket'taki yorumları görmeliler
- ✅ **Assigned Technician** - Yeni yorum/bilgi için
- ✅ **Assigned Group** - Grup üyeleri bilgilendirilir
- ⚠️ **Supervisor** - Önemli güncellemeler için

**GLPI Ayarı:**
```
Setup > Notifications > Notifications > Add Followup
Recipients:
- Requester
- Observer
- Assigned Technician
- Assigned Group
```

**Özel Durum:** Mention (@kullanıcı) özelliği kullanılıyorsa, mention edilen kişi de almalı.

---

### 5. Assignment (Atama)

**Kimler Almalı:**
- ✅ **Requester** - Kimin sorumlu olduğunu bilmeli
- ✅ **Observer** - Değişiklikten haberdar olmalı
- ✅ **Assigned Technician (Yeni)** - Yeni görev bildirimi
- ✅ **Assigned Group (Yeni)** - Yeni grup bilgilendirilir
- ⚠️ **Supervisor** - Önemli atamalar için
- ✅ **Supplier (Tedarikçi)** - Eğer dış kaynak atanıyorsa

**GLPI Ayarı:**
```
Setup > Notifications > Notifications > Assign Ticket
Recipients:
- Requester
- Observer
- Assigned Technician
- Assigned Group
- Supplier (if applicable)
```

---

### 6. Task (Görev)

**Kimler Almalı:**
- ❌ **Requester** - Teknik görevler son kullanıcıyı ilgilendirmez
- ⚠️ **Observer** - Sadece teknik observer'lar için
- ✅ **Assigned Technician** - Görev sahibi
- ✅ **Assigned Group** - Görevin atandığı grup
- ⚠️ **Supervisor** - Görev takibi için

**GLPI Ayarı:**
```
Setup > Notifications > Notifications > Add Task
Recipients:
- Assigned Technician
- Assigned Group
```

**Not:** Task'lar genellikle internal (dahili) işlemlerdir, son kullanıcıya gönderilmez.

---

### 7. SLA Warning (SLA Uyarısı)

**Kimler Almalı:**
- ⚠️ **Requester** - Sadece şeffaflık politikası varsa
- ❌ **Observer** - Genellikle gerekli değil
- ✅ **Assigned Technician** - Acil aksiyon almalı
- ✅ **Assigned Group** - Grup müdahale etmeli
- ✅ **Supervisor** - Escalation için
- ✅ **Admin** - SLA ihlali kritik durumdur

**GLPI Ayarı:**
```
Setup > Notifications > Notifications > SLA Warning
Recipients:
- Assigned Technician
- Assigned Group
- Supervisor
- Administrator
```

**Önemli:** SLA uyarıları genellikle sadece teknik ekip ve yönetime gönderilir.

---

### 8. Deletion (Silme/Recall)

**Kimler Almalı:**
- ✅ **Requester** - Ticket'ın silindiğini bilmeli
- ✅ **Observer** - Bilgilendirilmeli
- ✅ **Assigned Technician** - Artık üzerinde çalışmayacak
- ⚠️ **Assigned Group** - Kayıt için
- ✅ **Supervisor** - Silme işlemlerini takip için
- ✅ **Admin** - Audit trail için

**GLPI Ayarı:**
```
Setup > Notifications > Notifications > Delete Ticket
Recipients:
- Requester
- Observer
- Assigned Technician
- Supervisor
- Administrator
```

---

## 🎯 Genel Öneriler

### En İyi Uygulamalar

1. **Requester Her Zaman Bilgilendirilmeli**
   - Kendi ticket'ları hakkında tüm önemli değişiklikleri bilmelidirler
   - İstisna: Internal task'lar

2. **Observer'lar Pasif Takipçilerdir**
   - Tüm güncellemeleri almalılar
   - Spam'den kaçınmak için sadece önemli event'ler

3. **Teknik Ekip Sadece İlgili Bildirimleri Almalı**
   - Assigned technician: Sadece kendisine atanan ticket'lar
   - Assigned group: Grubun sorumlu olduğu ticket'lar

4. **Yönetim Sadece Kritik Durumlarda**
   - SLA uyarıları
   - Major incident'ler
   - Escalation durumları

5. **Spam'den Kaçının**
   - Çok fazla bildirim göndermek, önemli bildirimlerin gözden kaçmasına neden olur
   - Her alıcı grubunu dikkatli seçin

---

## 📧 GLPI'da Recipient Ayarlama

### Adım Adım:

1. **Setup > Notifications > Notifications**
2. İlgili notification'ı seçin (örn: "New Ticket")
3. **Recipients** sekmesine gidin
4. **Add** butonuna tıklayın
5. Alıcı tipini seçin:
   - **Requester**
   - **Observer**
   - **Assigned Technician**
   - **Assigned Group**
   - **Supervisor**
   - **Administrator**
   - **Supplier**
6. **Add** ile kaydedin
7. Diğer alıcı tipleri için tekrarlayın

---

## 🔔 Notification Event Mapping

GLPI'daki event'ler ve önerilen template'ler:

| GLPI Event | Template | Önerilen Recipients |
|------------|----------|---------------------|
| New ticket | New Ticket | Requester, Observer, Assigned Tech, Assigned Group |
| Add ticket | New Ticket | Requester, Observer, Assigned Tech, Assigned Group |
| Update ticket | Followup | Requester, Observer, Assigned Tech, Assigned Group |
| Close ticket | Resolution | Requester, Observer, Assigned Tech |
| Resolve ticket | Resolution | Requester, Observer, Assigned Tech |
| Add followup | Followup | Requester, Observer, Assigned Tech, Assigned Group |
| Update followup | Followup | Requester, Observer, Assigned Tech, Assigned Group |
| Add task | Task | Assigned Tech, Assigned Group |
| Update task | Task | Assigned Tech, Assigned Group |
| Delete task | Task | Assigned Tech, Assigned Group |
| Assign ticket to user | Assignment | Requester, Observer, Assigned Tech |
| Assign ticket to group | Assignment | Requester, Observer, Assigned Group |
| New user in requesters | New Ticket | New Requester |
| New user in observers | Followup | New Observer |
| New user in assignees | Assignment | New Assigned Tech |
| New group in assignees | Assignment | New Assigned Group |
| New supplier in assignees | Assignment | New Supplier |
| SLA warning | SLA Warning | Assigned Tech, Assigned Group, Supervisor, Admin |
| Delete ticket | Deletion | Requester, Observer, Assigned Tech, Supervisor, Admin |
| Ticket Recall | Deletion | Requester, Observer, Assigned Tech, Supervisor, Admin |
| New user mentioned | Followup | Mentioned User |

---

## ⚠️ Önemli Notlar

### Dikkat Edilmesi Gerekenler:

1. **Privacy (Gizlilik)**
   - Internal note'lar sadece teknik ekibe gitmeli
   - Public followup'lar requester'a da gider

2. **Spam Prevention**
   - Çok fazla bildirim kullanıcıları rahatsız eder
   - Sadece gerekli alıcıları ekleyin

3. **SLA Compliance**
   - SLA uyarıları mutlaka teknik ekip ve yönetime gitmeli
   - Requester'a gönderilmesi isteğe bağlı

4. **Audit Trail**
   - Önemli işlemler (silme, transfer) için admin'e de gönderin
   - Kayıt tutma amaçlı

5. **Language Selection**
   - GLPI kullanıcının dil tercihine göre otomatik template seçer
   - TR kullanıcılar TR template, EN kullanıcılar EN template alır

---

## 📊 Örnek Senaryo

### Senaryo: Yeni Ticket Oluşturuldu

**Ticket Bilgileri:**
- Requester: Ali Yılmaz (Muhasebe)
- Observer: Ayşe Demir (Muhasebe Müdürü)
- Assigned Group: IT Destek Ekibi
- Assigned Technician: Mehmet Kaya

**Kimler Bildirim Alır:**
1. ✅ Ali Yılmaz → "Ticket'ınız oluşturuldu" (New Ticket template)
2. ✅ Ayşe Demir → "Yeni ticket oluşturuldu" (New Ticket template)
3. ✅ IT Destek Ekibi → "Yeni ticket atandı" (New Ticket template)
4. ✅ Mehmet Kaya → "Size yeni ticket atandı" (New Ticket template)

**Kullanılan Template:** `ticket_new_notification_tr.html`

---

## 🎓 Best Practices Özeti

| Alıcı Grubu | Ne Zaman Ekle | Ne Zaman Ekleme |
|-------------|---------------|-----------------|
| **Requester** | Tüm ticket değişiklikleri | Internal task'lar |
| **Observer** | Tüm önemli güncellemeler | Çok sık olan küçük değişiklikler |
| **Assigned Tech** | Kendisine atanan işler | Başkasına atanan işler |
| **Assigned Group** | Gruba atanan işler | Başka gruba atanan işler |
| **Supervisor** | SLA uyarıları, escalation | Rutin işlemler |
| **Admin** | SLA ihlalleri, silme işlemleri | Normal ticket işlemleri |
| **Supplier** | Tedarikçiye atanan işler | Internal işler |

---

## 📞 Destek

Bu rehber hakkında sorularınız için:
- GLPI Dokümantasyonu: https://glpi-project.org/documentation/
- Template Dokümantasyonu: `templates/README.md`

**Son Güncelleme:** 2026-01-08
