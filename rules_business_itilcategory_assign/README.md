# GLPI ITIL Category Rule Automation (v3.1)

This script automates the creation and synchronization of ITIL Category-based group assignment rules in GLPI.

## Features
- **Smart Sync**: Diffing logic to only update rules when changed.
- **Professional Logging**: Dual output to console and `rules_business_itilcategory_assign.log`.
- **Dynamic Group Fetching**: Fetches all technician groups from GLPI at runtime.
- **Secure Session**: Context-managed GLPI API sessions.

## Installation
1. Ensure `config.json` is correctly configured with `GLPI_URL`, `GLPI_APP_TOKEN`, and `GLPI_USER_TOKEN`.
2. Install dependencies:
   ```bash
   pip install requests urllib3
   ```

## Usage
### Dry-Run (Simulation)
Recommended first-step to see what changes will be applied.
```bash
python rules_business_itilcategory_assign.py
```

### Live Execution
Apply the rules to the GLPI server.
```bash
python rules_business_itilcategory_assign.py --force
```

## Rule Logic
Rules follow the naming pattern `Auto-Category-[CategoryName]`. They assign a specific technician group to a ticket if:
1. The ticket's ITIL Category matches the defined ID.
2. The ticket has NO assigned technician.
3. The ticket has NO assigned technician group.
