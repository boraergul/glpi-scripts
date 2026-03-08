# osTicket → GLPI Değişken Dönüşüm Tablosu

Bu dokümant, osTicket notification template'lerindeki değişkenlerin GLPI karşılıklarını gösterir.

## 📋 Değişken Karşılıkları

| osTicket Değişkeni | GLPI Değişkeni | Açıklama |
|-------------------|----------------|----------|
| `%{ticket.number}` | `##ticket.id##` | Ticket numarası |
| `%{ticket.dept.name}` | `##ticket.assignedgroup##` | Departman/Grup adı |
| `%{recipient.name}` | `##ticket.user.name##` | Alıcı adı |
| `%{staff.name.short}` | `##ticket.assigneduser##` | Atanan personel adı |
| `%{ticket.subject}` | `##ticket.title##` | Ticket başlığı |
| `%{ticket.topic}` | `##ticket.category##` | Ticket kategorisi |
| `%{ticket.create_date}` | `##ticket.creationdate##` | Oluşturulma tarihi |
| `%{ticket.due_date}` | `##ticket.duedate##` | Bitiş tarihi |
| `%{ticket.status}` | `##ticket.status##` | Ticket durumu |
| `%{ticket.priority}` | `##ticket.priority##` | Öncelik |
| `%{ticket.url}` | `##ticket.url##` | Ticket URL'i |
| `%{recipient.email}` | `##ticket.user.email##` | Kullanıcı e-posta |
| `%{staff.email}` | `##ticket.assigneduser##` | Personel e-posta (GLPI'da ayrı değişken yok) |
| `%{ticket.message}` | `##ticket.description##` | Ticket mesajı/açıklaması |
| `%{response.message}` | `##followup.description##` | Yanıt mesajı |
| `%{ticket.team}` | `##ticket.assignedgroup##` | Takım/Grup |

## 🔄 Dönüştürülmüş Template Örnekleri

### Örnek 1: Transfer Bildirimi

**osTicket:**
```
Subj: Destek Talebi#%{ticket.number} transfer - %{ticket.dept.name}
Body: Merhaba %{recipient.name},
#%{ticket.number} numaralı talep %{staff.name.short} tarafından 
%{ticket.dept.name} bölümüne atandı
```

**GLPI:**
```
Subj: Destek Talebi ###ticket.id## transfer - ##ticket.assignedgroup##
Body: Merhaba ##ticket.user.name##,
###ticket.id## numaralı talep ##ticket.assigneduser## tarafından 
##ticket.assignedgroup## bölümüne atandı
```

### Örnek 2: Yeni Ticket Bildirimi

**osTicket:**
```
Subj: Yeni Destek Talebi #%{ticket.number}
Body: Sayın %{recipient.name},
%{ticket.subject} konulu talebiniz alınmıştır.
Talep No: %{ticket.number}
Durum: %{ticket.status}
```

**GLPI:**
```
Subj: Yeni Destek Talebi ###ticket.id##
Body: Sayın ##ticket.user.name##,
##ticket.title## konulu talebiniz alınmıştır.
Talep No: ##ticket.id##
Durum: ##ticket.status##
```

### Örnek 3: Yanıt Bildirimi

**osTicket:**
```
Subj: Yanıt: Destek Talebi #%{ticket.number}
Body: Merhaba %{recipient.name},
%{staff.name.short} talebinize yanıt verdi:
%{response.message}
```

**GLPI:**
```
Subj: Yanıt: Destek Talebi ###ticket.id##
Body: Merhaba ##ticket.user.name##,
##followup.author## talebinize yanıt verdi:
##followup.description##
```

## ⚠️ Önemli Farklılıklar

### 1. Değişken Formatı
- **osTicket:** `%{değişken.adı}` formatı kullanır
- **GLPI:** `##değişken.adı##` formatı kullanır

### 2. Personel Bilgileri
- **osTicket:** `%{staff.name.short}`, `%{staff.name.full}` gibi çeşitli formatlar
- **GLPI:** `##ticket.assigneduser##` tek format (tam ad)

### 3. Departman vs Grup
- **osTicket:** "Department" (Departman) kavramı kullanır
- **GLPI:** "Group" (Grup) kavramı kullanır

### 4. Yanıt/Takip
- **osTicket:** `%{response.message}` yanıt için
- **GLPI:** `##followup.description##` takip için

### 5. Entity Kavramı
- **osTicket:** Entity kavramı yok
- **GLPI:** `##ticket.entity##` ile çoklu kuruluş desteği var

## 🔧 GLPI'da Ek Özellikler

GLPI'da osTicket'ta olmayan bazı değişkenler:

| GLPI Değişkeni | Açıklama |
|----------------|----------|
| `##ticket.entity##` | Entity (Kuruluş) adı |
| `##ticket.sla.tto##` | Time To Own (Müdahale süresi) |
| `##ticket.sla.ttr##` | Time To Resolve (Çözüm süresi) |
| `##ticket.impact##` | Etki seviyesi |
| `##ticket.urgency##` | Aciliyet seviyesi |
| `##ticket.location##` | Lokasyon |
| `##task.description##` | Görev açıklaması |
| `##solution.description##` | Çözüm açıklaması |

## 📝 Dönüşüm İpuçları

1. **Toplu Değiştirme:** Metin editöründe "Find & Replace" kullanarak:
   - `%{` → `##`
   - `}` → `##`
   - `.` → `.` (aynı kalır)

2. **Manuel Kontrol:** Otomatik dönüşümden sonra mutlaka manuel kontrol edin:
   - `staff.name.short` → `ticket.assigneduser`
   - `dept.name` → `ticket.assignedgroup`
   - `recipient.name` → `ticket.user.name`

3. **Test Etme:** GLPI'da test notification göndererek değişkenlerin doğru çalıştığını kontrol edin

## 🎯 Yaygın Kullanım Senaryoları

### Senaryo 1: Ticket Ataması
```
osTicket: %{staff.name.short} tarafından %{ticket.dept.name} bölümüne atandı
GLPI:     ##ticket.assigneduser## tarafından ##ticket.assignedgroup## bölümüne atandı
```

### Senaryo 2: Kullanıcı Bilgilendirme
```
osTicket: Sayın %{recipient.name}, #%{ticket.number} numaralı talebiniz
GLPI:     Sayın ##ticket.user.name##, ###ticket.id## numaralı talebiniz
```

### Senaryo 3: Durum Güncelleme
```
osTicket: Talebinizin durumu %{ticket.status} olarak güncellendi
GLPI:     Talebinizin durumu ##ticket.status## olarak güncellendi
```

## 📚 Ek Kaynaklar

- [GLPI Notification Variables Reference](glpi_variables_reference.md)
- [osTicket Email Templates Documentation](https://docs.osticket.com/en/latest/Admin/Emails/Templates.html)
- [GLPI Official Documentation](https://glpi-install.readthedocs.io/)

## ✅ Dönüşüm Kontrol Listesi

Bir osTicket template'ini GLPI'ya dönüştürürken:

- [ ] Tüm `%{` ve `}` işaretlerini `##` ile değiştir
- [ ] `staff.name.short` → `ticket.assigneduser` dönüşümünü yap
- [ ] `dept.name` → `ticket.assignedgroup` dönüşümünü yap
- [ ] `recipient.name` → `ticket.user.name` dönüşümünü yap
- [ ] `ticket.number` → `ticket.id` dönüşümünü yap
- [ ] GLPI'da test notification gönder
- [ ] Tüm değişkenlerin doğru değerlerle değiştiğini kontrol et
- [ ] HTML ve Text versiyonlarının her ikisini de oluştur
