import requests
import json
import os
import sys
import urllib3
import argparse
import logging
import re
import traceback
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('rules_unknowndomain.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Suppress insecure request warnings if necessary
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

def init_session(url, app_token, user_token, verify=False):
    """Initialize GLPI session"""
    headers = {
        "App-Token": app_token,
        "Authorization": f"user_token {user_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(f"{url}/initSession", headers=headers, verify=verify, timeout=30)
        response.raise_for_status()
        return response.json()['session_token']
    except Exception as e:
        logger.error(f"Failed to initialize session: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        sys.exit(1)

def kill_session(url, app_token, session_token, verify=False):
    """Close GLPI session"""
    headers = {
        "App-Token": app_token,
        "Session-Token": session_token
    }
    try:
        requests.get(f"{url}/killSession", headers=headers, verify=verify, timeout=10)
    except Exception as e:
        logger.debug(f"Failed to kill session (silent ignore): {e}")

@contextmanager
def glpi_session(url, app_token, user_token, verify=False):
    """Context manager for GLPI REST API sessions"""
    session_token = init_session(url, app_token, user_token, verify=verify)
    try:
        yield session_token
    finally:
        kill_session(url, app_token, session_token, verify=verify)
        logger.info("Session closed.")

def fetch_all_entities(url, headers, verify=False):
    """Fetch all entities from GLPI"""
    logger.info("Fetching Entities...")
    entities = []
    range_start = 0
    range_step = 1000
    
    while True:
        range_end = range_start + range_step
        params = {"range": f"{range_start}-{range_end}"}  # Removed expand_dropdowns to get numeric IDs
        try:
            resp = requests.get(f"{url}/Entity", headers=headers, params=params, verify=verify, timeout=30)
            
            if resp.status_code not in [200, 206]:
                logger.error(f"Error fetching entities: {resp.status_code}")
                break
                
            batch = resp.json()
            if not batch: break
            
            entities.extend(batch)
            if len(batch) < range_step: break
            range_start += range_step
        except Exception as e:
            logger.error(f"Exception while fetching entities: {e}")
            break
        
    return entities

def find_entity_by_path(entities, path):
    """
    Find entity by hierarchical path like 'Root Entity > Ultron Bilişim > Internal IT > Genel destek'
    Returns entity ID or None
    """
    path_parts = [part.strip() for part in path.split('>')]
    
    # Start from root (entities_id = 0 means root level)
    # If path starts with "Root Entity", skip it and start from 0
    start_index = 0
    current_parent_id = 0
    
    if path_parts[0] == "Root Entity":
        start_index = 1  # Skip "Root Entity" in the path
    
    # Traverse the path
    for i in range(start_index, len(path_parts)):
        part_name = path_parts[i]
        found = False
        
        for entity in entities:
            if entity['name'] == part_name and int(entity.get('entities_id', -1)) == current_parent_id:
                current_parent_id = int(entity['id'])
                found = True
                if i == len(path_parts) - 1:  # Last part
                    return int(entity['id'])
                break
        
        if not found:
            return None
    
    return None

def fetch_existing_rule_id(url, headers, rule_name, verify=False):
    """Fetch existing rule ID by name, returns rule ID or None"""
    logger.debug(f"Searching for rule: {rule_name}")
    range_start = 0
    range_step = 100
    
    while True:
        range_end = range_start + range_step
        params = {"range": f"{range_start}-{range_end}", "forcedisplay[0]": "2", "forcedisplay[1]": "1"}
        try:
            resp = requests.get(f"{url}/search/RuleMailCollector", headers=headers, params=params, verify=verify, timeout=30)
            
            if resp.status_code not in [200, 206]:
                break
                
            data = resp.json().get('data', [])
            if not data: break
            
            for item in data:
                rule_id = item.get('2')
                name = item.get('1')
                if name == rule_name:
                    return rule_id
            
            if len(data) < range_step: break
            range_start += range_step
        except Exception as e:
            logger.error(f"Error fetching rule ID: {e}")
            break
        
    return None

def get_rule_base_data(url, headers, rule_id, verify=False):
    """Fetch base data for a specific rule (ranking, match mode, etc.)"""
    try:
        resp = requests.get(f"{url}/RuleMailCollector/{rule_id}", headers=headers, verify=verify, timeout=30)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.error(f"Error fetching rule base data for ID {rule_id}: {e}")
    return None

def get_rule_details(url, headers, rule_id, verify=False):
    """Fetch criteria and actions for a specific rule"""
    criteria = []
    actions = []
    
    try:
        # Criteria
        resp = requests.get(f"{url}/RuleMailCollector/{rule_id}/RuleCriteria", headers=headers, params={"range": "0-5000"}, verify=verify, timeout=30)
        if resp.status_code in [200, 206]:
            criteria = [item for item in resp.json() if int(item.get('rules_id')) == int(rule_id)]
            
        # Actions
        resp = requests.get(f"{url}/RuleMailCollector/{rule_id}/RuleAction", headers=headers, params={"range": "0-5000"}, verify=verify, timeout=30)
        if resp.status_code in [200, 206]:
            actions = [item for item in resp.json() if int(item.get('rules_id')) == int(rule_id)]
    except Exception as e:
        logger.error(f"Error fetching rule details for ID {rule_id}: {e}")
        
    return criteria, actions

def create_or_update_undefined_domain_rule(url, headers, target_entity_id, domains, dry_run=True, verify=False):
    """
    Create or update the 'Tanımsız-Domain' rule
    This rule catches emails from domains NOT in the provided list
    """
    rule_name = "Tanımsız-Domain"
    rule_id = fetch_existing_rule_id(url, headers, rule_name, verify=verify)
    
    # Desired state
    proposed_ranking = 999
    proposed_criteria = [{"criteria": "from", "condition": 3, "pattern": d} for d in sorted(domains)]
    proposed_action = {"action_type": "assign", "field": "entities_id", "value": str(target_entity_id)}

    if rule_id:
        # Smart Sync: Fetch current state
        rule_base = get_rule_base_data(url, headers, rule_id, verify=verify)
        curr_criteria, curr_actions = get_rule_details(url, headers, rule_id, verify=verify)
        
        # 1. Compare Ranking
        curr_ranking = int(rule_base.get('ranking')) if rule_base else None
        need_meta_update = (curr_ranking != proposed_ranking)
        
        # 2. Compare Criteria
        curr_domains = {c.get('pattern') for c in curr_criteria if c.get('criteria') == 'from'}
        proposed_set = {d for d in domains}
        added_domains = sorted(list(proposed_set - curr_domains))
        removed_domains = sorted(list(curr_domains - proposed_set))
        need_content_update = (bool(added_domains) or bool(removed_domains))
        
        # 3. Compare Action
        match_action = any(
            a.get('action_type') == proposed_action['action_type'] and 
            a.get('field') == proposed_action['field'] and 
            str(a.get('value')) == proposed_action['value']
            for a in curr_actions
        ) and len(curr_actions) == 1
        need_content_update = need_content_update or (not match_action)
        
        if not need_meta_update and not need_content_update:
            logger.info(f"SKIP: Rule '{rule_name}' is already up to date (Ranking: {curr_ranking}).")
            return "SKIPPED", 0, 0
        
        action_verb = "UPDATE"
    else:
        action_verb = "CREATE"
        added_domains = sorted(domains)
        removed_domains = []
        need_meta_update = False
        need_content_update = True

    logger.info(f"PROPOSE: {action_verb} rule '{rule_name}' (Target Entity: {target_entity_id})")
    
    if action_verb == "UPDATE":
        if need_meta_update: logger.info(f"  [*] Ranking change: {curr_ranking} -> {proposed_ranking}")
        if added_domains: logger.info(f"  [+] Adding {len(added_domains)} domains")
        if removed_domains: logger.info(f"  [-] Removing {len(removed_domains)} domains")
    
    if dry_run:
        logger.info("DRY-RUN MODE: No changes will be made.")
        return action_verb, len(added_domains), len(removed_domains)

    if rule_id:
        if need_meta_update:
            logger.info(f"  [*] Updating rule ranking to {proposed_ranking}...")
            requests.put(f"{url}/RuleMailCollector/{rule_id}", headers=headers, 
                        json={"input": {"ranking": proposed_ranking}}, verify=verify, timeout=30)
        
        if need_content_update:
            logger.info(f"  [*] Updating rule content. Purging old content...")
            for item in curr_criteria: requests.delete(f"{url}/RuleCriteria/{item['id']}", headers=headers, verify=verify, timeout=30)
            for item in curr_actions: requests.delete(f"{url}/RuleAction/{item['id']}", headers=headers, verify=verify, timeout=30)
    else:
        # Create new rule
        rule_payload = {"name": rule_name, "match": "AND", "is_active": 1, "sub_type": "RuleMailCollector", "ranking": proposed_ranking}
        resp = requests.post(f"{url}/RuleMailCollector", headers=headers, json={"input": rule_payload}, verify=verify, timeout=30)
        rule_id = resp.json()['id']
        logger.info(f"  ✓ CREATED Rule ID: {rule_id}")

    if action_verb == "CREATE" or need_content_update:
        logger.info(f"Adding {len(domains)} exclusion criteria...")
        for crit in proposed_criteria:
            payload = crit.copy(); payload["rules_id"] = rule_id
            requests.post(f"{url}/RuleMailCollector/{rule_id}/RuleCriteria", headers=headers, json={"input": payload}, verify=verify, timeout=30)
        
        action_payload = proposed_action.copy(); action_payload["rules_id"] = rule_id
        requests.post(f"{url}/RuleMailCollector/{rule_id}/RuleAction", headers=headers, json={"input": action_payload}, verify=verify, timeout=30)
        logger.info(f"  ✓ Content updated successfully.")

    logger.info(f"✓ {action_verb} completed successfully!")
    return action_verb, len(added_domains), len(removed_domains)


def main():
    parser = argparse.ArgumentParser(description="Create 'Tanımsız domain' Email Rule")
    parser.add_argument('--force', action='store_true', help="Execute changes (default is dry-run)")
    parser.add_argument('--target-entity', type=str, 
                       default="Root Entity > Ultron Bilişim > Internal IT > Genel destek",
                       help="Target entity path for undefined domains (default: Root Entity > Ultron Bilişim > Internal IT > Genel destek)")
    args = parser.parse_args()
    
    dry_run = not args.force
    
    config = load_config()
    glpi_url = config['GLPI_URL'].rstrip('/')
    app_token = config['GLPI_APP_TOKEN']
    user_token = config['GLPI_USER_TOKEN']
    verify_ssl = config.get('verify_ssl', False)
    
    if dry_run:
        logger.info("Running in DRY-RUN mode. No changes will be made.")
    else:
        logger.info("Running in FORCE mode. Changes will be applied.")

    logger.info(f"Connecting to {glpi_url}...")
    
    try:
        with glpi_session(glpi_url, app_token, user_token, verify=verify_ssl) as session_token:
            headers = {
                "App-Token": app_token,
                "Session-Token": session_token,
                "Content-Type": "application/json"
            }
            
            # Fetch all entities
            entities = fetch_all_entities(glpi_url, headers, verify=verify_ssl)
            logger.info(f"Found {len(entities)} entities.")
            
            # Extract valid mail domains
            domains = []
            for entity in entities:
                mail_domain = entity.get('mail_domain')
                if mail_domain:
                    mail_domain = mail_domain.strip()
                    if not mail_domain:
                        continue
                        
                    # Extract the domain part and normalize with @ prefix
                    if '@' in mail_domain:
                        parts = mail_domain.split('@')
                        domain_part = parts[-1].strip()
                    else:
                        domain_part = mail_domain
                        
                    if domain_part:
                        domains.append(f"@{domain_part}")
            
            # Remove duplicates and sort
            domains = list(set(domains))
            logger.info(f"Found {len(domains)} unique mail domains in entities.")
            
            if not domains:
                logger.error("ERROR: No valid mail domains found in entities!")
                return
            
            # Find target entity
            target_path = args.target_entity
            target_entity_id = find_entity_by_path(entities, target_path)
            
            if not target_entity_id:
                logger.error(f"ERROR: Could not find entity with path: {target_path}")
                
                # Build parent chain helper for debugging
                def get_full_path(entity_id, entities_dict):
                    if entity_id == 0: return "Root"
                    entity = entities_dict.get(entity_id)
                    if not entity: return "Unknown"
                    parent_id = int(entity.get('entities_id', 0))
                    if parent_id == 0: return entity['name']
                    return get_full_path(parent_id, entities_dict) + " > " + entity['name']
                
                entities_dict = {int(e['id']): e for e in entities}
                logger.info("\nEntities with 'destek', 'IT', or 'Ultron' in name (potential matches):")
                for entity in entities:
                    name = entity.get('name', '')
                    if any(x in name.lower() for x in ['destek', 'it', 'ultron']):
                        full_path = get_full_path(int(entity['id']), entities_dict)
                        logger.info(f"  {full_path} (ID: {entity['id']})")
                
                logger.info("\nPlease use --target-entity to specify the correct path.")
                return
            
            logger.info(f"Target entity '{target_path}' found with ID: {target_entity_id}")
            
            # Create or update the rule
            result, added_count, removed_count = create_or_update_undefined_domain_rule(glpi_url, headers, target_entity_id, domains, dry_run=dry_run, verify=verify_ssl)
            
            # Detailed Summary Report
            logger.info("\n" + "="*60)
            logger.info("DETAILED EXECUTION SUMMARY REPORT")
            logger.info("="*60)
            logger.info(f"Target Rule:    Tanımsız-Domain")
            logger.info(f"Target Entity:  {target_path} (ID: {target_entity_id})")
            logger.info(f"Domains Count:  {len(domains)}")
            logger.info(f"Operation:       {result}")
            if result == "UPDATE":
                logger.info(f"  [+] Added:     {added_count}")
                logger.info(f"  [-] Removed:   {removed_count}")
            logger.info("-"*60)
            if result == "SKIPPED":
                logger.info("Status: No changes required (Smart Sync).")
            elif result == "FAILED":
                logger.error("Status: Operation failed. Check logs for details.")
            else:
                verb = "created" if result == "CREATE" else "updated"
                logger.info(f"Status: Rule successfully {verb}.")
            logger.info("="*60 + "\n")
            
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())


if __name__ == "__main__":
    main()
