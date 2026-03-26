import requests
import json
import os
import sys
import urllib3
import logging
import argparse
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('rules_business_incident_major.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Constants for Log Enrichment
PRIORITY_NAMES = {
    1: "Very Low",
    2: "Low",
    3: "Medium",
    4: "High",
    5: "Very High",
    6: "Major"
}

# Suppress insecure request warnings if necessary
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
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading config file {path}: {e}")
                continue
                
    logger.error(f"File {CONFIG_FILE} not found!")
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
def init_session(url, app_token, user_token, verify=False):
    headers = {"App-Token": app_token, "Authorization": f"user_token {user_token}", "Content-Type": "application/json"}
    try:
        resp = requests.get(f"{url}/initSession", headers=headers, verify=verify, timeout=30)
        resp.raise_for_status()
        return resp.json().get('session_token')
    except Exception as e:
        logger.error(f"Session init failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
             logger.error(e.response.text)
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
    entities_name_to_id = {}
    entities_id_to_name = {}
    range_start = 0
    range_step = 1000
    
    logger.info("Fetching Entities...")
    while True:
        params = {"range": f"{range_start}-{range_start+range_step}", "is_deleted": 0}
        try:
            resp = requests.get(f"{url}/Entity", headers=headers, params=params, verify=verify, timeout=30)
            if resp.status_code not in [200, 206]: break
            batch = resp.json()
            if not batch: break
            
            for e in batch:
                entities_name_to_id[e['name'].lower()] = e['id']
                entities_id_to_name[str(e['id'])] = e['name']
            
            if len(batch) < range_step: break
            range_start += range_step
        except Exception as e:
            logger.error(f"Error fetching entities: {e}")
            break
    return entities_name_to_id, entities_id_to_name

def fetch_groups(url, headers, verify=False):
    """Fetch all groups to resolve IDs in logs"""
    groups_id_to_name = {}
    range_start = 0
    range_step = 1000
    logger.info("Fetching Groups...")
    try:
        while True:
            params = {"range": f"{range_start}-{range_start+range_step}", "is_deleted": 0}
            r = requests.get(f"{url}/Group", headers=headers, params=params, verify=verify, timeout=30)
            if r.status_code not in [200, 206]: break
            batch = r.json()
            if not batch: break
            for item in batch:
                groups_id_to_name[str(item['id'])] = item['name']
            if len(batch) < range_step: break
            range_start += range_step
    except Exception as e:
        logger.error(f"Error fetching groups: {e}")
    return groups_id_to_name

def fetch_p1_slas(url, headers, verify=False):
    """
    Fetches SLAs and returns:
    1. sla_p1_map: SLM Name -> { 'TTO': id, 'TTR': id }
    2. sla_id_to_name: id -> name (all P1 SLAs)
    """
    slm_map = {} 
    sla_id_to_name = {}
    
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
            for item in batch:
                slm_map[item['id']] = item['name']
            if len(batch) < range_step: break
            range_start += range_step
    except Exception as e:
        logger.error(f"Error fetching SLMs: {e}")
        return {}, {}

    sla_p1_map = {} # SLM_Name -> {'TTO': id, 'TTR': id}
    
    # 2. Fetch SLAs
    logger.info("Fetching SLAs (looking for P1)...")
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
                
                # Resolve SLM Name
                slm_name = None
                if isinstance(slm_id, int): slm_name = slm_map.get(slm_id)
                elif isinstance(slm_id, str) and slm_id.isdigit(): slm_name = slm_map.get(int(slm_id))
                
                if not slm_name: continue
                
                # Filter for P1 (Highest Priority / Fastest SLA)
                sla_name = item.get('name', '')
                if "P1" not in sla_name:
                    continue
                    
                if slm_name not in sla_p1_map:
                    sla_p1_map[slm_name] = {}
                
                # Type 0=TTR, 1=TTO
                sla_type = item.get('type')
                type_key = "TTR" if sla_type == 0 else "TTO"
                
                sla_p1_map[slm_name][type_key] = item.get('id')
                sla_id_to_name[str(item.get('id'))] = sla_name
            
            if len(batch) < range_step: break
            range_start += range_step
            
    except Exception as e:
        logger.error(f"Error fetching SLAs: {e}")
        
    return sla_p1_map, sla_id_to_name

def fetch_existing_rules(url, headers, verify=False):
    existing_rules = {} # Name -> ID
    logger.info("Fetching existing Major Incident rules via Search...")
    
    range_start = 0
    range_step = 100
    
    try:
        while True:
            params = {
                "criteria[0][field]": "1", # Name
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": "Auto-Major-Incident",
                "forcedisplay[0]": "2", # ID
                "range": f"{range_start}-{range_start+range_step}",
                "is_deleted": 0
            }
            
            r = requests.get(f"{url}/search/RuleTicket", headers=headers, params=params, verify=verify, timeout=30)
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
        logger.warning(f"Could not fetch existing rules: {e}")
        
    return existing_rules

def get_rule_details(url, headers, rule_id, verify=False):
    """Fetch criteria and actions for a specific rule"""
    criteria = []
    actions = []
    
    # Criteria
    resp = requests.get(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, params={"range": "0-5000"}, verify=verify, timeout=30)
    if resp.status_code in [200, 206]:
        criteria = [item for item in resp.json() if str(item.get('rules_id')) == str(rule_id)]
        
    # Actions
    resp = requests.get(f"{url}/RuleTicket/{rule_id}/RuleAction", headers=headers, params={"range": "0-5000"}, verify=verify, timeout=30)
    if resp.status_code in [200, 206]:
        actions = [item for item in resp.json() if str(item.get('rules_id')) == str(rule_id)]
        
    return criteria, actions

def clear_rule_details(url, headers, rule_id, verify=False):
    # Clear Actions
    criteria, actions = get_rule_details(url, headers, rule_id, verify=verify)
    
    for item in actions:
        try:
            requests.delete(f"{url}/RuleTicket/{rule_id}/RuleAction/{item['id']}", headers=headers, verify=verify, timeout=30)
        except Exception as e:
            logger.error(f"Failed to delete action {item['id']}: {e}")
            
    # Clear Criteria
    for item in criteria:
        try:
            requests.delete(f"{url}/RuleTicket/{rule_id}/RuleCriteria/{item['id']}", headers=headers, verify=verify, timeout=30)
        except Exception as e:
            logger.error(f"Failed to delete criteria {item['id']}: {e}")

def resolve_id(field, value, maps):
    """Helper to resolve ID to human-readable name for logging"""
    val_str = str(value)
    if field == "priority":
        return f"{val_str} ({PRIORITY_NAMES.get(int(value), 'Unknown')})"
    elif field == "itilcategories_id":
        return f"{val_str} (Major Incident)" if val_str == "229" else val_str
    elif field == "entities_id":
        return f"{val_str} ({maps.get('entities', {}).get(val_str, 'Unknown')})"
    elif field in ["slas_id_tto", "slas_id_ttr"]:
        return f"{val_str} ({maps.get('slas', {}).get(val_str, 'Unknown')})"
    elif field == "_groups_id_assign":
        return f"{val_str} ({maps.get('groups', {}).get(val_str, 'Unknown')})"
    return val_str

def create_or_update_rule(url, headers, rule_name, criteria_list, action_list, existing_rules_map, res_maps, dry_run=True, verify=False):
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

    rule_id = existing_rules_map.get(rule_name)
    
    if rule_id:
        # Smart Sync: Check if update is actually needed
        curr_criteria, curr_actions = get_rule_details(url, headers, rule_id, verify=verify)
        
        diffs = []
        
        # Compare criteria lists
        if len(curr_criteria) != len(criteria_list):
            diffs.append(f"Criteria count mismatch: current={len(curr_criteria)}, proposed={len(criteria_list)}")
        
        for proposed in criteria_list:
            found = any(
                c.get('criteria') == proposed['criteria'] and 
                int(c.get('condition')) == int(proposed['condition']) and 
                str(c.get('pattern')) == str(proposed['pattern'])
                for c in curr_criteria
            )
            if not found:
                field = proposed['criteria']
                val = proposed['pattern']
                diffs.append(f"Missing or changed criterion: {field} (Value: {resolve_id(field, val, res_maps)})")
        
        # Compare actions lists
        if len(curr_actions) != len(action_list):
            diffs.append(f"Action count mismatch: current={len(curr_actions)}, proposed={len(action_list)}")
            
        for proposed in action_list:
            found = any(
                a.get('field') == proposed['field'] and 
                a.get('action_type') == proposed['action_type'] and 
                str(a.get('value')) == str(proposed['value'])
                for a in curr_actions
            )
            if not found:
                field = proposed['field']
                val = proposed['value']
                diffs.append(f"Missing or changed action: {field} (Value: {resolve_id(field, val, res_maps)})")
                    
        if not diffs:
            logger.info(f"SKIP: Rule '{rule_name}' is already up to date.")
            return "SKIPPED"

        action_verb = "UPDATE"
        if dry_run:
            logger.info(f"[DRY RUN] Would UPDATE Rule '{rule_name}' (ID: {rule_id})")
            for d in diffs:
                logger.info(f"  - Change: {d}")
            return action_verb

        logger.info(f"Updating Rule '{rule_name}' (ID: {rule_id})")
        for d in diffs:
            logger.info(f"  - Change detected: {d}")
            
        try:
             requests.put(f"{url}/RuleTicket/{rule_id}", headers=headers, json={"input": {"id": rule_id, **rule_input}}, verify=verify, timeout=30)
             clear_rule_details(url, headers, rule_id, verify=verify)
             
             for crit in criteria_list:
                requests.post(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, json={"input": {"rules_id": rule_id, **crit}}, verify=verify, timeout=30)

             for act in action_list:
                 requests.post(f"{url}/RuleTicket/{rule_id}/RuleAction", headers=headers, json={"input": {"rules_id": rule_id, **act}}, verify=verify, timeout=30)
             
             logger.info(f"  ✓ UPDATED Rule '{rule_name}'.")
             return action_verb
        except Exception as e:
            logger.error(f"Failed to update rule '{rule_name}': {e}")
            return "FAILED"
    else:
        action_verb = "CREATE"
        if dry_run:
            logger.info(f"[DRY RUN] Would CREATE Rule: '{rule_name}'")
            return action_verb

        try:
            r = requests.post(f"{url}/RuleTicket", headers=headers, json={"input": rule_input}, verify=verify, timeout=30)
            r.raise_for_status()
            rule_id = r.json().get('id')
            logger.info(f"Created Rule '{rule_name}' (ID: {rule_id})")
            
            for crit in criteria_list:
                requests.post(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, json={"input": {"rules_id": rule_id, **crit}}, verify=verify, timeout=30)
                
            for act in action_list:
                 requests.post(f"{url}/RuleTicket/{rule_id}/RuleAction", headers=headers, json={"input": {"rules_id": rule_id, **act}}, verify=verify, timeout=30)
                 
            existing_rules_map[rule_name] = rule_id
            logger.info(f"  ✓ CREATED Rule '{rule_name}'.")
            return action_verb
        except Exception as e:
            logger.error(f"Failed to create rule '{rule_name}': {e}")
            return "FAILED"

# --- Main ---
def main():
    parser = argparse.ArgumentParser(description="GLPI Major Incident Rule Creator")
    parser.add_argument('--force', action='store_true', help="Execute changes (default is dry-run)")
    args = parser.parse_args()
    
    dry_run = not args.force
    
    if dry_run:
        logger.info("Running in DRY-RUN mode. No changes will be made.")
    else:
        logger.info("Running in FORCE mode. Changes will be applied.")

    # CONSTANTS
    MAJOR_INCIDENT_CATEGORY_ID = 229
    MAJOR_PRIORITY_ID = 6
    MAJOR_INCIDENT_GROUP_ID = 45 

    config = load_config()
    entity_map = load_entity_sla_map()
    
    glpi_url = config.get('GLPI_URL').rstrip('/')
    app_token = config.get('GLPI_APP_TOKEN')
    user_token = config.get('GLPI_USER_TOKEN')
    verify_ssl = config.get('verify_ssl', False)

    if not verify_ssl:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    report = {
        "CREATE": [],
        "UPDATE": [],
        "SKIPPED": [],
        "FAILED": []
    }
    
    try:
        with glpi_session(glpi_url, app_token, user_token, verify=verify_ssl) as session_token:
            headers = {
                "App-Token": app_token, 
                "Session-Token": session_token, 
                "Content-Type": "application/json"
            }
            
            entities_name_to_id, entities_id_to_name = fetch_all_entities(glpi_url, headers, verify=verify_ssl)
            sla_p1_map, sla_id_to_name = fetch_p1_slas(glpi_url, headers, verify=verify_ssl)
            groups_id_to_name = fetch_groups(glpi_url, headers, verify=verify_ssl)
            existing_rules_map = fetch_existing_rules(glpi_url, headers, verify=verify_ssl)
            
            # Resolution maps for logging
            res_maps = {
                "entities": entities_id_to_name,
                "slas": sla_id_to_name,
                "groups": groups_id_to_name
            }

            logger.info("\n--- Processing Entities ---")
            for entity_name, service_level_name in entity_map.items():
                entity_name_lower = entity_name.lower()
                if entity_name_lower not in entities_name_to_id:
                    logger.warning(f"SKIP: Entity '{entity_name}' not found.")
                    continue
                    
                if service_level_name not in sla_p1_map:
                    logger.warning(f"SKIP: No P1 SLAs found for Service Level '{service_level_name}'.")
                    continue
                    
                entity_id = entities_name_to_id[entity_name_lower]
                p1_slas = sla_p1_map[service_level_name]
                
                tto_id = p1_slas.get('TTO')
                ttr_id = p1_slas.get('TTR')
                
                if not tto_id and not ttr_id:
                    logger.warning(f"SKIP: Missing TTO/TTR IDs in P1 SLA for {service_level_name}")
                    continue
                    
                # Replace spaces in entity name with hyphens for consistent naming
                entity_name_clean = entity_name.replace(' ', '-')
                rule_name = f"Auto-Major-Incident-{entity_name_clean}"
                
                # Criteria
                criteria = [
                    {"criteria": "priority", "condition": 0, "pattern": MAJOR_PRIORITY_ID},
                    {"criteria": "itilcategories_id", "condition": 0, "pattern": MAJOR_INCIDENT_CATEGORY_ID},
                    {"criteria": "entities_id", "condition": 0, "pattern": entity_id}
                ]
                
                # Actions
                actions = [
                    {
                        "field": "_groups_id_assign",
                        "value": MAJOR_INCIDENT_GROUP_ID, 
                        "action_type": "assign"
                    }
                ]
                if tto_id: actions.append({"field": "slas_id_tto", "value": tto_id, "action_type": "assign"})
                if ttr_id: actions.append({"field": "slas_id_ttr", "value": ttr_id, "action_type": "assign"})
                
                actions.append({"field": "_stop_rules_processing", "value": 1, "action_type": "assign"})
                
                result = create_or_update_rule(glpi_url, headers, rule_name, criteria, actions, existing_rules_map, res_maps, dry_run=dry_run, verify=verify_ssl)
                if result in report:
                    report[result].append(rule_name)
                    
            # Final Detailed Report
            logger.info("-" * 60)
            logger.info("DETAILED EXECUTION SUMMARY REPORT")
            logger.info("-" * 60)
            
            if report["CREATE"]:
                logger.info(f"NEW RULES CREATED ({len(report['CREATE'])}):")
                for name in report["CREATE"]: logger.info(f"  + {name}")
                
            if report["UPDATE"]:
                logger.info(f"RULES UPDATED ({len(report['UPDATE'])}):")
                for name in report["UPDATE"]: logger.info(f"  * {name}")
            
            if report["SKIPPED"]:
                logger.info(f"ALREADY UP-TO-DATE ({len(report['SKIPPED'])}):")
                for name in report["SKIPPED"]: logger.info(f"  - {name}")

            if report["FAILED"]:
                logger.error(f"FAILED OPERATIONS ({len(report['FAILED'])}):")
                for name in report["FAILED"]: logger.error(f"  ! {name}")
                
            logger.info("-" * 60)
            logger.info(f"Total Processed: {len(entity_map)} mappings.")
            logger.info("-" * 60)
            
    except Exception as e:
        logger.critical(f"CRITICAL ERROR: {e}")
        import traceback
        logger.debug(traceback.format_exc())

if __name__ == "__main__":
    main()
