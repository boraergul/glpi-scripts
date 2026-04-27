# Project State: SLA Breach Report Plugin

## Project Overview
A specialized GLPI reporting plugin designed to provide accurate SLA compliance monitoring across GLPI 10.x and 11.x environments. Focused on resolving the reporting gap created by GLPI's dynamic SLA status handling.

## Technical Architecture
- **Core Strategy**: Real-time calculation of TTR/TTO breaches based on statistical delay constants (`solve_delay_stat`, `takeintoaccount_delay_stat`) and dynamic deadlines.
- **Custom Translation Engine**: A high-performance, cache-independent translation system (`PluginSlareportReport::trans`) that bypasses GLPI's native `__()` to ensure reliability across version updates and language cache clears.
- **Frontend**: Single-page interactive dashboard using CSS Grid and Chart.js.
- **Database**: Native GLPI `DBmysqlIterator` integration with strictly validated sorting to prevent SQL Injection.
- **Reporting**: Combined CSV (Native PHP) and PDF (TCPDF) export engines with memory-efficient buffered writing.
- **Deployment**: Dual-environment automated deployment (DEV and PROD) via SSH/SCP with automated ownership management.

## Chronological Work Log

### [2026-04-27] - Version 1.2.2 Translation Stability & PROD Deployment
- **[ENGINE]** Implemented **Custom Translation Engine** to resolve persistent translation key issues in GLPI 11.
    - Created `PluginSlareportReport::trans()` to manually load locale files from `locales/` directory.
    - Converted `.mo/.po` workflow to direct PHP array files (`locales/tr_TR.php`, `locales/en_GB.php`) for maximum reliability.
- **[PDF]** Restored and enhanced **Premium PDF Layout**:
    - Added Cover Page with dark slate theme.
    - Implemented Executive Summary and Entity Violation Charts (table-based bars).
    - Fixed TCPDF inclusion logic to support both GLPI 10 and 11 vendor structures.
- **[DEPLOY]** Created `deploy_prod.sh` for one-click deployment to **ITSM-PROD (10.42.2.149)** with `bora` user.
- **[FIX]** Resolved 500 error in `setup.php` by implementing `slareport_get_title_safe()` (avoids class calls during early plugin initialization).

### [2026-04-27] - Version 1.2.0 SLA Audit & Synchronization
- **[FEATURE]** Implemented **SLA Audit & Risk Analysis** system:
    - Added risk scoring logic in `report.class.php`.
    - Added risk flags: `stagnant`, `last_minute`, and `excessive_toggling`.
    - Visual risk badges and flag icons in the dashboard.
- **[UI]** Renamed all "Date" fields to **"Opening Date"** (Açılış Tarihi) for better clarity.
- **[FEATURE]** Synchronized PDF and CSV outputs.

### [2026-04-24] - Version 1.1.2 GLPI 11.0.6 Compatibility Patch
- **[FIX]** Migrated `CommonITILObject::PENDING` to `CommonITILObject::WAITING` to resolve "Undefined constant" error in GLPI 11.0.6.

... (History truncated for brevity in README, but maintained in full in docs/project_state.md)

## Technical Debt & Known Constraints
- **Menu Cache**: GLPI caches the plugin name from `setup.php`. A plugin Disable/Enable cycle is required to refresh the name after a translation update.
- **PDF Fonts**: Using `dejavusans` is mandatory for Turkish character support; standard PDF fonts like `helvetica` will fail.

## Environment Checklist
- **PHP**: 8.1+
- **GLPI**: 10.0, 11.0 (Tested)
- **Servers**: 
    - DEV: 10.42.2.146 (glpi user)
    - PROD: 10.42.2.149 (bora user)
