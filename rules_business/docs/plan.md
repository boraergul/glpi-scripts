# Plan: Modernize GLPI Business Rules (v3.1)

Modernize the `rules_business.py` script to align with v3.1 automation standards, focusing on efficiency, observability, and maintainability.

## Proposed Changes

### [Component] GLPI Business Rules Script (`rules_business.py`)

#### [MODIFY] [rules_business.py](file:///d:/Google%20Drive/Projeler/Script/rules_business/rules_business.py)
- **Logging**: Replace `print` statements with the `logging` module (Console + `rules_business.log`).
- **Session Management**: Implement `glpi_session` context manager for robust API connection handling.
- **Smart Sync**: 
    - Implement `get_rule_details` to fetch existing criteria/actions.
    - Update `create_or_update_rule` to use a diffing mechanism.
    - Only perform API `DELETE`/`POST` if the proposed configuration differs from the current state.
- **Dynamic Lookup**: Replace hardcoded Category ID `227` with a name-based lookup (default: "Genel Destek").
- **Reporting**: Add a structured execution summary (Created, Updated, Skipped, Failed).
- **Arguments**: Maintain support for `--force` (dry-run by default), `--priority`, and `--category`.

## Verification Plan

### Automated Tests
- Run `python rules_business.py` (Dry-Run):
    - Verify it correctly identifies existing rules.
    - Verify it proposes changes only when they differ from GLPI.
- Run `python rules_business.py --force` (Live-Run):
    - Verify rules are created/updated correctly in GLPI.
    - Verify subsequent runs result in "SKIPPED" status for unchanged rules.

### Manual Verification
1. Check `rules_business.log` for professional formatting.
2. Verify the terminal output shows a clear "DETAILED EXECUTION SUMMARY REPORT".
3. Check the GLPI interface (Administration > Rules > Business rules for tickets) to ensure "Auto-BR-" rules are correctly applied.
