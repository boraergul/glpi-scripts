# ITIL Category Assignment Project

## Architecture
- **Language**: Python 3.
- **API**: GLPI REST API.
- **Standards**: v3.1 Automation Protocols.

## Key Components
- `glpi_session`: Secure session management.
- `fetch_groups`: Dynamic technician group retrieval.
- `create_or_update_rule`: Smart Sync engine.

## Current Rule Table
Managed internally via `CATEGORY_GROUP_MAP` constants. Covers Server, Security, Network, Cloud, Monitoring, and General Support.
