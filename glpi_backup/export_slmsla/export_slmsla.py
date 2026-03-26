import requests
import json
import os
import sys
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Configuration
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
CALENDAR_EXPORT_FILE = os.path.join(os.path.dirname(__file__), 'calendars_export.json')
SLM_EXPORT_FILE = os.path.join(os.path.dirname(__file__), 'slms_export.json')

def load_json(path):
    if not os.path.exists(path):
        print(f"Error: File not found at {path}")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {path}")

def init_session(url, app_token, user_token):
    headers = {
        "App-Token": app_token,
        "Authorization": f"user_token {user_token}"
    }
    try:
        resp = requests.get(f"{url}/initSession", headers=headers, verify=False)
        resp.raise_for_status()
        return resp.json().get('session_token')
    except Exception as e:
        print(f"Session init failed: {e}")
        sys.exit(1)

def kill_session(url, app_token, session_token):
    headers = {
        "App-Token": app_token,
        "Session-Token": session_token
    }
    try:
        requests.get(f"{url}/killSession", headers=headers, verify=False)
    except:
        pass

def get_all_items(url, headers, item_type):
    """
    Generic function to get all items of a type using range.
    """
    items = []
    range_start = 0
    range_step = 100
    
    print(f"Fetching {item_type}...")
    
    while True:
        range_end = range_start + range_step
        params = {
            "range": f"{range_start}-{range_end}"
        }
        
        try:
            r = requests.get(f"{url}/{item_type}", headers=headers, params=params, verify=False)
            
            # 206 Partial Content or 200 OK
            if r.status_code not in [200, 206]:
                # If 400/404/etc, we might be out of range or error
                break
                
            data = r.json()
            if not isinstance(data, list):
                # Sometimes GLPI returns object if only one item or error/empty
                break
                
            if len(data) == 0:
                break
                
            items.extend(data)
            
            # If we got fewer items than step, we are done
            if len(data) < range_step:
                break
                
            range_start += range_step
            
        except Exception as e:
            print(f"Error fetching {item_type}: {e}")
            break
            
    print(f"  Found {len(items)} {item_type}.")
    return items

def main():
    config = load_json(CONFIG_FILE)
    glpi_url = config.get('GLPI_URL')
    if glpi_url.endswith('/'):
        glpi_url = glpi_url[:-1]
        
    app_token = config.get('GLPI_APP_TOKEN')
    user_token = config.get('GLPI_USER_TOKEN')
    
    session_token = init_session(glpi_url, app_token, user_token)
    headers = {
        "App-Token": app_token,
        "Session-Token": session_token,
        "Content-Type": "application/json"
    }
    
    try:
        # 1. Export Calendars (often linked in SLA)
        calendars = get_all_items(glpi_url, headers, "Calendar")
        
        calendar_export = {
            "Calendar": calendars
        }
        save_json(calendar_export, CALENDAR_EXPORT_FILE)

        # 2. Export SLMs (Service Level Management containers)
        slms = get_all_items(glpi_url, headers, "SLM")
        
        # 3. Export SLAs (Service Level Agreements - the actual rules)
        slas = get_all_items(glpi_url, headers, "SLA")
        
        # 4. Export SLA Levels (Escalation levels)
        sla_levels = get_all_items(glpi_url, headers, "SLALevel")
        
        slm_export = {
            "SLM": slms,
            "SLA": slas,
            "SLALevel": sla_levels
        }
        save_json(slm_export, SLM_EXPORT_FILE)
        
    finally:
        kill_session(glpi_url, app_token, session_token)
        print("Export finished.")

if __name__ == "__main__":
    main()
