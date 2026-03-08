# Project Logbook

| Date | Action | Description | Notes |
|------|--------|-------------|-------|
| 2026-02-26 | Setup | Initialized project governance files (`project.md`, `logbook.md`, `memory.md`). | Following `gemini.md` guardrails. |
| 2026-02-26 | Migration | Completed SLA Report plugin migration to GLPI 11. | Included KPIs, Charts, TR localization. |
| 2026-02-26 | Fix | Fixed sorting redirect and CSV export bugs. | Relative URLs used for sorting. |
| 2026-02-26 | Update | Updated version to 1.0.1 and author to Bora Ergül. | |
| 2026-02-26 | Docs | Refactored `project.md` and `plan.md` | **What**: Updated headers and structure. **Why**: To align with `GEMINI.md` rules. **How**: Changed English headers to Turkish protocol terms. |
| 2026-02-26 | Docs | Created `slareport/README.md` | **What**: User documentation for the new plugin. **Why**: To fulfill the "storefront" requirement for new project components. **How**: Documented installation and features. |
| 2026-02-26 | Dev | Added Plugin Localization (TR/EN) | **What**: Created `locales/` directory with `tr_TR.php` and `en_GB.php`. **Why**: To provide multi-language support as promised in documentation. **How**: Added translation mappings and registered the language domain in `setup.php`. |
| 2026-03-03 | Protokol Uyumu | Yönetim dosyaları `docs/` altına taşındı ve `plan.md` güncellendi. | `MEMORY[user_global]` kurallarına uyum sağlandı. |
