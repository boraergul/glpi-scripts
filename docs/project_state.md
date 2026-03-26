# Project State: GLPI Automation & Integration Scripts

## 🏗️ Architecture & Technical Design
A centralized repository for GLPI maintenance, automation, and reporting scripts. The repo follows a modular structure where each directory represents a specific functional area.

### Tech Stack
- **Languages**: Python 3.x, PHP 8.x
- **Frontend**: Vanilla JavaScript (ES6+), CSS3, HTML5, Chart.js
- **Database**: MariaDB/MySQL (GLPI Database)
- **API**: GLPI REST API

### Key Modules
- **`slareport` (Plugin)**: GLPI 11 compatible plugin for visual SLA breach reporting.
- **`sla_escalation`**: Proactive TTR/TTO monitoring and multi-tier escalation script.
- **`reports_sla`**: Flask-based API and dashboard for historical SLA compliance analysis.
- **`templates_export_import`**: Advanced tools for transferring GLPI notification templates between environments.
- **`glpi_backup`**: Automated entity, group, and ITIL category backup/restore system.
- **`notifications_export_import`**: Focused tools for notification settings migration.

---

## 💾 Unified Memory (Technical Debt & Rules)

### GLPI 11 Compatibility
- **Schema Changes**: `ttr_is_exceeded` and `tto_is_exceeded` columns are removed in GLPI 11. Manual calculation in `report.class.php` is required.
- **CSRF Protection**: Requires `_glpi_csrf_token` in all POST requests.
- **Localization**: UI components default to Turkish (TR) with support for GLPI's internal translation system.

### Standards & Quirks
- **CSV Encoding**: Use UTF-8 BOM (`chr(0xEF).chr(0xBB).chr(0xBF)`) for Excel compatibility with Turkish characters.
- **JS Scoping**: Use `addEventListener` and `window` assignments instead of inline scripts.
- **Chart.js**: Currently using CDN for loading.
### Business Logic & Rules
- **Rule Ordering**: 
    1. **Mail Collector Rules**: `rules_email.py` (Rank 1), `rules_unknowndomain.py` (Rank 2).
    2. **Business Rules**: `rules_business_incident_major.py` (Rank 10), `rules_business_sla.py` (Rank 15), `rules_business_itilcategory_assign.py` (Rank 20).
- **Naming Convention**: All rules follow standard `Auto-[Type]-[Entity]-[Priority]` kebab-case naming.
- **SLA Calculation**: Tickets exceeding 100% TTR are automatically set to Major (6) priority.
- **Detailed Flow**: See [GLPI Rule Execution Flow](file:///d:/Google%20Drive/Projeler/Script/docs/rule_execution_flow.md) for a full breakdown.

---

## 🪵 Chronological Work Log

| Date | Action | Description |
|------|--------|-------------|
| 2026-02-26 | Setup | Initialized project governance files. |
| 2026-02-26 | Migration | Completed SLA Report plugin migration to GLPI 11. |
| 2026-02-26 | Fix | Fixed sorting redirect and CSV export bugs. |
| 2026-02-26 | Update | Updated version to 1.0.1 and author to Bora Ergül. |
| 2026-03-03 | Protocol | Documentation moved to `docs/` and aligned with protocol. |
| 2026-03-08 | Consolidation| Merged `project.md`, `memory.md`, and `logbook.md` into `project_state.md`. |
| 2026-03-10 | Maintenance | Reverted "target name resolution" in `notifications_export_import` to standardize CSV structure. |
| 2026-03-10 | Export      | Successfully exported 278 notifications from ITSM-PROD to CSV. |

---

## 🐞 Critical Bugs & Known Issues
- **Sorting Redirect**: `$_SERVER['PHP_SELF']` can cause redirects to `/front/central.php`. Use relative query strings instead.
- **Export Variables**: Initialization order in `index.php` is critical to avoid "Undefined variable" errors during CSV export.
