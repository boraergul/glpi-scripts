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
    """Initialize GLPI session"""
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
    """Close GLPI session"""
    headers = {
        "App-Token": app_token,
        "Session-Token": session_token
    }
    try:
        requests.get(f"{url}/killSession", headers=headers, verify=False, timeout=10)
    except:
        pass

def fetch_all_entities(url, headers):
    """Fetch all entities from GLPI"""
    print("Fetching Entities...")
    entities = []
    range_start = 0
    range_step = 1000
    
    while True:
        range_end = range_start + range_step
        params = {"range": f"{range_start}-{range_end}"}  # Removed expand_dropdowns to get numeric IDs
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

def find_entity_by_path(entities, path):
    """
    Find entity by hierarchical path like 'Root Entity > Ultron Bilişim > Internal IT > Genel destek'
    Returns entity ID or None
    """
    path_parts = [part.strip() for part in path.split('>')]
    
    # Build entity lookup by id
    entities_by_id = {e['id']: e for e in entities}
    
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
            if entity['name'] == part_name and entity.get('entities_id') == current_parent_id:
                current_parent_id = entity['id']
                found = True
                if i == len(path_parts) - 1:  # Last part
                    return entity['id']
                break
        
        if not found:
            return None
    
    return None

def fetch_existing_rule(url, headers, rule_name):
    """Fetch existing rule by name, returns rule ID or None"""
    print(f"Checking for existing rule '{rule_name}'...")
    range_start = 0
    range_step = 100
    
    while True:
        range_end = range_start + range_step
        params = {"range": f"{range_start}-{range_end}", "forcedisplay[0]": "2", "forcedisplay[1]": "1"}
        resp = requests.get(f"{url}/search/RuleMailCollector", headers=headers, params=params, verify=False, timeout=30)
        
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
        
    return None

def create_or_update_undefined_domain_rule(url, headers, target_entity_id, domains, dry_run=True):
    """
    Create or update the 'Tanımsız-Domain' rule
    This rule catches emails from domains NOT in the provided list
    """
    rule_name = "Tanımsız-Domain"
    rule_id = fetch_existing_rule(url, headers, rule_name)
    
    action_verb = "UPDATE" if rule_id else "CREATE"
    
    print(f"\n{'='*60}")
    print(f"PROPOSE: {action_verb} rule '{rule_name}'")
    print(f"{'='*60}")
    print(f"Target Entity ID: {target_entity_id}")
    print(f"Number of domains to exclude: {len(domains)}")
    print(f"\nDomains that will be EXCLUDED (emails from these go to their respective entities):")
    for domain in sorted(domains):
        print(f"  - {domain}")
    print(f"\nAction: Emails from OTHER domains → Entity ID {target_entity_id}")
    print(f"{'='*60}\n")

    if dry_run:
        print("DRY-RUN MODE: No changes will be made. Use --force to execute.")
        return

    # If rule exists, delete old criteria and actions
    if rule_id:
        print(f"Updating existing rule ID: {rule_id}")
        
        # Delete existing criteria
        resp = requests.get(f"{url}/RuleMailCollector/{rule_id}/RuleCriteria", headers=headers, params={"range": "0-5000"}, verify=False, timeout=30)
        if resp.status_code in [200, 206]:
            criteria_list = resp.json()
            for item in criteria_list:
                if int(item.get('rules_id')) == int(rule_id):
                    requests.delete(f"{url}/RuleCriteria/{item['id']}", headers=headers, verify=False, timeout=30)
        
        # Delete existing actions
        resp = requests.get(f"{url}/RuleMailCollector/{rule_id}/RuleAction", headers=headers, params={"range": "0-5000"}, verify=False, timeout=30)
        if resp.status_code in [200, 206]:
            actions_list = resp.json()
            for item in actions_list:
                if int(item.get('rules_id')) == int(rule_id):
                    requests.delete(f"{url}/RuleAction/{item['id']}", headers=headers, verify=False, timeout=30)
        
        print(f"  ✓ Purged old criteria and actions")
    else:
        # Create new rule
        rule_payload = {
            "name": rule_name,
            "match": "AND",
            "is_active": 1,
            "sub_type": "RuleMailCollector",
            "ranking": 2  # As per backup XML
        }
        
        resp = requests.post(f"{url}/RuleMailCollector", headers=headers, json={"input": rule_payload}, verify=False, timeout=30)
        if resp.status_code != 201:
            print(f"  FAILED to create rule: {resp.status_code} {resp.text}")
            return
        
        rule_id = resp.json()['id']
        print(f"  ✓ CREATED Rule ID: {rule_id}")

    # Add criteria: from field does NOT match each domain (condition 3 = is not)
    print(f"Adding {len(domains)} exclusion criteria...")
    for domain in domains:
        criteria_payload = {
            "rules_id": rule_id,
            "criteria": "from",
            "condition": 3,  # 3 = is not / does not equal
            "pattern": domain
        }
        resp = requests.post(f"{url}/RuleMailCollector/{rule_id}/RuleCriteria", 
                           headers=headers, json={"input": criteria_payload}, verify=False, timeout=30)
        if resp.status_code != 201:
            print(f"  WARNING: Failed to add criterion for {domain}")

    print(f"  ✓ Added {len(domains)} exclusion criteria")

    # Add action: Assign to target entity
    action_payload = {
        "rules_id": rule_id,
        "action_type": "assign",
        "field": "entities_id",
        "value": target_entity_id
    }
    resp = requests.post(f"{url}/RuleMailCollector/{rule_id}/RuleAction", 
                        headers=headers, json={"input": action_payload}, verify=False, timeout=30)
    
    if resp.status_code == 201:
        print(f"  ✓ Added action: Assign to Entity ID {target_entity_id}")
    else:
        print(f"  WARNING: Failed to add action")

    print(f"\n✓ {action_verb} completed successfully!")


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
    
    print(f"Connecting to {glpi_url}...")
    session_token = init_session(glpi_url, app_token, user_token)
    
    headers = {
        "App-Token": app_token,
        "Session-Token": session_token,
        "Content-Type": "application/json"
    }
    
    try:
        # Fetch all entities
        entities = fetch_all_entities(glpi_url, headers)
        print(f"Found {len(entities)} entities.")
        
        # Extract valid mail domains
        domains = []
        for entity in entities:
            mail_domain = entity.get('mail_domain')
            if mail_domain:  # Check if not None or empty
                mail_domain = mail_domain.strip()
                if mail_domain and '@' in mail_domain:
                    domains.append(mail_domain)
        
        print(f"Found {len(domains)} entities with valid mail domains.")
        
        if not domains:
            print("ERROR: No valid mail domains found in entities!")
            return
        
        # Find target entity: Root Entity > Ultron Bilişim > Internal IT > Genel destek
        target_path = args.target_entity
        target_entity_id = find_entity_by_path(entities, target_path)
        
        if not target_entity_id:
            print(f"ERROR: Could not find entity with path: {target_path}")
            print("\nDEBUG: Showing entity hierarchy:")
            
            # Build parent chain helper
            def get_full_path(entity_id, entities_dict):
                if entity_id == 0:
                    return "Root"
                entity = entities_dict.get(entity_id)
                if not entity:
                    return "Unknown"
                parent_id = entity.get('entities_id', 0)
                if parent_id == 0:
                    return entity['name']
                return get_full_path(parent_id, entities_dict) + " > " + entity['name']
            
            entities_dict = {e['id']: e for e in entities}
            
            print("\nEntities with 'destek', 'IT', or 'Ultron' in name:")
            for entity in entities:
                name = entity.get('name', '')
                if 'destek' in name.lower() or 'it' in name.lower() or 'ultron' in name.lower():
                    full_path = get_full_path(entity['id'], entities_dict)
                    print(f"  {full_path} (ID: {entity['id']})")
            
            print("\nPlease use --target-entity to specify the correct path.")
            return
        
        print(f"Target entity '{target_path}' found with ID: {target_entity_id}")
        
        # Create or update the rule
        create_or_update_undefined_domain_rule(glpi_url, headers, target_entity_id, domains, dry_run=dry_run)
        
    finally:
        kill_session(glpi_url, app_token, session_token)
        print("\nSession closed.")


if __name__ == "__main__":
    main()
