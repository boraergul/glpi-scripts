# SLA Breach Report Plugin

## Overview
A GLPI plugin providing high-fidelity visual and tabular reporting for SLA breaches. Fully compatible with GLPI 10.x and 11.x, it specifically addresses the architectural changes in the GLPI 11 Database Abstraction Layer (DBAL) to ensure accurate real-time monitoring of TTR (Time To Resolve) and TTO (Time To Own).

## Key Features
- **Recursive Entity Filtering**: Native GLPI entity dropdown supporting hierarchical (recursive) selection to filter data across entire entity branches.
- **Enhanced Visual Dashboard**: Modern, responsive dashboard featuring interactive status distribution charts (Doughnut) and entity breach analysis (Bar).
- **Comprehensive Exporting**:
  - **PDF Export**: Professional multi-page report with cover page, executive summary, and detailed ticket list (using TCPDF).
  - **CSV Export**: Standardized data export for external spreadsheet analysis with full UTF-8 BOM support.
- **Real-time SLA Calculation**: Dynamic status determination (Compliant, Violated, Active) based on live ticket deadline data.
- **Secure Architecture**: CSRF-compliant query handling via GET-parameter state management.
- **Localization**: Full support for Turkish (TR) and English (EN).

## Requirements
- GLPI >= 10.0 (Fully tested on 11.0)
- PHP >= 8.1
- Chart.js (CDN)
- TCPDF (Core GLPI dependency)

## Installation
1. Copy the `slareport` directory into your GLPI `plugins/` folder.
2. Log in as super-admin.
3. Navigate to **Setup > Plugins**.
4. Find **SLA Breach Report** and click **Install**.
5. Click **Enable**.

## Usage
Access the report via **Tools > SLA Breach Report**.
1. Select appropriate **Start** and **End** dates.
2. Choose an **Entity** (Recursive selection enabled).
3. Click **Search** to regenerate metrics and charts.
4. Use **CSV** or **PDF** buttons for reporting.

## GLPI 11 Compatibility Notes
- **Database Iterator**: Uses strict associative array structures for WHERE clauses to comply with GLPI 11's `DBmysqlIterator` type-checking.
- **SLA State Monitoring**: Automatically adapts to GLPI 11's removal of certain persistent breach flags by calculating TTR/TTO status against dynamic deadlines.

## Calculation Logic
- **TTR (Time To Resolve)**:
  - Validates `solve_delay_stat` for solved tickets.
  - Compares `time_to_resolve` with `now()` for open tickets.
- **TTO (Time To Own)**:
  - Compares `takeintoaccount_delay_stat` against SLA definitions for owned tickets.
  - Compares `time_to_own` with `now()` for new tickets.

---
**Author**: Bora Ergül  
**Version**: 1.0.1  
**License**: GPLv2+
