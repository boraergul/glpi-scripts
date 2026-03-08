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
        data = resp.json()
        if isinstance(data, list):
            print(f"API Error Response: {data}")
            sys.exit(1)
        return data.get('session_token')
    except Exception as e:
        print(f"Session Init Failed: {e}")
        if 'resp' in locals():
            print(f"Status Code: {resp.status_code}")
            print(f"Response Content: {resp.text}")
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

def main():
    # Hardcoded credentials for target GLPI
    GLPI_URL = "https://itsmp.ultron.com.tr/api.php/v1"
    APP_TOKEN = "INs9pxumMDPZLXSigZVJ4UuRO5cZOHCRHjhS2OoL"
    USER_TOKEN = "g6e4U76CyB4VlKpK41kKvcySbqiVF97t2fXWJFFm"
    
    glpi_url = GLPI_URL.rstrip('/')
    session = init_session(glpi_url, APP_TOKEN, USER_TOKEN)
    headers = {"App-Token": APP_TOKEN, "Session-Token": session, "Content-Type": "application/json"}
    
    # Switch to Root
    requests.post(f"{glpi_url}/changeActiveEntities", 
                 headers=headers, 
                 json={"entities_id": 0, "is_recursive": True}, 
                 verify=False)

    try:
        print(f"Fetching data from {glpi_url}...\n")
        notifications = get_all_items(glpi_url, headers, "Notification")
        templates = get_all_items(glpi_url, headers, "NotificationTemplate")
        
        # Get Links
        links_data = get_all_items(glpi_url, headers, "Notification_NotificationTemplate")
        
        # Map notification to its template
        notif_to_template = {}
        for link in links_data.values():
            nid = link.get('notifications_id')
            tid = link.get('notificationtemplates_id')
            if nid and tid:
                template_name = templates.get(tid, {}).get('name', f"Unknown ({tid})")
                notif_to_template[nid] = f"{template_name} ({tid})"

        # Header
        print("| ID | Name | Type | Current Template |")
        print("|---|---|---|---|")
        
        # Sort by ID for easier comparison
        sorted_ids = sorted(notifications.keys())
        for nid in sorted_ids:
            notif = notifications[nid]
            name = notif.get('name')
            ntype = notif.get('itemtype')
            current_tpl = notif_to_template.get(nid, "None")
            print(f"| {nid} | {name} | {ntype} | {current_tpl} |")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        kill_session(glpi_url, APP_TOKEN, session)

if __name__ == "__main__":
    main()
