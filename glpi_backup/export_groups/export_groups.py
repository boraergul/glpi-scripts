import requests
import json
import os
import sys
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config_source.json')
EXPORT_FILE = os.path.join(os.path.dirname(__file__), 'groups_export.json')

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

def get_all_groups(url, headers):
    """
    Get all groups from GLPI.
    """
    groups = []
    range_start = 0
    range_step = 100
    
    print("Fetching groups...")
    
    while True:
        range_end = range_start + range_step
        params = {"range": f"{range_start}-{range_end}"}
        
        try:
            r = requests.get(f"{url}/Group", headers=headers, params=params, verify=False)
            if r.status_code not in [200, 206]:
                break
            data = r.json()
            if not isinstance(data, list) or len(data) == 0:
                break
            groups.extend(data)
            if len(data) < range_step:
                break
            range_start += range_step
        except Exception as e:
            print(f"Error fetching groups: {e}")
            break
    
    print(f"  Found {len(groups)} groups.")
    return groups

def build_hierarchy(groups):
    """
    Build hierarchical structure from flat group list.
    Returns groups sorted by hierarchy (parents before children).
    """
    # Sort by completename to ensure hierarchical order
    groups_sorted = sorted(groups, key=lambda x: x.get('completename', x.get('name', '')))
    
    return groups_sorted

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
        # Fetch all groups
        groups = get_all_groups(glpi_url, headers)
        
        # Build hierarchy
        groups_sorted = build_hierarchy(groups)
        
        # Export to JSON
        export_data = {
            "groups": groups_sorted,
            "total_count": len(groups_sorted)
        }
        save_json(export_data, EXPORT_FILE)
        
        # Print summary
        print(f"\n--- Export Summary ---")
        print(f"Total groups: {len(groups_sorted)}")
        print(f"\nFirst 10 groups:")
        for group in groups_sorted[:10]:
            print(f"  [{group['id']}] {group.get('completename', group.get('name'))}")
        
    finally:
        kill_session(glpi_url, app_token, session_token)
        print("\nExport finished.")

if __name__ == "__main__":
    main()
