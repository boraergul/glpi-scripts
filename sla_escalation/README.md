# sla_escalation

Açık ticket'ların TTR (Time To Resolve) tüketim yüzdesini izler ve belirlenen eşiklerde **otomatik aksiyon** alır. Süre dolmadan önce uyarır.

---

## 📂 Dosyalar

| Dosya | Açıklama |
|---|---|
| `sla_escalation.py` | Ana script (CLI) |
| `gui_sla_escalation.py` | Grafik arayüz — log canlı görünür |
| `sla_log_YYYYMMDD.csv` | Günlük CSV log — her çalışmada eklenir (otomatik) |

> **Not:** `config.json` gereklidir. Script aşağıdaki sırayla arar: `./config.json` → `../config/config.json` → `../Config/config.json`

---

## 🔄 Eskalasyon Mantığı

```
Açık ticket (status 1-4) + TTR atanmış
       │
       ├── TTR %75 - %89 → ⚠️  Followup uyarısı eklenir (bir kez)
       │
       ├── TTR %90 - %99 → 🔶  Priority +1 yükseltilir + followup (bir kez)
       │
       └── TTR %100+     → 🔴  Priority = Major (6) + followup (bir kez)
```

**Tekrar önleme:** Her ticket'ın followup'larına `[SLA-ESK-75]`, `[SLA-ESK-90]`, `[SLA-ESK-100]` tag'leri eklenir. Script sonraki çalışmada bu tag'leri kontrol ederek aynı eşik için tekrar aksiyon almaz.

---

## 🖥️ GUI Kullanımı

```bash
python gui_sla_escalation.py
```

GUI üzerinden:
- **🔍 Dry-Run** — simüle eder, değişiklik yapmaz
- **⚡ Uygula** — gerçek eskalasyon uygular
- Uyarı / Eskalasyon eşiklerini değiştirebilirsin
- Log satırları renk kodlu: 🔴 İhlal / 🔶 Eskalasyon / 🔵 Uyarı
- Verbose checkbox ile tüm ticket'ları görebilirsin

## 🚀 CLI Kullanımı

```bash
# Dry-run (değişiklik yapmaz, sadece gösterir)
python sla_escalation.py

# Gerçek değişiklikler
python sla_escalation.py --force

# Detaylı çıktı
python sla_escalation.py --force --verbose

# Özel eşikler
python sla_escalation.py --force --warn 70 --escalate 85
```

---

## ⏱️ Cron / Task Scheduler Kurulumu

### Windows Task Scheduler

Her 15 dakikada bir çalıştırmak için:

```
Eylem: python.exe "d:\Projeler\Script\sla_escalation\sla_escalation.py" --force
Tetikleyici: Günlük, 15 dakikada bir tekrarla
```

Veya PowerShell ile kayıt:

```powershell
$action = New-ScheduledTaskAction -Execute "python.exe" `
    -Argument '"d:\Google Drive\Projeler\Script\sla_escalation\sla_escalation.py" --force'
$trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 15) -Once -At (Get-Date)
Register-ScheduledTask -TaskName "GLPI-SLA-Escalation" -Action $action -Trigger $trigger
```

### Linux/macOS Cron

```bash
# Her 15 dakikada bir
*/15 * * * * /usr/bin/python3 /path/to/sla_escalation/sla_escalation.py --force >> /var/log/sla_escalation.log 2>&1
```

---

## 📊 Çıktı Örneği

```
============================================================
  GLPI SLA Eskalasyon  [LIVE]  2026-02-22 20:45:00
  Eşikler: Uyarı=%75 | Eskalasyon=%90 | İhlal=%100
============================================================

[WARN %77.3] Ticket #1042 | ~34dk kaldı | Sunucu erişim sorunu
[ESCALATE %91.8] Ticket #1038 | Prio: Medium → High | Network gecikmesi
[BREACH %103.4] Ticket #1031 | Prio: High → Major | Kritik sistem hatası

============================================================
  Özet:
    Taranan ticket    : 47
    ⚠️  Yeni uyarı     : 1
    🔶 Yeni eskalasyon: 1
    🔴 Yeni ihlal(Major): 1
    ↩️  Atlanan (no TTR): 3
============================================================
```

---

## ⚙️ Yapılandırma

Tüm eşikler CLI parametresiyle değiştirilebilir. Script içindeki sabit değerler:

| Sabit | Varsayılan | Açıklama |
|---|---|---|
| `THRESHOLD_WARN` | 75 | Uyarı eşiği (%) |
| `THRESHOLD_ESCALATE` | 90 | Eskalasyon eşiği (%) |
| `THRESHOLD_BREACH` | 100 | İhlal eşiği (%) |
| `PRIORITY_MAJOR` | 6 | İhlalde atanan öncelik |

---

## 🔗 İlgili Modüller

| Modül | İlişki |
|---|---|
| `rules_business_sla/` | SLA'ları ticket'lara atar (bu script izler) |
| `rules_business_incident_major/` | Manuel Major atama kuralı |

---

**Versiyon:** 1.1
**Son Güncelleme:** 22 Şubat 2026
**Hazırlayan:** Bora Ergül
