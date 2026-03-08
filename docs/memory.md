# Gemini's Memory Scratchpad

## Technical Debt / Known Issues
- **GLPI 11 Schema**: `ttr_is_exceeded` and `tto_is_exceeded` columns are no longer in `glpi_tickets`. Manual calculation in `report.class.php` is necessary.
- **CSV Encoding**: Using UTF-8 BOM (`chr(0xEF).chr(0xBB).chr(0xBF)`) for Excel compatibility in Turkish characters.
- **JS Scoping**: Observed potential scoping issues in GLPI with inline scripts; `addEventListener` and `window` assignments are preferred for robustness.

## Library-Specific Quirks
- **Chart.js**: Requires CDN or internal loading. Currently using CDN.
- **GLPI CSRF**: Requires `_glpi_csrf_token` in all POST requests for compatibility with GLPI 11.

## Bugs Encountered
- **Sorting Redirect**: `$_SERVER['PHP_SELF']` can cause redirects to `/front/central.php` in some GLPI configurations. Use relative query strings (e.g., `?sort=...`) instead.
- **Export Variables**: Initialization order in `index.php` is critical to avoid "Undefined variable" errors during early `exit` for CSV export.
