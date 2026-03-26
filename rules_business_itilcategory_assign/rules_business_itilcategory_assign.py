#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLPI Category-Based Group Assignment Rules Creator
Modernization: v3.1 - Smart Sync, Professional Logging, Dynamic Group Fetching.

Author: Bora Ergül
Date: 25 March 2026
"""

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
        logging.FileHandler('rules_business_itilcategory_assign.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Suppress insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_FILE = 'config.json'

# Category to Group mapping (Source of Truth)
CATEGORY_GROUP_MAP = {
    221: 3,   # Server & Storage → Sistem ve Yedekleme Ekibi
    222: 2,   # Security → Güvenlik Ekibi
    223: 1,   # Network & Firewall → Network & Firewall Ekibi
    226: 17,  # Cloud → Bulut Ekibi
    227: 16,  # Genel Destek → Genel Destek Ekibi
    228: 7,   # Monitoring Alerts → İzleme Ekibi
    # 229 (Major Incident) handled by rules_business_incident_major.py
}

def load_config():
    """Load configuration from config.json with robust path searching"""
    search_paths = [
        os.path.join(os.path.dirname(__file__), CONFIG_FILE),
        os.path.join(os.path.dirname(__file__), '..', 'Config', CONFIG_FILE),
        os.path.join(os.path.dirname(__file__), '..', '..', 'Config', CONFIG_FILE),
        CONFIG_FILE # Current working dir
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

def fetch_categories(url, headers, verify=False):
    """Fetch all ITIL categories for ID resolution"""
    categories_id_to_name = {}
    range_start = 0
    range_step = 100
    logger.info("Fetching ITIL Categories...")
    try:
        while True:
            params = {"range": f"{range_start}-{range_start+range_step-1}", "is_deleted": 0}
            r = requests.get(f"{url}/ITILCategory", headers=headers, params=params, verify=verify, timeout=30)
            if r.status_code not in [200, 206]: break
            batch = r.json()
            if not batch: break
            for item in batch:
                categories_id_to_name[str(item['id'])] = item.get('completename', item.get('name', 'Unknown'))
            if len(batch) < range_step: break
            range_start += range_step
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
    return categories_id_to_name

def fetch_groups(url, headers, verify=False):
    """Fetch all technician groups dynamically from API"""
    groups_id_to_name = {}
    range_start = 0
    range_step = 100
    logger.info("Fetching Groups...")
    try:
        while True:
            params = {"range": f"{range_start}-{range_start+range_step-1}", "is_deleted": 0}
            r = requests.get(f"{url}/Group", headers=headers, params=params, verify=verify, timeout=30)
            if r.status_code not in [200, 206]: break
            batch = r.json()
            if not batch: break
            for item in batch:
                groups_id_to_name[str(item['id'])] = item.get('completename', item.get('name', 'Unknown'))
            if len(batch) < range_step: break
            range_start += range_step
    except Exception as e:
        logger.error(f"Error fetching groups: {e}")
    return groups_id_to_name

def fetch_existing_rules(url, headers, verify=False):
    existing_rules = {} # Name -> ID
    logger.info("Fetching existing Category rules via Search...")
    range_start = 0
    range_step = 100
    try:
        while True:
            params = {
                "criteria[0][field]": "1", # Name
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": "Auto-Category-",
                "forcedisplay[0]": "2", # ID
                "range": f"{range_start}-{range_start+range_step-1}",
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
                    existing_rules[r_name] = int(r_id)
            total_count = data.get('totalcount', 0)
            if range_start + range_step >= total_count: break
            range_start += range_step
    except Exception as e:
        logger.warning(f"Could not fetch existing rules: {e}")
    return existing_rules

def get_rule_details(url, headers, rule_id, verify=False):
    """Fetch criteria and actions for Smart Sync"""
    criteria = []
    actions = []
    # Criteria
    resp = requests.get(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, params={"range": "0-1000"}, verify=verify, timeout=30)
    if resp.status_code in [200, 206]:
        criteria = [item for item in resp.json() if str(item.get('rules_id')) == str(rule_id)]
    # Actions
    resp = requests.get(f"{url}/RuleTicket/{rule_id}/RuleAction", headers=headers, params={"range": "0-1000"}, verify=verify, timeout=30)
    if resp.status_code in [200, 206]:
        actions = [item for item in resp.json() if str(item.get('rules_id')) == str(rule_id)]
    return criteria, actions

def clear_rule_details(url, headers, rule_id, verify=False):
    """Clear all criteria and actions from a rule"""
    criteria, actions = get_rule_details(url, headers, rule_id, verify=verify)
    for item in actions:
        try:
            requests.delete(f"{url}/RuleTicket/{rule_id}/RuleAction/{item['id']}", headers=headers, verify=verify, timeout=30)
        except Exception as e:
            logger.error(f"Failed to delete action {item['id']}: {e}")
    for item in criteria:
        try:
            requests.delete(f"{url}/RuleTicket/{rule_id}/RuleCriteria/{item['id']}", headers=headers, verify=verify, timeout=30)
        except Exception as e:
            logger.error(f"Failed to delete criteria {item['id']}: {e}")

def resolve_id(field, value, maps):
    """Helper to resolve ID to human-readable name for logging"""
    val_str = str(value)
    if field == "itilcategories_id":
        return f"{val_str} ({maps['categories'].get(val_str, 'Unknown')})"
    elif field in ["_groups_id_assign"]:
        return f"{val_str} ({maps['groups'].get(val_str, 'Unknown')})"
    elif field == "_users_id_assign" and val_str == "1":
        return f"{val_str} (Is Empty)"
    elif field == "_groups_id_assign" and val_str == "1":
         return f"{val_str} (Is Empty)"
    return val_str

def create_or_update_rule(url, headers, rule_name, criteria_list, action_list, existing_rules_map, res_maps, dry_run=True, verify=False):
    """
    Creates or updates a rule using Smart Sync logic.
    """
    rule_input = {
        "name": rule_name,
        "match": "AND",
        "is_active": 1,
        "sub_type": "RuleTicket",
        "entities_id": 0, # Root
        "is_recursive": 1,
        "condition": 3, # Add/Update
        "ranking": 20
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
            logger.info(f"SKIP: Rule '{rule_name}' already up to date.")
            return "SKIPPED"

        action_verb = "UPDATE"
        if dry_run:
            logger.info(f"[DRY RUN] Would UPDATE '{rule_name}' (ID: {rule_id})")
            for d in diffs: logger.info(f"  - Change: {d}")
            return action_verb

        logger.info(f"Updating Rule '{rule_name}' (ID: {rule_id})")
        for d in diffs: logger.info(f"  - Change detected: {d}")
            
        try:
             requests.put(f"{url}/RuleTicket/{rule_id}", headers=headers, json={"input": {"id": rule_id, **rule_input}}, verify=verify, timeout=30)
             clear_rule_details(url, headers, rule_id, verify=verify)
             for crit in criteria_list:
                requests.post(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, json={"input": {"rules_id": rule_id, **crit}}, verify=verify, timeout=30)
             for act in action_list:
                 requests.post(f"{url}/RuleTicket/{rule_id}/RuleAction", headers=headers, json={"input": {"rules_id": rule_id, **act}}, verify=verify, timeout=30)
             logger.info(f"  ✓ UPDATED '{rule_name}'.")
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
            logger.info(f"  ✓ CREATED '{rule_name}'.")
            return action_verb
        except Exception as e:
            logger.error(f"Failed to create rule '{rule_name}': {e}")
            return "FAILED"

def clean_category_name(name):
    """Clean category name for use in rule name"""
    if ' > ' in name: name = name.split(' > ')[-1]
    name = name.replace('&#38;', 'And').replace('&amp;', 'And').replace('&', 'And')
    return name.replace(' ', '-')

def main():
    parser = argparse.ArgumentParser(description="GLPI Category-Based Group Assignment Rule Creator (v3.1)")
    parser.add_argument('--force', action='store_true', help="Execute changes (default is dry-run)")
    args = parser.parse_args()
    
    dry_run = not args.force
    if dry_run: logger.info("Running in DRY-RUN mode. No changes will be applied.")
    else: logger.info("Running in FORCE mode. Changes will be applied.")

    config = load_config()
    glpi_url = config.get('GLPI_URL').rstrip('/')
    app_token = config.get('GLPI_APP_TOKEN')
    user_token = config.get('GLPI_USER_TOKEN')
    verify_ssl = config.get('verify_ssl', False)

    report = {"CREATE": [], "UPDATE": [], "SKIPPED": [], "FAILED": []}
    
    try:
        with glpi_session(glpi_url, app_token, user_token, verify=verify_ssl) as session_token:
            headers = {"App-Token": app_token, "Session-Token": session_token, "Content-Type": "application/json"}
            
            categories_map = fetch_categories(glpi_url, headers, verify=verify_ssl)
            groups_map = fetch_groups(glpi_url, headers, verify=verify_ssl)
            existing_rules_map = fetch_existing_rules(glpi_url, headers, verify=verify_ssl)
            
            res_maps = {"categories": categories_map, "groups": groups_map}

            logger.info("\n--- Processing Rules ---")
            
            for category_id, group_id in CATEGORY_GROUP_MAP.items():
                cat_id_str = str(category_id)
                if cat_id_str not in categories_map:
                    logger.warning(f"SKIP: Category ID {category_id} not found in GLPI.")
                    continue
                
                cat_name = categories_map[cat_id_str]
                group_name = groups_map.get(str(group_id), f"Unknown ({group_id})")
                rule_name = f"Auto-Category-{clean_category_name(cat_name)}"
                
                logger.info(f"Processing Category: '{cat_name}' -> Assign Group: '{group_name}'")

                # Criteria: Category = X, Technician empty, Group empty
                criteria = [
                    {"criteria": "itilcategories_id", "condition": 0, "pattern": category_id},
                    {"criteria": "_users_id_assign", "condition": 9, "pattern": "1"}, # 9 = is empty
                    {"criteria": "_groups_id_assign", "condition": 9, "pattern": "1"}  # 9 = is empty
                ]
                
                # Action: Assign Group Y
                actions = [{"field": "_groups_id_assign", "action_type": "assign", "value": group_id}]
                
                result = create_or_update_rule(glpi_url, headers, rule_name, criteria, actions, existing_rules_map, res_maps, dry_run=dry_run, verify=verify_ssl)
                if result in report: report[result].append(rule_name)

            # Final Report
            logger.info("-" * 60)
            logger.info("DETAILED EXECUTION SUMMARY REPORT")
            logger.info("-" * 60)
            for key, val in report.items():
                if val:
                    logger.info(f"{key} ({len(val)}):")
                    for name in val: logger.info(f"  {'*' if key=='UPDATE' else '+' if key=='CREATE' else '-'} {name}")
            logger.info("-" * 60)
            logger.info(f"Total Processed: {len(CATEGORY_GROUP_MAP)} mapping definitions.")
            logger.info("-" * 60)
            
    except Exception as e:
        logger.critical(f"CRITICAL ERROR: {e}")
        import traceback
        logger.debug(traceback.format_exc())

if __name__ == "__main__":
    main()
