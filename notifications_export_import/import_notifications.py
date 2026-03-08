"""
import_notifications.py
-----------------------
export_notifications.py ile dışa aktarılan CSV'deki
GLPI Notification'larını hedef GLPI sistemine aktarır.

Davranış:
  - Notification ismine göre eşleştirme yapar; varsa günceller, yoksa oluşturur.
  - Her notification için bağlı template linkleri (mode+template) upsert eder.
  - Her notification için hedef (NotificationTarget) kayıtları upsert eder.

Kullanım:
  python import_notifications.py              # En yeni CSV otomatik seçilir
  python import_notifications.py dosya.csv   # Belirli CSV
  python import_notifications.py --dry-run   # Gerçek değişiklik yapmaz
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
from collections import defaultdict

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'import_notifications.log')
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
def load_source_config():
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
                    return json.load(f), norm
            except Exception:
                pass
    return None, None

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
        logger.warning(f"Kill session failed: {e}")

# ─── API Helpers ──────────────────────────────────────────────────────────────
def api_get(url, endpoint, headers, params=None):
    try:
        resp = requests.get(f"{url}/{endpoint}", headers=headers,
                            params=params, verify=False, timeout=15)
        return resp
    except Exception as e:
        logger.error(f"GET /{endpoint}: {e}")
        return None


def api_post(url, endpoint, headers, payload, dry_run=False):
    if dry_run:
        logger.info(f"  [DRY-RUN] POST /{endpoint}")
        return True, {"id": -1}
    try:
        resp = requests.post(f"{url}/{endpoint}", headers=headers,
                             json=payload, verify=False, timeout=30)
        if resp.status_code == 201:
            return True, resp.json()
        logger.warning(f"  POST /{endpoint} → HTTP {resp.status_code}: {resp.text[:200]}")
        return False, None
    except Exception as e:
        logger.error(f"  POST /{endpoint}: {e}")
        return False, None


def api_put(url, endpoint, item_id, headers, payload, dry_run=False):
    if dry_run:
        logger.info(f"  [DRY-RUN] PUT /{endpoint}/{item_id}")
        return True
    try:
        resp = requests.put(f"{url}/{endpoint}/{item_id}", headers=headers,
                            json=payload, verify=False, timeout=30)
        if resp.status_code in [200, 201]:
            return True
        logger.warning(f"  PUT /{endpoint}/{item_id} → HTTP {resp.status_code}: {resp.text[:200]}")
        return False
    except Exception as e:
        logger.error(f"  PUT /{endpoint}/{item_id}: {e}")
        return False


def api_delete(url, endpoint, item_id, headers, dry_run=False):
    if dry_run:
        logger.info(f"  [DRY-RUN] DELETE /{endpoint}/{item_id}")
        return True
    try:
        resp = requests.delete(f"{url}/{endpoint}/{item_id}",
                               headers=headers, verify=False, timeout=15)
        return resp.status_code in [200, 204]
    except Exception as e:
        logger.error(f"  DELETE /{endpoint}/{item_id}: {e}")
        return False

# ─── CSV Parsing ──────────────────────────────────────────────────────────────
def find_latest_csv(directory):
    files = glob.glob(os.path.join(directory, 'notifications_*.csv'))
    return max(files, key=os.path.getmtime) if files else None


def parse_csv(csv_path):
    """
    Parse the CSV and return:
    {
      notif_name: {
        'itemtype': str,
        'event': str,
        'active': str ('1'/'0'),
        'templates': [ {'mode': str, 'template_name': str}, ... ],
        'targets': [ {'type': str, 'items_id': str}, ... ],
      }
    }
    """
    notifications = {}

    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            name   = row.get('Name', '').strip()
            if not name:
                continue

            if name not in notifications:
                notifications[name] = {
                    'itemtype': row.get('Item Type', '').strip(),
                    'event':    row.get('Event', '').strip(),
                    'active':   row.get('Active', '1').strip(),
                    'templates': [],
                    'targets': [],
                }

            mode     = row.get('Mode', '').strip()
            tmpl_id  = row.get('Template ID', '').strip()
            tmpl_name = row.get('Template Name', '').strip()
            tgt_type  = row.get('Target Type', '').strip()
            tgt_id    = row.get('Target Items_ID', '').strip()

            # Template link row
            if mode and tmpl_name:
                entry = {'mode': mode, 'template_name': tmpl_name, 'template_id_hint': tmpl_id}
                if entry not in notifications[name]['templates']:
                    notifications[name]['templates'].append(entry)

            # Target row
            if tgt_type and tgt_id:
                entry = {'type': tgt_type, 'items_id': tgt_id}
                if entry not in notifications[name]['targets']:
                    notifications[name]['targets'].append(entry)

    logger.info(f"Parsed {len(notifications)} unique notifications from CSV.")
    return notifications

# ─── Fetch Existing ───────────────────────────────────────────────────────────
def fetch_existing_notifications(url, headers):
    """Returns {name: id}"""
    existing = {}
    range_start = 0
    while True:
        resp = api_get(url, "Notification", headers,
                       params={"range": f"{range_start}-{range_start+499}", "is_deleted": 0})
        if not resp or resp.status_code not in [200, 206]:
            break
        batch = resp.json()
        if not batch or not isinstance(batch, list):
            break
        for n in batch:
            if isinstance(n, dict) and n.get('name'):
                existing[n['name']] = n['id']
        if len(batch) < 500:
            break
        range_start += 500
    logger.info(f"Existing notifications on target: {len(existing)}")
    return existing


def fetch_template_map(url, headers):
    """Returns {name: id} for all templates on target."""
    tmpl_map = {}
    range_start = 0
    while True:
        resp = api_get(url, "NotificationTemplate", headers,
                       params={"range": f"{range_start}-{range_start+499}", "is_deleted": 0})
        if not resp or resp.status_code not in [200, 206]:
            break
        batch = resp.json()
        if not batch or not isinstance(batch, list):
            break
        for t in batch:
            if isinstance(t, dict) and t.get('name'):
                tmpl_map[t['name']] = t['id']
        if len(batch) < 500:
            break
        range_start += 500
    logger.info(f"Templates on target: {len(tmpl_map)}")
    return tmpl_map

# ─── Notification Upsert ──────────────────────────────────────────────────────
def upsert_notification(url, headers, name, data, existing_map, dry_run):
    """Create or update a Notification. Returns (notif_id, action)."""
    existing_id = existing_map.get(name)

    payload = {
        "name":      name,
        "itemtype":  data['itemtype'],
        "event":     data['event'],
        "is_active": int(data['active']),
        "entities_id": 0,
        "is_recursive": 1,
    }

    if existing_id:
        ok = api_put(url, "Notification", existing_id, headers, {"input": payload}, dry_run)
        action = 'updated' if ok else 'update_failed'
        logger.info(f"  [{action.upper()}] '{name}' (ID: {existing_id})")
        return existing_id, action
    else:
        ok, result = api_post(url, "Notification", headers, {"input": payload}, dry_run)
        if dry_run:
            logger.info(f"  [DRY-RUN CREATE] '{name}'")
            return -1, 'dry_run_create'
        if ok and result:
            new_id = result.get('id') if isinstance(result, dict) else None
            if new_id:
                existing_map[name] = new_id
                logger.info(f"  [CREATED] '{name}' → ID: {new_id}")
                return new_id, 'created'
        logger.error(f"  [FAILED] Create '{name}'")
        return None, 'create_failed'

# ─── Template Links ───────────────────────────────────────────────────────────
def sync_template_links(url, headers, notif_id, wanted_templates, tmpl_name_to_id, dry_run):
    """
    Ensure the notification has exactly the template links specified in the CSV.
    Returns (created, skipped, failed) counts.
    """
    # Fetch existing links
    resp = api_get(url, f"Notification/{notif_id}/Notification_NotificationTemplate",
                   headers, params={"range": "0-200"})
    existing_links = []
    if resp and resp.status_code in [200, 206]:
        existing_links = resp.json() if isinstance(resp.json(), list) else []

    # Build a set of existing (template_id, mode) pairs
    existing_set = {(lnk.get('notificationtemplates_id'), lnk.get('mode')): lnk.get('id')
                    for lnk in existing_links}

    created = skipped = failed = 0

    for tl in wanted_templates:
        mode      = tl['mode']
        tmpl_name = tl['template_name']
        tmpl_id   = tmpl_name_to_id.get(tmpl_name)

        if tmpl_id is None:
            logger.warning(f"    Template '{tmpl_name}' not found on target — skipping link")
            skipped += 1
            continue

        key = (tmpl_id, mode)
        if key in existing_set:
            logger.info(f"    [EXISTS] Template link: {tmpl_name} [{mode}]")
            skipped += 1
        else:
            ok, _ = api_post(url, "Notification_NotificationTemplate", headers, {
                "input": {
                    "notifications_id": notif_id,
                    "notificationtemplates_id": tmpl_id,
                    "mode": mode,
                }
            }, dry_run)
            if ok:
                logger.info(f"    [LINK CREATED] {tmpl_name} [{mode}]")
                created += 1
            else:
                logger.warning(f"    [LINK FAILED] {tmpl_name} [{mode}]")
                failed += 1

    return created, skipped, failed

# ─── Targets ──────────────────────────────────────────────────────────────────
def sync_targets(url, headers, notif_id, wanted_targets, dry_run):
    """
    Ensure the notification has exactly the targets specified in the CSV.
    Returns (created, skipped, failed) counts.
    """
    resp = api_get(url, f"Notification/{notif_id}/NotificationTarget",
                   headers, params={"range": "0-200"})
    existing_targets = []
    if resp and resp.status_code in [200, 206]:
        existing_targets = resp.json() if isinstance(resp.json(), list) else []

    existing_set = {(str(t.get('type', '')), str(t.get('items_id', ''))): t.get('id')
                    for t in existing_targets}

    created = skipped = failed = 0

    for tgt in wanted_targets:
        ttype  = str(tgt['type'])
        titems = str(tgt['items_id'])
        key = (ttype, titems)

        if key in existing_set:
            logger.info(f"    [EXISTS] Target type={ttype} items_id={titems}")
            skipped += 1
        else:
            ok, _ = api_post(url, "NotificationTarget", headers, {
                "input": {
                    "notifications_id": notif_id,
                    "type":     int(ttype) if ttype.isdigit() else ttype,
                    "items_id": int(titems) if titems.isdigit() else 0,
                }
            }, dry_run)
            if ok:
                logger.info(f"    [TARGET CREATED] type={ttype} items_id={titems}")
                created += 1
            else:
                logger.warning(f"    [TARGET FAILED] type={ttype} items_id={titems}")
                failed += 1

    return created, skipped, failed

# ─── Connection Test (for GUI) ────────────────────────────────────────────────
def test_connection(url, app_token, user_token):
    """Returns (ok, session_token, version)"""
    # No Content-Type on GET—avoids 400 on some GLPI 11 builds
    headers = {
        "App-Token": app_token,
        "Authorization": f"user_token {user_token}",
    }
    try:
        resp = requests.get(f"{url}/initSession", headers=headers, verify=False, timeout=15)
        if resp.status_code == 200:
            session_token = resp.json().get('session_token')
            hdrs = {"App-Token": app_token, "Session-Token": session_token}
            ver_resp = requests.get(f"{url}/getGlpiConfig", headers=hdrs, verify=False, timeout=10)
            version = ''
            if ver_resp.status_code == 200:
                version = ver_resp.json().get('cfg_glpi', {}).get('version', '')
            requests.get(f"{url}/killSession", headers=hdrs, verify=False, timeout=5)
            return True, session_token, version
        return False, None, ''
    except Exception:
        return False, None, ''

# ─── Main ─────────────────────────────────────────────────────────────────────
def run_import(url, app_token, user_token, csv_path, dry_run=False, log_callback=None):
    """
    Core import logic. Can be called from GUI (with log_callback) or CLI.
    log_callback(msg, tag): called for each log line; tag in INFO/OK/WARNING/ERROR/DRY
    Returns stats dict.
    """
    def qlog(msg, tag="INFO"):
        logger.info(msg)
        if log_callback:
            log_callback(msg, tag)

    stats = defaultdict(int)

    qlog("=" * 56, "HEAD")
    qlog(f"  GLPI Notification Importer {'[DRY-RUN]' if dry_run else ''}", "HEAD")
    qlog(f"  CSV   : {os.path.basename(csv_path)}", "HEAD")
    qlog(f"  Target: {url}", "HEAD")
    qlog("=" * 56, "HEAD")

    # Parse
    qlog("\nCSV ayrıştırılıyor...")
    notifications = parse_csv(csv_path)
    qlog(f"  → {len(notifications)} notification", "OK")

    # Session
    session_token = init_session(url, app_token, user_token)
    headers = {
        "App-Token": app_token,
        "Session-Token": session_token,
        "Content-Type": "application/json"
    }

    try:
        # Fetch existing
        qlog("\nMevcut notification'lar kontrol ediliyor...")
        existing_map = fetch_existing_notifications(url, headers)
        qlog(f"  → {len(existing_map)} mevcut notification", "OK")

        qlog("Template haritası alınıyor...")
        tmpl_map = fetch_template_map(url, headers)
        qlog(f"  → {len(tmpl_map)} template", "OK")

        total = len(notifications)
        qlog(f"\nImport başlıyor — {total} notification...\n")

        for idx, (name, data) in enumerate(notifications.items(), 1):
            qlog(f"[{idx}/{total}] {name}")

            notif_id, action = upsert_notification(
                url, headers, name, data, existing_map, dry_run
            )
            stats[f'notif_{action}'] += 1

            if notif_id is None:
                qlog(f"  ✗ Notification oluşturulamadı, atlanıyor.", "ERROR")
                stats['skipped'] += 1
                continue

            if notif_id == -1:
                # dry-run create
                for tl in data['templates']:
                    qlog(f"  [DRY] Template link: {tl['template_name']} [{tl['mode']}]", "DRY")
                for tgt in data['targets']:
                    qlog(f"  [DRY] Target: type={tgt['type']} id={tgt['items_id']}", "DRY")
                continue

            tag = "OK" if action in ('created', 'updated') else "WARNING"
            qlog(f"  {'✓' if tag=='OK' else '⚠'} {action} (ID: {notif_id})", tag)

            # Template links
            if data['templates']:
                c, s, f = sync_template_links(url, headers, notif_id,
                                              data['templates'], tmpl_map, dry_run)
                stats['tmpl_link_created'] += c
                stats['tmpl_link_skipped'] += s
                stats['tmpl_link_failed']  += f

            # Targets
            if data['targets']:
                c, s, f = sync_targets(url, headers, notif_id, data['targets'], dry_run)
                stats['target_created'] += c
                stats['target_skipped'] += s
                stats['target_failed']  += f

        # Summary
        qlog("\n" + "=" * 56, "HEAD")
        qlog("  ÖZET", "HEAD")
        qlog("=" * 56, "HEAD")
        qlog(f"  Notification oluşturuldu : {stats.get('notif_created', 0)}", "OK")
        qlog(f"  Notification güncellendi : {stats.get('notif_updated', 0)}", "OK")
        qlog(f"  Template link eklendi    : {stats.get('tmpl_link_created', 0)}", "OK")
        qlog(f"  Hedef eklendi            : {stats.get('target_created', 0)}", "OK")
        failed = (stats.get('notif_create_failed', 0) +
                  stats.get('tmpl_link_failed', 0) +
                  stats.get('target_failed', 0))
        qlog(f"  Hata                     : {failed}", "ERROR" if failed else "INFO")
        if dry_run:
            qlog("\n  ** DRY-RUN: Hiçbir değişiklik yapılmadı **", "DRY")
        qlog(f"\n✅  Import {'tamamlandı' if not dry_run else 'simülasyonu tamamlandı'}.", "OK")

    finally:
        kill_session(url, app_token, session_token)

    return dict(stats)


def main():
    dry_run = '--dry-run' in sys.argv
    script_dir = os.path.dirname(os.path.abspath(__file__))

    csv_path = None
    for arg in sys.argv[1:]:
        if not arg.startswith('--') and arg.endswith('.csv'):
            csv_path = arg if os.path.isabs(arg) else os.path.join(script_dir, arg)
            break
    if not csv_path:
        csv_path = find_latest_csv(script_dir)
    if not csv_path or not os.path.exists(csv_path):
        print("[HATA] CSV bulunamadı.")
        sys.exit(1)

    src_cfg, _ = load_source_config()
    if not src_cfg:
        print("[HATA] config.json bulunamadı.")
        sys.exit(1)

    run_import(
        url        = src_cfg.get('GLPI_URL', '').rstrip('/'),
        app_token  = src_cfg['GLPI_APP_TOKEN'],
        user_token = src_cfg['GLPI_USER_TOKEN'],
        csv_path   = csv_path,
        dry_run    = dry_run
    )


if __name__ == "__main__":
    main()
