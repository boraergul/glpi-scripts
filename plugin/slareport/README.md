# SLA Breach Report Plugin

## Overview
A GLPI plugin providing visual and tabular reporting for SLA breaches. Designed to work with GLPI 10.x and 11.x, it specifically addresses schema changes in newer versions to ensure accurate TTR (Time To Resolve) and TTO (Time To Own) monitoring.

## Features
- **Visual Dashboard**: Pie charts showing the distribution of TTR vs TTO breaches.
- **Date Filtering**: analyze performance across specific time periods.
- **Drill-down Table**: Detailed list of breached tickets with direct links to GLPI ticket forms.
- **Entity Awareness**: Breaks down breaches by GLPI entities.
- **Localization**: Full support for Turkish (TR) and English (EN).

## Requirements
- GLPI >= 10.0
- PHP >= 8.0
- Chart.js (Loaded via CDN)

## Installation
1. Clone or copy the `slareport` directory into your GLPI `plugins/` folder.
2. Log in to GLPI as a super-admin.
3. Navigate to **Setup > Plugins**.
4. Find **SLA Breach Report** and click **Install**.
5. Click **Enable** (the power icon).

## Usage
Once installed, the report can be accessed via:
- **Tools > SLA Breach Report** (or from the top menu entries depending on your profile).
- Select your desired **Start Date** and **End Date**.
- Click **Search** to generate the report and charts.

## Technical Notes
- **GLPI 11 Compliance**: In GLPI 11, `ttr_is_exceeded` is no longer a persistent database column. This plugin performs real-time calculations to determine breach status accurately.
- **Performance**: Optimized for large ticket volumes using indexed SQL queries.

## Calculation Logic
The plugin determines the status (Compliant, Violated, Active) based on GLPI's internal statistical data:

1.  **TTR (Time To Resolve)**:
    - **Closed Tickets**: Checks if `solve_delay_stat` (actual time to solve in seconds) exceeds the SLA definition.
    - **Open Tickets**: Checks if the current time has passed the `time_to_resolve` deadline.
2.  **TTO (Time To Own)**:
    - **Owned Tickets**: Checks if `takeintoaccount_delay_stat` (actual time to take into account) exceeds the SLA definition.
    - **New Tickets**: Checks if the current time has passed the `time_to_own` deadline.

**Violation Rule**: If *either* TTR or TTO is exceeded, the ticket is marked as **İHLAL** (Violated).

## Localization
- **Turkish (TR)**: Default display and PDF/CSV labels.
- **English (EN)**: Supported via GLPI's standard translation files (`locales/`).

## Author
- Bora Ergül
- Version: 1.0.1
