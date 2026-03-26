# Technical Memory - rules_business_incident_major

## Implementation Quirks
- **Case Sensitivity**: Explicitly changed the entity matching to lowercase. Use `entity_name.lower()` when comparing configuration names with API responses to avoid "Entity Not Found" warnings.
- **SLA P1 Logic**: The script specifically looks for "P1" in the SLA name string to identify high-priority SLAs.
- **Purge vs Update**: When an update is needed, the current implementation purges existing criteria/actions and recreates them to ensure a clean state, instead of granularly deleting single items.

## Technical Debt / Caveats
- **Hardcoded Priority/Category**: `MAJOR_PRIORITY_ID = 6` and `MAJOR_INCIDENT_CATEGORY_ID = 229` are currently constants.
- **Group ID**: `MAJOR_INCIDENT_GROUP_ID = 45` is used for assignments.
- **SLA Matching**: Depends on a specific naming convention in GLPI (Service Level + "P1").
