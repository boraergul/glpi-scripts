# Template Import Guide

This guide details how to use `import_templates.py` to synchronize local templates with GLPI.

## Workflow

1. **Mapping**: The script reads `glpi_notifications.md` from the `templates_new` directory.
2. **Parsing**: It extracts Notification IDs and expected Template Names using RegEx.
3. **API Interaction**:
    - Checks if the Template exists in GLPI (Root Entity).
    - Creates the Template if missing.
    - Updates/Creates translations for `en_GB`, `en_US`, and `tr_TR`.
    - Links the notification to the template using the `mailing` mode.

## Usage

```bash
python import_templates.py
```

## Folder Structure Dependency

The script expects the following structure relative to its location:
```
..
├── templates_new/
│   ├── glpi_notifications.md  (Mapping file)
│   ├── generate_email_templates.py (Template definitions)
│   ├── html/
│   │   ├── en/
│   │   └── tr/
│   └── text/
│       ├── en/
│       └── tr/
└── templates_import/
    └── import_templates.py (This script)
```

## Mapping Table Format

The `glpi_notifications.md` must contain a table with at least the following columns:
`| Name (ID) | ... | Type | ... | Recommended Template |`

Example:
`| New Ticket (10) | Root | Tickets | ... | ticket_opening_confirmation |`
