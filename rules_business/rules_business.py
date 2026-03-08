import requests
import json
import os
import sys
import urllib3
import argparse

# Suppress insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_FILE = 'config.json'
ENTITY_SLA_MAP_FILE = 'entity_sla_map.json'

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

def load_entity_sla_map():
    """Load entity to SLA service level mapping with robust path search"""
    search_paths = [
        os.path.join(os.path.dirname(__file__), ENTITY_SLA_MAP_FILE),
        os.path.join(os.path.dirname(__file__), '..', 'Config', ENTITY_SLA_MAP_FILE),
        os.path.join(os.path.dirname(__file__), '..', '..', 'Config', ENTITY_SLA_MAP_FILE),
        ENTITY_SLA_MAP_FILE
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    print(f"Warning: {ENTITY_SLA_MAP_FILE} not found. SLA assignment will fail.")
    return {}

def init_session(url, app_token, user_token):
    headers = {"App-Token": app_token, "Authorization": f"user_token {user_token}", "Content-Type": "application/json"}
    try:
        resp = requests.get(f"{url}/initSession", headers=headers, verify=False, timeout=30)
        resp.raise_for_status()
        return resp.json().get('session_token')
    except Exception as e:
        print(f"Session init failed: {e}")
        sys.exit(1)

def kill_session(url, app_token, session_token):
    headers = {"App-Token": app_token, "Session-Token": session_token}
    try:
        requests.get(f"{url}/killSession", headers=headers, verify=False, timeout=10)
    except:
        pass

def fetch_all_entities(url, headers):
    entities = {}
    range_start = 0
    range_step = 1000
    
    print("Fetching Entities...")
    while True:
        range_end = range_start + range_step
        params = {"range": f"{range_start}-{range_end}", "is_deleted": 0}
        
        try:
            resp = requests.get(f"{url}/Entity", headers=headers, params=params, verify=False, timeout=30)
            if resp.status_code not in [200, 206]:
                break
                
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

def fetch_slas_by_service_level(url, headers):
    slm_map = {} 
    
    # 1. Fetch SLMs
    print("Fetching SLMs...")
    range_start = 0
    range_step = 200
    try:
        while True:
            params = {"range": f"{range_start}-{range_start+range_step}", "is_deleted": 0}
            r = requests.get(f"{url}/SLM", headers=headers, params=params, verify=False, timeout=30)
            if r.status_code not in [200, 206]: break
            batch = r.json()
            if not batch: break
            for slm in batch:
                slm_map[slm['id']] = slm['name']
            if len(batch) < range_step: break
            range_start += range_step
    except Exception as e:
        print(f"Error fetching SLMs: {e}")
        return {}

    sla_structure = {} 
    
    # 2. Fetch SLAs
    print("Fetching SLAs...")
    range_start = 0
    range_step = 1000
    try:
        while True:
            params = {"range": f"{range_start}-{range_start+range_step}", "is_deleted": 0}
            r = requests.get(f"{url}/SLA", headers=headers, params=params, verify=False, timeout=30)
            if r.status_code not in [200, 206]: break
            batch = r.json()
            if not batch: break
            
            for item in batch:
                slm_id = item.get('slms_id')
                if not slm_id: continue
                
                slm_name = None
                if isinstance(slm_id, int):
                    slm_name = slm_map.get(slm_id)
                elif isinstance(slm_id, str):
                     if slm_id.isdigit() and int(slm_id) in slm_map:
                         slm_name = slm_map[int(slm_id)]
                
                if not slm_name: continue 
                
                if slm_name not in sla_structure:
                    sla_structure[slm_name] = {}
                
                sla_name = item.get('name') 
                sla_type = item.get('type') # 0=TTR, 1=TTO
                type_str = "TTR" if sla_type == 0 else "TTO"
                
                priority_key = None
                for p in ["P1", "P2", "P3", "P4", "P5"]:
                    if p in sla_name:
                        priority_key = p
                        break
                
                if not priority_key: continue
                
                if priority_key not in sla_structure[slm_name]:
                    sla_structure[slm_name][priority_key] = {}
                
                # Store ID and Name for display
                sla_structure[slm_name][priority_key][type_str] = {
                    "id": item.get('id'),
                    "name": sla_name
                }
            
            if len(batch) < range_step: break
            range_start += range_step
            
    except Exception as e:
        print(f"Error fetching SLAs: {e}")
        
    return sla_structure

def fetch_existing_rules(url, headers):
    existing_rules = {} # Name -> ID
    print("Fetching existing Business Rules via Search...")
    
    range_start = 0
    range_step = 100
    
    try:
        while True:
            params = {
                "criteria[0][field]": "1", # Name
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": "Auto-BR-", # Common prefix
                "forcedisplay[0]": "2", # ID
                "range": f"{range_start}-{range_start+range_step}",
                "is_deleted": 0
            }
            
            r = requests.get(f"{url}/search/RuleTicket", headers=headers, params=params, verify=False, timeout=30)
            if r.status_code not in [200, 206]: break
            
            data = r.json()
            if 'data' not in data: break
            
            for item in data['data']:
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
    r = requests.get(f"{url}/RuleTicket/{rule_id}/RuleAction", headers=headers, params={"range": "0-5000"}, verify=False, timeout=30)
    if r.status_code in [200, 206]:
        for item in r.json():
            if str(item.get('rules_id')) == str(rule_id):
                requests.delete(f"{url}/RuleTicket/{rule_id}/RuleAction/{item['id']}", headers=headers, verify=False, timeout=30)
            
    # Clear Criteria
    r = requests.get(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, params={"range": "0-5000"}, verify=False, timeout=30)
    if r.status_code in [200, 206]:
        for item in r.json():
            if str(item.get('rules_id')) == str(rule_id):
                requests.delete(f"{url}/RuleTicket/{rule_id}/RuleCriteria/{item['id']}", headers=headers, verify=False, timeout=30)

def create_or_update_rule(url, headers, rule_name, criteria_list, action_list, existing_rules_map, dry_run=True):
    rule_input = {
        "name": rule_name,
        "match": "AND",
        "is_active": 1,
        "sub_type": "RuleTicket",
        "ranking": 1,    # High ranking for these rules
        "is_recursive": 1,
        "condition": 3,
        "entities_id": 0 # Root
    }

    if rule_name in existing_rules_map:
        # UPDATE
        rule_id = existing_rules_map[rule_name]
        if dry_run:
             print(f"[DRY RUN] Would UPDATE Rule '{rule_name}' (ID: {rule_id}) -> Full Recreation")
             return

        print(f"Updating Rule '{rule_name}' (ID: {rule_id})")
        
        try:
             # Full Update: Clear and Re-add
             clear_rule_details(url, headers, rule_id)
             
             # Re-apply Properties (Active etc)
             payload = {"input": rule_input}
             payload["input"]["id"] = rule_id
             requests.put(f"{url}/RuleTicket/{rule_id}", headers=headers, json=payload, verify=False, timeout=30)
             
             # Add Criteria
             for crit in criteria_list:
                crit_payload = {"input": { "rules_id": rule_id, **crit }}
                requests.post(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, json=crit_payload, verify=False, timeout=30)

             # Add Actions
             for act in action_list:
                 act_payload = {"input": { "rules_id": rule_id, "action_type": "assign", **act }}
                 requests.post(f"{url}/RuleTicket/{rule_id}/RuleAction", headers=headers, json=act_payload, verify=False, timeout=30)
             
             print("  - Updated and refreshed criteria/actions.")

        except Exception as e:
            print(f"Failed to update rule '{rule_name}': {e}")
            
    else:
        # CREATE
        if dry_run:
            print(f"[DRY RUN] Creating Rule: '{rule_name}'")
            return

        payload = {"input": rule_input}
        
        try:
            r = requests.post(f"{url}/RuleTicket", headers=headers, json=payload, verify=False, timeout=30)
            r.raise_for_status()
            rule_id = r.json().get('id')
            print(f"Created Rule '{rule_name}' (ID: {rule_id})")
            
            # Add Criteria
            for crit in criteria_list:
                crit_payload = {"input": { "rules_id": rule_id, **crit }}
                requests.post(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, json=crit_payload, verify=False, timeout=30)
                
            # Add Actions
            for act in action_list:
                 act_payload = {"input": { "rules_id": rule_id, "action_type": "assign", **act }}
                 requests.post(f"{url}/RuleTicket/{rule_id}/RuleAction", headers=headers, json=act_payload, verify=False, timeout=30)
                 
            existing_rules_map[rule_name] = rule_id

        except Exception as e:
            print(f"Failed to create rule '{rule_name}': {e}")


def main():
    parser = argparse.ArgumentParser(description="Create or Update Business Rules for Email Tickets")
    parser.add_argument('--force', action='store_true', help="Execute changes (default is dry-run)")
    parser.add_argument('--priority', default='P3', help="Default priority (P1-P5, default: P3)")
    parser.add_argument('--category', default='Genel Destek', help="Default category name (ID lookup needed for full robustness, defaulting ID 227)")
    args = parser.parse_args()
    
    dry_run = not args.force
    display_mode = "LIVE" if not dry_run else "DRY RUN"
    print(f"--- GLPI Business Rule Creator ({display_mode}) ---")

    config = load_config()
    entity_map = load_entity_sla_map()
    
    glpi_url = config.get('GLPI_URL').rstrip('/')
    session_token = init_session(glpi_url, config['GLPI_APP_TOKEN'], config['GLPI_USER_TOKEN'])
    headers = {"App-Token": config['GLPI_APP_TOKEN'], "Session-Token": session_token, "Content-Type": "application/json"}
    
    try:
        print("Fetching Entities, SLAs, and Existing Rules...")
        entities = fetch_all_entities(glpi_url, headers)
        sla_data = fetch_slas_by_service_level(glpi_url, headers)
        existing_rules_map = fetch_existing_rules(glpi_url, headers)
        
        # Priority Map: P3 -> 3, etc.
        prio_map_val = {'P1': 5, 'P2': 4, 'P3': 3, 'P4': 2, 'P5': 1}
        target_prio_val = prio_map_val.get(args.priority, 3)
        
        # NOTE: Hardcoded category ID 227 per previous script logic, 
        # but ideally should search category name. Keeping simple for now to match behavior.
        category_id = 227 
        
        print(f"Loaded {len(entities)} entities, {len(sla_data)} SLMs, {len(existing_rules_map)} existing rules.")
        print("\n--- Starting Processing ---\n")

        for entity_name, service_level_name in entity_map.items():
            if entity_name not in entities:
                print(f"SKIP: Entity '{entity_name}' not found.")
                continue
            
            if service_level_name not in sla_data:
                print(f"Warning: Service Level '{service_level_name}' not found or has no SLAs.")
                # We can still proceed but without SLA assignment if desired, 
                # but better to skip or warn.
            
            entity_id = entities[entity_name]
            # Replace spaces in entity name with hyphens for consistent naming
            entity_name_clean = entity_name.replace(' ', '-')
            rule_name = f"Auto-BR-{entity_name_clean}"
            
            # Find SLA IDs for the requested priority (e.g. P3)
            tto_id, ttr_id = None, None
            tto_name, ttr_name = None, None
            
            if service_level_name in sla_data:
                p_slas = sla_data[service_level_name].get(args.priority)
                if p_slas:
                    if 'TTO' in p_slas:
                        tto_id = p_slas['TTO']['id']
                        tto_name = p_slas['TTO']['name']
                    if 'TTR' in p_slas:
                        ttr_id = p_slas['TTR']['id']
                        ttr_name = p_slas['TTR']['name']

            # Criteria
            # 1. Entity is X
            # 2. Source is Email (2)
            # 3. Type is NOT Incident (1) -> so Request? Check logic.
            # Old script was: criteria 'type', condition 1 (is not), pattern 1 (Incident).
            # This means it applies to Requests coming via Email? Or just everything not Incident.
            criteria = [
                {"criteria": "entities_id", "condition": 0, "pattern": entity_id},
                {"criteria": "requesttypes_id", "condition": 0, "pattern": 2}, # Email
                {"criteria": "type", "condition": 1, "pattern": 1} # Not Incident
            ]
            
            # Actions
            actions = [
                {"field": "itilcategories_id", "value": category_id},
                {"field": "priority", "value": target_prio_val}
            ]
            
            if tto_id:
                actions.append({"field": "slas_id_tto", "value": tto_id})
            else:
                print(f"  WARNING: SLA TTO not found for {entity_name} - {args.priority}")
                
            if ttr_id:
                actions.append({"field": "slas_id_ttr", "value": ttr_id})
            else:
                print(f"  WARNING: SLA TTR not found for {entity_name} - {args.priority}")

            create_or_update_rule(glpi_url, headers, rule_name, criteria, actions, existing_rules_map, dry_run=dry_run)

    except Exception as e:
        print(f"Major Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        kill_session(glpi_url, config['GLPI_APP_TOKEN'], session_token)

if __name__ == "__main__":
    main()
