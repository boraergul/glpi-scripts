# Major Incident Rule Automation - Project Overview

## Purpose
This project manages GLPI business rules that automatically identify and process "Major Incidents" based on specific criteria (Priority: Major, Category: Major Incident).

## Architecture
- **Language**: Python 3
- **API**: GLPI REST API
- **Configuration**: `config/config.json` (API, Credentials), `config/entity_sla_map.json` (Entity -> SLA Map).
- **Core Logic**: `rules_business_incident_major.py`
    - Fetches Entities and P1 SLAs.
    - Synchronizes rules (`Auto-Major-Incident-[Entity]`).
    - Assigns to "Major Incident Ekibi" (Group ID: 45).
    - Stops further rule processing after association.

## Workflows
1. **Fetch**: Retrieve and cache all Entity and SLA (P1) mapping data.
2. **Compare**: Fetch existing rules and find differences in criteria or actions.
3. **Sync**: Add/Update only rules that have changed. Skip others.
4. **Report**: Output details about every processed entity.
