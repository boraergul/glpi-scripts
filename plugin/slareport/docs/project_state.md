# Project State: SLA Breach Report Plugin

## Project Overview
A specialized GLPI reporting plugin designed to provide accurate SLA compliance monitoring across GLPI 10.x and 11.x environments. Focused on resolving the reporting gap created by GLPI's dynamic SLA status handling.

## Technical Architecture
- **Core Strategy**: Real-time calculation of TTR/TTO breaches based on statistical delay constants (`solve_delay_stat`, `takeintoaccount_delay_stat`) and dynamic deadlines.
- **Frontend**: Single-page interactive dashboard using CSS Grid and Chart.js.
- **Database**: Native GLPI `DBmysqlIterator` integration with strictly validated sorting to prevent SQL Injection.
- **Reporting**: Combined CSV (Native PHP) and PDF (TCPDF) export engines with memory-efficient buffered writing.

## Chronological Work Log

### [2026-04-24] - Version 1.1.2 GLPI 11.0.6 Compatibility Patch
- **[FIX]** Migrated `CommonITILObject::PENDING` to `CommonITILObject::WAITING` to resolve "Undefined constant" error in GLPI 11.0.6.
- **[FIX]** Reverted "Pending Reasons" experimental integration to maintain core stability and layout simplicity.

### [2026-04-24] - Version 1.1.1 GLPI 11.0.6 Log Schema & Sorting Fixes
- **[FIX]** Updated `glpi_logs` usage to match GLPI 11 schema: migrated from `ticket_id`/`newvalue` to `items_id`/`new_value`.
- **[FIX]** Implemented `id_search_option => 12` filter for log analysis to accurately track status changes.
- **[FIX]** Added `glpi_entities` JOIN in `report.class.php` to resolve SQL errors when sorting by entity name.
- **[FIX]** Fixed `entity_id` parameter mismatch in PDF export URL.
- **[CLEAN]** Refactored `calculateTotalPendingTime` to use efficient array-based interval calculation.
- **[CLEAN]** Improved SLA name formatting using `array_filter` and `implode`.

### [2026-04-20] - Version 1.1.0 Security & Performance Hardening
- **[SEC]** Implemented strict allow-list for `ORDER BY` parameters in `report.class.php` to prevent SQL Injection.
- **[SEC]** Added `Html::escape()` to all user-generated outputs in the frontend to eliminate XSS vulnerabilities.
- **[PERF]** Optimized database queries by replacing `SELECT *` with specific required columns, reducing memory footprint.
- **[FIX]** Resolved entity filter mismatch between web view and PDF export (`entity_id` vs `entities_id`).
- **[PERF]** Refactored PDF export to use buffered row writing instead of large string concatenation, preventing Out-of-Memory (OOM) errors on large datasets.
- **[SLA]** Improved stability of TTO/TTR calculation logic.

### [2026-04-20] - Version 1.1.0 Stability & GLPI 11 Optimization
- **[FIX]** Reverted complex technician analytics and timeline features to ensure baseline stability in GLPI 11's stricter Database Iterator environment.
- **[FEATURE]** Implemented **Recursive Entity Selection** using native GLPI `Entity::dropdown()`.
- **[SEC]** Migrated search filters from POST to **GET** to eliminate CSRF `AccessDeniedHttpException` on report refreshes.
- **[FIX]** Resolved `Invalid criteria type` error in GLPI 11 by simplifying `WHERE` clause array structures.
- **[FIX]** Corrected TCPDF header misalignment by explicitly defining column widths in header and body cells.

### [2026-04-17] - Version 1.0.1 UI/UX Polish
- **[FEATURE]** Added PDF export capability using GLPI's bundled TCPDF library.
- **[FEATURE]** Added UTF8-BOM to CSV exports for Turkish character compatibility in Excel.
- **[UI]** Optimized dashboard layout for dashboard visibility.

## Technical Debt & Known Constraints
- **GLPI 11 Joins**: Complex `ON` conditions using nested arrays currently trigger `Invalid criteria type` errors. Baseline joins are currently used.
- **PDF Engine**: TCPDF is used for consistent formatting; explicit width management is required for table alignment.

## Environment Checklist
- **PHP**: 8.1+
- **GLPI**: 10.0, 11.0 (Tested)
- **Dependencies**: `tecnickcom/tcpdf` (must be available in GLPI vendor)
