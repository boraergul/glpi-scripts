# GLPI Template Import & Maintenance Scripts

A collection of Python tools for managing GLPI notification templates and ensuring consistency across the notification system.

## 🚀 Quick Start

1. **Configuration**: Ensure `config.json` exists in the project root or `../Config/` with your GLPI credentials:
   ```json
   {
     "GLPI_URL": "https://glpi.example.com/apirest.php",
     "GLPI_APP_TOKEN": "your_app_token",
     "GLPI_USER_TOKEN": "your_user_token"
   }
   ```
3. **Dry Run (Safety First)**:
   ```bash
   python import_templates.py --dry-run
   ```
4. **Compare with Target GLPI**:
   ```bash
   python compare_notifications.py
   ```

## 📂 Documentation

- **[Project Architecture](docs/project.md)**: Overview of the tech stack and business rules.
- **[Import Guide](docs/import_guide.md)**: Detailed instructions for the template synchronization process.
- **[Maintenance Guide](docs/maintenance_guide.md)**: How to use the audit and cleanup scripts.
- **[Technical Memory](docs/memory.md)**: Known quirks and GLPI API specific notes.
- **[Change Log](docs/logbook.md)**: Chronological record of updates.

## 🛠 Features

- **Automated Sync**: Synchronizes local HTML/Text templates with GLPI.
- **Smart Linking**: Maps notifications to templates using ID-based RegEx parsing.
- **Audit Tools**: Detects missing notification links and orphan templates.
- **Migration Utilities**: `list_glpi_notifications.py` and `compare_notifications.py` for safe transition between GLPI instances.
- **Dry Run Mode**: All destructive or creative operations support simulation mode via `--dry-run`.
- **Consistency**: Enforces mandatory translations (`en_GB`, `en_US`, `tr_TR`).
- **Cleanup**: Resolves duplicate translation entries automatically.

## 📝 Prerequisites

- Python 3.6+
- `requests` library
- GLPI 9.5+ or 10.0+ with REST API enabled

---
*Created and maintained for GLPI Workflow Automation.*
