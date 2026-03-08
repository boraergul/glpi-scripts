import requests
import json
import os
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = 'config.json'

def load_config():
    search_paths = [
        os.path.join(BASE_DIR, CONFIG_FILE),
        os.path.join(BASE_DIR, '..', 'Config', CONFIG_FILE),
        'config.json'
    ]
    for path in search_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    print("Config not found")
    sys.exit(1)

def init_session(url, app_token, user_token):
    headers = {"App-Token": app_token, "Authorization": f"user_token {user_token}", "Content-Type": "application/json"}
    try:
        resp = requests.get(f"{url}/initSession", headers=headers, verify=False)
        return resp.json().get('session_token')
    except Exception as e:
        print(f"Session Init Failed: {e}")
        sys.exit(1)

def kill_session(url, app_token, session_token):
    headers = {"App-Token": app_token, "Session-Token": session_token}
    requests.get(f"{url}/killSession", headers=headers, verify=False)

def get_all_items(url, headers, endpoint):
    items = {}
    range_start = 0
    range_step = 100
    
    while True:
        params = {"range": f"{range_start}-{range_start + range_step}"}
        r = requests.get(f"{url}/{endpoint}", headers=headers, verify=False, params=params)
        
        if r.status_code in [200, 206]:
            data = r.json()
            if not isinstance(data, list):
                break
            
            if len(data) == 0:
                break
                
            for item in data:
                items[item['id']] = item
            
            if len(data) < range_step:
                break
                
            range_start += range_step
        else:
            break
            
    return items

def get_all_links(url, headers):
    # Fetch all links from Notification_NotificationTemplate
    links = []
    range_start = 0
    
    # We use search endpoint for this table usually or generic get
    # Let's try direct GET first
    all_links = get_all_items(url, headers, "Notification_NotificationTemplate")
    return list(all_links.values())

def main():
    config = load_config()
    glpi_url = config.get('GLPI_URL').rstrip('/')
    tokens = (config['GLPI_APP_TOKEN'], config['GLPI_USER_TOKEN'])
    session = init_session(glpi_url, *tokens)
    headers = {"App-Token": tokens[0], "Session-Token": session, "Content-Type": "application/json"}
    
    # Switch to Root
    requests.post(f"{glpi_url}/changeActiveEntities", 
                 headers=headers, 
                 json={"entities_id": 0, "is_recursive": True}, 
                 verify=False)

    try:
        print("Fetching Notifications...")
        notifications = get_all_items(glpi_url, headers, "Notification")
        print(f"Found {len(notifications)} notifications.")
        
        print("Fetching Templates...")
        templates = get_all_items(glpi_url, headers, "NotificationTemplate")
        print(f"Found {len(templates)} templates.")
        
        print("Fetching Links...")
        links = get_all_links(glpi_url, headers)
        print(f"Found {len(links)} links.")
        
        # Analyze
        linked_notification_ids = set()
        used_template_ids = set()
        
        for link in links:
            notif_id = link.get('notifications_id')
            tpl_id = link.get('notificationtemplates_id')
            
            if notif_id: linked_notification_ids.add(notif_id)
            if tpl_id: used_template_ids.add(tpl_id)
            
        # 1. Notifications without Templates
        print("\n=== NOTIFICATIONS WITHOUT TEMPLATES ===")
        print("| ID | Name | Type |")
        print("|---|---|---|")
        missing_count = 0
        for nid, notif in notifications.items():
            if nid not in linked_notification_ids:
                print(f"| {nid} | {notif.get('name')} | {notif.get('itemtype')} |")
                missing_count += 1
        if missing_count == 0:
            print("None (All notifications have templates!)")

        # 2. Unused Templates
        # Filter for our custom templates (IDs > 200 roughly, or checking against known list)
        print("\n=== UNUSED TEMPLATES (Potential Orphans) ===")
        print("| ID | Name |")
        print("|---|---|")
        unused_count = 0
        for tid, tpl in templates.items():
            # Optional: Filter out default GLPI templates if ID is low (e.g. < 20)
            # if tid < 20: continue 
            
            if tid not in used_template_ids:
                print(f"| {tid} | {tpl.get('name')} |")
                unused_count += 1
        
        if unused_count == 0:
            print("None (All templates are used!)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        kill_session(glpi_url, tokens[0], session)

if __name__ == "__main__":
    main()
