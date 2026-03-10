# GLPI Onboarding Orchestrator

Bu modul, GLPI'da yeni bir musteri entity'si acildiktan sonra yapilmasi gereken standart tanimlamalari tek komutta sirayla calistirmak icin hazirlanmis bir orkestratordur.

Amac, yeni entity onboarding surecini tek tek manuel script calistirmadan, kontrollu ve tekrarlanabilir sekilde tamamlamaktir.

## Ne Yapar?

Yeni acilan bir entity icin asagidaki teknik hazirliklari sirayla uygular:

1. **Entity Group Sync:** Entity adina karsilik gelecek destek grubunu olusturur.
2. **Email Rules:** Entity'nin `mail_domain` bilgisine gore mail collector kurallarini olusturur veya gunceller.
3. **Unknown Domain Rule:** Tanimsiz domain kuralini yeni entity yapisina gore gunceller.
4. **SLA Rules:** Incident ve Request ticket'lari icin SLA atama kurallarini olusturur veya gunceller.
5. **Business Rules:** E-posta ile acilan ticket'lar icin kategori, oncelik, SLA ve grup atama kurallarini olusturur veya gunceller.

## Tetiklenme Mantigi

Bu script **GLPI tarafindan otomatik tetiklenmez**. Bir cron, scheduler, webhook veya event listener mekanizmasina bagli degildir.

Onboarding akisinin calisma sekli soyledir:

1. GLPI'da yeni entity olusturulur.
2. Gerekli mapping ve config dosyalari guncellenir.
3. Operator `onboarding.py` scriptini manuel olarak calistirir.
4. Script alt modulleri sirayla cagirir.
5. Bu modullerin GLPI icinde olusturdugu kurallar daha sonra mail geldiginde veya ticket create/update oldugunda otomatik calisir.

Yani bu modulun kendisi manuel bir hazirlik ve orkestrasyon katmanidir. Asil otomatik davranis, onboarding sonrasinda olusan GLPI kurallari tarafindan saglanir.

## Calistirilan Scriptler ve Sirasi

Ana script dosyasi: `onboarding.py`

Script asagidaki modulleri belirtilen sirada calistirir:

1. `../entity_group_sync/sync_entity_groups.py`
2. `../rules_email/email_rules.py`
3. `../rules_unknownDomain/create_undefined_domain_rule.py`
4. `../rules_business_sla/create_sla_rules.py`
5. `../rules_business/create_business_rules.py`

> **Siralama neden onemli?**
>
> Grup olusturma adimi ile business rule adimi arasinda dogrudan bagimlilik vardir.
> Business rule'lar ticket'i ilgili teknik gruba atayabildigi icin bu grubun once olusturulmus olmasi gerekir.
> Bu nedenle siralama degistirilmemelidir.

## Kullanim

Script `onboarding` klasoru icinden calistirilmalidir.

### Calistirmadan Once

Yeni entity icin SLA segmenti tanimlanmalidir. Bunun icin ilgili `entity_sla_map.json` dosyasina yeni kayit eklenmelidir.

Ornek:

```json
{
    "Mevcut Musteri": "SLA-GOLD-5X9",
    "Yeni Musteri Adi": "SLA-PLATINUM-7X24"
}
```

Bu mapping eklenmezse SLA ve business rule tarafinda eksik veya hatali atamalar olusabilir.

Ayrica:

- Entity GLPI'da gercekten olusturulmus olmalidir.
- Email rule uretilecekse entity uzerinde `mail_domain` bilgisi tanimli olmalidir.
- Alt modullerin kullandigi ortak `config.json` erisilebilir olmalidir.

### 1. Dry-Run

Varsayilan calisma sekli dry-run'dir. Alt scriptler gercek degisiklik yapmadan ne yapacaklarini gosterir.

```bash
python onboarding.py
```

### 2. Live Run

Gercek degisiklikleri uygulamak icin tum alt scriptler `--force` ile calistirilir:

```bash
python onboarding.py --force
```

## Calisma Bicimi

`onboarding.py`, her alt scripti kendi klasorunde `subprocess` ile calistirir. Boylece her modul kendi config ve relatif dosya yapisiyla uyumlu sekilde calisir.

Davranis kurallari:

- Varsayilan mod `dry-run`'dir
- `--force` verilirse tum alt scriptlere `--force` parametresi aktarilir
- Her adim sirayla calisir
- Bir adim hata verirse surec durdurulur
- Hata durumunda sonraki adimlara gecilmez

Bu yaklasim, onboarding sirasinda yari kalmis veya tutarsiz kurulumlari azaltmak icin tercih edilmistir.

## Onboarding Sonrasi Otomatik Davranis

Onboarding tamamlandiktan sonra otomasyon zinciri GLPI icinde su sekilde calisir:

1. Belirli domain'den mail gelir.
2. `rules_email` ile olusturulmus mail collector kurali dogru entity'yi atar.
3. Ticket olusturulunca veya guncellenince `rules_business_sla` ile olusturulan SLA kurallari devreye girer.
4. Ardindan `rules_business` ile olusturulan business rule'lar kategori, oncelik, SLA ve grup atamalarini tamamlar.

Bu nedenle onboarding scripti tek seferlik kurulum akisidir; surekli calisan servis degildir.

## Dikkat Edilmesi Gerekenler

- **Manuel tetikleme:** Yeni entity acildiginda scriptin ayrica calistirilmasi gerekir.
- **Guncel script adi:** Giris noktasi `run_onboarding.py` degil, `onboarding.py` dosyasidir.
- **Hata yonetimi:** Alt scriptlerden biri hata verirse tum surec durur.
- **Config bagimliligi:** Tum moduller ortak GLPI API config bilgilerine ihtiyac duyar.
- **Mapping bagimliligi:** `entity_sla_map.json` gibi yan dosyalar guncel degilse bazi kurallar eksik uretilebilir.
- **Dry-run onerisi:** Ilk calistirmada once dry-run ile kontrol edilmesi tavsiye edilir.

## Ozet

Bu modulun gorevi:

- yeni entity acildiktan sonra gerekli otomasyon kurallarini topluca hazirlamak,
- bagimli modulleri dogru sirayla calistirmak,
- sonrasinda GLPI'nin kendi kural motorunun otomatik calismasini mumkun hale getirmektir.

---
**Son Guncelleme:** 10 Mart 2026

Hazirlayan : Bora Ergul
