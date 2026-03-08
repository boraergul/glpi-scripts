# GLPI Onboarding Orchestrator

Bu proje, yeni bir müşteri (Entity) GLPI'a eklendiğinde yapılması gereken teknik tanımlamaları otomatize eder. Tek bir script üzerinden 5 farklı süreci sırasıyla çalıştırır.

## 🚀 Amaç

Yeni açılan bir Entity için şu adımları standart ve hatasız bir şekilde uygulamak:
1.  **Entity Group Sync:** Entity için destek grubu oluşturulması.
2.  **Email Rules:** Mail alım kurallarının tanımlanması.
3.  **Unknown Domain Rule:** Tanımsız domain kuralının güncellenmesi (yeni entity'i hariç tutmak için).
4.  **SLA Rules:** Incident ve Request'ler için SLA atama kurallarının oluşturulması.
5.  **Business Rules:** Request'ler için ticket atama kurallarının oluşturulması.

## 📦 Çalıştırılan Scriptler ve Sırası

Script (`run_onboarding.py`) aşağıdaki scriptleri belirtilen sırada tetikler:

1.  `entity_group_sync/sync_entity_groups.py`
2.  `rules_email/email_rules.py`
3.  `rules_unknownDomain/create_undefined_domain_rule.py`
4.  `rules_business_sla/create_sla_rules.py`
5.  `rules_business/create_business_rules.py`

> **🔔 Sıralama Mantığı:** 
> Özellikle **1. Adım (Grup)** ve **5. Adım (Business Rules)** arasındaki ilişki kritiktir. 
> Business Rule scripti, ticket'ı bir gruba atayacağı için (Örn: "Ankara Oto > Genel Destek"), bu grubun 1. adımda oluşturulmuş olması zorunludur. Sıralama değiştirilirse atamalar başarısız olabilir.

## 🛠 Kullanım

Scripti `onboarding` dizini içinden çalıştırabilirsiniz.

### 📋 Hazırlık (Zorunlu)
Scripti çalıştırmadan önce, yeni oluşturulan entity'nin SLA seviyesini belirlemek için **`Config/entity_sla_map.json`** dosyasını güncellemelisiniz.

```json
{
    "Mevcut Müşteri": "SLA-GOLD-5X9",
    "Yeni Müşteri Adı": "SLA-PLATINUM-7X24"  <-- Bunu ekleyin
}
```

Eğer bu adım atlanırsa, SLA ve Business Rule kuralları eksik oluşturulabilir.

### 1. Dry-Run (Test Modu)
Herhangi bir değişiklik yapmadan, sadece hangi işlemlerin yapılacağını görmek için:
```bash
python run_onboarding.py
```

### 2. Live Run (Değişiklikleri Uygula)
Tüm alt scriptleri `--force` parametresiyle çalıştırarak değişiklikleri uygulamak için:
```bash
python run_onboarding.py --force
```

## ⚠️ Dikkat Edilmesi Gerekenler

*   **Hata Yönetimi:** Scriptlerden biri hata verirse (Exit Code != 0), süreç durdurulur ve sonraki adımlara geçilmez.
*   **Config:** Tüm scriptler ortak `config.json` dosyasını kullanır.
*   **Bağımlılıklar:** Scriptlerin çalışması için ilgili klasörlerdeki yan dosyaların (`entity_sla_map.json` vb.) güncel olması gerekir.

---
**Son Güncelleme:** 19 Aralık 2025

Hazırlayan : Bora Ergül
