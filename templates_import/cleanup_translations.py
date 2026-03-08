import requests
import json
import os
import sys
import urllib3
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = 'config.json'

def load_config():
    search_paths = [
        os.path.join(BASE_DIR, CONFIG_FILE),
        os.path.join(BASE_DIR, '..', 'Config', CONFIG_FILE),
        'config.json'
    ]
    for path in search_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    print("Config not found")
    sys.exit(1)

def init_session(url, app_token, user_token):
    headers = {"App-Token": app_token, "Authorization": f"user_token {user_token}", "Content-Type": "application/json"}
    resp = requests.get(f"{url}/initSession", headers=headers, verify=False)
    session_token = resp.json().get('session_token')
    
    # Switch to Root
    headers_with_session = {"App-Token": app_token, "Session-Token": session_token, "Content-Type": "application/json"}
    requests.post(f"{url}/changeActiveEntities", 
                 headers=headers_with_session, 
                 json={"entities_id": 0, "is_recursive": True}, 
                 verify=False)
    return session_token

def kill_session(url, app_token, session_token):
    headers = {"App-Token": app_token, "Session-Token": session_token}
    requests.get(f"{url}/killSession", headers=headers, verify=False)

def main():
    config = load_config()
    glpi_url = config.get('GLPI_URL').rstrip('/')
    tokens = (config['GLPI_APP_TOKEN'], config['GLPI_USER_TOKEN'])
    session = init_session(glpi_url, *tokens)
    headers = {"App-Token": tokens[0], "Session-Token": session, "Content-Type": "application/json"}
    
    # Argument Parsing
    parser = argparse.ArgumentParser(description='GLPI Cleanup Duplicate Translations')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Perform a dry run without making changes')
    args = parser.parse_args()
    DRY_RUN = args.dry_run

    if DRY_RUN:
        print("!!! DRY RUN MODE ACTIVE - No changes will be made !!!\n")

    try:
        print("=== Cleaning Up Duplicate Translations ===")
        
        # Iterate our templates (205-247)
        # You can adjust range or fetch all
        for template_id in range(205, 248):
            r = requests.get(f"{glpi_url}/NotificationTemplate/{template_id}/NotificationTemplateTranslation", 
                            headers=headers, verify=False, params={"range": "0-100"})
            
            if r.status_code != 200:
                continue
                
            translations = r.json()
            if not isinstance(translations, list):
                continue
                
            # Group by language
            by_lang = {}
            for t in translations:
                lang = t.get('language')
                if lang not in by_lang:
                    by_lang[lang] = []
                by_lang[lang].append(t)
            
            # Check duplicates
            for lang, items in by_lang.items():
                if len(items) > 1:
                    print(f"Template {template_id} - {lang}: Found {len(items)} translations.")
                    
                    # Sort by ID (keep highest/latest)
                    items.sort(key=lambda x: x.get('id'), reverse=True)
                    keep = items[0]
                    remove = items[1:]
                    
                    print(f"  Keeping ID {keep.get('id')}. Removing {len(remove)} duplicates...")
                    
                    for item in remove:
                        del_id = item.get('id')
                        if DRY_RUN:
                            print(f"    [DRY RUN] Would delete ID {del_id}")
                            continue

                        print(f"    Deleting ID {del_id}...", end=" ")
                        d = requests.delete(f"{glpi_url}/NotificationTemplateTranslation/{del_id}", headers=headers, verify=False)
                        if d.status_code == 200:
                            print("OK")
                        else:
                            print(f"Failed ({d.status_code})")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        kill_session(glpi_url, tokens[0], session)

if __name__ == "__main__":
    main()
