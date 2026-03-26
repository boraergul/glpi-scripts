# Technical Memory & Debt - Email Rules Automation

## Resolved Debt
- **Security**: SSL verification is indi-configurable (`verify_ssl` in `config.json`).
- **Efficiency**: Smart Sync logic avoids redundant API calls.
- **Robustness**: Regex escaping now uses `re.escape`.
- **Validation**: Domain normalization handles leading `@`.
- **Session Management**: Guaranteed `kill_session` via `glpi_session` context manager.

## Ongoing Debts
- **Ranking**: Hardcoded ranking (1) for all rules.
- **Pagination**: Step limits (1000/100) are still fixed.
