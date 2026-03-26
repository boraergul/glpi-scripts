import requests
import json
import os
import sys
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
CALENDARS_FILE = os.path.join(os.path.dirname(__file__), 'calendars_export.json')
SLMS_FILE = os.path.join(os.path.dirname(__file__), 'slms_export.json')

def load_json(path):
    if not os.path.exists(path):
        print(f"Error: File not found at {path}")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

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

def get_all_items_simple(url, headers, item_type):
    """
    Get all items of a type (simplified version for duplicate check).
    """
    items = []
    range_start = 0
    range_step = 100
    
    while True:
        range_end = range_start + range_step
        params = {"range": f"{range_start}-{range_end}"}
        
        try:
            r = requests.get(f"{url}/{item_type}", headers=headers, params=params, verify=False)
            if r.status_code not in [200, 206]:
                break
            data = r.json()
            if not isinstance(data, list) or len(data) == 0:
                break
            items.extend(data)
            if len(data) < range_step:
                break
            range_start += range_step
        except:
            break
    
    return items

def search_item_by_name(url, headers, item_type, name):
    """
    Search for an item by name using direct GET.
    Returns the ID if found, else None.
    """
    items = get_all_items_simple(url, headers, item_type)
    for item in items:
        if item.get('name') == name:
            return item.get('id')
    return None

def create_item(url, headers, item_type, payload):
    try:
        r = requests.post(f"{url}/{item_type}", headers=headers, json={"input": payload}, verify=False)
        r.raise_for_status()
        return r.json().get('id')
    except Exception as e:
        print(f"Failed to create {item_type}: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(e.response.text)
        return None

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
        # --- PHASE 1: IMPORT CALENDARS ---
        print("\n--- Phase 1: Importing Calendars ---")
        calendars_data = load_json(CALENDARS_FILE)
        calendars_list = calendars_data.get('Calendar', [])
        
        calendar_map = {} # Old_ID -> New_ID
        
        for cal in calendars_list:
            old_id = cal.get('id')
            name = cal.get('name')
            
            existing_id = search_item_by_name(glpi_url, headers, "Calendar", name)
            
            if existing_id:
                print(f"Calendar '{name}' exists (ID: {existing_id}). Mapping Old ID {old_id} -> {existing_id}")
                calendar_map[old_id] = existing_id
            else:
                payload = {
                    "name": name,
                    "entities_id": cal.get('entities_id', 0),
                    "is_recursive": cal.get('is_recursive', 1),
                    "comment": cal.get('comment', ''),
                    "cache_duration": cal.get('cache_duration')
                }
                new_id = create_item(glpi_url, headers, "Calendar", payload)
                if new_id:
                     print(f"CREATED Calendar '{name}' (ID: {new_id}). Mapping Old ID {old_id} -> {new_id}")
                     calendar_map[old_id] = new_id
        
        # --- PHASE 2: IMPORT SLMs (Containers) ---
        print("\n--- Phase 2: Importing SLM Containers ---")
        slms_data = load_json(SLMS_FILE)
        slms_list = slms_data.get('SLM', [])
        
        slm_map = {} # Old_SLM_ID -> New_SLM_ID
        
        for slm in slms_list:
            old_id = slm.get('id')
            name = slm.get('name')
            
            existing_id = search_item_by_name(glpi_url, headers, "SLM", name)
            
            if existing_id:
                print(f"SLM '{name}' exists (ID: {existing_id}). Mapping Old ID {old_id} -> {existing_id}")
                slm_map[old_id] = existing_id
            else:
                # Get calendar ID if exists
                old_cal_id = slm.get('calendars_id', 0)
                new_cal_id = calendar_map.get(old_cal_id, 0)
                
                payload = {
                    "name": name,
                    "entities_id": slm.get('entities_id', 0),
                    "is_recursive": slm.get('is_recursive', 1),
                    "comment": slm.get('comment', ''),
                    "calendars_id": new_cal_id,
                    "use_ticket_calendar": slm.get('use_ticket_calendar', 0)
                }
                new_id = create_item(glpi_url, headers, "SLM", payload)
                if new_id:
                    print(f"CREATED SLM '{name}' (ID: {new_id}). Mapping Old ID {old_id} -> {new_id}")
                    slm_map[old_id] = new_id
        
        # --- PHASE 3: IMPORT SLAs (Rules) ---
        print("\n--- Phase 3: Importing SLA Rules ---")
        slas_list = slms_data.get('SLA', [])
        
        for sla in slas_list:
            name = sla.get('name')
            
            # Resolve Calendar ID
            old_cal_id = sla.get('calendars_id', 0)
            new_cal_id = calendar_map.get(old_cal_id, 0)
            
            # Resolve SLM ID (CRITICAL!)
            old_slm_id = sla.get('slms_id', 0)
            new_slm_id = slm_map.get(old_slm_id, 0)
            
            if old_slm_id and not new_slm_id:
                print(f"Warning: SLM ID {old_slm_id} not found in map for SLA '{name}'. Skipping.")
                continue
            
            # Check if SLA exists
            existing_id = search_item_by_name(glpi_url, headers, "SLA", name)
            
            if existing_id:
                print(f"SLA '{name}' exists (ID: {existing_id}). Skipping.")
            else:
                payload = {
                     "name": name,
                     "entities_id": sla.get('entities_id', 0),
                     "is_recursive": sla.get('is_recursive', 1),
                     "type": sla.get('type', 1), # 0=TTR, 1=TTO
                     "number_time": sla.get('number_time'),
                     "definition_time": sla.get('definition_time'),
                     "end_of_working_day": sla.get('end_of_working_day', 0),
                     "calendars_id": new_cal_id,
                     "slms_id": new_slm_id,  # Link to parent SLM
                     "use_ticket_calendar": sla.get('use_ticket_calendar', 0),
                     "comment": sla.get('comment', ''),
                }
                
                new_id = create_item(glpi_url, headers, "SLA", payload)
                if new_id:
                    print(f"CREATED SLA '{name}' (ID: {new_id})")
    
    finally:
        kill_session(glpi_url, app_token, session_token)
        print("\nImport Finished.")

if __name__ == "__main__":
    main()
