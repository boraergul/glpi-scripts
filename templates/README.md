# GLPI Notification Templates

Modern, multilingual notification templates for GLPI 10.0+

## 📧 Overview

This directory contains **32 professional notification templates** for GLPI, designed to replace the default complex template with scenario-specific, clean, and modern designs.

## 🌍 Languages

All templates are available in:
- **Turkish (TR)** - `*_tr.html` / `*_tr.txt`
- **English (EN)** - `*_en.html` / `*_en.txt`

## 📋 Available Templates

| # | Template Name | Purpose | Color Theme |
|---|---------------|---------|-------------|
| 1 | **New Ticket** | New ticket creation | Purple gradient |
| 2 | **Transfer** | Ticket transfer between groups | Cyan gradient |
| 3 | **Resolution** | Ticket closed/resolved | Green gradient |
| 4 | **Followup** | New comments/mentions | Cyan gradient |
| 5 | **Assignment** | User/group assignments | Purple gradient |
| 6 | **Task** | Task operations | Orange gradient |
| 7 | **SLA Warning** | SLA breach warnings | Red gradient |
| 8 | **Deletion** | Ticket deletion/recall | Gray gradient |

## 📁 File Structure

```
templates/
├── ticket_new_notification_tr.html          # Turkish HTML
├── ticket_new_notification_tr.txt           # Turkish Plain Text
├── ticket_new_notification_en.html          # English HTML
├── ticket_new_notification_en.txt           # English Plain Text
├── ticket_transfer_notification_tr.html
├── ticket_transfer_notification_tr.txt
├── ticket_transfer_notification_en.html
├── ticket_transfer_notification_en.txt
├── ticket_resolution_notification_tr.html
├── ticket_resolution_notification_tr.txt
├── ticket_resolution_notification_en.html
├── ticket_resolution_notification_en.txt
├── ticket_followup_notification_tr.html
├── ticket_followup_notification_tr.txt
├── ticket_followup_notification_en.html
├── ticket_followup_notification_en.txt
├── ticket_assignment_notification_tr.html
├── ticket_assignment_notification_tr.txt
├── ticket_assignment_notification_en.html
├── ticket_assignment_notification_en.txt
├── ticket_task_notification_tr.html
├── ticket_task_notification_tr.txt
├── ticket_task_notification_en.html
├── ticket_task_notification_en.txt
├── ticket_sla_warning_notification_tr.html
├── ticket_sla_warning_notification_tr.txt
├── ticket_sla_warning_notification_en.html
├── ticket_sla_warning_notification_en.txt
├── ticket_deletion_notification_tr.html
├── ticket_deletion_notification_tr.txt
├── ticket_deletion_notification_en.html
└── ticket_deletion_notification_en.txt
```

## ✨ Features

### Modern Design
- ✅ Fully responsive HTML layout
- ✅ **Mobile-optimized** with dedicated CSS media queries
- ✅ Gradient headers with distinct colors per scenario
- ✅ Clean, professional typography
- ✅ Optimized spacing (20-30% less padding for compact view)

### Multilingual Support
- ✅ Turkish (TR) and English (EN) versions
- ✅ **Proper Turkish terminology** ("Talep" instead of "Ticket")
- ✅ Localized date/time formats
- ✅ Language-specific content and phrasing

### Dual Format
- ✅ **HTML** - Rich, styled emails with colors and formatting
- ✅ **Plain Text** - Clean Unicode borders (═ and ─) for email clients that don't support HTML

### Simplified SLA Footer
All templates include a **concise, bullet-point SLA notice**:
- ✅ **Contracted customers:** Responses according to SLA times
- ✅ **Other customers:** Specialists contact you as soon as available

### GLPI 10.0 Compatible
- ✅ Uses modern GLPI variables (`##ticket.id##`, `##ticket.title##`, etc.)
- ✅ Supports FOREACH loops (`##FOREACHauthors##`)
- ✅ Conditional blocks (`##IFticket.category##`)
- ✅ Clean SLA labels (removed TTO/TTR abbreviations)

## 📝 Subject Lines

**New Format:** Short and concise with ticket ID in brackets for better readability.

See `SUBJECT_LINES.md` for complete documentation.

### Turkish (TR)
```
New Ticket:     [GLPI ###ticket.id##] Yeni Ticket: ##ticket.title##
Transfer:       [GLPI ###ticket.id##] Transfer: ##ticket.title##
Resolution:     [GLPI ###ticket.id##] Çözüldü: ##ticket.title##
Followup:       [GLPI ###ticket.id##] Yeni Yorum: ##ticket.title##
Assignment:     [GLPI ###ticket.id##] Atama: ##ticket.title##
Task:           [GLPI ###ticket.id##] Görev: ##ticket.title##
SLA Warning:    [GLPI ###ticket.id##] ⚠️ SLA: ##ticket.title##
Deletion:       [GLPI ###ticket.id##] Silindi: ##ticket.title##
```

### English (EN)
```
New Ticket:     [GLPI ###ticket.id##] New Ticket: ##ticket.title##
Transfer:       [GLPI ###ticket.id##] Transferred: ##ticket.title##
Resolution:     [GLPI ###ticket.id##] Resolved: ##ticket.title##
Followup:       [GLPI ###ticket.id##] New Comment: ##ticket.title##
Assignment:     [GLPI ###ticket.id##] Assigned: ##ticket.title##
Task:           [GLPI ###ticket.id##] Task: ##ticket.title##
SLA Warning:    [GLPI ###ticket.id##] ⚠️ SLA: ##ticket.title##
Deletion:       [GLPI ###ticket.id##] Deleted: ##ticket.title##
```

**Benefits:**
- ✅ 20-30% shorter than old format
- ✅ Ticket ID prominently displayed (#1234)
- ✅ Mobile-friendly (fits in preview)
- ✅ GitHub/Jira-style formatting

## 🚀 Installation

### Step 1: Create Template in GLPI
1. Go to **Setup → Notifications → Notification templates**
2. Click **"+"** to add new template
3. Enter:
   - **Name:** `New Ticket Notification (TR)` or `New Ticket Notification (EN)`
   - **Type:** `Tickets`
   - **Comment:** Optional description

### Step 2: Add Content
1. Go to **Translations** tab
2. Click **"+"** to add translation
3. Select **Language** (Turkish or English)
4. Enter **Subject** (see subject lines above)
5. **Email HTML body:** Copy entire `.html` file content and paste
6. **Email text body:** Copy entire `.txt` file content and paste
7. Click **Add**

### Step 3: Add Other Language
Repeat Step 2 for the other language version (if using both TR and EN)

### Step 4: Map to Notifications
1. Go to **Setup → Notifications → Notifications**
2. Find relevant notification (e.g., "New Ticket")
3. Go to **Notification templates** tab
4. Select your new template
5. Click **Update**

## 🔗 Template-Event Mapping

| Notification Event | Recommended Template |
|-------------------|---------------------|
| New ticket | New Ticket Notification |
| Add ticket | New Ticket Notification |
| Update ticket | Followup Notification |
| Close ticket | Resolution Notification |
| Resolve ticket | Resolution Notification |
| Add followup | Followup Notification |
| Update followup | Followup Notification |
| Add task | Task Notification |
| Update task | Task Notification |
| Assign ticket to user | Assignment Notification |
| Assign ticket to group | Assignment Notification |
| Change ticket assignee | Assignment Notification |
| SLA warning | SLA Warning Notification |
| Delete ticket | Deletion Notification |
| Recall ticket | Deletion Notification |

## 📚 Documentation

- **Upload Guide:** See `glpi_template_upload_guide.md` for detailed installation instructions
- **GLPI Variables:** See `GLPI_LANG_VARIABLES.md` for available GLPI 10.0 variables
- **Variable Reference:** See `glpi_10_correct_variables.md` for correct variable usage

## 🎨 Design Principles

1. **Scenario-Specific:** Each template shows only relevant information
2. **Color-Coded:** Different gradient colors for quick visual identification
3. **Responsive:** Works on desktop and mobile email clients
4. **Accessible:** Plain text versions for all email clients
5. **Professional:** Clean, modern design that reflects well on your organization

## 🔧 Customization

To customize templates:
1. Edit the HTML/TXT files in this directory
2. Modify colors, text, or layout as needed
3. Keep GLPI variables intact (e.g., `##ticket.id##`)
4. Test in GLPI before deploying to production
5. Commit changes to Git

## ⚠️ Important Notes

- ✅ Always copy the **entire** HTML file content (from `<!DOCTYPE html>` to `</html>`)
- ✅ Keep `<style>` tags - GLPI supports them
- ✅ Don't modify GLPI variables (they're surrounded by `##`)
- ✅ Test with real tickets before enabling for all users
- ⚠️ GLPI may have character limits - if template doesn't save, try minifying HTML

## 📞 Troubleshooting

**Problem:** Template doesn't save in GLPI
- **Solution:** HTML may be too large. Remove comments and extra whitespace, or use source code mode

**Problem:** GLPI variables not working
- **Solution:** Ensure variables are surrounded by `##` (e.g., `##ticket.id##`)

**Problem:** Email not received
- **Solution:** Check notification queue and cron jobs in GLPI

**Problem:** HTML not rendering
- **Solution:** Ensure you copied the entire HTML file including `<!DOCTYPE html>` and `<style>` tags

## 📄 License

These templates are part of the GLPI Scripts project and follow the same license.

## 🤝 Contributing

To contribute improvements:
1. Edit templates
2. Test in GLPI
3. Commit with descriptive message
4. Push to repository

---

**Total Templates:** 32 files (8 scenarios × 2 languages × 2 formats)
**GLPI Version:** 10.0+
**Last Updated:** 2026-01-08
**Optimization:** v2.0 (Mobile responsive, Turkish language, simplified footer)
