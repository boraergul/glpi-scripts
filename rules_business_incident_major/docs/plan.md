# Plan - rules_business_incident_major Modernization (v3.1)

## Goal
Modernize the Major Incident rule automation script to align with `rules_email.py` (v3.0) standards, ensuring efficiency, better logging, and case-insensitive entity matching.

## Completed Changes
### Smart Sync
- [x] Implement `get_rule_details` to check existing rule state.
- [x] Implement logic to SKIP updates when no changes are detected.
- [x] Add detailed difference logging for UPDATES.
- [x] Enrich logs with human-readable names for IDs (Priorities, Entities, SLAs, Groups).

### Safety & Performance
- [x] Default to DRY-RUN mode; added `--force` flag.
- [x] Set `timeout=30` for all API requests.
- [x] Implement `glpi_session` context manager for secure session handling.
- [x] Add case-insensitive entity matching.

### Reporting
- [x] Standardize logging via `logging` module (console and file).
- [x] Add "Detailed Execution Summary Report" at the end of the script.

## Verification
- [x] Dry-run testing with current configuration (42 entities mapped).
- [x] Verified "Smart Sync" skip/update logic.
- [x] Verified case-insensitive matching for "Trt" and others.
- [x] Code standard compatibility with `rules_email.py`.
