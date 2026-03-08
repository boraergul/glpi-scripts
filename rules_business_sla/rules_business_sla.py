import requests
import json
import os
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_FILE = 'config.json'
MAP_FILE = 'entity_sla_map.json'

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

def init_session(url, app_token, user_token):
    headers = {"App-Token": app_token, "Authorization": f"user_token {user_token}", "Content-Type": "application/json"}
    try:
        resp = requests.get(f"{url}/initSession", headers=headers, verify=False, timeout=30)
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
    
    # 1. Fetch SLMs (Paginated)
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
    
    # 2. Fetch SLAs (Paginated)
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
                sla_type = item.get('type') 
                # GLPI: Type 0 is TTR, Type 1 is TTO.
                type_str = "TTR" if sla_type == 0 else "TTO"
                
                # Extract priority from SLA name
                priority_key = None
                for p in ["P1", "P2", "P3", "P4", "P5"]:
                    if p in sla_name:
                        priority_key = p
                        break
                
                if not priority_key:
                    continue
                
                if priority_key not in sla_structure[slm_name]:
                    sla_structure[slm_name][priority_key] = {}
                
                sla_structure[slm_name][priority_key][type_str] = item.get('id')
            
            if len(batch) < range_step: break
            range_start += range_step
            
    except Exception as e:
        print(f"Error fetching SLAs: {e}")
        
    return sla_structure

def fetch_existing_rules(url, headers):
    existing_rules = {} # Name -> ID
    print("Fetching existing rules via Search...")
    
    # Searching for "Auto-SLA" covers our rules (with hyphen, not space)
    range_start = 0
    range_step = 100
    
    try:
        while True:
            params = {
                "criteria[0][field]": "1", # Name
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": "Auto-SLA",  # Fixed: Use hyphen to match actual rule names
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
            # Safety Check: Verify ID match
            if str(item.get('rules_id')) == str(rule_id):
                requests.delete(f"{url}/RuleTicket/{rule_id}/RuleAction/{item['id']}", headers=headers, verify=False, timeout=30)
            
    # Clear Criteria
    r = requests.get(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, params={"range": "0-5000"}, verify=False, timeout=30)
    if r.status_code in [200, 206]:
        for item in r.json():
            # Safety Check: Verify ID match
            if str(item.get('rules_id')) == str(rule_id):
                requests.delete(f"{url}/RuleTicket/{rule_id}/RuleCriteria/{item['id']}", headers=headers, verify=False, timeout=30)

def create_or_update_rule(url, headers, rule_name, criteria_list, action_list, existing_rules_map, dry_run=True):
    # Standard Rule Properties
    rule_input = {
        "name": rule_name,
        "match": "AND",
        "is_active": 1,
        "sub_type": "RuleTicket",
        "entities_id": 0, # Create in Root
        "is_recursive": 1, # Recursive to children
        "condition": 3,  # 0: Add, 1: Update, 2: Add/Update (Changed to 2 based on feedback)
        "ranking": 15      # Required for proper ordering
    }

    if rule_name in existing_rules_map:
        # UPDATE
        rule_id = existing_rules_map[rule_name]
        if dry_run:
             print(f"[DRY RUN] Would UPDATE Rule '{rule_name}' (ID: {rule_id}) -> Full Recreation of Criteria/Actions")
             return

        print(f"Updating Rule '{rule_name}' (ID: {rule_id})")
        payload = {"input": rule_input}
        payload["input"]["id"] = rule_id
        
        # Update main rule properties
        try:
            requests.put(f"{url}/RuleTicket/{rule_id}", headers=headers, json=payload, verify=False, timeout=30)
            
            # CLEAR existing criteria/actions (Wipe and Rebuild logic like Major Incident script)
            clear_rule_details(url, headers, rule_id)

            # 1. Add Criteria
            for crit in criteria_list:
                crit_payload = {
                    "input": {
                        "rules_id": rule_id,
                        "criteria": crit['criteria'],
                        "condition": crit['condition'], 
                        "pattern": crit['pattern'] 
                    }
                }
                requests.post(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, json=crit_payload, verify=False, timeout=30)

            # 2. Add Actions
            for act in action_list:
                 act_payload = {
                    "input": {
                        "rules_id": rule_id,
                        "action_type": "assign",
                        "field": act['field'], 
                        "value": act['value']
                    }
                 }
                 requests.post(f"{url}/RuleTicket/{rule_id}/RuleAction", headers=headers, json=act_payload, verify=False, timeout=30)
            
            print("  - Updated and refreshed criteria/actions.")

        except Exception as e:
            print(f"Failed to update rule '{rule_name}': {e}")
            
    else:
        # CREATE
        if dry_run:
            print(f"[DRY RUN] Creating Rule: '{rule_name}' (Recursive, condition=3, ranking=15)")
            print(f"  - Criteria: {criteria_list}")
            print(f"  - Actions: {action_list}")
            return

        payload = {"input": rule_input}
        
        try:
            r = requests.post(f"{url}/RuleTicket", headers=headers, json=payload, verify=False, timeout=30)
            r.raise_for_status()
            rule_id = r.json().get('id')
            print(f"Created Rule '{rule_name}' (ID: {rule_id})")
            
            # 2. Add Criteria
            for crit in criteria_list:
                crit_payload = {
                    "input": {
                        "rules_id": rule_id,
                        "criteria": crit['criteria'],
                        "condition": crit['condition'], 
                        "pattern": crit['pattern'] 
                    }
                }
                requests.post(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, json=crit_payload, verify=False, timeout=30)
                
            # 3. Add Actions
            for act in action_list:
                 act_payload = {
                    "input": {
                        "rules_id": rule_id,
                        "action_type": "assign",
                        "field": act['field'], 
                        "value": act['value']
                    }
                 }
                 requests.post(f"{url}/RuleTicket/{rule_id}/RuleAction", headers=headers, json=act_payload, verify=False, timeout=30)
                 
            # Add to local cache
            existing_rules_map[rule_name] = rule_id

        except Exception as e:
            print(f"Failed to create rule '{rule_name}': {e}")
            if hasattr(e, 'response') and e.response is not None:
                 print(e.response.text)

def main():
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        dry_run = False

    print(f"--- GLPI SLA Rule Creator ({'DRY RUN' if dry_run else 'LIVE'}) ---")

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
        
        # GLPI Priority to SLA Priority mapping
        # GLPI: 5=Very High, 4=High, 3=Medium, 2=Low, 1=Very Low
        # SLA: P1=Fastest response (shortest time), P5=Slowest response (longest time)
        # So: GLPI 5 (highest priority) -> P1 (fastest SLA)
        #     GLPI 1 (lowest priority) -> P5 (slowest SLA)
        prio_map = {
            5: "P1",  # Very High priority -> P1 SLA (fastest)
            4: "P2",  # High priority -> P2 SLA
            3: "P3",  # Medium priority -> P3 SLA
            2: "P4",  # Low priority -> P4 SLA
            1: "P5"   # Very Low priority -> P5 SLA (slowest)
        } 
        
        print(f"Loaded {len(entities)} entities, {len(sla_data)} SLMs, {len(existing_rules_map)} existing rules.")
        print(f"Entity map has {len(entity_map)} entries.")
        print("\n--- Starting Processing ---\n")

        for entity_name, service_level_name in entity_map.items():
            print(f"Processing: {entity_name} -> {service_level_name}")
            if entity_name not in entities:
                print(f"SKIP: Entity '{entity_name}' not found in GLPI.")
                continue
            
            if service_level_name not in sla_data:
                print(f"SKIP: Service Level '{service_level_name}' not found or has no SLAs.")
                print(f"  Available SLMs: {list(sla_data.keys())}")
                continue
                
            entity_id = entities[entity_name]
            sl_slas = sla_data[service_level_name]
            
            for prio_id, sla_target_name in prio_map.items():
                if sla_target_name not in sl_slas:
                    continue
                
                tto_id = sl_slas[sla_target_name].get('TTO')
                ttr_id = sl_slas[sla_target_name].get('TTR')
                
                if not tto_id and not ttr_id:
                    continue
                    
                # Rule name uses P1-P5 notation (ITIL standard)
                # GLPI Priority 5 -> P1 (highest), GLPI Priority 1 -> P5 (lowest)
                # Replace spaces in entity name with hyphens for consistent naming
                entity_name_clean = entity_name.replace(' ', '-')
                rule_name = f"Auto-SLA-{entity_name_clean}-Priority-{sla_target_name}-Incident"
                
                # Criteria: condition=0 means "is" (exact match), not "contains"
                # Type: 1 = Incident, 2 = Request in GLPI
                criteria = [
                    {"criteria": "type", "condition": 0, "pattern": 1},  # Ticket type is Incident
                    {"criteria": "entities_id", "condition": 0, "pattern": entity_id},
                    {"criteria": "priority", "condition": 0, "pattern": prio_id}
                ]
                
                actions = []
                if tto_id:
                    actions.append({"field": "slas_id_tto", "value": tto_id})
                if ttr_id:
                    actions.append({"field": "slas_id_ttr", "value": ttr_id})
                
                # REMOVED: Stop processing to allow category-based group assignment
                # This allows rules_itilcategory_assign.py (Ranking 20) to run after SLA assignment
                # Major Incident protection is maintained via stop processing in rules_business_incident_major.py (Ranking 10)
                # actions.append({"field": "_stop_rules_processing", "value": 1})
                    
                create_or_update_rule(glpi_url, headers, rule_name, criteria, actions, existing_rules_map, dry_run=dry_run)

        # ========================================================================
        # PART 2: REQUEST SLA RULES (Fixed P3 for all priorities)
        # ========================================================================
        print("\\n=== Processing REQUEST SLA Rules (P3 Medium for all) ===")
        
        for entity_name, service_level_name in entity_map.items():
            print(f"Processing Request: {entity_name} -> {service_level_name}")
            if entity_name not in entities:
                print(f"SKIP: Entity '{entity_name}' not found in GLPI.")
                continue
            
            if service_level_name not in sla_data:
                print(f"SKIP: Service Level '{service_level_name}' not found or has no SLAs.")
                continue
                
            entity_id = entities[entity_name]
            sl_slas = sla_data[service_level_name]
            
            # For Requests, always use P3 (Medium priority) SLA
            if "P3" not in sl_slas:
                print(f"  SKIP: P3 SLA not found for {service_level_name}")
                continue
            
            tto_id = sl_slas["P3"].get('TTO')
            ttr_id = sl_slas["P3"].get('TTR')
            
            if not tto_id and not ttr_id:
                print(f"  SKIP: P3 SLA has no TTO/TTR for {service_level_name}")
                continue
            
            # Rule name for Request type
            entity_name_clean = entity_name.replace(' ', '-')
            rule_name = f"Auto-SLA-{entity_name_clean}-Request-P3"
            
            # Criteria: Request type (2), entity match, no priority check
            criteria = [
                {"criteria": "type", "condition": 0, "pattern": 2},  # Ticket type is Request
                {"criteria": "entities_id", "condition": 0, "pattern": entity_id}
            ]
            
            actions = []
            if tto_id:
                actions.append({"field": "slas_id_tto", "value": tto_id})
            if ttr_id:
                actions.append({"field": "slas_id_ttr", "value": ttr_id})
            
            create_or_update_rule(glpi_url, headers, rule_name, criteria, actions, existing_rules_map, dry_run=dry_run)


    except Exception as e:
        print(f"Major Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        kill_session(glpi_url, config['GLPI_APP_TOKEN'], session_token)

if __name__ == "__main__":
    main()
