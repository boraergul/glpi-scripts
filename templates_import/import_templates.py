import requests
import json
import os
import sys
import re
import urllib3
import argparse

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_NEW_DIR = os.path.join(BASE_DIR, '..', 'templates_new')
CONFIG_FILE = 'config.json'
NOTIFICATIONS_MD = os.path.join(TEMPLATES_NEW_DIR, 'glpi_notifications.md')

# Global Dry Run flag
DRY_RUN = False

# Add templates_new to sys.path to import the dictionary
sys.path.append(TEMPLATES_NEW_DIR)
try:
    from generate_email_templates import TEMPLATES
except ImportError:
    print("Error: Could not import TEMPLATES from generate_email_templates.py")
    sys.exit(1)

def load_config():
    """Load configuration from config.json with path searching"""
    search_paths = [
        os.path.join(BASE_DIR, CONFIG_FILE),
        os.path.join(BASE_DIR, '..', 'Config', CONFIG_FILE),
        os.path.join(BASE_DIR, '..', '..', 'Config', CONFIG_FILE),
        'config.json'
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
    print(f"Error: File {CONFIG_FILE} not found in any path.")
    sys.exit(1)

def init_session(url, app_token, user_token):
    headers = {
        "App-Token": app_token, 
        "Authorization": f"user_token {user_token}", 
        "Content-Type": "application/json"
    }
    try:
        resp = requests.get(f"{url}/initSession", headers=headers, verify=False, timeout=30)
        resp.raise_for_status()
        session_token = resp.json().get('session_token')
        
        # Switch to Root Entity for visibility
        headers_with_session = {"App-Token": app_token, "Session-Token": session_token, "Content-Type": "application/json"}
        requests.post(f"{url}/changeActiveEntities", 
                     headers=headers_with_session, 
                     json={"entities_id": 0, "is_recursive": True}, 
                     verify=False)
        
        return session_token
    except Exception as e:
        print(f"Session init failed: {e}")
        sys.exit(1)

def kill_session(url, app_token, session_token):
    headers = {"App-Token": app_token, "Session-Token": session_token}
    try:
        requests.get(f"{url}/killSession", headers=headers, verify=False, timeout=10)
    except:
        pass

def map_plural_to_itemtype(plural_type):
    """Maps GLPI 'Type' column values to GLPI internal Class Names (itemtype)"""
    mapping = {
        "Tickets": "Ticket",
        "Problems": "Problem",
        "Changes": "Change",
        "Projects": "Project",
        "Project tasks": "ProjectTask",
        "Users": "User",
        "Contracts": "Contract",
        "Reservations": "Reservation",
        "Computers": "Computer",
        "Cartridges": "CartridgeItem", # Likely Ticket is for Model
        "Cartridge models": "CartridgeItem",
        "Consumables": "ConsumableItem",
        "Consumable models": "ConsumableItem",
        "Licenses": "SoftwareLicense",
        "Certificates": "Certificate",
        "Domains": "Domain",
        "Saved searches alerts": "SavedSearch",
        "Marketplace": "Plugin", # Generic fallback
        "More Reporting": "PluginMoreReporting", # Guess
        "Crontask": "CronTask",
        "Automatic actions": "CronTask",
        "Receivers": "MailCollector",
        "Financial and administrative information": "Infocom"
    }
    return mapping.get(plural_type.strip(), "Ticket") # Default to Ticket if unknown

def parse_markdown_mapping():
    """Parses glpi_notifications.md to get Notification ID -> (Template Key, Itemtype) mapping"""
    mapping = {}
    
    if not os.path.exists(NOTIFICATIONS_MD):
        print(f"Error: Mapping file not found at {NOTIFICATIONS_MD}")
        sys.exit(1)
        
    print(f"Reading mapping from: {NOTIFICATIONS_MD}")
    
    with open(NOTIFICATIONS_MD, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line.startswith('|') or '---' in line or 'Recommended Template' in line:
            continue
            
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 3: continue
        
        name_col = parts[1]
        type_col = parts[3] # Column index 3 is Type (0=empty, 1=Name, 2=Entity, 3=Type)
        
        match = re.search(r'\((\d+)\)', name_col)
        if not match:
            continue
            
        notif_id = int(match.group(1))
        template_col = parts[-2] if parts[-1] == '' else parts[-1]
        
        if not template_col or template_col.lower() in ['(custom)', '(n/a)', '(n/a - plugin)', '']:
            continue
            
        template_key = template_col.split('/')[0].strip()
        itemtype = map_plural_to_itemtype(type_col)
        
        mapping[notif_id] = (template_key, itemtype)
        
    return mapping

def get_or_create_template(url, headers, template_key, itemtype, all_templates_cache=None):
    """Finds or creates a NotificationTemplate by name"""
    
    # If cache not provided, fetch all templates
    if all_templates_cache is None:
        print("  Fetching all templates...")
        all_templates_cache = {}
        try:
            # Get all templates using range
            r = requests.get(f"{url}/NotificationTemplate", headers=headers, verify=False, params={"range": "0-500"})
            if r.status_code == 200:
                templates = r.json()
                if isinstance(templates, list):
                    for tpl in templates:
                        if isinstance(tpl, dict) and 'name' in tpl and 'id' in tpl:
                            all_templates_cache[tpl['name']] = tpl['id']
        except Exception as e:
            print(f"  Warning: Could not fetch templates: {e}")
    
    # Check if template exists in cache
    current_id = all_templates_cache.get(template_key)
    
    if current_id:
        print(f"  Found existing template '{template_key}' (ID: {current_id})")
    else:
        # Create new template
        if DRY_RUN:
            print(f"  [DRY RUN] Would create new template '{template_key}' (Type: {itemtype})")
            return "DRY_RUN_ID", all_templates_cache

        print(f"  Creating new template '{template_key}' (Type: {itemtype})...")
        payload = {
            "input": {
                "name": template_key,
                "itemtype": itemtype,
                "css": "",
                "entities_id": 0,    # Critical for root entity
                "is_recursive": 1    # Make available to children
            }
        }
        r = requests.post(f"{url}/NotificationTemplate", headers=headers, json=payload, verify=False)
        if r.status_code == 201:
            current_id = r.json()['id']
            print(f"  Created '{template_key}' (ID: {current_id})")
            
            # Add to cache
            all_templates_cache[template_key] = current_id
            
            # Verify creation
            verify = requests.get(f"{url}/NotificationTemplate/{current_id}", headers=headers, verify=False)
            if verify.status_code != 200:
                print(f"  WARNING: Created template ID {current_id} but cannot retrieve it!")
                return None, all_templates_cache
        else:
            print(f"  ERROR creating template: {r.status_code} - {r.text}")
            return None, all_templates_cache
            
    return current_id, all_templates_cache

def get_template_translations(url, headers, template_id):
    """Fetches existing translations for a template"""
    try:
        r = requests.get(f"{url}/NotificationTemplate/{template_id}/NotificationTemplateTranslation", 
                        headers=headers, verify=False, params={"range": "0-100"})
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                # Return dict: {lang: id}
                # If duplicates exist, this will just keep the last one, which is fine for now
                return {item.get('language'): item.get('id') for item in data}
    except:
        pass
    return {}

def update_template_translation(url, headers, template_id, lang, subject, html_content, text_content, existing_translations=None):
    """Updates or Creates translation for a template"""
    
    input_data = {
        "notificationtemplates_id": template_id,
        "language": lang,
        "subject": subject,
        "content_html": html_content,
        "content_text": text_content
    }
    
    trans_id = None
    if existing_translations and lang in existing_translations:
        trans_id = existing_translations[lang]
        
    if trans_id:
        # Update existing
        if DRY_RUN:
            print(f"  [DRY RUN] Would update translation for {lang} in template {template_id}")
            return
        r = requests.put(f"{url}/NotificationTemplateTranslation/{trans_id}", headers=headers, json={"input": input_data}, verify=False)
    else:
        # Create new
        if DRY_RUN:
            print(f"  [DRY RUN] Would create translation for {lang} in template {template_id}")
            return
        r = requests.post(f"{url}/NotificationTemplateTranslation", headers=headers, json={"input": input_data}, verify=False)
    
    if r.status_code not in [200, 201]:
        pass

def update_notification(url, headers, notif_id, template_id):
    """Links notification to template using robust method"""
    # Use POST to Notification_NotificationTemplate endpoint
    # This is the correct way to create notification-template links
    print(f"  Linking Notif {notif_id} -> Template {template_id}...")
    
    payload = {
        "input": {
            "notifications_id": notif_id,
            "notificationtemplates_id": template_id,
            "mode": "mailing"
        }
    }
    
    if DRY_RUN:
        print(f"  [DRY RUN] Would link Notif {notif_id} -> Template {template_id}")
        return

    r = requests.post(f"{url}/Notification_NotificationTemplate", headers=headers, json=payload, verify=False)
    
    if r.status_code == 201:
        print(f"[OK] Notification {notif_id} linked.")
    elif r.status_code == 400 and "Duplicate entry" in r.text:
        # MySQL error 1062 is "Duplicate entry" for the unique key (notifications_id, mode, notificationtemplates_id)
        print(f"[OK] Notification {notif_id} already linked (exists).")
    else:
        print(f"[ERR] Failed link Notif {notif_id}: {r.status_code} {r.text}")

def read_file_content(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    print("--- GLPI Template Importer ---")
    config = load_config()
    
    glpi_url = config.get('GLPI_URL').rstrip('/')
    app_token = config['GLPI_APP_TOKEN']
    user_token = config['GLPI_USER_TOKEN']
    
    # Argument Parsing
    global DRY_RUN
    parser = argparse.ArgumentParser(description='GLPI Template Importer')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Perform a dry run without making changes')
    args = parser.parse_args()
    DRY_RUN = args.dry_run

    if DRY_RUN:
        print("!!! DRY RUN MODE ACTIVE - No changes will be made !!!\n")

    session_token = init_session(glpi_url, app_token, user_token)
    headers = {"App-Token": app_token, "Session-Token": session_token, "Content-Type": "application/json"}
    
    try:
        # 1. Parse Mapping
        mapping = parse_markdown_mapping()
        print(f"Found {len(mapping)} notifications to update.")
        
        # 2. Fetch all existing templates once (for performance and consistency)
        print("Fetching all existing templates...")
        all_templates_cache = {}
        try:
            r = requests.get(f"{glpi_url}/NotificationTemplate", headers=headers, verify=False, params={"range": "0-500"})
            if r.status_code == 200:
                templates = r.json()
                if isinstance(templates, list):
                    for tpl in templates:
                        if isinstance(tpl, dict) and 'name' in tpl and 'id' in tpl:
                            all_templates_cache[tpl['name']] = tpl['id']
            print(f"Found {len(all_templates_cache)} existing templates.")
        except Exception as e:
            print(f"Warning: Could not fetch templates: {e}")
        
        # 3. Iterate mappings
        processed_templates = {} # key -> id cache (for content updates)
        
        for notif_id, (template_key, itemtype) in mapping.items():
            if template_key not in TEMPLATES:
                print(f"Warning: Template '{template_key}' found in mapping but NOT in generate_email_templates.py. Skipping.")
                continue
                
            # Get Template ID (create if needed)
            if template_key in processed_templates:
                template_id = processed_templates[template_key]
            else:
                template_id, all_templates_cache = get_or_create_template(glpi_url, headers, template_key, itemtype, all_templates_cache)
                if not template_id: continue
                
                # Fetch existing translations ONCE for this template
                existing_translations = get_template_translations(glpi_url, headers, template_id)

                # Update Content
                en_subject = TEMPLATES[template_key]['en']['subject']
                en_html = read_file_content(os.path.join(TEMPLATES_NEW_DIR, 'html', 'en', f"{template_key}.html"))
                en_text = read_file_content(os.path.join(TEMPLATES_NEW_DIR, 'text', 'en', f"{template_key}.txt"))
                
                tr_subject = TEMPLATES[template_key]['tr']['subject']
                tr_html = read_file_content(os.path.join(TEMPLATES_NEW_DIR, 'html', 'tr', f"{template_key}.html"))
                tr_text = read_file_content(os.path.join(TEMPLATES_NEW_DIR, 'text', 'tr', f"{template_key}.txt"))
                
                update_template_translation(glpi_url, headers, template_id, "en_GB", en_subject, en_html, en_text, existing_translations)
                update_template_translation(glpi_url, headers, template_id, "en_US", en_subject, en_html, en_text, existing_translations)
                update_template_translation(glpi_url, headers, template_id, "tr_TR", tr_subject, tr_html, tr_text, existing_translations)
                
                processed_templates[template_key] = template_id
                print(f"  Template '{template_key}' content updated.")

            # Link Notification
            update_notification(glpi_url, headers, notif_id, template_id)
            
    except Exception as e:
        print(f"Critical Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        kill_session(glpi_url, app_token, session_token)
        print("Done.")

if __name__ == "__main__":
    main()
