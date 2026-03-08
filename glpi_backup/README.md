# GLPI Backup & Recovery Scripts

Bu dizin, GLPI sunucuları arasında veri taşımak veya mevcut sistemi yedeklemek için kullanılan Python scriptlerini içerir.

## 📂 Modüller

Proje, taşınacak veri tipine göre alt dizinlere ayrılmıştır:

| Dizin | Açıklama |
|---|---|
| [`export_entities/`](file:///d:/Google%20Drive/Projeler/Script/glpi_backup/export_entities) | Birim (Entity) yapısını dışa aktarır. |
| [`import_entities/`](file:///d:/Google%20Drive/Projeler/Script/glpi_backup/import_entities) | Birim (Entity) yapısını içe aktarır. |
| [`export_groups/`](file:///d:/Google%20Drive/Projeler/Script/glpi_backup/export_groups) | Kullanıcı gruplarını dışa aktarır. |
| [`import_groups/`](file:///d:/Google%20Drive/Projeler/Script/glpi_backup/import_groups) | Kullanıcı gruplarını içe aktarır. |
| [`export_itil_categories/`](file:///d:/Google%20Drive/Projeler/Script/glpi_backup/export_itil_categories) | ITIL kategorilerini dışa aktarır. |
| [`import_itil_categories/`](file:///d:/Google%20Drive/Projeler/Script/glpi_backup/import_itil_categories) | ITIL kategorilerini içe aktarır. |
| [`export_slmsla/`](file:///d:/Google%20Drive/Projeler/Script/glpi_backup/export_slmsla) | SLM/SLA ve takvim tanımlarını dışa aktarır. |
| [`import_slmsla/`](file:///d:/Google%20Drive/Projeler/Script/glpi_backup/import_slmsla) | SLM/SLA ve takvim tanımlarını içe aktarır. |

## 🚀 Genel Kullanım

1. **Kaynak Seçimi:** İlgili `export_*` dizinine gidip `config_source.json` dosyasını düzenleyin.
2. **Dışa Aktarma:** Scripti çalıştırarak `.json` çıktısını alın.
3. **Hedef Seçimi:** İlgili `import_*` dizinine gidip `config_target.json` dosyasını düzenleyin.
4. **İçe Aktarma:** `.json` dosyasını import dizinine kopyalayıp import scriptini çalıştırın.

## 🔧 Gereksinimler

- Python 3.x
- `requests` kütüphanesi
- GLPI REST API erişimi

---

**Son Güncelleme:** 2026-03-08
**Hazırlayan:** Bora Ergül
