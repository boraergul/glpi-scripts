# Analysis of GLPI Rule Script Execution Sequence

The objective is to provide a clear, detailed overview of how existing rule scripts are applied when a new entity is created or an email received, including their order, core logic, and naming conventions.

## Proposed Documentation Changes

### GLPI Automation Project (Root)
#### [NEW] [rule_execution_flow.md](file:///d:/Google%20Drive/Projeler/Script/docs/rule_execution_flow.md)
Create a comprehensive guide and table detailing:
- **Execution Stage**: Differentiating between `RuleMailCollector` (runs during email ticket creation) and `RuleTicket` (runs after ticket is created).
- **Script Name**: The Python script responsible for generating/updating the rule.
- **Reasoning**: Why the rule exists and what it solves.
- **Ranking**: The order in which GLPI applies the rules in that stage.
- **Rule Name Example**: Format used for the rule names.

#### [MODIFY] [project_state.md](file:///d:/Google%20Drive/Projeler/Script/docs/project_state.md)
- Update the "Business Logic" section to summarize the overall rule flow.
- Ensure all rule naming conventions are documented centrally.

---

## Technical Summary of Findings

| Sequence | Category | Script | Rule Name Example | Goal/Reasoning | Ranking |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ST-1 (Mail)** | Mail Collector | [rules_email.py](file:///d:/Google%20Drive/Projeler/Script/rules_email/rules_email.py) | `Auto-Email-Ankara-Oto` | Assigns the correct Entity based on sender domain. | 1 |
| **ST-2 (Mail)** | Mail Collector | [rules_unknowndomain.py](file:///d:/Google%20Drive/Projeler/Script/rules_unknowndomain/rules_unknowndomain.py) | `Tanımsız-Domain` | Catch-all for unknown domains; redirects to "Genel destek". | 2 |
| **ST-3 (Ticket)** | Business Rule | [rules_business_incident_major.py](file:///d:/Google%20Drive/Projeler/Script/rules_business_incident_major/rules_business_incident_major.py) | `Auto-Major-Incident-Dorçe` | Priority 6 incidents go to "Major Incident Ekibi" immediately. | 10 |
| **ST-4 (Ticket)** | Business Rule | [rules_business_sla.py](file:///d:/Google%20Drive/Projeler/Script/rules_business_sla/rules_business_sla.py) | `Auto-SLA-Dorçe-Priority-P1-Incident` | Sets P1-P5 SLAs for Incidents; P3 for Requests. | 15 |
| **ST-5 (Ticket)** | Business Rule | [rules_business_itilcategory_assign.py](file:///d:/Google%20Drive/Projeler/Script/rules_business_itilcategory_assign/rules_business_itilcategory_assign.py) | `Auto-Category-Security` | Assigns Technician Group based on ITIL Category. | 20 |
| **ST-6 (Ticket)**| Business Rule | [rules_business.py](file:///d:/Google%20Drive/Projeler/Script/rules_business/rules_business.py) | `Auto-BR-Ankara-Oto` | Default Category/Prio/SLA for non-Incident email tickets. | 1 (high) |

## Verification Plan

### Manual Verification
- Review the generated `rule_execution_flow.md` for accuracy against current Python scripts.
- Check that all `rules_id`, `criteria`, and `action` field codes match the GLPI API logic documented in the READMEs.
- Confirm logical flow by cross-referencing [onboarding.py](file:///d:/Google%20Drive/Projeler/Script/onboarding/onboarding.py) orchestrator script.
