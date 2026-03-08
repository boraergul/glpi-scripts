# GLPI Notification Event - Template Mapping

## 📋 Tüm Event'ler ve Önerilen Template'ler

| Event ID | Event Adı | Önerilen Template | Açıklama |
|----------|-----------|-------------------|----------|
| 4 | Close Ticket | **Resolution** | Ticket kapatıldığında (çözümlendi ile aynı) |
| 5 | Add Followup | **Followup** | Yeni yorum/takip eklendiğinde |
| 6 | Add Task | **Task** | Yeni görev eklendiğinde |
| 7 | Update Followup | **Followup** | Yorum güncellendiğinde |
| 8 | Update Task | **Task** | Görev güncellendiğinde |
| 9 | Delete Followup | **Followup** | Yorum silindiğinde |
| 10 | Delete Task | **Task** | Görev silindiğinde |
| 11 | Resolve ticket | **Resolution** | Ticket çözüldüğünde |
| 24 | Ticket Recall | **Deletion** | Ticket geri çağrıldığında |
| 59 | New user in requesters | **New Ticket** | Yeni talep eden eklendiğinde |
| 60 | New group in requesters | **New Ticket** | Yeni talep eden grup eklendiğinde |
| 61 | New user in observers | **Followup** | Yeni gözlemci eklendiğinde |
| 62 | New group in observers | **Followup** | Yeni gözlemci grup eklendiğinde |
| 63 | New user in assignees | **Assignment** | Yeni teknisyen atandığında |
| 64 | New group in assignees | **Assignment** | Yeni grup atandığında |
| 65 | New supplier in assignees | **Assignment** | Yeni tedarikçi atandığında |
| 72 | New user mentioned | **Followup** | Kullanıcı mention edildiğinde (@user) |
| - | SLA TTO Warning | **SLA Warning** | SLA müdahale süresi uyarısı |
| - | SLA TTR Warning | **SLA Warning** | SLA çözüm süresi uyarısı |
| - | Change ticket assignee | **Assignment** veya **Transfer** | Atanan kişi/grup değiştiğinde |

---

## 📧 Template Bazında Gruplandırma

### 1. New Ticket Template
**Kullanıldığı Event'ler:**
- New user in requesters (59)
- New group in requesters (60)

**Neden?** Yeni talep eden eklendiğinde, onlara ticket bilgilerini göstermek için.

---

### 2. Resolution Template
**Kullanıldığı Event'ler:**
- Close Ticket (4)
- Resolve ticket (11)

**Neden?** Her iki event de ticket'ın çözüldüğünü/kapatıldığını gösterir.

---

### 3. Followup Template
**Kullanıldığı Event'ler:**
- Add Followup (5)
- Update Followup (7)
- Delete Followup (9)
- New user in observers (61)
- New group in observers (62)
- New user mentioned (72)

**Neden?** Tüm yorum/takip ile ilgili işlemler ve yeni gözlemciler için.

---

### 4. Task Template
**Kullanıldığı Event'ler:**
- Add Task (6)
- Update Task (8)
- Delete Task (10)

**Neden?** Tüm görev işlemleri için.

---

### 5. Assignment Template
**Kullanıldığı Event'ler:**
- New user in assignees (63)
- New group in assignees (64)
- New supplier in assignees (65)

**Neden?** Tüm atama işlemleri için.

---

### 6. Deletion Template
**Kullanıldığı Event'ler:**
- Ticket Recall (24)

**Neden?** Ticket geri çağırma, silme işlemine benzer.

---

## 🎯 GLPI'da Ayarlama Rehberi

### Event 4: Close Ticket
```
Template: ticket_resolution_notification_tr / _en
Recipients: Requester, Observer, Assigned Technician
```

### Event 5: Add Followup
```
Template: ticket_followup_notification_tr / _en
Recipients: Requester, Observer, Assigned Technician, Assigned Group
```

### Event 6: Add Task
```
Template: ticket_task_notification_tr / _en
Recipients: Assigned Technician, Assigned Group
NOT: Requester (internal işlem)
```

### Event 7: Update Followup
```
Template: ticket_followup_notification_tr / _en
Recipients: Requester, Observer, Assigned Technician, Assigned Group
```

### Event 8: Update Task
```
Template: ticket_task_notification_tr / _en
Recipients: Assigned Technician, Assigned Group
```

### Event 9: Delete Followup
```
Template: ticket_followup_notification_tr / _en
Recipients: Requester, Observer, Assigned Technician
Note: "Yorum silindi" mesajı için
```

### Event 10: Delete Task
```
Template: ticket_task_notification_tr / _en
Recipients: Assigned Technician, Assigned Group
```

### Event 11: Resolve ticket
```
Template: ticket_resolution_notification_tr / _en
Recipients: Requester, Observer, Assigned Technician
```

### Event 24: Ticket Recall
```
Template: ticket_deletion_notification_tr / _en
Recipients: Requester, Observer, Assigned Technician, Supervisor, Admin
```

### Event 59: New user in requesters
```
Template: ticket_new_notification_tr / _en
Recipients: New Requester
Note: Yeni eklenen kişiye ticket bilgilerini göster
```

### Event 60: New group in requesters
```
Template: ticket_new_notification_tr / _en
Recipients: New Requester Group
```

### Event 61: New user in observers
```
Template: ticket_followup_notification_tr / _en
Recipients: New Observer
Note: Yeni gözlemciye mevcut durumu göster
```

### Event 62: New group in observers
```
Template: ticket_followup_notification_tr / _en
Recipients: New Observer Group
```

### Event 63: New user in assignees
```
Template: ticket_assignment_notification_tr / _en
Recipients: Requester, Observer, New Assigned Technician
```

### Event 64: New group in assignees
```
Template: ticket_assignment_notification_tr / _en
Recipients: Requester, Observer, New Assigned Group
```

### Event 65: New supplier in assignees
```
Template: ticket_assignment_notification_tr / _en
Recipients: Requester, Observer, New Supplier
```

### Event 72: New user mentioned
```
Template: ticket_followup_notification_tr / _en
Recipients: Mentioned User
Note: @mention özelliği için
```

---

## 📊 Özet Tablo

| Template | Event Sayısı | Event ID'ler |
|----------|--------------|--------------|
| **New Ticket** | 2 | 59, 60 |
| **Resolution** | 2 | 4, 11 |
| **Followup** | 6 | 5, 7, 9, 61, 62, 72 |
| **Task** | 3 | 6, 8, 10 |
| **Assignment** | 3 | 63, 64, 65 |
| **Deletion** | 1 | 24 |
| **TOPLAM** | **17 event** | |

---

## ⚠️ Önemli Notlar

### 1. Task Event'leri (6, 8, 10)
- **Requester'a GÖNDERMEYİN**
- Sadece teknik ekip (Assigned Tech, Assigned Group)
- Internal işlemlerdir

### 2. Delete Event'leri (9, 10)
- Silme bildirimleri opsiyoneldir
- Gerekirse devre dışı bırakabilirsiniz
- Spam'den kaçınmak için

### 3. New User/Group Event'leri (59-65)
- Sadece YENİ eklenen kişi/gruba gönderin
- Diğer alıcıları eklemeyin (spam olur)

### 4. Mention Event (72)
- Sadece mention edilen kişiye gönderin
- Followup template kullanın
- Context göstermek için

---

## 🔧 Hızlı Kurulum Scripti

GLPI'da tüm bu ayarları yapmak için:

1. **Setup > Notifications > Notifications**
2. Her event için:
   - Template seç (yukarıdaki tablodan)
   - Recipients ekle (yukarıdaki rehberden)
   - Save

**Tahmini Süre:** ~30 dakika (17 event × ~2 dakika)

---

## 📞 Destek

Bu mapping hakkında sorularınız için:
- `templates/NOTIFICATION_RECIPIENTS.md` - Detaylı alıcı rehberi
- `templates/README.md` - Template dokümantasyonu

**Son Güncelleme:** 2026-01-08
