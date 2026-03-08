# SLA Report GLPI Plugin

## Proje Mimarisi
A centralized repository for GLPI maintenance, automation, and reporting scripts. The repo follows a modular structure where each directory represents a specific functional area (e.g., `/plugin/slareport` for GLPI extensions, `/sla_escalation` for background monitoring).

## Teknoloji Yığını
- **Languages**: Python 3.x, PHP 8.x
- **Frontend**: Vanilla JavaScript (ES6+), CSS3, HTML5, Chart.js
- **Database**: MariaDB/MySQL (GLPI Database)
- **API**: GLPI REST API

## Önemli Endpoint'ler
- **`slareport` (Plugin)**: GLPI 11 compatible plugin for visual SLA breach reporting.
- **`sla_escalation`**: Proactive TTR/TTO monitoring and multi-tier escalation script.
- **`reports_sla`**: Flask-based API and dashboard for historical SLA compliance analysis.

### 2. Migration & Backup
- **`templates_export_import`**: Advanced tools for transferring GLPI notification templates between environments.
- **`glpi_backup`**: Automated entity, group, and ITIL category backup/restore system.
- **`notifications_export_import`**: Focused tools for notification settings migration.

### 3. Rules & Automation
- **`rules_business_*`**: Specialized scripts for automating business rules (SLAs, categories, incident priority).
- **`entity_group_sync`**: Synchronization logic for entity and group structures.
- **`zabbix_webhook`**: Integration layer for processing Zabbix alerts into GLPI tickets.

### 4. Configuration
- **`config/`**: Centralized configuration management (API tokens, URLs, entity maps).

## İş Kuralları
- **GLPI 11 Compatibility**: All new developments must account for schema changes in GLPI 11 (e.g., removal of `ttr_is_exceeded` column).
- **Localization**: UI components should default to Turkish (TR) with support for GLPI's internal translation system.
- **SLA Calculation**: SLA compliance is calculated manually by comparing ticket solve/own delays against SLA definitions when persistent columns are absent.
- **Escalation Priority**: Tickets exceeding 100% TTR are automatically set to Major (6) priority.

## Versioning
- Initial consolidation: 1.0.0
- SLA Report Refactor: 1.0.1
