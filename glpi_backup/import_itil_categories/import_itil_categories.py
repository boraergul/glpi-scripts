#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import json
import requests
import re
import os
import sys
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

try:
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
        GLPI_URL = config.get('GLPI_URL')
        # Remove trailing slash for this script
        if GLPI_URL.endswith('/'):
            GLPI_URL = GLPI_URL[:-1]
        APP_TOKEN = config.get('GLPI_APP_TOKEN')
        USER_TOKEN = config.get('GLPI_USER_TOKEN')
except Exception as e:
    print(f"Error loading config.json: {e}")
    sys.exit(1)

CSV_FILE = os.path.join(os.path.dirname(__file__), 'itil_categories.csv')

def init_session():
    url = f"{GLPI_URL}/initSession"
    headers = {
        "App-Token": APP_TOKEN,
        "Authorization": f"user_token {USER_TOKEN}"
    }
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json().get('session_token')
    except Exception as e:
        print(f"Session initialization failed: {e}")
        sys.exit(1)

def kill_session(session_token):
    url = f"{GLPI_URL}/killSession"
    headers = {
        "App-Token": APP_TOKEN,
        "Session-Token": session_token
    }
    try:
        requests.get(url, headers=headers, verify=False)
    except:
        pass

def main():
    print("--- GLPI ITIL Category Import (Python) ---")
    
    session_token = init_session()
    print(f"Session Token: {session_token}")
    
    headers = {
        "App-Token": APP_TOKEN,
        "Session-Token": session_token,
        "Content-Type": "application/json"
    }
    
    if not os.path.exists(CSV_FILE):
        print(f"Error: CSV file not found at {CSV_FILE}")
        kill_session(session_token)
        sys.exit(1)
        
    category_cache = {} # Key: Code (e.g., "01.01"), Value: GLPI_ID
    
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        rows = list(reader)
        print(f"Found {len(rows)} categories to process.")
        
        for row in rows:
            full_name = row['name']
            
            # Regex to parse "01.01 - Firewall" -> Code: "01.01", Name: "Firewall"
            match = re.match(r"^([\d\.]+)\s-\s(.+)", full_name)
            if match:
                code = match.group(1)
                real_name = match.group(2)
                
                # Determine Parent
                parent_id = 0
                if "." in code:
                    # 01.01 -> Parent is 01
                    parent_code = code.rsplit('.', 1)[0]
                    if parent_code in category_cache:
                        parent_id = category_cache[parent_code]
                    else:
                        print(f"Warning: Parent code '{parent_code}' not found for '{real_name}'. Creating as root.")
                
                # Create Payload
                payload = {
                    "input": {
                        "name": real_name,
                        "code": code,           # Adding Code
                        "entities_id": 0,       # Root entity
                        "is_recursive": 1,      # Visible in sub-entities
                        "itilcategories_id": parent_id,
                        "is_helpdeskvisible": 1,
                        "is_incident": 1,
                        "is_request": 1
                    }
                }
                
                try:
                    res = requests.post(f"{GLPI_URL}/ITILCategory", headers=headers, json=payload, verify=False)
                    res.raise_for_status()
                    new_id = res.json().get('id')
                    category_cache[code] = new_id
                    print(f"CREATED: [{new_id}] {real_name} (Parent: {parent_id})")
                except Exception as e:
                    print(f"FAILED to create '{full_name}': {e}")
                    if hasattr(e, 'response') and e.response is not None:
                        print(f"Response Body: {e.response.text}")
                    # If we fail, we continue, but children will fail to find parent.
            else:
                print(f"Skipping invalid format: {full_name}")

    kill_session(session_token)
    print("--- Import Complete ---")

if __name__ == "__main__":
    main()
