import requests
import json
import os
import sys
import urllib3
import argparse
import logging
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('rules_business.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

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
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading config file {path}: {e}")
                continue
                
    logger.error(f"File {CONFIG_FILE} not found in any of the search paths:")
    for path in search_paths:
        logger.error(f"  - {os.path.abspath(path)}")
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
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading {ENTITY_SLA_MAP_FILE}: {e}")
                continue
    
    logger.warning(f"{ENTITY_SLA_MAP_FILE} not found. SLA assignment will fail.")
    return {}

def init_session(url, app_token, user_token, verify=False):
    headers = {"App-Token": app_token, "Authorization": f"user_token {user_token}", "Content-Type": "application/json"}
    try:
        resp = requests.get(f"{url}/initSession", headers=headers, verify=verify, timeout=30)
        resp.raise_for_status()
        return resp.json().get('session_token')
    except Exception as e:
        logger.error(f"Session init failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        sys.exit(1)

def kill_session(url, app_token, session_token, verify=False):
    headers = {"App-Token": app_token, "Session-Token": session_token}
    try:
        requests.get(f"{url}/killSession", headers=headers, verify=verify, timeout=10)
    except Exception as e:
        logger.debug(f"Failed to kill session (silent ignore): {e}")

@contextmanager
def glpi_session(url, app_token, user_token, verify=False):
    session_token = init_session(url, app_token, user_token, verify=verify)
    try:
        yield session_token
    finally:
        kill_session(url, app_token, session_token, verify=verify)
        logger.info("Session closed.")

def fetch_all_entities(url, headers, verify=False):
    entities = {}
    range_start = 0
    range_step = 1000
    
    logger.info("Fetching Entities...")
    while True:
        range_end = range_start + range_step
        params = {"range": f"{range_start}-{range_end}", "is_deleted": 0}
        
        try:
            resp = requests.get(f"{url}/Entity", headers=headers, params=params, verify=verify, timeout=30)
            if resp.status_code not in [200, 206]:
                break
                
            batch = resp.json()
            if not batch: break
            
            for e in batch:
                entities[e['name']] = e['id']
            
            if len(batch) < range_step: break
            range_start += range_step
            
        except Exception as e:
            logger.error(f"Error fetching entities: {e}")
            break
            
    return entities

def fetch_slas_by_service_level(url, headers, verify=False):
    slm_map = {} 
    
    # 1. Fetch SLMs
    logger.info("Fetching SLMs...")
    range_start = 0
    range_step = 200
    try:
        while True:
            params = {"range": f"{range_start}-{range_start+range_step}", "is_deleted": 0}
            r = requests.get(f"{url}/SLM", headers=headers, params=params, verify=verify, timeout=30)
            if r.status_code not in [200, 206]: break
            batch = r.json()
            if not batch: break
            for slm in batch:
                slm_map[slm['id']] = slm['name']
            if len(batch) < range_step: break
            range_start += range_step
    except Exception as e:
        logger.error(f"Error fetching SLMs: {e}")
        return {}

    sla_structure = {} 
    
    # 2. Fetch SLAs
    logger.info("Fetching SLAs...")
    range_start = 0
    range_step = 1000
    try:
        while True:
            params = {"range": f"{range_start}-{range_start+range_step}", "is_deleted": 0}
            r = requests.get(f"{url}/SLA", headers=headers, params=params, verify=verify, timeout=30)
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
        logger.error(f"Error fetching SLAs: {e}")
        
    return sla_structure

def fetch_itil_category_id(url, headers, name, verify=False):
    """Fetch all ITIL categories and find matching ID by name (more robust than search)"""
    range_start = 0
    range_step = 1000
    try:
        while True:
            params = {"range": f"{range_start}-{range_start+range_step}", "is_deleted": 0}
            resp = requests.get(f"{url}/ITILCategory", headers=headers, params=params, verify=verify, timeout=30)
            if resp.status_code not in [200, 206]: break
            batch = resp.json()
            if not batch: break
            for cat in batch:
                if cat['name'].lower() == name.lower():
                    return cat['id']
            if len(batch) < range_step: break
            range_start += range_step
    except Exception as e:
        logger.error(f"Error resolving ITILCategory '{name}': {e}")
    return None

def fetch_existing_rules(url, headers, verify=False):
    existing_rules = {} # Name -> ID
    logger.info("Fetching existing Business Rules via Search...")
    
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
            
            r = requests.get(f"{url}/search/RuleTicket", headers=headers, params=params, verify=verify, timeout=30)
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
        logger.warning(f"Could not fetch existing rules: {e}")
        
    return existing_rules

def get_rule_details(url, headers, rule_id, verify=False):
    """Fetch criteria and actions for a specific rule (Smart Sync)"""
    criteria = []
    actions = []
    
    # Criteria
    try:
        resp = requests.get(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, params={"range": "0-5000"}, verify=verify, timeout=30)
        if resp.status_code in [200, 206]:
            criteria = [item for item in resp.json() if str(item.get('rules_id')) == str(rule_id)]
    except Exception as e:
        logger.error(f"Error fetching criteria for rule {rule_id}: {e}")
        
    # Actions
    try:
        resp = requests.get(f"{url}/RuleTicket/{rule_id}/RuleAction", headers=headers, params={"range": "0-5000"}, verify=verify, timeout=30)
        if resp.status_code in [200, 206]:
            actions = [item for item in resp.json() if str(item.get('rules_id')) == str(rule_id)]
    except Exception as e:
        logger.error(f"Error fetching actions for rule {rule_id}: {e}")
        
    return criteria, actions

def create_or_update_rule(url, headers, rule_name, proposed_criteria, proposed_actions, existing_rules_map, dry_run=True, verify=False):
    rule_id = existing_rules_map.get(rule_name)
    
    # Generic Rule properties
    rule_input = {
        "name": rule_name,
        "match": "AND",
        "is_active": 1,
        "sub_type": "RuleTicket",
        "ranking": 1,
        "is_recursive": 1,
        "condition": 3, # 3 = Add / Update
        "entities_id": 0 # Root
    }

    if rule_id:
        # Check if update is needed (Smart Sync / Diffing)
        curr_criteria, curr_actions = get_rule_details(url, headers, rule_id, verify=verify)
        
        # Compare Criteria: Check if all proposed exist exactly as specified
        # Proposed: list of dicts with 'criteria', 'condition', 'pattern'
        needs_update = False
        
        if len(curr_criteria) != len(proposed_criteria):
            needs_update = True
        else:
            for p_crit in proposed_criteria:
                match = any(
                    str(c.get('criteria')) == str(p_crit['criteria']) and 
                    int(c.get('condition')) == int(p_crit['condition']) and 
                    str(c.get('pattern')) == str(p_crit['pattern'])
                    for c in curr_criteria
                )
                if not match:
                    needs_update = True
                    break
        
        if not needs_update:
            if len(curr_actions) != len(proposed_actions):
                needs_update = True
            else:
                for p_act in proposed_actions:
                    match = any(
                        str(a.get('field')) == str(p_act['field']) and 
                        str(a.get('value')) == str(p_act['value']) and
                        a.get('action_type', 'assign') == p_act.get('action_type', 'assign')
                        for a in curr_actions
                    )
                    if not match:
                        needs_update = True
                        break

        if not needs_update:
            logger.info(f"SKIPPED: Rule '{rule_name}' is already up-to-date.")
            return "SKIPPED"

        verb = "UPDATE"
    else:
        verb = "CREATE"

    logger.info(f"PROPOSE: {verb} Rule '{rule_name}'")
    for c in proposed_criteria: logger.info(f"  Criteria: {c.get('criteria')} {c.get('condition')} {c.get('pattern')}")
    for a in proposed_actions: logger.info(f"  Action: {a.get('field')} -> {a.get('value')}")

    if dry_run:
        return verb

    try:
        if rule_id:
            # UPDATE: Pure clean state approach is safest for complex rules
            logger.info(f"  Purging current state for Rule ID: {rule_id}")
            # Delete Criteria
            curr_c, curr_a = get_rule_details(url, headers, rule_id, verify=verify)
            for c in curr_c:
                requests.delete(f"{url}/RuleTicket/{rule_id}/RuleCriteria/{c['id']}", headers=headers, verify=verify, timeout=30)
            # Delete Actions
            for a in curr_a:
                requests.delete(f"{url}/RuleTicket/{rule_id}/RuleAction/{a['id']}", headers=headers, verify=verify, timeout=30)
        else:
            # CREATE
            payload = {"input": rule_input}
            r = requests.post(f"{url}/RuleTicket", headers=headers, json=payload, verify=verify, timeout=30)
            r.raise_for_status()
            rule_id = r.json().get('id')
            logger.info(f"  ✓ Created Rule ID: {rule_id}")

        # Add Proposed Criteria
        for crit in proposed_criteria:
            crit_payload = {"input": { "rules_id": rule_id, **crit }}
            requests.post(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, json=crit_payload, verify=verify, timeout=30)

        # Add Proposed Actions
        for act in proposed_actions:
            act_payload = {"input": { "rules_id": rule_id, "action_type": "assign", **act }}
            requests.post(f"{url}/RuleTicket/{rule_id}/RuleAction", headers=headers, json=act_payload, verify=verify, timeout=30)
        
        logger.info(f"  ✓ Successfully {verb}D Rule.")
        return verb

    except Exception as e:
        logger.error(f"Failed to {verb} rule '{rule_name}': {e}")
        return "FAILED"
def main():
    parser = argparse.ArgumentParser(description="Create or Update Business Rules for Email Tickets (v3.1)")
    parser.add_argument('--force', action='store_true', help="Execute changes (default is dry-run)")
    parser.add_argument('--priority', default='P3', help="Default priority (P1-P5, default: P3)")
    parser.add_argument('--category', default='Genel Destek', help="Default category name (default: 'Genel Destek')")
    args = parser.parse_args()
    
    dry_run = not args.force
    if dry_run:
        logger.info("Running in DRY-RUN mode. No changes will be made.")
    else:
        logger.info("Running in FORCE mode. Changes will be applied.")
 
    config = load_config()
    entity_map = load_entity_sla_map()
    
    glpi_url = config.get('GLPI_URL', '').rstrip('/')
    app_token = config.get('GLPI_APP_TOKEN')
    user_token = config.get('GLPI_USER_TOKEN')
    verify_ssl = config.get('verify_ssl', False)
    
    if not glpi_url or not app_token or not user_token:
        logger.error("Missing GLPI configuration (URL, App-Token, or User-Token).")
        sys.exit(1)
 
    try:
        with glpi_session(glpi_url, app_token, user_token, verify=verify_ssl) as session_token:
            headers = {
                "App-Token": app_token,
                "Session-Token": session_token,
                "Content-Type": "application/json"
            }
            
            logger.info("Fetching required metadata (Entities, SLAs, Category, Existing Rules)...")
            entities = fetch_all_entities(glpi_url, headers, verify=verify_ssl)
            sla_data = fetch_slas_by_service_level(glpi_url, headers, verify=verify_ssl)
            existing_rules_map = fetch_existing_rules(glpi_url, headers, verify=verify_ssl)
            
            # Dynamic Category Lookup
            category_id = fetch_itil_category_id(glpi_url, headers, args.category, verify=verify_ssl)
            if not category_id:
                logger.error(f"Could not resolve Category ID for '{args.category}'. Aborting.")
                sys.exit(1)
            logger.info(f"Resolved Category '{args.category}' to ID: {category_id}")
            
            # Priority Map: P3 -> 3, etc.
            prio_map_val = {'P1': 5, 'P2': 4, 'P3': 3, 'P4': 2, 'P5': 1}
            target_prio_val = prio_map_val.get(args.priority, 3)
            
            logger.info(f"Metadata: {len(entities)} entities, {len(sla_data)} SLMs, {len(existing_rules_map)} rules found.")
            logger.info("-" * 60)
 
            report = {
                "CREATE": [],
                "UPDATE": [],
                "SKIPPED": [],
                "FAILED": [],
                "MISSING_METADATA": []
            }
 
            for entity_name, service_level_name in entity_map.items():
                if entity_name not in entities:
                    logger.warning(f"SKIP: Entity '{entity_name}' not found in GLPI.")
                    report["MISSING_METADATA"].append(f"Entity: {entity_name}")
                    continue
                
                entity_id = entities[entity_name]
                entity_name_clean = entity_name.replace(' ', '-')
                rule_name = f"Auto-BR-{entity_name_clean}"
                
                # SLA Resolution
                tto_id, ttr_id = None, None
                if service_level_name in sla_data:
                    p_slas = sla_data[service_level_name].get(args.priority)
                    if p_slas:
                        tto_id = p_slas.get('TTO', {}).get('id')
                        ttr_id = p_slas.get('TTR', {}).get('id')
                
                if not tto_id or not ttr_id:
                    logger.warning(f"SLA Missing for {entity_name} ({service_level_name}) - {args.priority}")
 
                # Defined Criteria (v3.1)
                # 1. Entity is X
                # 2. Source is Email (2)
                # 3. Type is NOT Incident (1) -> Request
                criteria = [
                    {"criteria": "entities_id", "condition": 0, "pattern": str(entity_id)},
                    {"criteria": "requesttypes_id", "condition": 0, "pattern": "2"}, # Email
                    {"criteria": "type", "condition": 1, "pattern": "1"} # Not Incident
                ]
                
                # Defined Actions
                actions = [
                    {"field": "itilcategories_id", "value": str(category_id)},
                    {"field": "priority", "value": str(target_prio_val)}
                ]
                
                if tto_id: actions.append({"field": "slas_id_tto", "value": str(tto_id)})
                if ttr_id: actions.append({"field": "slas_id_ttr", "value": str(ttr_id)})
 
                result = create_or_update_rule(glpi_url, headers, rule_name, criteria, actions, existing_rules_map, dry_run=dry_run, verify=verify_ssl)
                if result in report:
                    report[result].append(rule_name)
 
            # Final Report
            logger.info("-" * 60)
            logger.info("DETAILED EXECUTION SUMMARY REPORT (v3.1)")
            logger.info("-" * 60)
            
            for key in ["CREATE", "UPDATE", "SKIPPED", "MISSING_METADATA", "FAILED"]:
                if report[key]:
                    logger.info(f"{key} ({len(report[key])}):")
                    for item in report[key]: logger.info(f"  - {item}")
            
            logger.info("-" * 60)
            logger.info(f"Total entries processed from map: {len(entity_map)}")
            logger.info("-" * 60)
 
    except Exception as e:
        logger.error(f"Major Error: {e}")
        import traceback
        logger.debug(traceback.format_exc())
 
if __name__ == "__main__":
    main()
