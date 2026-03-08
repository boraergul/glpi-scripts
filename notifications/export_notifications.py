import requests
import json
import os
import sys
import csv
import urllib3
import time
import logging
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('export_notifications.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CONFIG_FILE = 'config.json'

def load_config():
    """Load configuration from config.json with robust path searching.
    
    Returns:
        dict: Configuration dictionary containing GLPI credentials
    """
    search_paths = [
        os.path.join(os.path.dirname(__file__), CONFIG_FILE),
        os.path.join(os.path.dirname(__file__), '..', CONFIG_FILE),
        os.path.join(os.path.dirname(__file__), '..', 'config', CONFIG_FILE),
        os.path.join(os.path.dirname(__file__), '..', '..', 'Config', CONFIG_FILE),
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info(f"Configuration loaded from: {path}")
                    return config
            except Exception as e:
                logger.error(f"Error reading config file at {path}: {e}")
                
    logger.critical(f"Error: File {CONFIG_FILE} not found in any of the search paths.")
    sys.exit(1)

def init_session(url, app_token, user_token):
    """Initialize GLPI API session.
    
    Args:
        url: GLPI API base URL
        app_token: Application token
        user_token: User authentication token
        
    Returns:
        str: Session token for API requests
    """
    headers = {"App-Token": app_token, "Authorization": f"user_token {user_token}", "Content-Type": "application/json"}
    try:
        logger.info("Initializing GLPI API session...")
        resp = requests.get(f"{url}/initSession", headers=headers, verify=False, timeout=30)
        resp.raise_for_status()
        session_token = resp.json().get('session_token')
        logger.info("Session initialized successfully")
        return session_token
    except Exception as e:
        logger.error(f"Session init failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        sys.exit(1)

def kill_session(url, app_token, session_token):
    """Terminate GLPI API session.
    
    Args:
        url: GLPI API base URL
        app_token: Application token
        session_token: Active session token
    """
    headers = {"App-Token": app_token, "Session-Token": session_token}
    try:
        requests.get(f"{url}/killSession", headers=headers, verify=False, timeout=10)
        logger.info("Session terminated successfully")
    except Exception as e:
        logger.warning(f"Failed to terminate session: {e}")

def fetch_all_pages(url, endpoint, headers, params=None, max_items=None):
    """Fetch all items from a GLPI API endpoint with pagination.
    
    Args:
        url: GLPI API base URL
        endpoint: API endpoint to fetch from
        headers: Request headers including session token
        params: Additional query parameters
        max_items: Maximum number of items to fetch (None for all)
        
    Returns:
        list: All fetched items
    """
    if params is None:
        params = {}
    
    results = []
    range_start = 0
    range_step = 1000
    
    logger.info(f"Fetching {endpoint}...")
    
    while True:
        if max_items and len(results) >= max_items:
            logger.info(f"Reached max items limit ({max_items}) for {endpoint}")
            break
            
        current_params = params.copy()
        current_params["range"] = f"{range_start}-{range_start+range_step}"
        current_params["is_deleted"] = 0
        
        try:
            resp = requests.get(f"{url}/{endpoint}", headers=headers, params=current_params, verify=False, timeout=30)
            if resp.status_code not in [200, 206]:
                logger.warning(f"Failed to fetch {endpoint} range {range_start}: {resp.status_code}")
                break
                
            batch = resp.json()
            if not batch: 
                break
            
            if isinstance(batch, list):
                results.extend(batch)
                logger.debug(f"Fetched {len(batch)} items from {endpoint} (total: {len(results)})")
            else:
                logger.warning(f"Unexpected response format for {endpoint}")
                break

            if len(batch) < range_step: 
                break
            range_start += range_step
            
        except Exception as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            break
    
    logger.info(f"Completed fetching {endpoint}: {len(results)} items")
    return results

def get_entity_name(entity_id, entity_cache, url, headers):
    """Fetch and cache entity name.
    
    Args:
        entity_id: Entity ID to resolve
        entity_cache: Dictionary cache for entity names
        url: GLPI API base URL
        headers: Request headers
        
    Returns:
        str: Entity name or ID if not found
    """
    if entity_id in entity_cache:
        return entity_cache[entity_id]
    
    if entity_id == 0:
        entity_cache[entity_id] = "Root Entity"
        return "Root Entity"
    
    try:
        ent_resp = requests.get(f"{url}/Entity/{entity_id}", headers=headers, verify=False, timeout=10)
        if ent_resp.status_code == 200:
            name = ent_resp.json().get('name', f"ID: {entity_id}")
            entity_cache[entity_id] = name
            return name
    except Exception as e:
        logger.warning(f"Failed to fetch entity {entity_id}: {e}")
    
    entity_cache[entity_id] = f"ID: {entity_id}"
    return f"ID: {entity_id}"

def main():
    config = load_config()
    glpi_url = config.get('GLPI_URL').rstrip('/')
    app_token = config['GLPI_APP_TOKEN']
    user_token = config['GLPI_USER_TOKEN']
    
    session_token = init_session(glpi_url, app_token, user_token)
    headers = {"App-Token": app_token, "Session-Token": session_token, "Content-Type": "application/json"}
    
    try:
        # 1. Fetch Templates (id -> name)
        templates = fetch_all_pages(glpi_url, "NotificationTemplate", headers)
        template_map = {t['id']: t['name'] for t in templates}
        print(f"Loaded {len(template_map)} templates.")

        # 2. Fetch Profiles & Groups for caching recipients
        profiles = fetch_all_pages(glpi_url, "Profile", headers)
        profile_map = {p['id']: p['name'] for p in profiles}
        
        groups = fetch_all_pages(glpi_url, "Group", headers)
        group_map = {g['id']: g['name'] for g in groups}
        
        # User cache (fetch all users for complete coverage)
        logger.info("Fetching all users for recipient resolution...")
        users = fetch_all_pages(glpi_url, "User", headers)
        user_map = {u['id']: u['name'] for u in users}
        logger.info(f"Loaded {len(user_map)} users into cache")
        
        recipient_cache = {
            'Profile': profile_map,
            'Group': group_map,
            'User': user_map
        }

        # 3. Fetch Notifications
        notifications = fetch_all_pages(glpi_url, "Notification", headers)
        print(f"Loaded {len(notifications)} notifications.")
        
        # Entity Cache
        entity_map = {}
        
        csv_file = os.path.join(os.path.dirname(__file__), 'notifications_export_improved.csv')
        
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['Notification ID', 'Notification Name', 'Entity', 'Type', 'Active', 'Event Label', 'Template', 'Recipient Type', 'Recipient Name'])
            
            for notif in notifications:
                notif_id = notif['id']
                notif_name = notif['name']
                is_active = "Yes" if notif['is_active'] == 1 else "No"
                event = notif.get('event', '')
                
                # Entity Resolution
                ent_id = notif.get('entities_id', 0)
                entity_name = get_entity_name(ent_id, entity_map, glpi_url, headers)
                
                # Item Type
                item_type = notif.get('itemtype', '')
                
                # Event mapping
                rawevt = event
                EVENT_LABELS = {
                    'new': 'New item', 'update': 'Update of an item', 'solved': 'Item solved',
                    'add_task': 'New task', 'update_task': 'Update of a task', 'delete_task': 'Deletion of a task',
                    'closed': 'Closing of the item', 'autoclose': 'Automatic closing',
                    'add_followup': 'New followup', 'update_followup': 'Update of a followup', 'delete_followup': 'Deletion of a followup',
                    'validation': 'Validation request', 'validation_answer': 'Validation request answer',
                    'user_mention': 'User mentioned', 'alertnotclosed': 'Not solved tickets',
                    'recall': 'Planning recall', 'satisfaction': 'Satisfaction survey'
                }
                friendly_event = EVENT_LABELS.get(rawevt, rawevt)
                
                # Custom overrides from user data
                if notif_id == 58: friendly_event = "Unlock Item Request"
                elif notif_id == 72: friendly_event = "User mentioned"
                elif notif_id == 29: friendly_event = "New problem"

                # Fetch Linked Templates
                # Notification -> Notification_NotificationTemplate -> Template Name
                tmpl_url = f"{glpi_url}/Notification/{notif_id}/Notification_NotificationTemplate"
                tmpl_resp = requests.get(tmpl_url, headers=headers, params={"range": "0-100"}, verify=False)
                
                template_names = []
                if tmpl_resp.status_code in [200, 206]:
                    linked_templates = tmpl_resp.json()
                    for lt in linked_templates:
                        tid = lt.get('notificationtemplates_id')
                        tmode = lt.get('mode', 'unknown')
                        tname = template_map.get(tid, f"ID: {tid}")
                        template_names.append(f"{tname} ({tmode})")
                
                template_str = ", ".join(template_names) if template_names else "None"
                
                # 4. Fetch Targets for this Notification
                # Range param handles pagination if needed, but usually targets per notification are few
                targets_url = f"{glpi_url}/Notification/{notif_id}/NotificationTarget"
                targets_resp = requests.get(targets_url, headers=headers, params={"range": "0-100"}, verify=False)
                
                if targets_resp.status_code in [200, 206]:
                    targets = targets_resp.json()
                    
                    if not targets:
                        writer.writerow([notif_id, notif_name, entity_name, item_type, is_active, friendly_event, template_str, "None", ""])
                    
                    for target in targets:
                        # Try to find readable type
                        r_type = target.get('itemtype_name')
                        r_id = target.get('items_id', 0)
                        
                        # Fallback for type
                        if not r_type:
                            raw_type = target.get('type')
                            if raw_type == 1: r_type = 'User'
                            elif raw_type == 2: r_type = 'Group'
                            elif raw_type == 3: r_type = 'Profile'
                            else: r_type = f"Type {raw_type}"
                        # Constants Map (GLPI Notification Target Types)
                        # Based on standard GLPI and User feedback
                        # Type 1 (User/Actor) related constants
                        USER_CONSTANTS = {
                            1: "Requester",
                            2: "Former technician in charge of the ticket", # Updated based on screenshot
                            3: "Administrator", 
                            4: "Technician in charge of the ticket", # Updated based on screenshot
                            5: "Group in charge of the ticket",
                            6: "Assignee",
                            7: "Supervisor of the group in charge of the ticket", 
                            11: "Administrator", 
                            14: "Approver",
                            19: "User",
                            21: "Watcher",
                            23: "Technician in charge of the domain", # Added based on user feedback for Domain
                            31: "Project Manager"
                        }
                        
                        r_name = ""
                        is_constant = False
                        
                        # Priority 1: Custom ItemType Overrides
                        if item_type == 'Domain':
                            if r_id == 5:
                                r_name = "Group in charge of the domain"
                                is_constant = True
                            elif r_id == 23:
                                r_name = "Technician in charge of the domain"
                                is_constant = True
                        
                        elif item_type == 'Project':
                            if r_id == 27:
                                r_name = "Manager in charge of the project"
                                is_constant = True
                            elif r_id == 28:
                                r_name = "Technician in charge of the project"
                                is_constant = True
                                
                        elif item_type == 'ProjectTask':
                            if r_id == 32:
                                r_name = "Technician in charge of the project task"
                                is_constant = True
                                
                        # Priority 1.1: Event Specific Overrides
                        # User feedback: 'alertnotclosed' event ID 1 is Administrator, not Requester
                        if not is_constant and rawevt == 'alertnotclosed' and r_id == 1:
                            r_name = "Administrator"
                            is_constant = True
                        
                        # Priority 2: Standard User Constants
                        if not is_constant and r_type == 'User' and r_id in USER_CONSTANTS:
                            r_name = USER_CONSTANTS[r_id]
                            is_constant = True
                            
                        # Priority 3: Check Caches for Specific Objects
                        if not is_constant:
                            if r_type == 'Group' and r_id in recipient_cache['Group']:
                                 r_name = recipient_cache['Group'][r_id]
                            elif r_type == 'Profile' and r_id in recipient_cache['Profile']:
                                 r_name = recipient_cache['Profile'][r_id]
                            elif r_type == 'User' and r_id in recipient_cache['User']:
                                 r_name = recipient_cache['User'][r_id]
                            else:
                                 # Final Fallback
                                 r_name = f"ID: {r_id}"

                        writer.writerow([notif_id, notif_name, entity_name, item_type, is_active, friendly_event, template_str, r_type, r_name])
                        
                else:
                    print(f"Failed to fetch targets for {notif_name}: {targets_resp.status_code}")
                    writer.writerow([notif_id, notif_name, entity_name, item_type, is_active, friendly_event, template_str, "Error Fetching Targets", ""])

        print(f"\nExport complete: {csv_file}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
    finally:
        kill_session(glpi_url, app_token, session_token)

if __name__ == "__main__":
    main()
