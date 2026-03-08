import requests
import json
import os
import sys
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Target GLPI Credentials
GLPI_URL = "https://itsmp.ultron.com.tr/api.php/v1"
APP_TOKEN = "INs9pxumMDPZLXSigZVJ4UuRO5cZOHCRHjhS2OoL"
USER_TOKEN = "g6e4U76CyB4VlKpK41kKvcySbqiVF97t2fXWJFFm"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTIFICATIONS_MD = os.path.join(BASE_DIR, '..', 'templates_new', 'glpi_notifications.md')

def init_session(url, app_token, user_token):
    headers = {"App-Token": app_token, "Authorization": f"user_token {user_token}", "Content-Type": "application/json"}
    try:
        resp = requests.get(f"{url}/initSession", headers=headers, verify=False, timeout=30)
        return resp.json().get('session_token')
    except Exception as e:
        print(f"Session Init Failed: {e}")
        sys.exit(1)

def get_all_items(url, headers, endpoint):
    items = {}
    range_start = 0
    range_step = 100
    while True:
        params = {"range": f"{range_start}-{range_start + range_step}"}
        r = requests.get(f"{url}/{endpoint}", headers=headers, verify=False, params=params)
        if r.status_code in [200, 206]:
            data = r.json()
            if not isinstance(data, list) or len(data) == 0: break
            for item in data: items[item['id']] = item
            if len(data) < range_step: break
            range_start += range_step
        else: break
    return items

def parse_markdown_mapping():
    mapping = {} # Name -> ID
    if not os.path.exists(NOTIFICATIONS_MD): return None
    with open(NOTIFICATIONS_MD, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip().startswith('|') or '---' in line or 'Recommended Template' in line: continue
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 3: continue
            name_col = parts[1]
            match = re.search(r'^(.*)\((\d+)\)$', name_col)
            if match:
                clean_name = match.group(1).strip()
                match_id = int(match.group(2))
                mapping[clean_name] = match_id
    return mapping

def main():
    print(f"--- GLPI Notification Comparison ---")
    session = init_session(GLPI_URL, APP_TOKEN, USER_TOKEN)
    headers = {"App-Token": APP_TOKEN, "Session-Token": session, "Content-Type": "application/json"}
    
    # 1. Get Live Notifications
    print("Fetching live notifications...")
    live_notifications = get_all_items(GLPI_URL, headers, "Notification")
    live_name_to_id = {v['name']: v['id'] for v in live_notifications.values()}
    
    # 2. Parse MD
    print("Parsing glpi_notifications.md...")
    md_mapping = parse_markdown_mapping()
    
    if md_mapping is None:
        print("MD file not found.")
        return

    # 3. Compare
    print("\n=== Comparison Results ===\n")
    print("| Notification Name | MD ID | Live ID | Status |")
    print("|---|---|---|---|")
    
    mismatches = 0
    not_found = 0
    
    for name, md_id in md_mapping.items():
        live_id = live_name_to_id.get(name)
        
        if live_id is None:
            status = "❌ NOT FOUND"
            not_found += 1
        elif live_id != md_id:
            status = f"⚠️ MISMATCH (Update to {live_id})"
            mismatches += 1
        else:
            status = "✅ OK"
            
        print(f"| {name} | {md_id} | {live_id if live_id else 'N/A'} | {status} |")

    print(f"\nSummary: {mismatches} mismatches, {not_found} not found in live instance.")

if __name__ == "__main__":
    main()
