# GLPI Notification Event - Template Mapping (Complete)

## 📋 Tüm Event'ler ve Template Eşleştirmeleri

| Event Adı | GLPI Event | Önerilen Template | Recipients |
|-----------|------------|-------------------|------------|
| **Add Followup** | New followup | **Followup** | Requester, Observer, Assigned Tech, Assigned Group |
| **Add Task** | New task | **Task** | Assigned Tech, Assigned Group |
| **Close Ticket** | Closing of the ticket | **Resolution** | Requester, Observer, Assigned Tech |
| **Delete Followup** | Deletion of a followup | **Followup** | Requester, Observer, Assigned Tech |
| **Delete Task** | Deletion of a task | **Task** | Assigned Tech, Assigned Group |
| **Delete Ticket** | Deletion of a ticket | **Deletion** | Requester, Observer, Assigned Tech, Supervisor, Admin |
| **New document** | New document | **Followup** | Requester, Observer, Assigned Tech |
| **New group in assignees** | New group in assignees | **Assignment** | Requester, Observer, New Assigned Group |
| **New group in observers** | New group in observers | **Followup** | New Observer Group |
| **New group in requesters** | New group in requesters | **New Ticket** | New Requester Group |
| **New supplier in assignees** | New supplier in assignees | **Assignment** | Requester, Observer, New Supplier |
| **New Ticket** | New ticket | **New Ticket** | Requester, Observer, Assigned Tech, Assigned Group |
| **New user in assignees** | New user in assignees | **Assignment** | Requester, Observer, New Assigned Tech |
| **New user in observers** | New user in observers | **Followup** | New Observer |
| **New user in requesters** | New user in requesters | **New Ticket** | New Requester |
| **New user mentioned** | User mentioned | **Followup** | Mentioned User |
| **Resolve ticket** | Ticket solved | **Resolution** | Requester, Observer, Assigned Tech |
| **Ticket Recall** | Automatic reminders of SLAs | **Deletion** | Requester, Observer, Assigned Tech, Supervisor |
| **Update Followup** | Update of a followup | **Followup** | Requester, Observer, Assigned Tech, Assigned Group |
| **Update Task** | Update of a task | **Task** | Assigned Tech, Assigned Group |
| **Update Ticket** | Update of a ticket | **Followup** | Requester, Observer, Assigned Tech, Assigned Group |

---

## 📊 Template Bazında Gruplandırma

### 1. New Ticket Template
**Event'ler:**
- New Ticket
- New user in requesters
- New group in requesters

### 2. Resolution Template
**Event'ler:**
- Close Ticket
- Resolve ticket

### 3. Followup Template
**Event'ler:**
- Add Followup
- Update Followup
- Delete Followup
- New document
- New user in observers
- New group in observers
- New user mentioned
- Update Ticket

### 4. Task Template
**Event'ler:**
- Add Task
- Update Task
- Delete Task

### 5. Assignment Template
**Event'ler:**
- New user in assignees
- New group in assignees
- New supplier in assignees

### 6. Deletion Template
**Event'ler:**
- Delete Ticket
- Ticket Recall

---

## ⚠️ Özel Durumlar

### Update Ticket Event
**Sorun:** Çok genel bir event, her güncelleme için tetiklenir  
**Çözüm:** Followup template kullanın veya devre dışı bırakın  
**Alternatif:** Sadece önemli güncellemeler için manuel bildirim

### New document Event
**Sorun:** Dokuman eklendiğinde tetiklenir  
**Çözüm:** Followup template kullanın (yeni içerik eklendi anlamında)  
**Alternatif:** Özel bir template oluşturun (opsiyonel)

### Ticket Recall Event
**Not:** "Automatic reminders of SLAs" açıklaması yanıltıcı  
**Gerçek:** Ticket geri çağırma/hatırlatma  
**Template:** Deletion template uygun

---

## 🎯 Hızlı Kurulum Tablosu

| Template Dosyası | Kaç Event | Event Sayısı |
|------------------|-----------|--------------|
| ticket_new_notification | 3 | New Ticket, New user/group in requesters |
| ticket_resolution_notification | 2 | Close Ticket, Resolve ticket |
| ticket_followup_notification | 8 | Add/Update/Delete Followup, New document, New observers, Mentioned, Update Ticket |
| ticket_task_notification | 3 | Add/Update/Delete Task |
| ticket_assignment_notification | 3 | New user/group/supplier in assignees |
| ticket_deletion_notification | 2 | Delete Ticket, Ticket Recall |

**TOPLAM:** 21 event → 6 template ile kapsanıyor ✅

---

## 📝 GLPI'da Ayarlama Sırası

### 1. Önce Kritik Event'leri Ayarlayın
1. ✅ New Ticket → New Ticket template
2. ✅ Resolve ticket → Resolution template
3. ✅ Add Followup → Followup template
4. ✅ New user in assignees → Assignment template

### 2. Sonra Opsiyonel Event'leri Ayarlayın
5. ⚠️ Update Ticket → Followup template (veya devre dışı)
6. ⚠️ Delete Followup → Followup template (veya devre dışı)
7. ⚠️ Delete Task → Task template (veya devre dışı)
8. ⚠️ New document → Followup template (veya devre dışı)

### 3. Son Olarak Nadir Event'leri Ayarlayın
9. 🔹 Delete Ticket → Deletion template
10. 🔹 Ticket Recall → Deletion template

---

## 💡 Öneriler

### Devre Dışı Bırakılabilecek Event'ler
- ❌ Update Ticket (çok fazla spam)
- ❌ Delete Followup (nadiren gerekli)
- ❌ Delete Task (nadiren gerekli)
- ❌ Update Followup (çok fazla bildirim)
- ❌ Update Task (internal işlem)

### Mutlaka Aktif Olması Gerekenler
- ✅ New Ticket
- ✅ Resolve ticket
- ✅ Add Followup
- ✅ New user in assignees
- ✅ New user mentioned

---

## 🔧 Task Template Özel Notu

**ÖNEMLİ:** Task template'leri **ASLA** Requester'a göndermeyin!

```
Recipients for Task events:
✅ Assigned Technician
✅ Assigned Group
❌ Requester (ASLA)
❌ Observer (ASLA)
```

Task'lar internal (dahili) işlemlerdir, son kullanıcıyı ilgilendirmez.

---

**Son Güncelleme:** 2026-01-08  
**Toplam Event:** 21  
**Toplam Template:** 6
