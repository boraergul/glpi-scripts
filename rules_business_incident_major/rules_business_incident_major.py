import requests
import json
import os
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_FILE = 'config.json'
MAP_FILE = 'entity_sla_map.json'

# --- Configuration Loaders ---
def load_config():
    """Load configuration from config.json with robust path searching"""
    search_paths = [
        os.path.join(os.path.dirname(__file__), CONFIG_FILE),
        os.path.join(os.path.dirname(__file__), '..', 'Config', CONFIG_FILE),
        os.path.join(os.path.dirname(__file__), '..', '..', 'Config', CONFIG_FILE),
        CONFIG_FILE # Working dir
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
    print(f"Error: File {CONFIG_FILE} not found!")
    sys.exit(1)

def load_entity_sla_map():
    """Load entity to SLM mapping"""
    search_paths = [
        os.path.join(os.path.dirname(__file__), MAP_FILE),
        os.path.join(os.path.dirname(__file__), '..', 'Config', MAP_FILE),
        os.path.join(os.path.dirname(__file__), '..', '..', 'Config', MAP_FILE),
        MAP_FILE
    ]
    for path in search_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    print(f"Error: Map file {MAP_FILE} not found!")
    sys.exit(1)

# --- GLPI API Helpers ---
def init_session(url, app_token, user_token):
    headers = {"App-Token": app_token, "Authorization": f"user_token {user_token}", "Content-Type": "application/json"}
    try:
        resp = requests.get(f"{url}/initSession", headers=headers, verify=False)
        resp.raise_for_status()
        return resp.json().get('session_token')
    except Exception as e:
        print(f"Session init failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(e.response.text)
        sys.exit(1)

def kill_session(url, app_token, session_token):
    headers = {"App-Token": app_token, "Session-Token": session_token}
    try:
        requests.get(f"{url}/killSession", headers=headers, verify=False)
    except:
        pass

def fetch_all_entities(url, headers):
    entities = {}
    range_start = 0
    range_step = 1000
    
    print("Fetching Entities...")
    while True:
        params = {"range": f"{range_start}-{range_start+range_step}", "is_deleted": 0}
        try:
            resp = requests.get(f"{url}/Entity", headers=headers, params=params, verify=False)
            if resp.status_code not in [200, 206]: break
            batch = resp.json()
            if not batch: break
            
            for e in batch:
                entities[e['name']] = e['id']
            
            if len(batch) < range_step: break
            range_start += range_step
        except Exception as e:
            print(f"Error fetching entities: {e}")
            break
    return entities

def fetch_p1_slas(url, headers):
    """
    Fetches SLAs and returns a map: SLM Name -> { 'TTO': id, 'TTR': id }
    Only captures P1 (Fastest) SLAs based on naming convention (Priority 5 in GLPI logic = P1).
    """
    slm_map = {} 
    
    # 1. Fetch SLMs
    print("Fetching SLMs...")
    range_start = 0
    range_step = 200
    try:
        while True:
            params = {"range": f"{range_start}-{range_start+range_step}", "is_deleted": 0}
            r = requests.get(f"{url}/SLM", headers=headers, params=params, verify=False)
            if r.status_code not in [200, 206]: break
            batch = r.json()
            if not batch: break
            for item in batch:
                slm_map[item['id']] = item['name']
            if len(batch) < range_step: break
            range_start += range_step
    except Exception as e:
        print(f"Error fetching SLMs: {e}")
        return {}

    sla_p1_map = {} # SLM_Name -> {'TTO': id, 'TTR': id}
    
    # 2. Fetch SLAs
    print("Fetching SLAs (looking for P1)...")
    range_start = 0
    range_step = 1000
    try:
        while True:
            params = {"range": f"{range_start}-{range_start+range_step}", "is_deleted": 0}
            r = requests.get(f"{url}/SLA", headers=headers, params=params, verify=False)
            if r.status_code not in [200, 206]: break
            batch = r.json()
            if not batch: break
            
            for item in batch:
                slm_id = item.get('slms_id')
                if not slm_id: continue
                
                # Resolve SLM Name
                slm_name = None
                if isinstance(slm_id, int): slm_name = slm_map.get(slm_id)
                elif isinstance(slm_id, str) and slm_id.isdigit(): slm_name = slm_map.get(int(slm_id))
                
                if not slm_name: continue
                
                # Filter for P1 (Highest Priority / Fastest SLA)
                # Naming convention assumed: " ... P1" or GLPI logic
                # The user's previous scripts map GLPI Priority 5 -> P1.
                # So we look for "P1" in the SLA name.
                sla_name = item.get('name', '')
                if "P1" not in sla_name:
                    continue
                    
                if slm_name not in sla_p1_map:
                    sla_p1_map[slm_name] = {}
                
                # Type 0=TTR, 1=TTO
                sla_type = item.get('type')
                type_key = "TTR" if sla_type == 0 else "TTO"
                
                sla_p1_map[slm_name][type_key] = item.get('id')
            
            if len(batch) < range_step: break
            range_start += range_step
            
    except Exception as e:
        print(f"Error fetching SLAs: {e}")
        
    return sla_p1_map

def fetch_existing_rules(url, headers):
    existing_rules = {} # Name -> ID
    print("Fetching existing rules via Search...")
    
    # We will search for all rules (empty criteria usually returns all, or we search by our prefix)
    # Searching for "Auto-Major-Incident" covers our rules (with hyphens, not spaces)
    range_start = 0
    range_step = 100
    
    try:
        while True:
            params = {
                "criteria[0][field]": "1", # Name
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": "Auto-Major-Incident",  # Fixed: Use hyphens to match actual rule names
                "forcedisplay[0]": "2", # ID
                "range": f"{range_start}-{range_start+range_step}",
                "is_deleted": 0
            }
            
            r = requests.get(f"{url}/search/RuleTicket", headers=headers, params=params, verify=False)
            if r.status_code not in [200, 206]: break
            
            data = r.json()
            if 'data' not in data: break
            
            for item in data['data']:
                # Item format specific to search: {"1": "Name", "2": ID, ...}
                # We need to map field IDs to names based on what we see in debug or standard mapping
                # Field 1 is Name, Field 2 is ID (requested via forcedisplay)
                r_name = item.get('1')
                r_id = item.get('2')
                if r_name and r_id:
                    existing_rules[r_name] = r_id
            
            total_count = data.get('totalcount', 0)
            if range_start + range_step >= total_count:
                break
                
            range_start += range_step
            
    except Exception as e:
        print(f"Warning: Could not fetch existing rules: {e}")
        
    return existing_rules

def clear_rule_details(url, headers, rule_id):
    # Clear Actions
    r = requests.get(f"{url}/RuleTicket/{rule_id}/RuleAction", headers=headers, params={"range": "0-5000"}, verify=False)
    if r.status_code in [200, 206]:
        for item in r.json():
            # CRITICAL FIX: The API might return actions for OTHER rules. Verify ID match.
            if str(item.get('rules_id')) == str(rule_id):
                requests.delete(f"{url}/RuleTicket/{rule_id}/RuleAction/{item['id']}", headers=headers, verify=False)
            
    # Clear Criteria
    r = requests.get(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, params={"range": "0-5000"}, verify=False)
    if r.status_code in [200, 206]:
        for item in r.json():
            # CRITICAL FIX: Verify ID match for Criteria too.
            if str(item.get('rules_id')) == str(rule_id):
                requests.delete(f"{url}/RuleTicket/{rule_id}/RuleCriteria/{item['id']}", headers=headers, verify=False)

def create_or_update_rule(url, headers, rule_name, criteria_list, action_list, existing_rules_map, dry_run=True):
    rule_input = {
        "name": rule_name,
        "match": "AND",
        "is_active": 1,
        "sub_type": "RuleTicket",
        "entities_id": 0, # Root
        "is_recursive": 1,
        "condition": 3, # 3=Add/Update
        "ranking": 10 # High ranking for Major Incidents
    }

    if rule_name in existing_rules_map:
        rule_id = existing_rules_map[rule_name]
        if dry_run:
            print(f"[DRY RUN] Would UPDATE Rule '{rule_name}' (ID: {rule_id})")
            return

        print(f"Updating Rule '{rule_name}' (ID: {rule_id})")
        try:
             requests.put(f"{url}/RuleTicket/{rule_id}", headers=headers, json={"input": {"id": rule_id, **rule_input}}, verify=False)
             clear_rule_details(url, headers, rule_id)
             
             for crit in criteria_list:
                requests.post(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, json={"input": {"rules_id": rule_id, **crit}}, verify=False, timeout=30)

             for act in action_list:
                 requests.post(f"{url}/RuleTicket/{rule_id}/RuleAction", headers=headers, json={"input": {"rules_id": rule_id, **act}}, verify=False)
             
             print("  - Updated.")
        except Exception as e:
            print(f"Failed to update rule '{rule_name}': {e}")
    else:
        if dry_run:
            print(f"[DRY RUN] Creating Rule: '{rule_name}'")
            print(f"  - Criteria: {criteria_list}")
            print(f"  - Actions: {action_list}")
            return

        try:
            r = requests.post(f"{url}/RuleTicket", headers=headers, json={"input": rule_input}, verify=False, timeout=30)
            r.raise_for_status()
            rule_id = r.json().get('id')
            print(f"Created Rule '{rule_name}' (ID: {rule_id})")
            
            for crit in criteria_list:
                requests.post(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, json={"input": {"rules_id": rule_id, **crit}}, verify=False, timeout=30)
                
            for act in action_list:
                 requests.post(f"{url}/RuleTicket/{rule_id}/RuleAction", headers=headers, json={"input": {"rules_id": rule_id, **act}}, verify=False, timeout=30)
                 
            existing_rules_map[rule_name] = rule_id
        except Exception as e:
            print(f"Failed to create rule '{rule_name}': {e}")

# --- Main ---
def main():
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        dry_run = False
        
    print(f"--- GLPI Major Incident Rule Creator ({'DRY RUN' if dry_run else 'LIVE'}) ---")
    
    # CONSTANTS
    MAJOR_INCIDENT_CATEGORY_ID = 229
    MAJOR_PRIORITY_ID = 6
    MAJOR_INCIDENT_GROUP_ID = 45 

    config = load_config()
    entity_map = load_entity_sla_map()
    
    glpi_url = config.get('GLPI_URL').rstrip('/')
    session_token = init_session(glpi_url, config['GLPI_APP_TOKEN'], config['GLPI_USER_TOKEN'])
    headers = {"App-Token": config['GLPI_APP_TOKEN'], "Session-Token": session_token, "Content-Type": "application/json"}
    
    try:
        entities = fetch_all_entities(glpi_url, headers)
        sla_p1_map = fetch_p1_slas(glpi_url, headers)
        existing_rules_map = fetch_existing_rules(glpi_url, headers)
        
        print("\n--- Processing Entities ---")
        for entity_name, service_level_name in entity_map.items():
            if entity_name not in entities:
                print(f"SKIP: Entity '{entity_name}' not found.")
                continue
                
            if service_level_name not in sla_p1_map:
                print(f"SKIP: No P1 SLAs found for Service Level '{service_level_name}'.")
                continue
                
            entity_id = entities[entity_name]
            p1_slas = sla_p1_map[service_level_name]
            
            tto_id = p1_slas.get('TTO')
            ttr_id = p1_slas.get('TTR')
            
            if not tto_id and not ttr_id:
                print(f"SKIP: Missing TTO/TTR IDs in P1 SLA for {service_level_name}")
                continue
                
            # Replace spaces in entity name with hyphens for consistent naming
            entity_name_clean = entity_name.replace(' ', '-')
            rule_name = f"Auto-Major-Incident-{entity_name_clean}"
            
            # Criteria
            # Priority 6 (Major) AND Category 229 (Major Incident) AND Entity matches
            criteria = [
                {"criteria": "priority", "condition": 0, "pattern": MAJOR_PRIORITY_ID},
                {"criteria": "itilcategories_id", "condition": 0, "pattern": MAJOR_INCIDENT_CATEGORY_ID},
                {"criteria": "entities_id", "condition": 0, "pattern": entity_id}
            ]
            
            # Actions
            # User Request: Technician group	Assign	Ultron Bilişim > Teknik Ekipler > Major Incident Ekibi
            actions = [
                {
                    "field": "_groups_id_assign",  # This is 'Technician group' (Requires underscore)
                    "value": MAJOR_INCIDENT_GROUP_ID, 
                    "action_type": "assign"       # This is 'Assign'
                }
            ]
            if tto_id: actions.append({"field": "slas_id_tto", "value": tto_id, "action_type": "assign"})
            if ttr_id: actions.append({"field": "slas_id_ttr", "value": ttr_id, "action_type": "assign"})
            
            # Stop detailed processing? Assuming yes to prevent other lower rules overriding
            actions.append({"field": "_stop_rules_processing", "value": 1, "action_type": "assign"})
            
            create_or_update_rule(glpi_url, headers, rule_name, criteria, actions, existing_rules_map, dry_run=dry_run)
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        kill_session(glpi_url, config['GLPI_APP_TOKEN'], session_token)

if __name__ == "__main__":
    main()
