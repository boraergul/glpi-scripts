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
    resp = requests.get(f"{url}/initSession", headers=headers, verify=False)
    session_token = resp.json().get('session_token')
    
    # Switch to Root
    headers_with_session = {"App-Token": app_token, "Session-Token": session_token, "Content-Type": "application/json"}
    requests.post(f"{url}/changeActiveEntities", 
                 headers=headers_with_session, 
                 json={"entities_id": 0, "is_recursive": True}, 
                 verify=False)
    return session_token

def kill_session(url, app_token, session_token):
    headers = {"App-Token": app_token, "Session-Token": session_token}
    requests.get(f"{url}/killSession", headers=headers, verify=False)

def main():
    config = load_config()
    glpi_url = config.get('GLPI_URL').rstrip('/')
    tokens = (config['GLPI_APP_TOKEN'], config['GLPI_USER_TOKEN'])
    session = init_session(glpi_url, *tokens)
    headers = {"App-Token": tokens[0], "Session-Token": session, "Content-Type": "application/json"}

    try:
        # Check translations for Template 206 (ticket_opening_confirmation)
        TEMPLATE_ID = 206
        
        print(f"=== Checking Translations for Template {TEMPLATE_ID} ===\n")
        
        params = {
            "criteria[0][field]": "4",  # notificationtemplates_id
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": TEMPLATE_ID,
            "range": "0-100"
        }
        
        r = requests.get(f"{glpi_url}/search/NotificationTemplateTranslation", headers=headers, params=params, verify=False)
        
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                total = data.get('totalcount', 0)
                print(f"Total translations: {total}")
                print(f"Expected: 3 (en_GB, en_US, tr_TR)\n")
                
                if 'data' in data:
                    for item in data['data']:
                        print(f"Translation ID: {item.get('2')}")
                        print(f"  Language: {item.get('5')}")
                        print()
                
                if total > 3:
                    print(f"⚠️ WARNING: {total - 3} duplicate translations found!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        kill_session(glpi_url, tokens[0], session)

if __name__ == "__main__":
    main()
