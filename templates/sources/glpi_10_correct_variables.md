# GLPI 10.0.x Doğru Notification Değişkenleri

GLPI 10.0.19 için test edilmiş ve çalışan değişkenler.

## ✅ Temel Ticket Değişkenleri

| Kullanım | Doğru Değişken | Açıklama |
|----------|----------------|----------|
| Ticket ID | `##ticket.id##` | Ticket numarası |
| Ticket Başlık | `##ticket.title##` | Ticket başlığı |
| Ticket Açıklama | `##ticket.content##` | Ticket içeriği (description yerine) |
| Ticket URL | `##ticket.url##` | Ticket linki |
| Ticket Durum | `##ticket.status##` | Durum |
| Öncelik | `##ticket.priority##` | Öncelik seviyesi |
| Kategori | `##ticket.itilcategory##` | ITIL Kategorisi |
| Entity (Tam Yol) | `##ticket.entity##` | Entity tam hiyerarşi (örn: Root Entity > Ultron Bilişim) |
| Entity (Sadece Ad) | `##ticket.shortentity##` | Sadece entity adı (örn: Ultron Bilişim) |
| Lokasyon | `##ticket.location##` | Lokasyon |

## 👤 Kullanıcı Değişkenleri (GLPI 10.0)

### Talep Eden (Requester)

#### Doğrudan Kullanım
| Kullanım | Doğru Değişken | Açıklama |
|----------|----------------|----------|
| Talep Eden Adı (Liste) | `##ticket.authors##` | Talep eden kişi(ler) - Liste formatında |
| Alıcı Adı | `##recipient.name##` | Mail alan kişinin adı |
| Alıcı Email | `##recipient.email##` | Mail alan kişinin email'i |

#### FOREACH ile Kullanım (Detaylı Bilgi İçin)
`##author.*##` değişkenleri **FOREACH döngüsü içinde** kullanılmalıdır:

```
##FOREACHauthors##
Ad Soyad:       ##author.name##
E-posta:        ##author.email##
Telefon:        ##author.phone##
Telefon 2:      ##author.phone2##
Mobil:          ##author.mobile##
Kategori:       ##author.category##
Lokasyon:       ##author.location##
Ünvan:          ##author.title##
##ENDFOREACHauthors##
```

> **ÖNEMLİ:** 
> - `##ticket.authors##` → Doğrudan kullanılabilir, liste formatında
> - `##author.name##`, `##author.email##`, vb. → **FOREACH döngüsü içinde** kullanılmalı
> - GLPI 10.0'da `##ticket.user.name##` artık kullanılmıyor!

### Atanan Kullanıcı/Grup
| Kullanım | Doğru Değişken | Açıklama |
|----------|----------------|----------|
| Atanan Teknisyen | `##ticket.assigntousers##` | Atanan kullanıcı(lar) |
| Atanan Grup (Tam Yol) | `##ticket.assigntogroups##` | Atanan grup(lar) - Tam hiyerarşi |
| Atanan Grup (Sadece Ad) | `##FOREACHassigntogroups####assigntogroups.name####ENDFOREACHassigntogroups##` | Sadece grup adı |

> **ÖNEMLİ:** GLPI 10.0'da çoğul form kullanılır: `assigntousers` ve `assigntogroups`
> 
> **İPUCU:** `##ticket.assigntogroups##` "Entity > Parent > Group" şeklinde tam yol gösterir. Sadece grup adını göstermek için FOREACH kullanın.

## 📅 Tarih Değişkenleri

| Kullanım | Doğru Değişken |
|----------|----------------|
| Oluşturulma | `##ticket.creationdate##` |
| Son Güncelleme | `##ticket.lastupdate##` |
| Çözüm Tarihi | `##ticket.solvedate##` |
| Kapanma Tarihi | `##ticket.closedate##` |

## ⏱️ SLA Değişkenleri

| Kullanım | Doğru Değişken | Açıklama |
|----------|----------------|----------|
| TTO SLA | `##ticket.sla_tto##` | SLA / Time to Own |
| TTR SLA | `##ticket.sla_ttr##` | SLA / Time to Resolve |

> **ÖNEMLİ:** GLPI 10.0'da `##ticket.sla.tto##` değil, `##ticket.sla_tto##` kullanılır (nokta değil, alt çizgi)!

## 💬 Timeline (Takip/Görev/Çözüm)

### FOREACH ile Kullanım

```
##FOREACHtimelineitems##
Yazar: ##timelineitems.author##
Tarih: ##timelineitems.date##
İçerik: ##timelineitems.description##
##ENDFOREACHtimelineitems##
```

## 🔧 Transfer Notification için Doğru Değişkenler

Transfer bildirimi için özel değişkenler:

| Kullanım | Doğru Değişken | Açıklama |
|----------|----------------|----------|
| Transfer Eden | `##task.author##` veya `##update.author##` | Transfer işlemini yapan kişi |
| Yeni Grup | `##ticket.assigntogroups##` | Yeni atanan grup |
| Eski Grup | `##task.oldvalue##` (özel durumlar için) | Eski grup |

## 📝 Örnek: Transfer Notification Template

### Subject:
```
[GLPI] Ticket ##ticket.id## - ##ticket.assigntogroups## bölümüne atandı
```

### Body (Text):
```
Merhaba ##recipient.name##,

##ticket.id## numaralı talep ##ticket.assigntogroups## bölümüne atandı.

Ticket Başlığı: ##ticket.title##

Sözleşmeli müşterilerimiz için sözleşme kapsamındaki SLA sürelerine uygun 
olarak dönüş sağlanmaktadır, sözleşmeniz yok ise ilgili departmandaki 
uzmanlarımız sizlerle ilk müsait olduklarında iletişime geçecektir.

Anlayışınız için teşekkür ederiz.

Ticket URL: ##ticket.url##

Ultron Yardım Masası
```

## 🎯 Koşullu Kullanım (IF)

```
##IFticket.assigntousers##
Atanan Teknisyen: ##ticket.assigntousers##
##ENDIFticket.assigntousers##
```

## ⚠️ Yaygın Hatalar ve Çözümleri

| ❌ Yanlış | ✅ Doğru | Not |
|----------|---------|-----|
| `##ticket.user.name##` | `##author.name##` | GLPI 10.0'da değişti |
| `##ticket.user.email##` | `##author.email##` | GLPI 10.0'da değişti |
| `##ticket.user.phone##` | `##author.phone##` | GLPI 10.0'da değişti |
| `##ticket.assigneduser##` | `##ticket.assigntousers##` | Çoğul form |
| `##ticket.assignedgroup##` | `##ticket.assigntogroups##` | Çoğul form |
| `##ticket.description##` | `##ticket.content##` | İsim değişikliği |
| `##ticket.category##` | `##ticket.itilcategory##` | Tam isim |
| `##ticket.sla.tto##` | `##ticket.sla_tto##` | Nokta yerine alt çizgi |
| `##ticket.sla.ttr##` | `##ticket.sla_ttr##` | Nokta yerine alt çizgi |
| `##ticket.updatedate##` | `##ticket.lastupdate##` | İsim değişikliği |

## 🔍 Değişkenleri Test Etme

GLPI'da doğru değişkenleri görmek için:

1. **Setup > Notifications > Notification templates**
2. Herhangi bir template'i açın
3. **Available tags** sekmesine tıklayın
4. Tüm kullanılabilir değişkenleri göreceksiniz

## 📚 Referans

- GLPI 10.0 Documentation: https://glpi-install.readthedocs.io/
- Notification Template Tags: Setup > Notifications > Notification templates > Available tags
