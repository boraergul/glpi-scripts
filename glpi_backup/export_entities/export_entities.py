import requests
import json
import os
import sys
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config_source.json')
EXPORT_FILE = os.path.join(os.path.dirname(__file__), 'entities_export.json')

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

def get_all_entities(url, headers):
    """
    Get all entities from GLPI.
    """
    entities = []
    range_start = 0
    range_step = 100
    
    print("Fetching entities...")
    
    while True:
        range_end = range_start + range_step
        params = {"range": f"{range_start}-{range_end}"}
        
        try:
            r = requests.get(f"{url}/Entity", headers=headers, params=params, verify=False)
            if r.status_code not in [200, 206]:
                break
            data = r.json()
            if not isinstance(data, list) or len(data) == 0:
                break
            entities.extend(data)
            if len(data) < range_step:
                break
            range_start += range_step
        except Exception as e:
            print(f"Error fetching entities: {e}")
            break
    
    print(f"  Found {len(entities)} entities.")
    return entities

def build_hierarchy(entities):
    """
    Build hierarchical structure from flat entity list.
    Returns entities sorted by hierarchy (parents before children).
    """
    # Create a map of id -> entity
    entity_map = {e['id']: e for e in entities}
    
    # Sort by completename to ensure hierarchical order
    entities_sorted = sorted(entities, key=lambda x: x.get('completename', ''))
    
    return entities_sorted

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
        # Fetch all entities
        entities = get_all_entities(glpi_url, headers)
        
        # Build hierarchy
        entities_sorted = build_hierarchy(entities)
        
        # Export to JSON
        export_data = {
            "entities": entities_sorted,
            "total_count": len(entities_sorted)
        }
        save_json(export_data, EXPORT_FILE)
        
        # Print summary
        print(f"\n--- Export Summary ---")
        print(f"Total entities: {len(entities_sorted)}")
        print(f"\nFirst 10 entities:")
        for entity in entities_sorted[:10]:
            print(f"  [{entity['id']}] {entity.get('completename', entity.get('name'))}")
        
    finally:
        kill_session(glpi_url, app_token, session_token)
        print("\nExport finished.")

if __name__ == "__main__":
    main()
