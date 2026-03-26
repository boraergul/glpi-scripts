# Project: GLPI SLA Rule Automation

## Overview
This script automates the creation and synchronization of Business Rules for Tickets in GLPI, specifically for SLA assignment. It ensures that every entity has the correct SLA (TTO/TTR) applied based on ticket type (Incident/Request) and priority.

## Standards
- **Modernization Level**: v3.1
- **Key Features**: Smart Sync, Professional Logging, Secure Session, Case-insensitive matching, Dry-run by default.

## Architecture
- **GLPI API**: Uses REST API for all operations.
- **Config**: External `config.json` for credentials.
- **Mapping**: `entity_sla_map.json` defines which entity uses which Service Level (SLM).
- **Rule Naming**: 
  - Incidents: `Auto-SLA-[Entity]-Priority-[P1-P5]-Incident`
  - Requests: `Auto-SLA-[Entity]-Request-P3`
