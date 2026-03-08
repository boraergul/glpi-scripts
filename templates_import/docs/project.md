# Project Architecture: GLPI Template Import

This project provides a suite of Python scripts to manage GLPI Notification Templates and their links to Notifications via the GLPI REST API.

## Technology Stack

- **Language**: Python 3.x
- **Integration**: GLPI REST API
- **Dependencies**: `requests`, `urllib3`
- **Source Material**: Markdown files (`glpi_notifications.md`), Python templates (`generate_email_templates.py`)

## Business Rules

1. **Centralized Template Management**: All templates are defined in a central directory and pushed to GLPI.
2. **Translation Consistency**: Each template must have at least three translations (`en_GB`, `en_US`, `tr_TR`).
3. **Automated Linking**: Notifications are automatically linked to their respective templates based on ID-to-Name mapping provided in documentation.
4. **Maintenance-First**: Regular checks for orphans (notifications without templates) and duplicate translations.

## Component Overview

| Component | Responsibility |
|---|---|
| `import_templates.py` | Primary execution script for template creation, content update, and notification linking. |
| `analyze_usage.py` | Audits the GLPI environment to find unlinked notifications and unused templates. |
| `check_translations.py` | Verifies the integrity of translations for specific templates. |
| `cleanup_translations.py` | Automatically removes redundant translation entries to prevent API issues. |
| `list_glpi_notifications.py` | Lists notifications from target GLPI to verify IDs manually. |
| `compare_notifications.py` | Compares documentation IDs with live GLPI IDs by notification name. |
| `config.json` | Stores GLPI URL and API tokens (App-Token and User-Token). |
