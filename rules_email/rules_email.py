import requests
import json
import os
import sys
import urllib3
import argparse

# Suppress insecure request warnings
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
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
    print(f"Error: File {CONFIG_FILE} not found in any of the search paths:")
    for path in search_paths:
        print(f"  - {os.path.abspath(path)}")
    sys.exit(1)

def init_session(url, app_token, user_token):
    headers = {
        "App-Token": app_token,
        "Authorization": f"user_token {user_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(f"{url}/initSession", headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        return response.json()['session_token']
    except Exception as e:
        print(f"Failed to initialize session: {e}")
        sys.exit(1)

def kill_session(url, app_token, session_token):
    headers = {
        "App-Token": app_token,
        "Session-Token": session_token
    }
    try:
        requests.get(f"{url}/killSession", headers=headers, verify=False, timeout=10)
    except:
        pass

def fetch_all_entities(url, headers):
    print("Fetching Entities...")
    entities = []
    range_start = 0
    range_step = 1000
    
    while True:
        range_end = range_start + range_step
        params = {"range": f"{range_start}-{range_end}", "expand_dropdowns": "true"}
        resp = requests.get(f"{url}/Entity", headers=headers, params=params, verify=False, timeout=30)
        
        if resp.status_code not in [200, 206]:
            print(f"Error fetching entities: {resp.status_code}")
            break
            
        batch = resp.json()
        if not batch: break
        
        entities.extend(batch)
        if len(batch) < range_step: break
        range_start += range_step
        
    return entities

def fetch_existing_rules(url, headers):
    print("Fetching existing Mail Rules...")
    rules_map = {}
    range_start = 0
    range_step = 100
    
    while True:
        range_end = range_start + range_step
        # 1=Name, 2=ID
        params = {"range": f"{range_start}-{range_end}", "forcedisplay[0]": "2", "forcedisplay[1]": "1"}
        resp = requests.get(f"{url}/search/RuleMailCollector", headers=headers, params=params, verify=False, timeout=30)
        
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
        
    return rules_map

def create_or_update_rule(url, headers, entity_name, entity_id, mail_domain, existing_rules, dry_run=True):
    # Replace spaces in entity name with hyphens for consistent naming
    entity_name_clean = entity_name.replace(' ', '-')
    rule_name = f"Auto-Email-{entity_name_clean}"
    rule_id = existing_rules.get(rule_name)
    
    # Check valid domain
    if not mail_domain or '@' not in mail_domain:
        # print(f"SKIP: Entity '{entity_name}' has no valid mail domain ({mail_domain}).")
        return

    # Prepare Regex Pattern: /@domain\.com$/i (Match end of string)
    # Escape dots
    escaped_domain = mail_domain.replace('.', '\.')
    regex_pattern = f"/{escaped_domain}$/i"
    
    action_verb = "UPDATE" if rule_id else "CREATE"
    
    print(f"PROPOSE: {action_verb} rule '{rule_name}' for Entity '{entity_name}' (ID: {entity_id})")
    print(f"  Criteria: From email header (name) REGEX MATCHES '{regex_pattern}'")
    print(f"  Action 1: Assign Entity -> {entity_name} (ID: {entity_id})")

    if dry_run:
        return

    # If rule exists, update it
    if rule_id:
        # Delete existing criteria and actions
        print(f"  Purging existing criteria and actions for Rule ID: {rule_id}")
        
        # Delete Criteria
        resp = requests.get(f"{url}/RuleMailCollector/{rule_id}/RuleCriteria", headers=headers, params={"range": "0-5000"}, verify=False, timeout=30)
        if resp.status_code in [200, 206]:
            for item in resp.json():
                if int(item.get('rules_id')) == int(rule_id):
                    requests.delete(f"{url}/RuleCriteria/{item['id']}", headers=headers, verify=False, timeout=30)
        
        # Delete Actions
        resp = requests.get(f"{url}/RuleMailCollector/{rule_id}/RuleAction", headers=headers, params={"range": "0-5000"}, verify=False, timeout=30)
        if resp.status_code in [200, 206]:
            for item in resp.json():
                if int(item.get('rules_id')) == int(rule_id):
                    requests.delete(f"{url}/RuleAction/{item['id']}", headers=headers, verify=False, timeout=30)
        
        print(f"  ✓ UPDATED Rule ID: {rule_id}")
    else:
        # Create new rule
        rule_payload = {
            "name": rule_name,
            "match": "AND",
            "is_active": 1,
            "sub_type": "RuleMailCollector", 
            "ranking": 1
        }
        
        resp = requests.post(f"{url}/RuleMailCollector", headers=headers, json={"input": rule_payload}, verify=False, timeout=30)
        if resp.status_code != 201:
            print(f"  FAILED to create rule: {resp.status_code} {resp.text}")
            return
        
        rule_id = resp.json()['id']
        print(f"  ✓ CREATED Rule ID: {rule_id}")

    # Add Criteria (condition: 6 = Regex match)
    criteria_payload = {
        "rules_id": rule_id,
        "criteria": "from", 
        "condition": 6,
        "pattern": regex_pattern
    }
    requests.post(f"{url}/RuleMailCollector/{rule_id}/RuleCriteria", headers=headers, json={"input": criteria_payload}, verify=False, timeout=30)

    # Add Action: Assign Entity
    action_entity_payload = {
        "rules_id": rule_id,
        "action_type": "assign",
        "field": "entities_id",
        "value": entity_id
    }
    requests.post(f"{url}/RuleMailCollector/{rule_id}/RuleAction", headers=headers, json={"input": action_entity_payload}, verify=False, timeout=30)


def main():
    parser = argparse.ArgumentParser(description="Create Email Receiver Rules")
    parser.add_argument('--force', action='store_true', help="Execute changes (default is dry-run)")
    args = parser.parse_args()
    
    dry_run = not args.force
    
    config = load_config()
    glpi_url = config['GLPI_URL'].rstrip('/')
    app_token = config['GLPI_APP_TOKEN']
    user_token = config['GLPI_USER_TOKEN']
    
    print(f"Connecting to {glpi_url}...")
    session_token = init_session(glpi_url, app_token, user_token)
    
    headers = {
        "App-Token": app_token,
        "Session-Token": session_token,
        "Content-Type": "application/json"
    }
    
    try:
        entities = fetch_all_entities(glpi_url, headers)
        existing_rules = fetch_existing_rules(glpi_url, headers)
        
        print(f"Found {len(entities)} entities and {len(existing_rules)} existing rules.")
        print("-" * 60)
        
        for entity in entities:
            e_id = entity.get('id')
            e_name = entity.get('name')
            mail_domain = entity.get('mail_domain') # Correct field name from discovery
            
            # Skip templates/root if needed? Root (ID 0) usually valid but mail_domain might be empty.
            if e_id == 0: continue 

            create_or_update_rule(glpi_url, headers, e_name, e_id, mail_domain, existing_rules, dry_run=dry_run)
            
    finally:
        kill_session(glpi_url, app_token, session_token)
        print("\nSession closed.")

if __name__ == "__main__":
    main()
