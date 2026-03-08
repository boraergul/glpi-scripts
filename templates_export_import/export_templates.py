import requests
import json
import os
import sys
import csv
import urllib3
import logging
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'export_templates.log'),
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CONFIG_FILE = 'config.json'

# ─── Config ───────────────────────────────────────────────────────────────────
def load_config():
    """Load configuration from config.json with robust path searching."""
    search_paths = [
        os.path.join(os.path.dirname(__file__), CONFIG_FILE),
        os.path.join(os.path.dirname(__file__), '..', CONFIG_FILE),
        os.path.join(os.path.dirname(__file__), '..', 'config', CONFIG_FILE),
        os.path.join(os.path.dirname(__file__), '..', '..', 'Config', CONFIG_FILE),
    ]
    for path in search_paths:
        norm = os.path.normpath(path)
        if os.path.exists(norm):
            try:
                with open(norm, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info(f"Configuration loaded from: {norm}")
                    return config
            except Exception as e:
                logger.error(f"Error reading config file at {norm}: {e}")
    logger.critical(f"{CONFIG_FILE} not found in any searched path. Aborting.")
    sys.exit(1)

# ─── Session ──────────────────────────────────────────────────────────────────
def init_session(url, app_token, user_token):
    """Initialize GLPI API session and switch to Root Entity (recursive)."""
    headers = {
        "App-Token": app_token,
        "Authorization": f"user_token {user_token}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.get(f"{url}/initSession", headers=headers, verify=False, timeout=30)
        resp.raise_for_status()
        session_token = resp.json().get('session_token')
        logger.info("Session initialized successfully.")

        # Switch to Root Entity with recursion to access all child entities
        hdrs_s = {"App-Token": app_token, "Session-Token": session_token, "Content-Type": "application/json"}
        requests.post(
            f"{url}/changeActiveEntities",
            headers=hdrs_s,
            json={"entities_id": 0, "is_recursive": True},
            verify=False
        )
        logger.info("Switched to Root Entity (recursive).")
        return session_token
    except Exception as e:
        logger.error(f"Session init failed: {e}")
        sys.exit(1)


def kill_session(url, app_token, session_token):
    """Terminate GLPI API session."""
    headers = {"App-Token": app_token, "Session-Token": session_token}
    try:
        requests.get(f"{url}/killSession", headers=headers, verify=False, timeout=10)
        logger.info("Session terminated.")
    except Exception as e:
        logger.warning(f"Failed to terminate session: {e}")

# ─── Fetch helpers ────────────────────────────────────────────────────────────
def fetch_all_pages(url, endpoint, headers, params=None):
    """Fetch all items from a GLPI API endpoint using pagination."""
    if params is None:
        params = {}
    results = []
    range_start = 0
    range_step = 500

    logger.info(f"Fetching /{endpoint} ...")
    while True:
        current_params = params.copy()
        current_params["range"] = f"{range_start}-{range_start + range_step - 1}"
        current_params["is_deleted"] = 0

        try:
            resp = requests.get(
                f"{url}/{endpoint}", headers=headers,
                params=current_params, verify=False, timeout=30
            )
            if resp.status_code not in [200, 206]:
                logger.warning(f"  /{endpoint}: HTTP {resp.status_code} at range {range_start}")
                break

            batch = resp.json()
            if not batch:
                break
            if isinstance(batch, list):
                results.extend(batch)
                logger.debug(f"  /{endpoint}: +{len(batch)} items (total {len(results)})")
            else:
                logger.warning(f"  /{endpoint}: unexpected response type, stopping.")
                break

            if len(batch) < range_step:
                break
            range_start += range_step

        except Exception as e:
            logger.error(f"  /{endpoint} error: {e}")
            break

    logger.info(f"  /{endpoint}: fetched {len(results)} items total.")
    return results


def fetch_sub_resource(url, parent_endpoint, parent_id, sub_endpoint, headers):
    """Fetch sub-resources for a given parent item (no pagination needed usually)."""
    full_url = f"{url}/{parent_endpoint}/{parent_id}/{sub_endpoint}"
    try:
        resp = requests.get(full_url, headers=headers, params={"range": "0-200"}, verify=False, timeout=15)
        if resp.status_code in [200, 206]:
            data = resp.json()
            if isinstance(data, list):
                return data
        elif resp.status_code == 404:
            return []
        else:
            logger.debug(f"  Sub-resource {full_url}: HTTP {resp.status_code}")
    except Exception as e:
        logger.warning(f"  Sub-resource {full_url} error: {e}")
    return []

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    logger.info("=" * 60)
    logger.info("GLPI Notification Template Exporter")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    config = load_config()
    glpi_url = config.get('GLPI_URL', '').rstrip('/')
    app_token = config['GLPI_APP_TOKEN']
    user_token = config['GLPI_USER_TOKEN']

    session_token = init_session(glpi_url, app_token, user_token)
    headers = {
        "App-Token": app_token,
        "Session-Token": session_token,
        "Content-Type": "application/json"
    }

    output_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = os.path.join(output_dir, f"templates_export_{timestamp}.csv")

    try:
        # ── 1. Fetch all Notifications (for the "linked notifications" column) ──
        logger.info("Step 1: Fetching all Notifications...")
        all_notifications = fetch_all_pages(glpi_url, "Notification", headers)
        logger.info(f"  Found {len(all_notifications)} notifications.")

        # Build a reverse map: template_id -> list of notification names
        # We'll need to query Notification_NotificationTemplate or use the
        # direct approach below after we have template IDs.
        # For efficiency we also build a notif id->name map.
        notif_id_to_name = {n['id']: n['name'] for n in all_notifications}

        # ── 2. Fetch all NotificationTemplates ──────────────────────────────────
        logger.info("Step 2: Fetching all NotificationTemplates...")
        all_templates = fetch_all_pages(glpi_url, "NotificationTemplate", headers)
        logger.info(f"  Found {len(all_templates)} templates.")

        # ── 3. For each template, fetch Translations and linked Notifications ───
        # Build template_id -> list of notif names using Notification_NotificationTemplate
        logger.info("Step 3: Fetching Notification<->Template links...")
        all_links = fetch_all_pages(glpi_url, "Notification_NotificationTemplate", headers)
        logger.info(f"  Found {len(all_links)} notification-template links.")

        # Build map: template_id -> [(notif_name, mode), ...]
        tmpl_to_notifs = {}
        for link in all_links:
            tid = link.get('notificationtemplates_id')
            nid = link.get('notifications_id')
            mode = link.get('mode', '')
            if tid is None:
                continue
            n_name = notif_id_to_name.get(nid, f"ID:{nid}")
            tmpl_to_notifs.setdefault(tid, []).append(f"{n_name} [{mode}]")

        # ── 4. Write CSV ─────────────────────────────────────────────────────────
        logger.info(f"Step 4: Writing CSV to {csv_file} ...")

        # CSV columns (semicolon separated)
        fieldnames = [
            'Template ID',
            'Name',
            'Item Type',
            'Comments',
            'CSS',
            'Date Modified',
            'Date Creation',
            'Translation Language',
            'Translation Subject',
            'Translation Content HTML',
            'Translation Content Text',
            'Linked Notifications',
        ]

        rows_written = 0

        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';',
                                    extrasaction='ignore', quoting=csv.QUOTE_ALL)
            writer.writeheader()

            for tmpl in all_templates:
                tmpl_id   = tmpl.get('id', '')
                tmpl_name = tmpl.get('name', '')
                itemtype  = tmpl.get('itemtype', '')
                comments  = tmpl.get('comment', '')
                css       = tmpl.get('css', '')
                date_mod  = tmpl.get('date_mod', '')
                date_crea = tmpl.get('date_creation', '')

                # Linked notifications (all modes)
                linked = tmpl_to_notifs.get(tmpl_id, [])
                linked_str = ' | '.join(linked) if linked else ''

                # Fetch translations for this template
                logger.info(f"  Fetching translations for template '{tmpl_name}' (ID: {tmpl_id})...")
                translations = fetch_sub_resource(
                    glpi_url, "NotificationTemplate", tmpl_id,
                    "NotificationTemplateTranslation", headers
                )

                if not translations:
                    # Write a single row with no translation data
                    row = {
                        'Template ID': tmpl_id,
                        'Name': tmpl_name,
                        'Item Type': itemtype,
                        'Comments': comments,
                        'CSS': css,
                        'Date Modified': date_mod,
                        'Date Creation': date_crea,
                        'Translation Language': '',
                        'Translation Subject': '',
                        'Translation Content HTML': '',
                        'Translation Content Text': '',
                        'Linked Notifications': linked_str,
                    }
                    writer.writerow(row)
                    rows_written += 1
                else:
                    # One row per translation language
                    for trans in translations:
                        lang         = trans.get('language', '')
                        subject      = trans.get('subject', '')
                        content_html = trans.get('content_html', '')
                        content_text = trans.get('content_text', '')

                        row = {
                            'Template ID': tmpl_id,
                            'Name': tmpl_name,
                            'Item Type': itemtype,
                            'Comments': comments,
                            'CSS': css,
                            'Date Modified': date_mod,
                            'Date Creation': date_crea,
                            'Translation Language': lang,
                            'Translation Subject': subject,
                            'Translation Content HTML': content_html,
                            'Translation Content Text': content_text,
                            'Linked Notifications': linked_str,
                        }
                        writer.writerow(row)
                        rows_written += 1

        logger.info(f"\n{'=' * 60}")
        logger.info(f"Export complete!")
        logger.info(f"  Templates exported : {len(all_templates)}")
        logger.info(f"  Rows written       : {rows_written}")
        logger.info(f"  Output file        : {csv_file}")
        logger.info(f"{'=' * 60}")
        print(f"\n[OK] Export complete -> {csv_file}  ({rows_written} rows)")

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())

    finally:
        kill_session(glpi_url, app_token, session_token)


if __name__ == "__main__":
    main()
