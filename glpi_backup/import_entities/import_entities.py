import requests
import json
import os
import sys
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config_target.json')
IMPORT_FILE = os.path.join(os.path.dirname(__file__), 'entities_export.json')

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

def get_all_entities_simple(url, headers):
    """
    Get all entities from target GLPI for duplicate check.
    """
    entities = []
    range_start = 0
    range_step = 100
    
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
        except:
            break
    
    return entities

def search_entity_by_name(existing_entities, name):
    """
    Search for an entity by name.
    Returns the entity if found, else None.
    """
    for entity in existing_entities:
        if entity.get('name') == name:
            return entity
    return None

def needs_update(existing, new_data):
    """
    Check if entity needs update by comparing key fields.
    """
    fields_to_compare = ['comment', 'address', 'postcode', 'town', 'state', 
                         'country', 'website', 'phonenumber', 'fax', 'email']
    
    for field in fields_to_compare:
        if existing.get(field) != new_data.get(field):
            return True
    return False

def create_entity(url, headers, payload):
    try:
        r = requests.post(f"{url}/Entity", headers=headers, json={"input": payload}, verify=False)
        r.raise_for_status()
        return r.json().get('id')
    except Exception as e:
        print(f"Failed to create entity: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(e.response.text)
        return None

def update_entity(url, headers, entity_id, payload):
    try:
        r = requests.put(f"{url}/Entity/{entity_id}", headers=headers, json={"input": payload}, verify=False)
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"Failed to update entity: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(e.response.text)
        return False

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
        # Load import data
        import_data = load_json(IMPORT_FILE)
        entities_to_import = import_data.get('entities', [])
        
        print(f"\n--- Importing {len(entities_to_import)} entities ---")
        
        # Get existing entities for duplicate check
        print("Fetching existing entities...")
        existing_entities = get_all_entities_simple(glpi_url, headers)
        print(f"Found {len(existing_entities)} existing entities.")
        
        # ID mapping: old_id -> new_id
        id_map = {}
        
        # Process entities in order (hierarchical)
        for entity in entities_to_import:
            old_id = entity.get('id')
            name = entity.get('name')
            old_parent_id = entity.get('entities_id', 0)
            
            # Map parent ID
            new_parent_id = id_map.get(old_parent_id, old_parent_id)
            
            # Check if exists
            existing = search_entity_by_name(existing_entities, name)
            
            if existing:
                existing_id = existing['id']
                id_map[old_id] = existing_id
                
                # Check if update needed
                if needs_update(existing, entity):
                    # Update
                    payload = {
                        "id": existing_id,
                        "comment": entity.get('comment', ''),
                        "address": entity.get('address', ''),
                        "postcode": entity.get('postcode', ''),
                        "town": entity.get('town', ''),
                        "state": entity.get('state', ''),
                        "country": entity.get('country', ''),
                        "website": entity.get('website', ''),
                        "phonenumber": entity.get('phonenumber', ''),
                        "fax": entity.get('fax', ''),
                        "email": entity.get('email', ''),
                        "entities_id": new_parent_id
                    }
                    if update_entity(glpi_url, headers, existing_id, payload):
                        print(f"UPDATED Entity '{name}' (ID: {existing_id})")
                    else:
                        print(f"FAILED to update Entity '{name}'")
                else:
                    print(f"Entity '{name}' exists (ID: {existing_id}). No update needed.")
            else:
                # Create new
                payload = {
                    "name": name,
                    "entities_id": new_parent_id,
                    "comment": entity.get('comment', ''),
                    "address": entity.get('address', ''),
                    "postcode": entity.get('postcode', ''),
                    "town": entity.get('town', ''),
                    "state": entity.get('state', ''),
                    "country": entity.get('country', ''),
                    "website": entity.get('website', ''),
                    "phonenumber": entity.get('phonenumber', ''),
                    "fax": entity.get('fax', ''),
                    "email": entity.get('email', '')
                }
                new_id = create_entity(glpi_url, headers, payload)
                if new_id:
                    print(f"CREATED Entity '{name}' (ID: {new_id})")
                    id_map[old_id] = new_id
                    # Add to existing list for future duplicate checks
                    existing_entities.append({"id": new_id, "name": name})
        
    finally:
        kill_session(glpi_url, app_token, session_token)
        print("\nImport finished.")

if __name__ == "__main__":
    main()
