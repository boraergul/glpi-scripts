# Project: Modern GLPI Email Templates Pack

## Overview
This project provides a set of modern, mobile-responsive, and professional email notification templates for GLPI (ITSM software). It replaces the default, often plain, GLPI notifications with structured, table-based layouts.

## Technology Stack
- **Python**: Used for the template generation engine (`generate_email_templates.py`).
- **HTML/CSS**: Table-based layouts for maximum email client compatibility (Outlook, Gmail, Mobile).
- **GLPI Placeholder Tags**: Integrated tags (e.g., `##ticket.title##`, `##ticket.url##`) for dynamic content injection by GLPI.

## Architecture
- **Generator Pattern**: Templates are not edited manually in the `html/` or `text/` folders. Instead, they are defined in a centralized `TEMPLATES` dictionary within `generate_email_templates.py`.
- **Internationalization (i18n)**: Supports both Turkish (`tr`) and English (`en`) outputs.
- **Boilerplate System**: Uses a consistent `HTML_TEMPLATE` string to ensure all emails share the same brand identity (headers, footers, styles).

## Critical Endpoints/Files
- `generate_email_templates.py`: The "Source of Truth" for all template content and logic.
- `glpi_notifications.md`: Mapping guide between GLPI notification events and the corresponding template files.
- `html/`: Generated production-ready HTML files.
- `text/`: Generated production-ready plain-text files.

## Business Rules
- **Table-Based Design**: All templates must use tables for layout to ensure consistency across legacy email clients.
- **Brand Consistency**: Header must always feature "Ultron Bilişim A.Ş.".
- **Responsive**: Max-width of 600px for mobile readability.
- **Automated Workflow**: Any change to a template must be followed by running the Python generator to sync the output files.
