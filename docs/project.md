# GLPI Script Project

## Project Architecture
- **GLPI Template Transfer**: Scripts to export and import Notification Templates between GLPI instances.
- **Components**:
    - `export_templates.py`: CLI script for exporting.
    - `import_templates.py`: CLI script for importing.
    - `Gui_templates_export_v2.py`: Tkinter-based GUI that combines export and import.
- **Tech Stack**: Python, requests, tkinter.
- **Config**: `config/servers.json` contains server profiles.

## Business Rules
- Templates are matched by name.
- Multiple translations are supported.
- Dry-run mode for safety.
