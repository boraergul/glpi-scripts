# Memory: Modern GLPI Email Templates Pack

## Technical Debt & Quirks
- **Monolithic Script**: `generate_email_templates.py` is over 2,000 lines long. It contains both the generation logic, the HTML boilerplate, and the content for dozens of templates. This makes maintenance difficult.
    - *Potential Fix*: Break down the `TEMPLATES` dictionary into separate JSON or YAML files grouped by category (Ticket, Alarm, Change).
- **Hardcoded Styles**: CSS styles are embedded in a string within the Python script.
    - *Potential Fix*: Extract CSS into a separate `base.css` file and read it during generation.
- **Template Versioning**: Currently, there is no explicit versioning for individual templates.
    - *Potential Fix*: Add a `version` key to each template definition.

## Lessons Learned
- Table-based layouts are essential for GLPI notifications because many recipients use older versions of Outlook or mobile clients with limited CSS support.
- GLPI tags are very sensitive; ensure double hashes (`##`) are always closed.
