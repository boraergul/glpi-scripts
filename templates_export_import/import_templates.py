"""
import_templates.py
-------------------
export_templates.py ile dışa aktarılan; noktalı virgül (;) ile ayrılmış CSV'deki
Notification Template'lerini hedef GLPI sistemine aktarır.

Davranış:
  - Çalışırken hedef GLPI URL, App-Token ve User-Token bilgilerini sorar.
  - Template ismine göre arama yapar; varsa günceller, yoksa oluşturur.
  - Her template için CSV'deki her dil çevirisini CREATE veya UPDATE eder.

Kullanım:
  python import_templates.py                          # En yeni CSV otomatik seçilir
  python import_templates.py templates_export_X.csv  # Belirli bir CSV dosyası
  python import_templates.py --dry-run               # Gerçek değişiklik yapmaz
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
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'import_templates.log')
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

# ─── Config (Kaynak - sadece referans için) ───────────────────────────────────
def load_source_config():
    """Kaynak GLPI config.json'u okur (gösterim için referans)."""
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


# ─── Interactive Prompt ───────────────────────────────────────────────────────
def prompt_target_credentials(source_config, source_path):
    """
    Hedef GLPI bağlantı bilgilerini interaktif olarak sorar.
    Kaynak config bilgilerini referans olarak gösterir.
    """
    SEP = '─' * 58
    print(f"\n{SEP}")
    print("  GLPI Notification Template Importer")
    print(f"{SEP}")

    if source_config:
        src_url = source_config.get('GLPI_URL', 'N/A')
        print(f"  Kaynak GLPI (config): {src_url}")
        print(f"  Config dosyası      : {source_path}")
    else:
        print("  Kaynak config.json bulunamadı.")

    print(f"{SEP}")
    print("  Hedef GLPI bilgilerini girin (boş bırakırsanız kaynak kullanılır):")
    print(f"{SEP}\n")

    # URL
    default_url = source_config.get('GLPI_URL', '').rstrip('/') if source_config else ''
    url_input = input(f"  Hedef GLPI URL [{default_url}]: ").strip()
    target_url = (url_input or default_url).rstrip('/')
    if not target_url:
        print("  [HATA] URL boş bırakılamaz.")
        sys.exit(1)

    # App Token
    default_app = source_config.get('GLPI_APP_TOKEN', '') if source_config else ''
    default_app_display = default_app[:6] + '...' if len(default_app) > 6 else default_app
    app_input = input(f"  Hedef App-Token [{default_app_display}]: ").strip()
    target_app_token = app_input or default_app
    if not target_app_token:
        print("  [HATA] App-Token boş bırakılamaz.")
        sys.exit(1)

    # User Token
    import getpass
    default_user = source_config.get('GLPI_USER_TOKEN', '') if source_config else ''
    default_user_display = default_user[:6] + '...' if len(default_user) > 6 else default_user
    user_input = getpass.getpass(f"  Hedef User-Token [{default_user_display}]: ").strip()
    target_user_token = user_input or default_user
    if not target_user_token:
        print("  [HATA] User-Token boş bırakılamaz.")
        sys.exit(1)

    return target_url, target_app_token, target_user_token


def test_connection(url, app_token, user_token):
    """Hedef GLPI'ye test bağlantısı yapar. (session_token, glpi_version) döner."""
    print(f"\n  Bağlantı test ediliyor: {url} ...")
    headers = {
        "App-Token": app_token,
        "Authorization": f"user_token {user_token}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.get(f"{url}/initSession", headers=headers, verify=False, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            session_token = data.get('session_token')
            # Get GLPI version
            hdrs = {"App-Token": app_token, "Session-Token": session_token}
            ver_resp = requests.get(f"{url}/getGlpiConfig", headers=hdrs, verify=False, timeout=10)
            version = ''
            if ver_resp.status_code == 200:
                version = ver_resp.json().get('cfg_glpi', {}).get('version', '')
            # Kill test session
            requests.get(f"{url}/killSession", headers=hdrs, verify=False, timeout=5)
            return True, session_token, version
        else:
            print(f"  [HATA] HTTP {resp.status_code}: {resp.text[:150]}")
            return False, None, ''
    except requests.exceptions.ConnectionError:
        print(f"  [HATA] Sunucuya ulaşılamıyor: {url}")
        return False, None, ''
    except Exception as e:
        print(f"  [HATA] {e}")
        return False, None, ''

# ─── Session ──────────────────────────────────────────────────────────────────
def init_session(url, app_token, user_token):
    headers = {
        "App-Token": app_token,
        "Authorization": f"user_token {user_token}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.get(f"{url}/initSession", headers=headers, verify=False, timeout=30)
        resp.raise_for_status()
        session_token = resp.json().get('session_token')
        logger.info("Session initialized.")

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
    try:
        requests.get(
            f"{url}/killSession",
            headers={"App-Token": app_token, "Session-Token": session_token},
            verify=False, timeout=10
        )
        logger.info("Session terminated.")
    except Exception as e:
        logger.warning(f"Failed to terminate session: {e}")

# ─── API Helpers ──────────────────────────────────────────────────────────────
def api_get(url, endpoint, headers, params=None, timeout=15):
    try:
        resp = requests.get(f"{url}/{endpoint}", headers=headers,
                            params=params, verify=False, timeout=timeout)
        return resp
    except Exception as e:
        logger.error(f"GET /{endpoint} error: {e}")
        return None


def api_post(url, endpoint, headers, payload, dry_run=False):
    if dry_run:
        logger.info(f"  [DRY-RUN] POST /{endpoint}: {list(payload.get('input', {}).keys())}")
        return True, None
    try:
        resp = requests.post(f"{url}/{endpoint}", headers=headers,
                             json=payload, verify=False, timeout=30)
        if resp.status_code == 201:
            return True, resp.json()
        else:
            logger.warning(f"  POST /{endpoint} -> HTTP {resp.status_code}: {resp.text[:200]}")
            return False, None
    except Exception as e:
        logger.error(f"  POST /{endpoint} error: {e}")
        return False, None


def api_put(url, endpoint, item_id, headers, payload, dry_run=False):
    if dry_run:
        logger.info(f"  [DRY-RUN] PUT /{endpoint}/{item_id}: {list(payload.get('input', {}).keys())}")
        return True
    try:
        resp = requests.put(f"{url}/{endpoint}/{item_id}", headers=headers,
                            json=payload, verify=False, timeout=30)
        if resp.status_code in [200, 201]:
            return True
        else:
            logger.warning(f"  PUT /{endpoint}/{item_id} -> HTTP {resp.status_code}: {resp.text[:200]}")
            return False
    except Exception as e:
        logger.error(f"  PUT /{endpoint}/{item_id} error: {e}")
        return False

# ─── CSV Parsing ──────────────────────────────────────────────────────────────
def find_latest_csv(directory):
    """Find the most recently created templates_export_*.csv file."""
    pattern = os.path.join(directory, 'templates_export_*.csv')
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def parse_csv(csv_path):
    """
    Parse the semicolon-delimited CSV and return a dict:
      {
        template_name: {
          'itemtype': str,
          'comments': str,
          'css': str,
          'translations': {
            lang_code: {
              'subject': str,
              'content_html': str,
              'content_text': str
            }, ...
          }
        }, ...
      }
    """
    templates = {}

    logger.info(f"Parsing CSV: {csv_path}")
    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, delimiter=';')
        rows_read = 0
        for row in reader:
            rows_read += 1
            name     = row.get('Name', '').strip()
            itemtype = row.get('Item Type', '').strip()
            comments = row.get('Comments', '').strip()
            css      = row.get('CSS', '').strip()
            lang     = row.get('Translation Language', '').strip()
            subject  = row.get('Translation Subject', '').strip()
            html_c   = row.get('Translation Content HTML', '').strip()
            text_c   = row.get('Translation Content Text', '').strip()

            if not name:
                continue

            if name not in templates:
                templates[name] = {
                    'itemtype': itemtype,
                    'comments': comments,
                    'css': css,
                    'translations': {}
                }

            if lang:
                templates[name]['translations'][lang] = {
                    'subject': subject,
                    'content_html': html_c,
                    'content_text': text_c,
                }

    logger.info(f"  Parsed {rows_read} CSV rows -> {len(templates)} unique templates.")
    return templates


# ─── Template Upsert ──────────────────────────────────────────────────────────
def fetch_existing_templates(url, headers):
    """Fetch all existing templates from target GLPI. Returns {name: id}."""
    existing = {}
    range_start = 0
    range_step = 500
    while True:
        resp = api_get(url, "NotificationTemplate", headers,
                       params={"range": f"{range_start}-{range_start + range_step - 1}", "is_deleted": 0})
        if not resp or resp.status_code not in [200, 206]:
            break
        batch = resp.json()
        if not batch or not isinstance(batch, list):
            break
        for t in batch:
            if isinstance(t, dict) and 'name' in t:
                existing[t['name']] = t['id']
        if len(batch) < range_step:
            break
        range_start += range_step
    logger.info(f"Existing templates on target: {len(existing)}")
    return existing


def upsert_template(url, headers, name, data, existing_map, dry_run):
    """Create or update a NotificationTemplate. Returns (template_id, action)."""
    existing_id = existing_map.get(name)

    payload_input = {
        "name": name,
        "itemtype": data['itemtype'],
        "comment": data['comments'],
        "css": data['css'],
        "entities_id": 0,
        "is_recursive": 1
    }

    if existing_id:
        # Update
        ok = api_put(url, "NotificationTemplate", existing_id, headers,
                     {"input": payload_input}, dry_run)
        if ok:
            logger.info(f"  [UPDATE] Template '{name}' (ID: {existing_id})")
            return existing_id, 'updated'
        else:
            logger.warning(f"  [FAIL]   Template '{name}' update failed, using existing ID.")
            return existing_id, 'update_failed'
    else:
        # Create
        ok, result = api_post(url, "NotificationTemplate", headers,
                              {"input": payload_input}, dry_run)
        if dry_run:
            logger.info(f"  [DRY-RUN CREATE] Template '{name}'")
            return -1, 'dry_run_create'
        if ok and result:
            new_id = result.get('id') if isinstance(result, dict) else None
            if new_id:
                logger.info(f"  [CREATE] Template '{name}' -> ID: {new_id}")
                existing_map[name] = new_id   # update cache
                return new_id, 'created'
        logger.error(f"  [FAIL]   Template '{name}' creation failed.")
        return None, 'create_failed'


# ─── Translation Upsert ───────────────────────────────────────────────────────
def fetch_existing_translations(url, headers, template_id):
    """Returns {language_code: translation_id}."""
    resp = api_get(url,
                   f"NotificationTemplate/{template_id}/NotificationTemplateTranslation",
                   headers, params={"range": "0-200"})
    if resp and resp.status_code in [200, 206]:
        data = resp.json()
        if isinstance(data, list):
            return {item.get('language'): item.get('id') for item in data if item.get('language')}
    return {}


def upsert_translation(url, headers, template_id, lang, trans_data, existing_trans, dry_run):
    """Create or update a NotificationTemplateTranslation."""
    payload_input = {
        "notificationtemplates_id": template_id,
        "language": lang,
        "subject": trans_data['subject'],
        "content_html": trans_data['content_html'],
        "content_text": trans_data['content_text'],
    }

    existing_id = existing_trans.get(lang)

    if existing_id:
        ok = api_put(url, "NotificationTemplateTranslation", existing_id, headers,
                     {"input": payload_input}, dry_run)
        action = 'trans_updated' if ok else 'trans_update_failed'
        logger.info(f"    [{action.upper()}] Lang: {lang}")
    else:
        ok, result = api_post(url, "NotificationTemplateTranslation", headers,
                              {"input": payload_input}, dry_run)
        if dry_run:
            logger.info(f"    [DRY-RUN CREATE TRANS] Lang: {lang}")
            return 'dry_run_create'
        if ok and result:
            new_id = result.get('id') if isinstance(result, dict) else None
            if new_id:
                existing_trans[lang] = new_id
                logger.info(f"    [TRANS_CREATED] Lang: {lang} -> ID: {new_id}")
                return 'trans_created'
        logger.warning(f"    [TRANS_FAIL] Lang: {lang}")
        return 'trans_create_failed'
    return action

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    dry_run = '--dry-run' in sys.argv

    # ── CSV dosyasını belirle ────────────────────────────────────────────────
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = None
    for arg in sys.argv[1:]:
        if not arg.startswith('--') and arg.endswith('.csv'):
            csv_path = arg if os.path.isabs(arg) else os.path.join(script_dir, arg)
            break
    if not csv_path:
        csv_path = find_latest_csv(script_dir)
    if not csv_path or not os.path.exists(csv_path):
        print("[HATA] CSV dosyası bulunamadı. Önce export_templates.py çalıştırın.")
        sys.exit(1)

    # ── Kaynak config'i oku (referans için) ──────────────────────────────────
    source_config, source_path = load_source_config()

    # ── Hedef GLPI bilgilerini sor ───────────────────────────────────────────
    glpi_url, app_token, user_token = prompt_target_credentials(source_config, source_path)

    # ── Bağlantı testi ───────────────────────────────────────────────────────
    ok, _, version = test_connection(glpi_url, app_token, user_token)
    if ok:
        ver_str = f" (GLPI {version})" if version else ''
        print(f"  [OK] Bağlantı başarılı{ver_str}")
    else:
        retry = input("  Bağlantı başarısız. Yine de devam etmek istiyor musunuz? (e/H): ").strip().lower()
        if retry != 'e':
            print("  İptal edildi.")
            sys.exit(0)

    # ── Onay al ──────────────────────────────────────────────────────────────
    SEP = '─' * 58
    print(f"\n{SEP}")
    print(f"  CSV Dosyası : {os.path.basename(csv_path)}")
    print(f"  Hedef GLPI  : {glpi_url}")
    print(f"  Dry Run     : {'EVET - Değişiklik yapılmayacak' if dry_run else 'HAYIR - Gerçek import'}")
    print(f"{SEP}")
    confirm = input("  İmport başlatılsın mı? (e/H): ").strip().lower()
    if confirm != 'e':
        print("  İptal edildi.")
        sys.exit(0)

    # ── Session başlat ───────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("GLPI Notification Template Importer")
    logger.info(f"Started at : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"CSV file   : {csv_path}")
    logger.info(f"Target URL : {glpi_url}")
    logger.info(f"Dry run    : {dry_run}")
    logger.info("=" * 60)

    session_token = init_session(glpi_url, app_token, user_token)
    headers = {
        "App-Token": app_token,
        "Session-Token": session_token,
        "Content-Type": "application/json"
    }

    # Counters
    stats = defaultdict(int)

    try:
        # ── 1. Parse CSV ────────────────────────────────────────────────────────
        templates_data = parse_csv(csv_path)

        # ── 2. Fetch existing templates from target ──────────────────────────────
        existing_map = fetch_existing_templates(glpi_url, headers)

        # ── 3. Process each template ─────────────────────────────────────────────
        total = len(templates_data)
        for idx, (tmpl_name, tmpl_data) in enumerate(templates_data.items(), 1):
            logger.info(f"\n[{idx}/{total}] Processing: '{tmpl_name}'")

            template_id, action = upsert_template(
                glpi_url, headers, tmpl_name, tmpl_data, existing_map, dry_run
            )
            stats[action] += 1

            if template_id is None:
                logger.error(f"  Skipping translations for '{tmpl_name}' (template upsert failed).")
                stats['skipped'] += 1
                continue

            if template_id == -1:
                # dry-run create, no real ID, skip translation upsert
                for lang in tmpl_data['translations']:
                    logger.info(f"    [DRY-RUN] Would upsert translation: {lang}")
                    stats['dry_run_create'] += 1
                continue

            # Fetch existing translations for this template
            existing_trans = fetch_existing_translations(glpi_url, headers, template_id)

            translations = tmpl_data.get('translations', {})
            if not translations:
                logger.info(f"  No translations in CSV for '{tmpl_name}', skipping.")
            else:
                for lang, trans_data in translations.items():
                    result = upsert_translation(
                        glpi_url, headers, template_id, lang,
                        trans_data, existing_trans, dry_run
                    )
                    stats[result] += 1

        # ── 4. Summary ───────────────────────────────────────────────────────────
        logger.info(f"\n{'=' * 60}")
        logger.info("Import Summary")
        logger.info(f"{'=' * 60}")
        logger.info(f"  Templates in CSV          : {total}")
        logger.info(f"  Templates created          : {stats.get('created', 0)}")
        logger.info(f"  Templates updated          : {stats.get('updated', 0)}")
        logger.info(f"  Templates create_failed    : {stats.get('create_failed', 0)}")
        logger.info(f"  Templates update_failed    : {stats.get('update_failed', 0)}")
        logger.info(f"  Templates skipped          : {stats.get('skipped', 0)}")
        logger.info(f"  Translations created       : {stats.get('trans_created', 0)}")
        logger.info(f"  Translations updated       : {stats.get('trans_updated', 0)}")
        logger.info(f"  Translations failed        : {stats.get('trans_create_failed', 0) + stats.get('trans_update_failed', 0)}")
        if dry_run:
            logger.info("  ** DRY RUN - No actual changes were made **")
        logger.info(f"{'=' * 60}")

        print(f"\n[OK] Import {'(DRY-RUN) ' if dry_run else ''}complete. "
              f"Created: {stats.get('created', 0)}, Updated: {stats.get('updated', 0)}, "
              f"Trans created: {stats.get('trans_created', 0)}, Trans updated: {stats.get('trans_updated', 0)}")

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())

    finally:
        kill_session(glpi_url, app_token, session_token)


if __name__ == "__main__":
    main()
