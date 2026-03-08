"""
export_notifications.py
-----------------------
GLPI Notification'larini export eder.

CSV Yapisi (noktalı virgülle ayrılmış):
  Her satır bir template bağlantısı veya hedef temsil eder.
  Notification ID | Name | Item Type | Event | Active | Mode | Template Name | Target Type | Target Items_ID | Target Name

Kullanım:
  python export_notifications.py                  # kaynak config.json kullanır
"""

import requests
import json
import os
import sys
import csv
import glob
import urllib3
import logging
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'export_notifications.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CONFIG_FILE = 'config.json'

# ─── Config ───────────────────────────────────────────────────────────────────
def load_config():
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
                    logger.info(f"Config loaded: {norm}")
                    return config
            except Exception as e:
                logger.error(f"Error reading config at {norm}: {e}")
    logger.critical(f"{CONFIG_FILE} not found.")
    sys.exit(1)

# ─── Session ──────────────────────────────────────────────────────────────────
def init_session(url, app_token, user_token):
    # Content-Type intentionally omitted for GET — some GLPI 11 versions return 400 otherwise
    headers = {
        "App-Token": app_token,
        "Authorization": f"user_token {user_token}",
    }
    try:
        resp = requests.get(f"{url}/initSession", headers=headers, verify=False, timeout=30)
        if resp.status_code != 200:
            body = resp.text[:400]
            raise RuntimeError(
                f"initSession döndü HTTP {resp.status_code}\n"
                f"URL : {url}/initSession\n"
                f"Body: {body}\n\n"
                f"Olası nedenler:\n"
                f"  • App-Token veya User-Token yanlış\n"
                f"  • API URL formatı hatalı (ör: /apirest.php yerine /api.php/v1)\n"
                f"  • GLPI API kapalı (Administration > API)"
            )
        session_token = resp.json().get('session_token')
        logger.info("Session initialized.")
        hdrs = {"App-Token": app_token, "Session-Token": session_token}
        requests.post(f"{url}/changeActiveEntities",
                      headers=hdrs,
                      json={"entities_id": 0, "is_recursive": True},
                      verify=False)
        return session_token
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"initSession bağlantı hatası: {e}\nURL: {url}/initSession") from e


def kill_session(url, app_token, session_token):
    try:
        requests.get(f"{url}/killSession",
                     headers={"App-Token": app_token, "Session-Token": session_token},
                     verify=False, timeout=10)
        logger.info("Session terminated.")
    except Exception as e:
        logger.warning(f"Failed to terminate session: {e}")

# ─── API Helpers ──────────────────────────────────────────────────────────────
def fetch_all_pages(url, endpoint, headers, extra_params=None):
    results = []
    range_start = 0
    range_step  = 500
    while True:
        params = {"range": f"{range_start}-{range_start+range_step-1}", "is_deleted": 0}
        if extra_params:
            params.update(extra_params)
        try:
            resp = requests.get(f"{url}/{endpoint}", headers=headers,
                                params=params, verify=False, timeout=30)
            if resp.status_code not in [200, 206]:
                break
            batch = resp.json()
            if not batch or not isinstance(batch, list):
                break
            results.extend(batch)
            if len(batch) < range_step:
                break
            range_start += range_step
        except Exception as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            break
    logger.info(f"  → {len(results)} items fetched from {endpoint}")
    return results


def fetch_sub(url, endpoint, item_id, sub, headers):
    try:
        resp = requests.get(f"{url}/{endpoint}/{item_id}/{sub}",
                            headers=headers,
                            params={"range": "0-500"},
                            verify=False, timeout=15)
        if resp.status_code in [200, 206]:
            data = resp.json()
            return data if isinstance(data, list) else []
    except Exception:
        pass
    return []

# ─── Main ─────────────────────────────────────────────────────────────────────
def export(url, app_token, user_token, output_path=None, server_name=""):
    """
    Export notifications from a GLPI instance to a semicolon-delimited CSV.
    Returns the path to the created CSV file.
    """
    session_token = init_session(url, app_token, user_token)
    headers = {
        "App-Token": app_token,
        "Session-Token": session_token,
        "Content-Type": "application/json"
    }

    try:
        logger.info("=" * 60)
        logger.info("GLPI Notification Exporter")
        logger.info(f"Started : {datetime.now():%Y-%m-%d %H:%M:%S}")
        logger.info(f"Source  : {url}")
        logger.info("=" * 60)

        # ── Fetch reference data ─────────────────────────────────────────────
        logger.info("\nFetching reference data...")
        all_templates = fetch_all_pages(url, "NotificationTemplate", headers)
        tmpl_map = {t['id']: t['name'] for t in all_templates}
        logger.info(f"  Templates: {len(tmpl_map)}")

        all_notifications = fetch_all_pages(url, "Notification", headers)
        logger.info(f"  Notifications: {len(all_notifications)}")

        # ── Build CSV ────────────────────────────────────────────────────────
        if output_path is None:
            timestamp  = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name  = server_name.replace(' ', '_').replace('(', '').replace(')', '') if server_name else 'export'
            output_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                f"notifications_{safe_name}_{timestamp}.csv"
            )

        FIELDNAMES = [
            'Notification ID', 'Name', 'Item Type', 'Event', 'Active',
            'Mode', 'Template ID', 'Template Name',
            'Target Type', 'Target Items_ID',
        ]

        rows_written = 0
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES, delimiter=';',
                                    extrasaction='ignore', quoting=csv.QUOTE_ALL)
            writer.writeheader()

            for notif in all_notifications:
                nid    = notif['id']
                nname  = notif.get('name', '')
                itype  = notif.get('itemtype', '')
                event  = notif.get('event', '')
                active = '1' if notif.get('is_active', 0) == 1 else '0'

                logger.info(f"  Processing '{nname}' (ID: {nid})")

                # Linked templates (via Notification_NotificationTemplate)
                tmpl_links = fetch_sub(url, "Notification", nid,
                                       "Notification_NotificationTemplate", headers)

                # Targets
                targets = fetch_sub(url, "Notification", nid,
                                    "NotificationTarget", headers)

                def base_row():
                    return {
                        'Notification ID': nid,
                        'Name': nname,
                        'Item Type': itype,
                        'Event': event,
                        'Active': active,
                    }

                if not tmpl_links and not targets:
                    writer.writerow(base_row())
                    rows_written += 1
                    continue

                # One row per (template_link × target) combination
                # If no targets: one row per template_link
                if not targets:
                    for tl in tmpl_links:
                        row = base_row()
                        row.update({
                            'Mode': tl.get('mode', ''),
                            'Template ID': tl.get('notificationtemplates_id', ''),
                            'Template Name': tmpl_map.get(tl.get('notificationtemplates_id'), ''),
                        })
                        writer.writerow(row)
                        rows_written += 1
                elif not tmpl_links:
                    for tgt in targets:
                        row = base_row()
                        row.update({
                            'Target Type': tgt.get('type', ''),
                            'Target Items_ID': tgt.get('items_id', ''),
                        })
                        writer.writerow(row)
                        rows_written += 1
                else:
                    # Write one block per template, then targets appended per template's first row
                    # Strategy: one row per tmpl_link (first), targets on separate rows with same notif but blank template cols
                    for tl in tmpl_links:
                        row = base_row()
                        row.update({
                            'Mode': tl.get('mode', ''),
                            'Template ID': tl.get('notificationtemplates_id', ''),
                            'Template Name': tmpl_map.get(tl.get('notificationtemplates_id'), ''),
                        })
                        writer.writerow(row)
                        rows_written += 1
                    for tgt in targets:
                        row = base_row()
                        row.update({
                            'Target Type': tgt.get('type', ''),
                            'Target Items_ID': tgt.get('items_id', ''),
                        })
                        writer.writerow(row)
                        rows_written += 1

        logger.info(f"\nExport complete: {rows_written} rows → {output_path}")
        return output_path

    finally:
        kill_session(url, app_token, session_token)


def main():
    config     = load_config()
    glpi_url   = config.get('GLPI_URL', '').rstrip('/')
    app_token  = config['GLPI_APP_TOKEN']
    user_token = config['GLPI_USER_TOKEN']
    export(glpi_url, app_token, user_token)


if __name__ == "__main__":
    main()
