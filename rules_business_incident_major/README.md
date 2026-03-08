# Major Incident Rules

Bu modül, Major Incident (Öncelikli Olay) biletleri için özel iş kurallarını yönetir.

## Amaç
Kritik seviyedeki (Priority: Major) biletlerin:
1.  Hemen ilgili özel ekibe (**Major Incident Ekibi**) atanmasını,
2.  En sıkı SLA sürelerinin (**P1: Fastest**) otomatik tanımlanmasını sağlar.

## Çalışma Mantığı
Script (`rules_business_incident_major.py`), `entity_sla_map.json` dosyasındaki her Entity için GLPI üzerinde bir "Business Rule Ticket" oluşturur veya günceller.

### Kural Kriterleri:
*   **Kategori:** Major Incident (ID: 229)
*   **Öncelik:** Major (ID: 6)
*   **Entity:** İlgili Entity (Örn: Çiftay)

### Kural Aksiyonları:
*   **Gruba Ata (Teknisyen Grubu):** Ultron Bilişim > Teknik Ekipler > Major Incident Ekibi (ID: 45)
*   **SLA TTO Ata:** Entity'nin hizmet seviyesine (SLA-GOLD vb.) ait **P1** TTO süresi.
*   **SLA TTR Ata:** Entity'nin hizmet seviyesine (SLA-GOLD vb.) ait **P1** TTR süresi.

### Önemli Özellikler
*   **Duplicate Check (Tekrar Kontrolü):** Script, GLPI Search API kullanarak "Auto-Major-Incident" adıyla başlayan kuralları tarar. Eğer kural zaten varsa **yeni oluşturmak yerine günceller**.
*   **Grup Ataması:** Atama işlemi `groups_id_assign` (Technician Group) alanı üzerinden yapılır. "Observer" veya "Requester" grubu etkilenmez.

## Kullanım

**Kuru Çalıştırma (Dry Run):** Değişiklik yapmadan simülasyon yapar.
```bash
python rules_business_incident_major.py
```

**Canlı Çalıştırma:** Kuralları GLPI'da oluşturur/günceller.
```bash
python rules_business_incident_major.py --force
```

## Özellikler (v2.4)
- ✅ **Timeout Koruması:** Tüm API çağrılarında 30sn timeout
- ✅ **Duplicate Prevention:** Range parametresi (0-5000) ile güvenli silme
- ✅ **Search API:** Geliştirilmiş duplicate detection
- ✅ **Güncelleme Modu:** Mevcut kuralları güvenli şekilde günceller
- ✅ **Standardize Naming:** Hyphen-only format (`Auto-Major-Incident-Entity-Name`)
- ✅ **Space Handling:** Entity adlarındaki boşluklar otomatik olarak tire ile değiştirilir

---
**Versiyon:** 2.5  
**Son Güncelleme:** 26 Aralık 2024

**Değişiklikler (v2.5):**
- ✅ **Add/Update Trigger:** Condition 3 ile hem oluşturma hem güncelleme anında tetiklenir
