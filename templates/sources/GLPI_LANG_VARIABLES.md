# GLPI ##lang.*## Değişkenleri Kullanımı

Bu doküman, GLPI'nin varsayılan "Tickets" template'inden öğrenilen `##lang.*##` değişkenlerinin kullanımını açıklar.

## 📌 `##lang.*##` Nedir?

`##lang.*##` değişkenleri **etiket/label** gösterir, **değer** göstermez. GLPI'nin dil ayarına göre otomatik olarak çevrilir.

## 🎯 Kullanım Amacı

### ✅ Doğru Kullanım: Dinamik Etiketler
GLPI'nin dil ayarına göre etiketlerin otomatik çevrilmesini sağlar.

```plaintext
##lang.ticket.title## : ##ticket.title##
```

**Sonuç:**
- Türkçe GLPI: `Başlık : deneme ticket`
- İngilizce GLPI: `Title : deneme ticket`

### ❌ Yanlış Kullanım: Sabit Türkçe Etiketler
Eğer etiketleriniz zaten sabit Türkçe ise, `##lang.*##` kullanmanıza gerek yok.

```plaintext
Konu: ##ticket.title##  ← Daha basit ve okunabilir
```

## 📋 GLPI Varsayılan Template Örneği

GLPI'nin "Tickets" template'i 20 farklı notification tarafından kullanılır ve `##lang.*##` yoğun kullanır:

```plaintext
##lang.ticket.title## : ##ticket.title##
##lang.ticket.status## : ##ticket.status##
##lang.ticket.priority## : ##ticket.priority##
##lang.ticket.creationdate## : ##ticket.creationdate##
```

## 🔍 Önemli Örnekler

### 1. Durum Kontrolü (storestatus)
```plaintext
##IFticket.storestatus=5##
  Ticket çözüldü!
  ##lang.ticket.solvedate## : ##ticket.solvedate##
##ENDIFticket.storestatus##
```

**Durum Kodları:**
- `5` = Solved (Çözüldü)
- `6` = Closed (Kapatıldı)

### 2. ELSE Kullanımı
```plaintext
##IFticket.storestatus=5##
  ##lang.ticket.url## : ##ticket.urlapprove##
##ELSEticket.storestatus##
  ##lang.ticket.url## : ##ticket.url##
##ENDELSEticket.storestatus##
```

### 3. Timeline Items (FOREACH)
```plaintext
##FOREACHtimelineitems##
[##timelineitems.date##]
##lang.timelineitems.author## ##timelineitems.author##
##lang.timelineitems.description## ##timelineitems.description##
##ENDFOREACHtimelineitems##
```

### 4. Bağlı Cihazlar (Items)
```plaintext
##FOREACHitems##
  ##IFticket.itemtype##
    ##ticket.itemtype## - ##ticket.item.name##
    ##IFticket.item.serial##
      ##lang.ticket.item.serial## : ##ticket.item.serial##
    ##ENDIFticket.item.serial##
  ##ENDIFticket.itemtype##
##ENDFOREACHitems##
```

## 💡 Bizim Yaklaşımımız vs GLPI Varsayılan

### GLPI Varsayılan Template
```plaintext
##lang.ticket.title## : ##ticket.title##
##lang.ticket.status## : ##ticket.status##
##lang.ticket.priority## : ##ticket.priority##
```

**Avantajlar:**
- ✅ Çok dilli destek
- ✅ Tek template, tüm diller

**Dezavantajlar:**
- ❌ Karmaşık ve okunması zor
- ❌ Etiketler ve değerler karışık

### Bizim Custom Template
```plaintext
Konu:           ##ticket.title##
Durum:          ##ticket.status##
Öncelik:        ##ticket.priority##
```

**Avantajlar:**
- ✅ Basit ve okunabilir
- ✅ Türkçe odaklı
- ✅ Bakımı kolay

**Dezavantajlar:**
- ❌ Sadece Türkçe için optimize

## 🎯 Ne Zaman Hangisini Kullanmalı?

### `##lang.*##` Kullanın:
- ✅ Çok dilli ortam (Türkçe + İngilizce kullanıcılar)
- ✅ GLPI'nin varsayılan template'lerini kullanıyorsanız
- ✅ Tek template ile tüm dilleri desteklemek istiyorsanız

### Sabit Etiketler Kullanın:
- ✅ Sadece Türkçe kullanıcılar
- ✅ Özel, okunabilir template'ler istiyorsanız
- ✅ Basitlik ve netlik öncelikliyse

## 📚 Yaygın ##lang.*## Değişkenleri

| Değişken | Türkçe | İngilizce |
|----------|--------|-----------|
| `##lang.ticket.title##` | Başlık | Title |
| `##lang.ticket.status##` | Durum | Status |
| `##lang.ticket.priority##` | Öncelik | Priority |
| `##lang.ticket.creationdate##` | Oluşturulma Tarihi | Creation Date |
| `##lang.ticket.authors##` | Talep Edenler | Requesters |
| `##lang.ticket.assigntousers##` | Atanan Teknisyenler | Assigned to Technicians |
| `##lang.ticket.assigntogroups##` | Atanan Gruplara | Assigned to Groups |
| `##lang.ticket.content##` | İçerik | Description |
| `##lang.ticket.url##` | URL | URL |
| `##lang.ticket.solvedate##` | Çözüm Tarihi | Date Solved |

## 📖 Referans

Tam GLPI varsayılan template için: `glpi_default_tickets_template.txt`

---

**Not:** GLPI'nin "Tickets" template'i 20 farklı notification tarafından kullanılır, bu yüzden çok genel ve kapsamlıdır. Özel ihtiyaçlarınız için custom template'ler oluşturmak daha iyi bir yaklaşımdır.
