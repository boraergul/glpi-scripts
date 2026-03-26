import requests
import json
import os
import sys
import urllib3
import argparse
import logging
import re
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('rules_email.log', encoding='utf-8')
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
    session_token = init_session(url, app_token, user_token, verify=verify)
    try:
        yield session_token
    finally:
        kill_session(url, app_token, session_token, verify=verify)
        logger.info("Session closed.")

def fetch_all_entities(url, headers, verify=False):
    logger.info("Fetching Entities...")
    entities = []
    range_start = 0
    range_step = 1000
    
    while True:
        range_end = range_start + range_step
        params = {"range": f"{range_start}-{range_end}", "expand_dropdowns": "true"}
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

def fetch_existing_rules(url, headers, verify=False):
    logger.info("Fetching existing Mail Rules...")
    rules_map = {}
    range_start = 0
    range_step = 100
    
    while True:
        range_end = range_start + range_step
        # 1=Name, 2=ID
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
                if name:
                    rules_map[name] = rule_id
            
            if len(data) < range_step: break
            range_start += range_step
        except Exception as e:
            logger.error(f"Exception while fetching rules: {e}")
            break
            
    return rules_map

def get_rule_details(url, headers, rule_id, verify=False):
    """Fetch criteria and actions for a specific rule"""
    criteria = []
    actions = []
    
    # Criteria
    resp = requests.get(f"{url}/RuleMailCollector/{rule_id}/RuleCriteria", headers=headers, params={"range": "0-5000"}, verify=verify, timeout=30)
    if resp.status_code in [200, 206]:
        criteria = [item for item in resp.json() if int(item.get('rules_id')) == int(rule_id)]
        
    # Actions
    resp = requests.get(f"{url}/RuleMailCollector/{rule_id}/RuleAction", headers=headers, params={"range": "0-5000"}, verify=verify, timeout=30)
    if resp.status_code in [200, 206]:
        actions = [item for item in resp.json() if int(item.get('rules_id')) == int(rule_id)]
        
    return criteria, actions

def create_or_update_rule(url, headers, entity_name, entity_id, mail_domain, existing_rules, dry_run=True, verify=False):
    # Normalize domain: strip leading '@' if present
    clean_domain = (mail_domain or "").strip()
    if clean_domain.startswith('@'):
        clean_domain = clean_domain[1:]
        
    if not clean_domain or '.' not in clean_domain:
        logger.warning(f"SKIP: Entity '{entity_name}' has no valid mail domain ({mail_domain}).")
        return "MISSING_DOMAIN"

    # Replace spaces in entity name with hyphens for consistent naming
    entity_name_clean = entity_name.replace(' ', '-')
    rule_name = f"Auto-Email-{entity_name_clean}"
    rule_id = existing_rules.get(rule_name)
    
    # Prepare Regex Pattern: /@domain\.com$/i (Match end of string)
    escaped_domain = re.escape(clean_domain)
    regex_pattern = f"/@{escaped_domain}$/i"
    
    proposed_criteria = {
        "criteria": "from", 
        "condition": 6, # 6 = Regex match
        "pattern": regex_pattern
    }
    proposed_action = {
        "action_type": "assign",
        "field": "entities_id",
        "value": str(entity_id) # API values are strings in criteria/actions
    }
    
    if rule_id:
        # Check if update is actually needed (Smart Sync)
        curr_criteria, curr_actions = get_rule_details(url, headers, rule_id, verify=verify)
        
        match_criteria = any(
            c.get('criteria') == proposed_criteria['criteria'] and 
            int(c.get('condition')) == proposed_criteria['condition'] and 
            c.get('pattern') == proposed_criteria['pattern']
            for c in curr_criteria
        )
        
        match_actions = any(
            a.get('action_type') == proposed_action['action_type'] and 
            a.get('field') == proposed_action['field'] and 
            str(a.get('value')) == proposed_action['value']
            for a in curr_actions
        )
        
        if match_criteria and match_actions and len(curr_criteria) == 1 and len(curr_actions) == 1:
            logger.info(f"SKIP: Rule '{rule_name}' is already up to date.")
            return "SKIPPED"

        action_verb = "UPDATE"
    else:
        action_verb = "CREATE"
    
    logger.info(f"PROPOSE: {action_verb} rule '{rule_name}' for Entity '{entity_name}' (ID: {entity_id})")
    logger.info(f"  Criteria: From email header (name) REGEX MATCHES '{regex_pattern}'")
    logger.info(f"  Action 1: Assign Entity -> {entity_name} (ID: {entity_id})")

    if dry_run:
        return action_verb

    # If rule exists, update it by purging and recreating (simplest way to ensure clean state if different)
    if rule_id:
        logger.info(f"  Purging existing criteria and actions for Rule ID: {rule_id}")
        
        # Delete Criteria
        criteria, actions = get_rule_details(url, headers, rule_id, verify=verify)
        for item in criteria:
            try:
                requests.delete(f"{url}/RuleCriteria/{item['id']}", headers=headers, verify=verify, timeout=30)
            except Exception as e:
                logger.error(f"Failed to delete criteria {item['id']}: {e}")
        
        # Delete Actions
        for item in actions:
            try:
                requests.delete(f"{url}/RuleAction/{item['id']}", headers=headers, verify=verify, timeout=30)
            except Exception as e:
                logger.error(f"Failed to delete action {item['id']}: {e}")
        
        logger.info(f"  ✓ UPDATED Rule ID: {rule_id}")
    else:
        # Create new rule
        rule_payload = {
            "name": rule_name,
            "match": "AND",
            "is_active": 1,
            "sub_type": "RuleMailCollector", 
            "ranking": 1
        }
        
        try:
            resp = requests.post(f"{url}/RuleMailCollector", headers=headers, json={"input": rule_payload}, verify=verify, timeout=30)
            resp.raise_for_status()
            rule_id = resp.json()['id']
            logger.info(f"  ✓ CREATED Rule ID: {rule_id}")
        except Exception as e:
            logger.error(f"  FAILED to create rule: {e}")
            return "FAILED"

    # Add Criteria
    try:
        criteria_payload = proposed_criteria.copy()
        criteria_payload["rules_id"] = rule_id
        requests.post(f"{url}/RuleMailCollector/{rule_id}/RuleCriteria", headers=headers, json={"input": criteria_payload}, verify=verify, timeout=30)
    except Exception as e:
        logger.error(f"Failed to add criteria: {e}")

    # Add Action
    try:
        action_payload = proposed_action.copy()
        action_payload["rules_id"] = rule_id
        requests.post(f"{url}/RuleMailCollector/{rule_id}/RuleAction", headers=headers, json={"input": action_payload}, verify=verify, timeout=30)
    except Exception as e:
        logger.error(f"Failed to add action: {e}")
        
    return action_verb


def main():
    parser = argparse.ArgumentParser(description="Create Email Receiver Rules")
    parser.add_argument('--force', action='store_true', help="Execute changes (default is dry-run)")
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
            
            entities = fetch_all_entities(glpi_url, headers, verify=verify_ssl)
            existing_rules = fetch_existing_rules(glpi_url, headers, verify=verify_ssl)
            
            logger.info(f"Found {len(entities)} entities and {len(existing_rules)} existing rules.")
            logger.info("-" * 60)
            
            # Detailed stats collection
            report = {
                "CREATE": [],
                "UPDATE": [],
                "SKIPPED": [],
                "MISSING_DOMAIN": [],
                "FAILED": []
            }
            
            for entity in entities:
                e_id = entity.get('id')
                e_name = entity.get('name')
                mail_domain = entity.get('mail_domain')
                
                # Skip templates/root if needed? Root (ID 0) usually valid but mail_domain might be empty.
                if e_id == 0: continue 

                result = create_or_update_rule(glpi_url, headers, e_name, e_id, mail_domain, existing_rules, dry_run=dry_run, verify=verify_ssl)
                if result in report:
                    report[result].append(e_name)
            
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
                # Listing all might be long, but requested by user
                for name in report["SKIPPED"]: logger.info(f"  - {name}")

            if report["MISSING_DOMAIN"]:
                logger.info(f"SKIPPED - MISSING MAIL DOMAIN ({len(report['MISSING_DOMAIN'])}):")
                for name in report["MISSING_DOMAIN"]: logger.info(f"  ? {name}")

            if report["FAILED"]:
                logger.error(f"FAILED OPERATIONS ({len(report['FAILED'])}):")
                for name in report["FAILED"]: logger.error(f"  ! {name}")
                
            logger.info("-" * 60)
            logger.info(f"Total Processed: {len(entities)} entities.")
            logger.info("-" * 60)
            
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        import traceback
        logger.debug(traceback.format_exc())

if __name__ == "__main__":
    main()
