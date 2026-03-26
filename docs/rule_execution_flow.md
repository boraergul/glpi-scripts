# GLPI Rule Execution Flow & Logic

Bu doküman, GLPI otomasyon sistemindeki kural scriptlerinin (Python) çalışma sırasını, isimlendirme standartlarını ve teknik mantığını açıklar.

## 🔄 Genel Akış (Lifecycle)

Sistemdeki kurallar iki ana aşamada çalışır:
1. **RuleMailCollector (E-posta Kuralları)**: E-posta geldiğinde, ticket henüz oluşmadan çalışır. Temel amacı doğru **Entity (Birim)** atamasını yapmaktır.
2. **RuleTicket (İş Kuralları)**: Ticket oluştuktan sonra çalışır. Kategori, grup, öncelik ve **SLA** atamalarını yapar.

---

## 📊 Kural Uygulama Tablosu

| Sıra | Aşama | Script | Kural Adı Örneği | Amaç / Mantık | Ranking |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | Mail | `rules_email.py` | `Auto-Email-Ankara-Oto` | Gönderen domainine göre doğru Entity'yi (Müşteriyi) atar. | 1 |
| **2** | Mail | `rules_unknowndomain.py` | `Tanımsız-Domain` | Bilinmeyen domain'lerden gelen e-postaları "Genel destek" birimine yönlendirir. | 2 |
| **3** | Ticket | `rules_business_incident_major.py` | `Auto-Major-Incident-Ankara-Yem` | Major (P6) öncelikli olayları anında "Major Incident" ekibine ve P1 SLA'ya atar. | 10 |
| **4** | Ticket | `rules_business_sla.py` | `Auto-SLA-Dorçe-Priority-P1-Incident` | Entity, Öncelik ve Tip (Incident/Request) bazlı SLA (TTO/TTR) ataması yapar. | 15 |
| **5** | Ticket | `rules_business_itilcategory_assign.py` | `Auto-Category-Security` | Seçilen ITIL kategorisine göre ilgili teknik grubu (Network, Güvenlik vb.) atar. | 20 |
| **6** | Ticket | `rules_business.py` | `Auto-BR-Ankara-Oto` | E-posta ile gelen ve Incident olmayan (Request vb.) biletlere varsayılan kategori ve SLA atar. | 1 |

---

## 🛠️ Teknik Detaylar

### 📌 İsimlendirme Standartları
*   Tüm kural isimleri **kebab-case** (tire ile ayrılmış) formatındadır.
*   Boşluklar otomatik olarak `-` karakterine çevrilir.
*   Prefixler: `Auto-Email-`, `Auto-SLA-`, `Auto-BR-`, `Auto-Category-`, `Auto-Major-`.

### 📌 Tetikleyiciler (Triggers)
*   **Condition 3 (Add/Update)**: Kurallar hem yeni kayıt oluşturulduğunda hem de mevcut kayıt güncellendiğinde tetiklenecek şekilde yapılandırılmıştır.
*   **Recursive**: Tüm kurallar "Alt varlıklar dahil" (Recursive) olarak Root Entity seviyesinde tanımlanır.

### 📌 Orchestrator
Yeni bir Entity tanımlandığında tüm bu kuralların sırayla oluşturulması/güncellenmesi için `onboarding/onboarding.py` scripti kullanılır.

```bash
# Tüm kuralları yeni entity'lere göre güncellemek için:
python onboarding/onboarding.py --force
```

---
**Son Güncelleme:** 25 Mart 2026  
**Hazırlayan:** Bora Ergül
