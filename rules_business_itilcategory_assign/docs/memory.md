# Technical Memory & Quirks

### Known Issues
- **Category ID 225 (Endpoint & End-User)**: This ID was found to be missing or deleted in the GLPI production environment. It has been removed from the script to prevent recurring warnings.

### Lessons Learned
- **v2 Experiment (Mapping-Free)**: An attempt was made to use a dynamic string-matching algorithm to eliminate the ID mapping. While it worked for common names, it proved brittle for hierarchical and translated names (e.g., "System" vs "Sistem ve Yedekleme"). The decision was made to revert to ID-based mapping for reliability.

### Standardized Rules
- Rule Ranking: Always set to `20`.
- Rule Condition: `Add/Update` (Type 3).
- Match Logic: `AND`.
