# Plan: Modernize GLPI SLA Rules Script (v3.1)

## Goal
Modernize `rules_business_sla.py` to match v3.1 standards established in `rules_business_incident_major.py`.

## Code Analysis Findings
1.  **Current Logic**: The script correctly iterates through entities and maps them to SLMs. It creates P1-P5 rules for Incidents and a single P3 rule for Requests.
2.  **Smart Sync Gaps**: The current diffing logic in `create_or_update_rule` only checks `field` and `value`. It misses `action_type`, which is critical for complex rules.
3.  **Logging**: While it has logging, the detailed "Change detected" messages can be more verbose and include human-readable labels for everything (e.g., SLA names instead of just IDs).
4.  **Timeouts**: Some API calls have 30s timeouts, but consistency across all calls is needed.
5.  **Entities**: Case-insensitive matching is implemented in `fetch_all_entities` but can be reinforced.

## Verification
- Test with multiple entity-SLA mappings in `entity_sla_map.json`.
- Verify diff reporting by manually modifying a rule in GLPI and checking if the script detects it.
