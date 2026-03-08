| Name | Entity | Type | Active | Event | Notification templates | Child entities | Notification method | Comments | Allow response | Recommended Template |
|---|---|---|---|---|---|---|---|---|---|---|
| Alert Tickets not closed (1) | Root Entity | Tickets | Yes | Not solved tickets | Alert Tickets not closed (6) | Yes | Email | | Yes | ticket_recall |
| New Ticket (2) | Root Entity | Tickets | Yes | New ticket | ticket_opening_confirmation (50) | Yes | Email | | Yes | ticket_opening_confirmation / proactive_alarm_first |
| Update Ticket (3) | Root Entity | Tickets | Yes | Update of a ticket | ticket_followup_notification (39) | Yes | Email | | Yes | status_update |
| Close Ticket (4) | Root Entity | Tickets | Yes | Closing of the ticket | ticket_resolution_notification (38) | Yes | Email | | Yes | generic_ticket_resolution |
| Add Followup (5) | Root Entity | Tickets | Yes | New followup | ticket_followup_notification (39) | Yes | Email | | Yes | status_update |
| Add Task (6) | Root Entity | Tickets | Yes | New task | ticket_task_notification (41) | Yes | Email | | Yes | ticket_task_notification |
| Update Followup (7) | Root Entity | Tickets | Yes | Update of a followup | ticket_followup_notification (39) | Yes | Email | | Yes | status_update |
| Update Task (8) | Root Entity | Tickets | Yes | Update of a task | ticket_task_notification (41) | Yes | Email | | Yes | ticket_task_notification |
| Delete Followup (9) | Root Entity | Tickets | Yes | Deletion of a followup | ticket_deletion_notification (37) | Yes | Email | | Yes | status_update |
| Delete Task (10) | Root Entity | Tickets | Yes | Deletion of a task | ticket_task_notification (41) | Yes | Email | | Yes | ticket_task_notification |
| Resolve ticket (11) | Root Entity | Tickets | Yes | Ticket solved | ticket_resolution_notification (38) | Yes | Email | | Yes | generic_ticket_resolution / proactive_alarm_resolution |
| Ticket Validation (12) | Root Entity | Tickets | Yes | Approval request | Tickets Validation (7) | Yes | Email | | Yes | ticket_validation_request |
| New Reservation (13) | Root Entity | Reservations | Yes | New reservation | Reservations (2) | Yes | Email | | Yes | new_reservation |
| Update Reservation (14) | Root Entity | Reservations | Yes | Update of a reservation | Reservations (2) | Yes | Email | | Yes | new_reservation |
| Delete Reservation (15) | Root Entity | Reservations | Yes | Deletion of a reservation | Reservations (2) | Yes | Email | | Yes | new_reservation |
| Alert Reservation (16) | Root Entity | Reservations | Yes | Reservation expired | Alert Reservation (3) | Yes | Email | | Yes | new_reservation |
| Contract Notice (17) | Root Entity | Contracts | Yes | Notice | Contracts (12) | Yes | Email | | Yes | contract_renewal_90 |
| Contract End (18) | Root Entity | Contracts | Yes | End of contract | Contracts (12) | Yes | Email | | Yes | contract_end_30 |
| MySQL Synchronization (19) | Root Entity | SQL replicas | Yes | Desynchronization SQL replica | MySQL Synchronization (1) | Yes | Email | | Yes | custom_mysql_sync |
| Cartridges (20) | Root Entity | Cartridge models | Yes | Cartridges alarm | Cartridges (8) | Yes | Email | | Yes | consumable_alert |
| Consumables (21) | Root Entity | Consumable models | Yes | Consumables alarm | Consumables (9) | Yes | Email | | Yes | consumable_alert |
| Infocoms (22) | Root Entity | Financial and administrative information | Yes | Alarms on financial and administrative information | Infocoms (10) | Yes | Email | | Yes | custom_infocoms |
| Software Licenses (23) | Root Entity | Licenses | Yes | Alarms on expired licenses | Licenses (11) | Yes | Email | | Yes | contract_end_30 |
| Ticket Recall (24) | Root Entity | Tickets | Yes | Automatic reminders of SLAs | ticket_deletion_notification (37) | Yes | Email | | Yes | sla_breach_warning |
| Password Forget (25) | Root Entity | Users | Yes | Forgotten password? | Password Forget (13) | Yes | Email | | Yes | password_forget |
| Ticket Satisfaction (26) | Root Entity | Tickets | Yes | Satisfaction survey | Ticket Satisfaction (14) | Yes | Email | | Yes | csat_survey |
| Item not unique (27) | Root Entity | Fields unicity | Yes | Alert on duplicate record | Item not unique (15) | Yes | Email | | Yes | custom_item_not_unique |
| CronTask Watcher (28) | Root Entity | Automatic actions | Yes | Monitoring of automatic actions | CronTask (16) | Yes | Email | | Yes | custom_crontask_watcher |
| New Problem (29) | Root Entity | Problems | Yes | New problem | Problems (17) | Yes | Email | | Yes | new_problem |
| Update Problem (30) | Root Entity | Problems | Yes | Update of a problem | Problems (17) | Yes | Email | | Yes | update_problem |
| Resolve Problem (31) | Root Entity | Problems | Yes | Problem solved | Problems (17) | Yes | Email | | Yes | resolve_problem |
| Add Task (32) | Root Entity | Problems | Yes | New task | Problems (17) | Yes | Email | | Yes | update_problem |
| Update Task (33) | Root Entity | Problems | Yes | Update of a task | Problems (17) | Yes | Email | | Yes | update_problem |
| Delete Task (34) | Root Entity | Problems | Yes | Deletion of a task | Problems (17) | Yes | Email | | Yes | update_problem |
| Close Problem (35) | Root Entity | Problems | Yes | Closure of a problem | Problems (17) | Yes | Email | | Yes | resolve_problem |
| Delete Problem (36) | Root Entity | Problems | Yes | Deleting a problem | Problems (17) | Yes | Email | | Yes | custom_delete_problem |
| Ticket Validation Answer (37) | Root Entity | Tickets | Yes | Approval request answer | Tickets Validation (7) | Yes | Email | | Yes | ticket_validation_request |
| Contract End Periodicity (38) | Root Entity | Contracts | Yes | Periodicity | Contracts (12) | Yes | Email | | Yes | contract_end_30 |
| Contract Notice Periodicity (39) | Root Entity | Contracts | Yes | Periodicity notice | Contracts (12) | Yes | Email | | Yes | contract_renewal_90 |
| Planning recall (40) | Root Entity | Planning reminders | Yes | Planning recall | Planning recall (18) | Yes | Email | | Yes | ticket_recall |
| Delete Ticket (41) | Root Entity | Tickets | Yes | Deletion of a ticket | ticket_deletion_notification (37) | Yes | Email | | Yes | delete_ticket |
| New Change (42) | Root Entity | Changes | Yes | New change | Changes (19) | Yes | Email | | Yes | planned_change_notification |
| Update Change (43) | Root Entity | Changes | Yes | Update of a change | Changes (19) | Yes | Email | | Yes | generic_update_change |
| Resolve Change (44) | Root Entity | Changes | Yes | Change solved | Changes (19) | Yes | Email | | Yes | generic_update_change |
| Add Task (45) | Root Entity | Changes | Yes | New task | Changes (19) | Yes | Email | | Yes | generic_update_change |
| Update Task (46) | Root Entity | Changes | Yes | Update of a task | Changes (19) | Yes | Email | | Yes | generic_update_change |
| Delete Task (47) | Root Entity | Changes | Yes | Deletion of a task | Changes (19) | Yes | Email | | Yes | generic_update_change |
| Close Change (48) | Root Entity | Changes | Yes | Closure of a change | Changes (19) | Yes | Email | | Yes | generic_update_change |
| Delete Change (49) | Root Entity | Changes | Yes | Deleting a change | Changes (19) | Yes | Email | | Yes | custom_delete_change |
| Ticket Satisfaction Answer (50) | Root Entity | Tickets | Yes | Satisfaction survey answer | Ticket Satisfaction (14) | Yes | Email | | Yes | csat_survey |
| Receiver errors (51) | Root Entity | Receivers | Yes | Receiver errors | Receiver errors (20) | Yes | Email | | Yes | custom_receiver_errors |
| New Project (52) | Root Entity | Projects | Yes | New project | Projects (21) | Yes | Email | | Yes | new_project |
| Update Project (53) | Root Entity | Projects | Yes | Update of a project | Projects (21) | Yes | Email | | Yes | new_project |
| Delete Project (54) | Root Entity | Projects | Yes | Deletion of a project | Projects (21) | Yes | Email | | Yes | custom_delete_project |
| New Project Task (55) | Root Entity | Project tasks | Yes | New project task | Project Tasks (22) | Yes | Email | | Yes | project_task |
| Update Project Task (56) | Root Entity | Project tasks | Yes | Update of a project task | Project Tasks (22) | Yes | Email | | Yes | project_task |
| Delete Project Task (57) | Root Entity | Project tasks | Yes | Deletion of a project task | Project Tasks (22) | Yes | Email | | Yes | project_task |
| Request Unlock Items (58) | Root Entity | Object Locks | Yes | Unlock Item Request | Unlock Item request (23) | Yes | Email | | Yes | custom_unlock_item |
| New user in requesters (59) | Root Entity | Tickets | Yes | New user in requesters | | Yes | (N/A) | | Yes | ticket_opening_confirmation |
| New group in requesters (60) | Root Entity | Tickets | Yes | New group in requesters | | Yes | (N/A) | | Yes | ticket_opening_confirmation |
| New user in observers (61) | Root Entity | Tickets | Yes | New user in observers | ticket_followup_notification (39) | Yes | Email | | Yes | status_update |
| New group in observers (62) | Root Entity | Tickets | Yes | New group in observers | ticket_followup_notification (39) | Yes | Email | | Yes | status_update |
| New user in assignees (63) | Root Entity | Tickets | Yes | New user in assignees | ticket_assignment_notification (40) | Yes | Email | | Yes | escalation_customer |
| New group in assignees (64) | Root Entity | Tickets | Yes | New group in assignees | ticket_assignment_notification (40) | Yes | Email | | Yes | escalation_customer |
| New supplier in assignees (65) | Root Entity | Tickets | Yes | New supplier in assignees | ticket_assignment_notification (40) | Yes | Email | | Yes | escalation_customer |
| Saved searches (66) | Root Entity | Saved searches alerts | Yes | Private search alert | Saved searches alerts (24) | Yes | Email | | Yes | custom_saved_search_alert |
| Certificates (67) | Root Entity | Certificates | Yes | Alarm on expired certificate | Certificates (25) | Yes | Email | | Yes | contract_end_30 |
| Alert expired domains (68) | Root Entity | Domains | Yes | Expired domains | Alert domains (26) | Yes | Email | | Yes | contract_end_30 |
| Alert domains close expiries (69) | Root Entity | Domains | Yes | Expiring domains | Alert domains (26) | Yes | Email | | Yes | contract_end_30 |
| Password expires alert (70) | Root Entity | Users | Yes | Password expires | Password expires alert (27) | Yes | Email | | Yes | password_expiration |
| Check plugin updates (71) | Root Entity | Marketplace | Yes | Check all plugin updates | Plugin updates (28) | Yes | Email | | Yes | custom_plugin_updates |
| New user mentioned (72) | Root Entity | Tickets | Yes | User mentioned | Tickets (4) | Yes | Email | | Yes | status_update |
| New Task (73) | Root Entity | GlpiPlugin\Releases\Task | Yes | N/A | Tasks (29) | Yes | Email | | Yes | custom_plugin_releasetask_new |
| Update Task (74) | Root Entity | GlpiPlugin\Releases\Task | Yes | N/A | Tasks (29) | Yes | Email | | Yes | custom_plugin_releasetask_update |
| Delete Task (75) | Root Entity | GlpiPlugin\Releases\Task | Yes | N/A | Tasks (29) | Yes | Email | | Yes | custom_plugin_releasetask_delete |
| Notification for "More Reporting" (76) | Root Entity | More Reporting | Yes | More Reporting | Notification for "More Reporting" (30) | Yes | Email | | Yes | daily_report |
| Credit expired (79) | Root Entity | Credit vouchers | Yes | Expiration date | Credit expired (33) | Yes | Email | | Yes | custom_credit_expired |
| Low credits (80) | Root Entity | Credit vouchers | Yes | Low credits | Low credits (34) | Yes | Email | | Yes | custom_low_credits |
| New knowledge base item (81) | Root Entity | Knowledge base | No | New knowledge base item | Knowledge base item (45) | Yes | Email | | Yes | custom_kb_new |
| Updating knowledge base item (82) | Root Entity | Knowledge base | No | Update of a knowledge base item | Knowledge base item (45) | Yes | Email | | Yes | custom_kb_update |
| Delete knowledge base item (83) | Root Entity | Knowledge base | No | Deleting a knowledge base item | Knowledge base item (45) | Yes | Email | | Yes | custom_kb_delete |
| Password Initialization (84) | Root Entity | Users | Yes | Password initialization | Password Initialization (46) | Yes | Email | | Yes | password_forget |
| Change Satisfaction (85) | Root Entity | Changes | Yes | Satisfaction survey | Change Satisfaction (47) | Yes | Email | | Yes | csat_survey |
| Change Satisfaction Answer (86) | Root Entity | Changes | Yes | Satisfaction survey answer | Change Satisfaction (47) | Yes | Email | | Yes | csat_survey |
| Automatic reminder (87) | Root Entity | Tickets | No | Automatic reminder | Automatic reminder (48) | Yes | Email | | Yes | ticket_recall |
| New Task (88) | Root Entity | Tasks | Yes | A task has been added | Tasks (49) | Yes | Email | | Yes | ticket_task_notification |
| Update Task (89) | Root Entity | Tasks | Yes | A task has been updated | Tasks (49) | Yes | Email | | Yes | ticket_task_notification |
| Delete Task (90) | Root Entity | Tasks | Yes | A task has been removed | Tasks (49) | Yes | Email | | Yes | ticket_task_notification |
