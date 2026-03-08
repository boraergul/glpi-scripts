# Maintenance Guide

Detailed instructions for maintenance scripts to keep the GLPI notification system clean.

## 1. Usage Analysis (`analyze_usage.py`)

Identifies gaps in the notification setup.

- **Notifications Without Templates**: Lists active GLPI notifications that have no associated template.
- **Unused Templates**: Lists custom templates that are not linked to any notification.

**Run command:**
```bash
python analyze_usage.py
```

---

## 2. Translation Cleanup (`cleanup_translations.py`)

During heavy updates, GLPI might occasionally end up with duplicate translation entries for the same language on a single template. This script resolves those.

- **Logic**: Groups translations by language. If more than one exists, it keeps the entry with the highest ID (latest) and deletes the others.
- **Range**: Currently targets Template IDs 205 to 247 (can be adjusted in `main()`).

**Run command:**
```bash
python cleanup_translations.py
```

---

## 3. Translation Check (`check_translations.py`)

A troubleshooting script to verify if a specific template has the required translations.

- **Target**: Uses `TEMPLATE_ID = 206` (ticket_opening_confirmation) by default.
- **Verification**: Checks for the existence of `en_GB`, `en_US`, and `tr_TR`.

**Run command:**
```bash
python check_translations.py
```
---

## 4. Multi-Instance Migration Utilities

### Notification Listing (`list_glpi_notifications.py`)
Fetches all notifications from a live GLPI instance to help verify IDs before migration.
```bash
python list_glpi_notifications.py
```

### Notification Comparison (`compare_notifications.py`)
Automatically cross-references `glpi_notifications.md` with a live GLPI instance by name to detect ID mismatches.
```bash
python compare_notifications.py
```
**Recommended Step**: Always run this before an import on a new server to ensure IDs match.
