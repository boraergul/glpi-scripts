# Memory: Technical Notes & Quirks

## GLPI API Specifics

- **Session Tokens**: Scripts use `initSession` and MUST call `killSession` in a `finally` block to prevent session leakage.
- **Active Entity**: Defaulting to Root Entity (ID 0) with `is_recursive: True` is critical for template visibility across the entire GLPI instance.
- **Linking Endpoint**: The correct endpoint for linking notifications and templates is `Notification_NotificationTemplate`. Linking via a direct update to `Notification` items is often unsupported or fails to trigger correctly.
- **Itemtype Mapping**: GLPI uses internal class names (e.g., `Ticket`, `Problem`, `ProjectTask`). The `import_templates.py` script includes a `map_plural_to_itemtype` helper to handle the labels seen in the GLPI UI.

## Common Error: Duplicate Entry
- During `import_templates.py`, a `400` error with "Duplicate entry" is safely ignored as it indicates the link already exists.

## Translation IDs
- GLPI requires specific language codes: `en_GB`, `en_US`, `tr_TR`.
- If a template update fails, check if the `entities_id` for the template is 0.
