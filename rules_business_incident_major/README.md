# GLPI Major Incident Rule Automation (v3.1)

This script automates the creation and synchronization of Major Incident business rules in GLPI based on an entity-to-SLA mapping.

## Key Features

- **Smart Sync**: Automatically compares current GLPI rules with the local configuration. It skips redundant API calls if the rule is already up-to-date.
- **Detailed Logging**: Provides granular logs of every action, including specific field differences (e.g., missing criteria or changed SLA values).
- **Human-Readable Logs**: Resolves GLPI internal IDs (SLA, Group, Entity, Priority) to their human-readable names in the logs for easier debugging.
- **Case-Insensitive Matching**: Matches GLPI entities regardless of case differences between the config file and the API response.
- **Safe Execution (Dry Run)**: Defaults to dry-run mode. Use the `--force` flag to apply changes to the live system.
- **Professional Session Management**: Uses a secure context manager for session initialization and cleanup.

## Installation & Requirements

- Python 3.x
- `requests` library

```bash
pip install requests
```

## Configuration

The script depends on two main configuration files:
1. `config/config.json`: Contains GLPI API URL, tokens, and SSL verification settings.
2. `config/entity_sla_map.json`: Defines the mapping between Entity names and the desired Service Level (e.g., "SLA-BRONZE-5X9").

## Usage

### Dry Run (Recommended first)
```bash
python rules_business_incident_major.py
```

### Apply Changes
```bash
python rules_business_incident_major.py --force
```

## Logs
Logs are written to both the console and `rules_business_incident_major.log` in the application directory.
