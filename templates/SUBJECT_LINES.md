# GLPI Notification Template Subject Lines

Bu dosya, GLPI notification template'leri için kullanılacak **Subject (Başlık)** satırlarını içerir.

> [!WARNING]
> **Çift Prefix Sorunu (Double Prefix Issue)**
> Eğer GLPI ayarlarında "Notification subject tag" (Prefix) aktif ise (Varsayılan: Aktif), aşağıdaki subject'lerdeki `[GLPI ###ticket.id##]` kısmını **SİLMELİSİNİZ**.
> Aksi takdirde konu satırı şöyle görünür: `[GLPI #123] [GLPI #123] Yeni Yorum...`
>
> **Çözüm:** Subject satırını sadece `<Eylem>: <Başlık>` olarak kullanın. GLPI otomatik olarak prefix ekleyecektir.

---

## 📧 1. New Ticket Notification Subject

### Türkçe (TR)
**GLPI Prefix Açıksa (Önerilen):**
```
Yeni Ticket: ##ticket.title##
```
**GLPI Prefix Kapalıysa:**
```
[GLPI ###ticket.id##] Yeni Ticket: ##ticket.title##
```

### English (EN)
**If GLPI Prefix Enabled (Recommended):**
```
New Ticket: ##ticket.title##
```
**If GLPI Prefix Disabled:**
```
[GLPI ###ticket.id##] New Ticket: ##ticket.title##
```

---

## 📧 2. Transfer Notification Subject

### Türkçe (TR)
**GLPI Prefix Açıksa:**
```
Transfer: ##ticket.title##
```
**GLPI Prefix Kapalıysa:**
```
[GLPI ###ticket.id##] Transfer: ##ticket.title##
```

### English (EN)
**If GLPI Prefix Enabled:**
```
Transferred: ##ticket.title##
```
**If GLPI Prefix Disabled:**
```
[GLPI ###ticket.id##] Transferred: ##ticket.title##
```

---

## 📧 3. Resolution Notification Subject

### Türkçe (TR)
**GLPI Prefix Açıksa:**
```
Çözüldü: ##ticket.title##
```
**GLPI Prefix Kapalıysa:**
```
[GLPI ###ticket.id##] Çözüldü: ##ticket.title##
```

### English (EN)
**If GLPI Prefix Enabled:**
```
Resolved: ##ticket.title##
```
**If GLPI Prefix Disabled:**
```
[GLPI ###ticket.id##] Resolved: ##ticket.title##
```

---

## 📧 4. Followup Notification Subject

### Türkçe (TR)
**GLPI Prefix Açıksa:**
```
Yeni Yorum: ##ticket.title##
```
**GLPI Prefix Kapalıysa:**
```
[GLPI ###ticket.id##] Yeni Yorum: ##ticket.title##
```

### English (EN)
**If GLPI Prefix Enabled:**
```
New Comment: ##ticket.title##
```
**If GLPI Prefix Disabled:**
```
[GLPI ###ticket.id##] New Comment: ##ticket.title##
```

---

## 📧 5. Assignment Notification Subject

### Türkçe (TR)
**GLPI Prefix Açıksa:**
```
Atama: ##ticket.title##
```
**GLPI Prefix Kapalıysa:**
```
[GLPI ###ticket.id##] Atama: ##ticket.title##
```

### English (EN)
**If GLPI Prefix Enabled:**
```
Assigned: ##ticket.title##
```
**If GLPI Prefix Disabled:**
```
[GLPI ###ticket.id##] Assigned: ##ticket.title##
```

---

## 📧 6. Task Notification Subject

### Türkçe (TR)
**GLPI Prefix Açıksa:**
```
Görev: ##ticket.title##
```
**GLPI Prefix Kapalıysa:**
```
[GLPI ###ticket.id##] Görev: ##ticket.title##
```

### English (EN)
**If GLPI Prefix Enabled:**
```
Task: ##ticket.title##
```
**If GLPI Prefix Disabled:**
```
[GLPI ###ticket.id##] Task: ##ticket.title##
```

---

## 📧 7. SLA Warning Notification Subject

### Türkçe (TR)
**GLPI Prefix Açıksa:**
```
⚠️ SLA: ##ticket.title##
```
**GLPI Prefix Kapalıysa:**
```
[GLPI ###ticket.id##] ⚠️ SLA: ##ticket.title##
```

### English (EN)
**If GLPI Prefix Enabled:**
```
⚠️ SLA: ##ticket.title##
```
**If GLPI Prefix Disabled:**
```
[GLPI ###ticket.id##] ⚠️ SLA: ##ticket.title##
```

---

## � 8. Deletion Notification Subject

### Türkçe (TR)
**GLPI Prefix Açıksa:**
```
Silindi: ##ticket.title##
```
**GLPI Prefix Kapalıysa:**
```
[GLPI ###ticket.id##] Silindi: ##ticket.title##
```

### English (EN)
**If GLPI Prefix Enabled:**
```
Deleted: ##ticket.title##
```
**If GLPI Prefix Disabled:**
```
[GLPI ###ticket.id##] Deleted: ##ticket.title##
```

---

## 📋 Özet Tablo (GLPI Prefix AÇIK ise)

| Template | TR Subject (Prefix Otomatik) | EN Subject (Prefix Auto) |
|----------|------------------------------|--------------------------|
| **New Ticket** | `Yeni Ticket: ##ticket.title##` | `New Ticket: ##ticket.title##` |
| **Transfer** | `Transfer: ##ticket.title##` | `Transferred: ##ticket.title##` |
| **Resolution** | `Çözüldü: ##ticket.title##` | `Resolved: ##ticket.title##` |
| **Followup** | `Yeni Yorum: ##ticket.title##` | `New Comment: ##ticket.title##` |
| **Assignment** | `Atama: ##ticket.title##` | `Assigned: ##ticket.title##` |
| **Task** | `Görev: ##ticket.title##` | `Task: ##ticket.title##` |
| **SLA Warning** | `⚠️ SLA: ##ticket.title##` | `⚠️ SLA: ##ticket.title##` |
| **Deletion** | `Silindi: ##ticket.title##` | `Deleted: ##ticket.title##` |

---

## � GLPI Prefix Ayarı Nerede?

1. **Setup > Notifications** menüsüne gidin.
2. **Notification templates** (veya General configuration) altında **Prefix for notifications** ayarını kontrol edin.
3. Eğer burada bir prefix tanımlıysa (örn: `GLPI`), sistem otomatik olarak `[GLPI #123]` ekler.
