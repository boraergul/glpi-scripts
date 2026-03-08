import requests
import json
import os
import sys
import urllib3
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
CONFIG_FILE = 'config.json'

def load_config():
    """Load configuration from config.json with robust path searching"""
    search_paths = [
        os.path.join(os.path.dirname(__file__), CONFIG_FILE),
        os.path.join(os.path.dirname(__file__), '..', 'Config', CONFIG_FILE),
        os.path.join(os.path.dirname(__file__), '..', '..', 'Config', CONFIG_FILE),
        CONFIG_FILE # Current working directory fallback
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
    print(f"Error: File {CONFIG_FILE} not found in any of the search paths:")
    for path in search_paths:
        print(f"  - {os.path.abspath(path)}")
    sys.exit(1)

def init_session(url, app_token, user_token):
    headers = {"App-Token": app_token, "Authorization": f"user_token {user_token}"}
    try:
        resp = requests.get(f"{url}/initSession", headers=headers, verify=False)
        resp.raise_for_status()
        return resp.json()['session_token']
    except Exception as e:
        print(f"Failed to initialize session: {e}")
        sys.exit(1)

def kill_session(url, app_token, session_token):
    headers = {"App-Token": app_token, "Session-Token": session_token}
    try:
        requests.get(f"{url}/killSession", headers=headers, verify=False)
    except:
        pass

def fetch_group_id(url, headers, name, parent_id=None):
    # Search for group by name
    # Criteria: Name equals name
    params = {
        "criteria[0][field]": 1,
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": name,
        "forcedisplay[0]": 2, # ID
        "forcedisplay[1]": 49 # Parent group
    }
    
    r = requests.get(f"{url}/search/Group", headers=headers, params=params, verify=False)
    if r.status_code in [200, 206]:
        data = r.json().get('data', [])
        for item in data:
            gid = item.get('2')
            return gid 
    return None

def find_group_reliable(url, headers, name, parent_id=None):
    # Retrieve groups with matching name (Contains search)
    params = {
        "range": "0-100", 
        "searchText[name]": name, # Contains search
        "forcedisplay[0]": 2,  # ID
        "forcedisplay[1]": 49  # Parent Group
    }
    r = requests.get(f"{url}/search/Group", headers=headers, params=params, verify=False)
    
    if r.status_code in [200, 206]:
        data = r.json().get('data', [])
        
        for item in data:
            gid = item.get('2')
            
            g_r = requests.get(f"{url}/Group/{gid}", headers=headers, verify=False)
            if g_r.status_code == 200:
                g_data = g_r.json()
                g_real_name = g_data.get('name')
                g_parent = g_data.get('groups_id')
                
                # Check Name Match (Case Insensitive strip)
                if g_real_name.strip().lower() == name.strip().lower():
                    # Check Parent if required
                    if parent_id is not None:
                        if str(g_parent) == str(parent_id):
                             return gid
                    else:
                        return gid
                
    return None

def fetch_all_entities(url, headers):
    entities = []
    range_start = 0
    range_step = 1000
    
    while True:
        range_end = range_start + range_step
        params = {"range": f"{range_start}-{range_end}", "is_deleted": 0}
        resp = requests.get(f"{url}/Entity", headers=headers, params=params, verify=False)
        
        if resp.status_code not in [200, 206]:
            break
            
        batch = resp.json()
        if not batch: break
        
        entities.extend(batch)
        if len(batch) < range_step: break
        range_start += range_step
        
    return entities

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true', help="Execute changes")
    args = parser.parse_args()
    
    dry_run = not args.force
    
    config = load_config()
    glpi_url = config['GLPI_URL'].rstrip('/')
    session_token = init_session(glpi_url, config['GLPI_APP_TOKEN'], config['GLPI_USER_TOKEN'])
    headers = {"App-Token": config['GLPI_APP_TOKEN'], "Session-Token": session_token, "Content-Type": "application/json"}
    
    try:
        print("--- Sync Entities to Groups ---")
        
        # 1. Find 'Ultron Bilişim'
        ultron_id = find_group_reliable(glpi_url, headers, "Ultron Bilişim")
        if not ultron_id:
            print("ERROR: Group 'Ultron Bilişim' not found!")
            return
        print(f"Found 'Ultron Bilişim': {ultron_id}")
        
        # 2. Find 'Müşteriler' (Parent: Ultron Bilişim)
        musteriler_id = find_group_reliable(glpi_url, headers, "Müşteriler", parent_id=ultron_id)
        if not musteriler_id:
            print(f"ERROR: Group 'Müşteriler' (under Ultron Bilişim {ultron_id}) not found!")
            # Fallback: Maybe search Müşteriler without parent check just to see?
            # But user insisted on hierarchy.
            return
        print(f"Found 'Müşteriler': {musteriler_id}")
        
        # 3. List Entities and Sync
        entities = fetch_all_entities(glpi_url, headers)
        print(f"Found {len(entities)} Entities.")
        
        for ent in entities:
            e_name = ent['name']
            
            # Skip Root or Templates or Parent Groups themselves
            # We don't want to create "Ultron Bilişim" under "Müşteriler" if Ultron Bilişim is also an entity.
            skip_names = ['Root Entity', 'Root', 'Ultron Bilişim', 'Müşteriler']
            if e_name in skip_names: 
                print(f"SKIP: Excluded Entity '{e_name}'")
                continue
                
            # Check if Group exists under Müşteriler
            # We search for Group Name = e_name AND Parent = musteriler_id
            target_group_id = find_group_reliable(glpi_url, headers, e_name, parent_id=musteriler_id)
            
            if target_group_id:
                print(f"SKIP: Group '{e_name}' already exists (ID: {target_group_id})")
            else:
                if dry_run:
                    print(f"PROPOSE: Create Group '{e_name}' under 'Müşteriler'")
                else:
                    # Create
                    payload = {
                        "input": {
                            "name": e_name,
                            "groups_id": musteriler_id, # Parent
                            "is_recursive": 1, # Usually groups are recursive?
                            "entities_id": 0   # Defines visibility. 0 = Root (visible everywhere)
                        }
                    }
                    c_r = requests.post(f"{glpi_url}/Group", headers=headers, json=payload, verify=False)
                    if c_r.status_code == 201:
                        new_id = c_r.json().get('id')
                        print(f"CREATED: Group '{e_name}' (ID: {new_id})")
                    else:
                        print(f"FAILED to check/create '{e_name}': {c_r.status_code} {c_r.text}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        kill_session(glpi_url, config['GLPI_APP_TOKEN'], session_token)

if __name__ == "__main__":
    main()
