# Project: GLPI Business Rules

## Overview
This module automates the creation and management of Business Rules (`RuleTicket`) in GLPI. It ensures that tickets coming from specified entities via email are correctly categorized, prioritized, and assigned SLAs.

## Architecture
- **Script**: `rules_business.py`
- **Configuration**:
    - `config.json`: API credentials and GLPI URL.
    - `entity_sla_map.json`: Mapping of Entity names to SLM (Service Level Management) names.
- **V3.1 Implementation**:
    - Uses `glpi_session` context manager for robust session lifecycle.
    - Implements Smart Sync to minimize API calls by only updating rules when differences are detected.
    - Professional dual-output logging (Console + `rules_business.log`).
    - Dynamic resolution of ITIL Category IDs.
    - Standardized execution summary report.
