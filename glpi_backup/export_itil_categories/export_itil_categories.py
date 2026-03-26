import requests
import json
import os
import csv
import sys
import urllib3

# Suppress insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'config.json')
OUTPUT_FILE = 'glpi_itil_categories_v2.csv'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Config file not found at {CONFIG_FILE}")
        sys.exit(1)
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def init_session(url, app_token, user_token):
    headers = {
        "App-Token": app_token,
        "Authorization": f"user_token {user_token}"
    }
    try:
        response = requests.get(f"{url}/initSession", headers=headers, verify=False)
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
    requests.get(f"{url}/killSession", headers=headers, verify=False)

def fetch_all_itil_categories(url, headers):
    print("Fetching ITIL Categories...")
    categories = []
    range_start = 0
    range_step = 1000
    
    while True:
        range_end = range_start + range_step
        params = {
            "range": f"{range_start}-{range_end}",
            "sort": "completename",
            "order": "ASC",
            "expand_dropdowns": "true" # Get readable names
        }
        
        # Endpoint for ITIL Categories (Ticket Categories)
        resp = requests.get(f"{url}/ITILCategory", headers=headers, params=params, verify=False)
        
        if resp.status_code != 200:
            print(f"Error fetching categories: {resp.status_code} - {resp.text}")
            break
            
        data = resp.json()
        if not data:
            break
            
        batch = data if isinstance(data, list) else data.get('data', [])
        if not batch:
            break
            
        categories.extend(batch)
        print(f"Fetched {len(batch)} categories ({len(categories)} total)...")
        
        if len(batch) < range_step:
            break
            
        range_start += range_step
        
    return categories

import html

def export_to_csv(categories, filename):
    if not categories:
        print("No categories found to export.")
        return

    print(f"Exporting {len(categories)} categories to {filename}...")
    
    # Sort by complete name (hierarchy order)
    categories.sort(key=lambda x: x.get('completename', ''))
    
    # Store assigned codes: { 'Complete Name': '01.02' }
    name_to_code = {}
    
    # Store next available index for a parent: { 'Parent Code': 1 }
    # Root is represented by empty string key: { '': 1 }
    counters = { '': 1 }
    
    rows = []
    
    for cat in categories:
        completename = cat.get('completename', '')
        # Unescape HTML entities (e.g., &#38; -> &)
        real_name = html.unescape(cat.get('name'))
        
        parts = completename.split(' > ')
        parent_completename = ' > '.join(parts[:-1]) if len(parts) > 1 else ''
        
        # Determine Parent Code
        if parent_completename:
            # If parent was processed, get its code
            # Note: Because we sorted, parent should be in the map mostly.
            # If GLPI returns orphans or odd order, this might fail, so we fallback.
            parent_code = name_to_code.get(parent_completename, '')
        else:
            parent_code = ''
            
        # Get next index for this parent
        if parent_code not in counters:
            counters[parent_code] = 1
            
        current_index = counters[parent_code]
        counters[parent_code] += 1
        
        # Format: 01 or 01.02
        index_str = f"{current_index:02d}"
        if parent_code:
            current_code = f"{parent_code}.{index_str}"
        else:
            current_code = index_str
            
        # Save mapping
        name_to_code[completename] = current_code
        
        # Prepare "Code - Name" format
        formatted_name = f"{current_code} - {real_name}"
        
        rows.append({'name': formatted_name})

    # Write to CSV with ';' delimiter
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['name']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(rows)
            
    print("Export completed successfully!")

def main():
    config = load_config()
    glpi_url = config['GLPI_URL'].rstrip('/')
    app_token = config['GLPI_APP_TOKEN']
    user_token = config['GLPI_USER_TOKEN']
    
    print(f"Connecting to GLPI: {glpi_url}")
    session_token = init_session(glpi_url, app_token, user_token)
    
    headers = {
        "App-Token": app_token,
        "Session-Token": session_token,
        "Content-Type": "application/json"
    }
    
    try:
        categories = fetch_all_itil_categories(glpi_url, headers)
        export_to_csv(categories, OUTPUT_FILE)
        
        # Print a preview
        print("\n--- Preview (First 10) ---")
        for i, cat in enumerate(categories[:10]):
            print(f"{cat.get('id')}: {cat.get('completename')}")
            
    finally:
        kill_session(glpi_url, app_token, session_token)
        print("\nSession closed.")

if __name__ == "__main__":
    main()
