# GLPI Notification to Template Mapping Guide

This guide describes how to link the 18 generated email templates to your **specific GLPI Notifications**.

## 1. Incident & Request Management (Tickets)

| Generated Template | Link to this GLPI Notification | Strategy |
| :--- | :--- | :--- |
| **ticket_opening_confirmation** | **New Ticket (2)** | This is the standard "New ticket" notification. |
| **status_update** | **Update Ticket (3)** OR **Add Followup (5)** | Use for general updates and followups. |
| **proactive_alarm_first** | **New Ticket (2)** | **IMPORTANT:** Do NOT overwrite the default template. Add a **Translation** or use **Notification Rules** to trigger this *only* if `Category = Alarm`. |
| **proactive_alarm_resolution** | **Resolve ticket (11)** | **IMPORTANT:** Use Rules to trigger only for Alarm category. |
| **sla_breach_warning** | **Ticket Recall (24)** | Handles "Automatic reminders of SLAs". |
| **escalation_customer** | **New user in assignees (63)** | Triggered when a ticket is escalated (reassigned) to a new user. |
| **csat_survey** | **Ticket Satisfaction (26)** | Standard survey notification. |

## 2. Major Incident Management
*These usually share the "Tickets" notifications but need distinct criteria.*

| Generated Template | Link to this GLPI Notification | Strategy |
| :--- | :--- | :--- |
| **major_incident_announcement** | **New Ticket (2)** | Trigger if `Priority = Major`. |
| **major_incident_update** | **Update Ticket (3)** | Trigger if `Priority = Major`. |
| **major_incident_resolution** | **Resolve ticket (11)** | Trigger if `Priority = Major`. |

## 3. Change Management

| Generated Template | Link to this GLPI Notification | Strategy |
| :--- | :--- | :--- |
| **planned_change_notification** | **New Change (42)** | Standard new change notification. |
| **emergency_change_notification** | **New Change (42)** | Trigger if `Urgency = Emergency`. |

## 4. Field Service

| Generated Template | Link to this GLPI Notification | Strategy |
| :--- | :--- | :--- |
| **field_service_appointment** | **Add Task (6)** | Trigger when a task is added (Field Service scheduling). |
| **field_service_completion** | **Resolve ticket (11)** | Trigger if `Category = Field Service`. |

## 5. Contract Management

| Generated Template | Link to this GLPI Notification | Strategy |
| :--- | :--- | :--- |
| **contract_renewal_90** | **Contract Notice (17)** | Configure automatic action to 90 days. |
| **contract_end_30** | **Contract Notice (17)** | Configure automatic action to 30 days. |

## 6. Reports (Plugin Dependent)

| Generated Template | Link to this GLPI Notification | Strategy |
| :--- | :--- | :--- |
| **daily_report** | **Notification for "More Reporting" (76)** | If you use the "More Reporting" plugin. |
| **monthly_report** | **Notification for "More Reporting" (76)** | If you use the "More Reporting" plugin. |

---

## Action Plan

1.  **Go to `Setup > Notifications > Notification Templates`.**
    *   Create 18 new templates using the HTML from `templates_new\html\`.
2.  **Go to `Setup > Notifications > Notifications`.**
    *   Open the corresponding notification ID (e.g., **New Ticket (2)**).
    *   **Option A (Simple):** Change the "Template" dropdown to your new template (applies to ALL tickets).
    *   **Option B (Advanced):** Use the **Templates** tab *inside* the Notification to add rules (e.g., "If Category is Alarm, use `proactive_alarm_first`").
