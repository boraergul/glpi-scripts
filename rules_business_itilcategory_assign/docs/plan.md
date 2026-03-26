# ITIL Category Assignment Modernization Plan (v3.1)

## Goal
Modernize the category-to-group assignment automation to align with v3.1 standards.

## Final Decisions
- **Matching Mechanism**: ID-Based (Source of Truth in `CATEGORY_GROUP_MAP`).
- **Dynamic Data**: All Group names and Category names are fetched from API for logging/resolution.
- **Script Name**: `rules_business_itilcategory_assign.py`.

## Implementation Details
- Applied Smart Sync to compare criteria and actions.
- Integrated `logging` module with UTF-8 support.
- Implemented `resolve_id` for human-readable naming in logs.
- Removed ID 225 from the mapping as it was verified as missing in GLPI.
