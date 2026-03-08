#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLPI Category-Based Group Assignment Rules Creator
Creates business rules to automatically assign technician groups based on ITIL category selection.

Author: Bora Ergül
Version: 1.0
Date: 25 December 2024
"""

import requests
import json
import os
import sys
import argparse
import urllib3
from typing import Dict, List, Optional, Tuple

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Category to Group mapping
CATEGORY_GROUP_MAP = {
    221: 3,   # Server & Storage → Sistem ve Yedekleme Ekibi
    222: 2,   # Security → Güvenlik Ekibi
    223: 1,   # Network & Firewall → Network & Firewall Ekibi
    225: 18,  # Endpoint & End-User → Endpoint & Enduser Ekibi
    226: 17,  # Cloud → Bulut Ekibi
    227: 16,  # Genel Destek → Genel Destek Ekibi
    228: 7,   # Monitoring Alerts → İzleme Ekibi
    # 229 (Major Incident) handled by rules_business_incident_major.py
}

# Group names (hardcoded to avoid API timeout issues)
GROUP_NAMES = {
    1: "Network & Firewall Ekibi",
    2: "Güvenlik Ekibi",
    3: "Sistem ve Yedekleme Ekibi",
    7: "İzleme Ekibi",
    16: "Genel Destek Ekibi",
    17: "Bulut Ekibi",
    18: "Endpoint & Enduser Ekibi",
    45: "Major Incident Ekibi"
}

def load_config() -> Dict:
    """Load configuration from config.json file."""
    config_paths = [
        'config.json',
        '../config/config.json',
        '../Config/config.json',
        '../../config/config.json',
        '../../Config/config.json'
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    raise FileNotFoundError("config.json not found in any of the expected locations")

def init_session(config: Dict) -> Tuple[str, Dict]:
    """Initialize GLPI API session."""
    glpi_url = config['GLPI_URL']
    headers = {
        'Content-Type': 'application/json',
        'App-Token': config['GLPI_APP_TOKEN'],
        'Authorization': f"user_token {config['GLPI_USER_TOKEN']}"
    }
    
    try:
        response = requests.get(
            f"{glpi_url}/initSession",
            headers=headers,
            verify=False,
            timeout=30
        )
        response.raise_for_status()
        session_token = response.json()['session_token']
        headers['Session-Token'] = session_token
        print(f"✓ Session initialized: {session_token[:20]}...")
        return glpi_url, headers
    except Exception as e:
        print(f"✗ Failed to initialize session: {e}")
        sys.exit(1)

def kill_session(glpi_url: str, headers: Dict):
    """Close GLPI API session."""
    try:
        requests.get(f"{glpi_url}/killSession", headers=headers, verify=False, timeout=30)
        print("✓ Session closed")
    except:
        pass

def fetch_categories(glpi_url: str, headers: Dict) -> Dict[int, str]:
    """Fetch all ITIL categories."""
    categories = {}
    range_start = 0
    range_size = 100
    
    print("Fetching ITIL Categories...")
    
    while True:
        try:
            response = requests.get(
                f"{glpi_url}/ITILCategory",
                headers={**headers, 'Range': f'{range_start}-{range_start + range_size - 1}'},
                verify=False,
                timeout=30
            )
            
            if response.status_code == 206 or response.status_code == 200:
                batch = response.json()
                if not batch:
                    break
                
                for cat in batch:
                    categories[cat['id']] = cat['completename']
                
                if response.status_code == 200:
                    break
                    
                range_start += range_size
            else:
                break
                
        except Exception as e:
            print(f"Warning: Error fetching categories: {e}")
            break
    
    print(f"✓ Loaded {len(categories)} categories")
    return categories

def fetch_groups(glpi_url: str, headers: Dict) -> Dict[int, str]:
    """Fetch all technician groups."""
    groups = {}
    range_start = 0
    range_size = 100
    
    print("Fetching Groups...")
    
    while True:
        try:
            response = requests.get(
                f"{glpi_url}/Group",
                headers={**headers, 'Range': f'{range_start}-{range_start + range_size - 1}'},
                verify=False,
                timeout=30
            )
            
            if response.status_code == 206 or response.status_code == 200:
                batch = response.json()
                if not batch:
                    break
                
                for group in batch:
                    groups[group['id']] = group.get('completename', group.get('name', 'Unknown'))
                
                if response.status_code == 200:
                    break
                    
                range_start += range_size
            else:
                break
                
        except Exception as e:
            print(f"Warning: Error fetching groups: {e}")
            break
    
    print(f"✓ Loaded {len(groups)} groups")
    return groups

def fetch_existing_rules(glpi_url: str, headers: Dict) -> Dict[str, int]:
    """Fetch existing category-based group assignment rules."""
    existing_rules = {}
    
    print("Fetching existing rules...")
    
    range_start = 0
    range_step = 100
    
    try:
        while True:
            params = {
                "criteria[0][field]": "1",  # Name field
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": "Auto-Category-",
                "forcedisplay[0]": "2",  # ID field
                "is_deleted": 0
            }
            
            # Add Range header for pagination
            search_headers = {**headers, 'Range': f'{range_start}-{range_start+range_step-1}'}
            
            response = requests.get(
                f"{glpi_url}/search/RuleTicket",
                headers=search_headers,
                params=params,
                verify=False,
                timeout=30
            )
            
            if response.status_code not in [200, 206]:
                break
            
            data = response.json()
            if 'data' not in data:
                break
            
            for item in data['data']:
                # Field 1 is Name, Field 2 is ID
                rule_name = item.get('1')
                rule_id = item.get('2')
                if rule_name and rule_id:
                    existing_rules[rule_name] = int(rule_id)
            
            total_count = data.get('totalcount', 0)
            if range_start + range_step >= total_count:
                break
                
            range_start += range_step
        
        print(f"✓ Found {len(existing_rules)} existing rules")
        
    except Exception as e:
        print(f"Warning: Could not fetch existing rules: {e}")
    
    return existing_rules

def clear_rule_details(url, headers, rule_id):
    """Safely clear existing criteria and actions for a rule (Wipe and Rebuild)."""
    # Clear Actions
    try:
        r = requests.get(f"{url}/RuleTicket/{rule_id}/RuleAction", headers=headers, params={"range": "0-5000"}, verify=False, timeout=30)
        if r.status_code in [200, 206]:
            for item in r.json():
                if str(item.get('rules_id')) == str(rule_id):
                    requests.delete(f"{url}/RuleTicket/{rule_id}/RuleAction/{item['id']}", headers=headers, verify=False, timeout=30)
    except Exception as e:
         print(f"Warning: Failed to clear actions for rule {rule_id}: {e}")

    # Clear Criteria
    try:
        r = requests.get(f"{url}/RuleTicket/{rule_id}/RuleCriteria", headers=headers, params={"range": "0-5000"}, verify=False, timeout=30)
        if r.status_code in [200, 206]:
            for item in r.json():
                if str(item.get('rules_id')) == str(rule_id):
                    requests.delete(f"{url}/RuleTicket/{rule_id}/RuleCriteria/{item['id']}", headers=headers, verify=False, timeout=30)
    except Exception as e:
         print(f"Warning: Failed to clear criteria for rule {rule_id}: {e}")


def create_or_update_rule(
    glpi_url: str,
    headers: Dict,
    rule_name: str,
    category_id: int,
    category_name: str,
    group_id: int,
    group_name: str,
    existing_rules: Dict[str, int],
    dry_run: bool = True
) -> bool:
    """Create or update a category-based group assignment rule."""
    
    print(f"\n{'='*70}")
    print(f"PROPOSE: {'UPDATE' if rule_name in existing_rules else 'CREATE'} rule '{rule_name}'")
    print(f"  Category: {category_name} (ID: {category_id})")
    print(f"  Assign Group: {group_name} (ID: {group_id})")
    print(f"  Criteria:")
    print(f"    - ITIL Category = {category_name} (ID: {category_id})")
    print(f"    - Technician does not exist")
    print(f"    - Technician group does not exist")
    print(f"  Actions:")
    print(f"    - Assign Technician Group → {group_name} (ID: {group_id})")
    
    if dry_run:
        print(f"  [DRY RUN] No changes made")
        return True
    
    try:
        # Check if rule exists
        rule_id = existing_rules.get(rule_name)
        
        if rule_id:
            # Update existing rule - delete old criteria/actions
            print(f"  Updating existing rule (ID: {rule_id})...")
            
            # Update rule properties to ensure condition is set to 3 (Add/Update)
            rule_data = {
                "id": rule_id,
                "name": rule_name,
                "is_active": 1,
                "is_recursive": 1,
                "match": "AND",
                "condition": 3,  # 3 = Add/Update
                "ranking": 20
            }
            try:
                requests.put(f"{glpi_url}/RuleTicket/{rule_id}", headers=headers, json={"input": rule_data}, verify=False, timeout=30)
            except Exception as e:
                print(f"  Warning: Failed to update rule properties: {e}")

            # Safe Purge
            clear_rule_details(glpi_url, headers, rule_id)
        else:
            # Create new rule
            rule_data = {
                "name": rule_name,
                "is_active": 1,
                "is_recursive": 1,
                "match": "AND",
                "condition": 3,  # 3 = Add/Update
                "ranking": 20  # After SLA rules (15) but before other rules
            }
            
            response = requests.post(
                f"{glpi_url}/RuleTicket",
                headers=headers,
                json={"input": rule_data},
                verify=False,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                rule_id = response.json()['id']
                print(f"  ✓ Created rule (ID: {rule_id})")
            else:
                print(f"  ✗ Failed to create rule: {response.status_code}")
                return False
        
        # Add criterion 1: Category = category_id
        criterion_data = {
            "rules_id": rule_id,
            "criteria": "itilcategories_id",
            "condition": 0,  # is / equals
            "pattern": category_id
        }
        
        response = requests.post(
            f"{glpi_url}/RuleTicket/{rule_id}/RuleCriteria",
            headers=headers,
            json={"input": criterion_data},
            verify=False,
            timeout=30
        )
        
        if response.status_code not in [200, 201]:
            print(f"  ✗ Failed to add category criterion: {response.status_code}")
            return False
        
        # Add criterion 2: Technician is empty
        criterion_data = {
            "rules_id": rule_id,
            "criteria": "_users_id_assign",
            "condition": 9,  # is empty
            "pattern": "1"
        }
        
        response = requests.post(
            f"{glpi_url}/RuleTicket/{rule_id}/RuleCriteria",
            headers=headers,
            json={"input": criterion_data},
            verify=False,
            timeout=30
        )
        
        if response.status_code not in [200, 201]:
            print(f"  ✗ Failed to add technician criterion: {response.status_code}")
            return False
        
        # Add criterion 3: Technician group is empty
        criterion_data = {
            "rules_id": rule_id,
            "criteria": "_groups_id_assign",
            "condition": 9,  # is empty
            "pattern": "1"
        }
        
        response = requests.post(
            f"{glpi_url}/RuleTicket/{rule_id}/RuleCriteria",
            headers=headers,
            json={"input": criterion_data},
            verify=False,
            timeout=30
        )
        
        if response.status_code not in [200, 201]:
            print(f"  ✗ Failed to add group criterion: {response.status_code}")
            return False
        
        # Add action: Assign group
        action_data = {
            "rules_id": rule_id,
            "action_type": "assign",
            "field": "_groups_id_assign",
            "value": group_id
        }
        
        response = requests.post(
            f"{glpi_url}/RuleTicket/{rule_id}/RuleAction",
            headers=headers,
            json={"input": action_data},
            verify=False,
            timeout=30
        )
        
        if response.status_code not in [200, 201]:
            print(f"  ✗ Failed to add action: {response.status_code}")
            return False
        
        print(f"  ✓ {'UPDATED' if rule_name in existing_rules else 'CREATED'} Rule ID: {rule_id}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def clean_category_name(name: str) -> str:
    """Clean category name for use in rule name (replace spaces with hyphens)."""
    # Remove "Root entity > " prefix if present
    if ' > ' in name:
        name = name.split(' > ')[-1]
    
    # Replace HTML entities
    name = name.replace('&#38;', 'And')
    name = name.replace('&amp;', 'And')
    
    # Replace & with And
    name = name.replace('&', 'And')
    
    # Replace spaces with hyphens
    name = name.replace(' ', '-')
    
    return name

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Create GLPI category-based group assignment rules'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Actually create/update rules (default is dry-run)'
    )
    args = parser.parse_args()
    
    dry_run = not args.force
    
    print("\n" + "="*70)
    print("GLPI Category-Based Group Assignment Rule Creator")
    print("="*70)
    print(f"Mode: {'LIVE' if not dry_run else 'DRY-RUN (simulation only)'}")
    print("="*70 + "\n")
    
    # Load config and initialize session
    config = load_config()
    glpi_url, headers = init_session(config)
    
    try:
        # Fetch data
        categories = fetch_categories(glpi_url, headers)
        # Skip group fetching - use hardcoded GROUP_NAMES instead (API timeout issue)
        existing_rules = fetch_existing_rules(glpi_url, headers)
        
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        print(f"Categories: {len(categories)}")
        print(f"Groups: {len(GROUP_NAMES)} (hardcoded)")
        print(f"Existing Rules: {len(existing_rules)}")
        print(f"Rules to Create/Update: {len(CATEGORY_GROUP_MAP)}")
        print(f"{'='*70}\n")
        
        # Create rules
        success_count = 0
        skip_count = 0
        
        for category_id, group_id in CATEGORY_GROUP_MAP.items():
            category_name = categories.get(category_id, f"Unknown ({category_id})")
            group_name = GROUP_NAMES.get(group_id, f"Unknown ({group_id})")
            
            # Generate rule name with category name (hyphen-only format)
            category_name_clean = clean_category_name(category_name)
            rule_name = f"Auto-Category-{category_name_clean}"
            
            # Create or update rule
            if create_or_update_rule(
                glpi_url,
                headers,
                rule_name,
                category_id,
                category_name,
                group_id,
                group_name,
                existing_rules,
                dry_run
            ):
                success_count += 1
            else:
                skip_count += 1
        
        # Final summary
        print(f"\n{'='*70}")
        print("RESULTS")
        print(f"{'='*70}")
        print(f"Rules created/updated: {success_count}")
        print(f"Rules skipped/failed: {skip_count}")
        
        if dry_run:
            print(f"\n⚠️  DRY-RUN MODE: No changes were made")
            print(f"Run with --force to actually create/update rules")
        
        print(f"{'='*70}\n")
        
    finally:
        kill_session(glpi_url, headers)

if __name__ == "__main__":
    main()
