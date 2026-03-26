# Project: Email Rules Automation (GLPI)

## Overview
This script automates the creation of Mail Collector rules in GLPI based on Entity `mail_domain` information.

## Architecture
- `rules_email.py`: Main execution script.
- `config.json`: Configuration for GLPI API (must be in `../Config/` or local).

## Features
- **Smart Sync**: Fetches existing rules and compares criteria/actions to avoid redundant API updates.
- **Robust Regex**: Uses `re.escape()` to safely handle complex email domains.
- **Detailed Logging**: Logs to both console and `rules_email.log` with a final execution summary report.
- **Safe Session Handling**: Context manager ensures `killSession` is called on exit.

## Workflow
1. Load configuration and initialize GLPI session.
2. Fetch all Entities (filtering by valid `mail_domain`).
3. Fetch existing `RuleMailCollector` rules.
4. Process each entity:
    - If a rule exists and matches (Smart Sync), skip.
    - If a rule is missing or different, create/update it.
5. Generate and log a detailed execution summary report (Created, Updated, Skipped, Failed).
6. Securely close the GLPI session.
