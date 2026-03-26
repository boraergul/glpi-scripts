# Memory: GLPI Business Rules

## Technical Debt / Quirks
- **Hardcoded IDs**: Historically used hardcoded Category ID `227`. Modernization will transition to name-based lookup.
- **Full Refresh**: Previous version cleared all criteria/actions on every update. V3.1 introduces diffing.
- **Ranking**: Rules are assigned a high ranking (`1`) to ensure they execute early in the GLPI rule chain.
