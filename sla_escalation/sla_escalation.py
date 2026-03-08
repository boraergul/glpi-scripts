#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sla_escalation.py
-----------------
Proaktif SLA Eskalasyon Scripti

TTR (Time To Resolve) tüketim yüzdesine göre açık ticket'ları izler
ve belirlenen eşiklerde otomatik aksiyon alır:

  %75 → ⚠️  Followup uyarısı (bir kez)
  %90 → 🔶  Priority +1 arttırır + followup
  %100+→ 🔴  Priority = Major (6) + followup

Her eşik için aksiyon yalnızca bir kez uygulanır (followup tag kontrolü).

Kullanım:
  python sla_escalation.py            # Dry-run (değişiklik yapmaz)
  python sla_escalation.py --force    # Gerçek değişiklikler
  python sla_escalation.py --force --verbose  # Detaylı çıktı
"""

import requests
import json
import os
import sys
import argparse
import urllib3
import csv
from datetime import datetime, timezone

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─── Eşikler ──────────────────────────────────────────────────────────────────
THRESHOLD_WARN     = 75   # %75 → followup uyarısı
THRESHOLD_ESCALATE = 90   # %90 → priority +1
THRESHOLD_BREACH   = 100  # %100+ → Major (6)

# Followup tag'leri (tekrar kontrolü için)
TAG_WARN     = "[SLA-ESK-75]"
TAG_ESCALATE = "[SLA-ESK-90]"
TAG_BREACH   = "[SLA-ESK-100]"

PRIORITY_MAJOR = 6  # GLPI Major priority

# GLPI ticket statuses: 1=New, 2=Processing(assigned), 3=Processing(planned), 4=Pending
# 5=Solved, 6=Closed → bunları atla
OPEN_STATUSES = [1, 2, 3, 4]

# ─── Config ───────────────────────────────────────────────────────────────────
def load_config():
    search_paths = [
        os.path.join(os.path.dirname(__file__), "config.json"),
        os.path.join(os.path.dirname(__file__), "..", "config", "config.json"),
        os.path.join(os.path.dirname(__file__), "..", "Config", "config.json"),
        os.path.join(os.path.dirname(__file__), "..", "..", "Config", "config.json"),
        "config.json",
    ]
    for path in search_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    print("HATA: config.json bulunamadı!")
    sys.exit(1)

# ─── Session ──────────────────────────────────────────────────────────────────
def init_session(url, app_token, user_token):
    headers = {
        "App-Token": app_token,
        "Authorization": f"user_token {user_token}",
        "Content-Type": "application/json",
    }
    try:
        r = requests.get(f"{url}/initSession", headers=headers, verify=False, timeout=30)
        r.raise_for_status()
        return r.json()["session_token"]
    except Exception as e:
        print(f"Session başlatılamadı: {e}")
        sys.exit(1)

def kill_session(url, app_token, session_token):
    headers = {"App-Token": app_token, "Session-Token": session_token}
    try:
        requests.get(f"{url}/killSession", headers=headers, verify=False, timeout=10)
    except:
        pass

def make_headers(app_token, session_token):
    return {
        "App-Token": app_token,
        "Session-Token": session_token,
        "Content-Type": "application/json",
    }

# ─── Ticket Çekme ─────────────────────────────────────────────────────────────
def fetch_open_tickets(url, headers, verbose=False):
    """
    TTR atanmış ve açık (status 1-4) ticket'ları çeker.
    time_to_resolve alanı dolu olanları döndürür.
    Tekrar eden ticket ID'leri atlar.
    """
    tickets  = []
    seen_ids = set()
    range_start = 0
    range_step  = 200

    if verbose:
        print("Açık ticket'lar çekiliyor...")

    while True:
        params = {
            "range": f"{range_start}-{range_start + range_step}",
            "is_deleted": 0,
            "expand_dropdowns": 0,
        }
        try:
            r = requests.get(
                f"{url}/Ticket",
                headers=headers,
                params=params,
                verify=False,
                timeout=30,
            )
            if r.status_code not in [200, 206]:
                break
            batch = r.json()
            if not batch:
                break

            for t in batch:
                tid    = t.get("id")
                status = t.get("status")
                ttr    = t.get("time_to_resolve")
                if status in OPEN_STATUSES and ttr and tid not in seen_ids:
                    seen_ids.add(tid)
                    tickets.append(t)

            if len(batch) < range_step:
                break
            range_start += range_step

        except Exception as e:
            print(f"Ticket çekme hatası: {e}")
            break

    if verbose:
        print(f"  → {len(tickets)} açık & TTR'lı ticket bulundu.")
    return tickets

# ─── TTR % Hesaplama ──────────────────────────────────────────────────────────
def parse_glpi_dt(dt_str):
    """GLPI tarih stringini UTC datetime'a çevirir."""
    if not dt_str:
        return None
    try:
        # Format: "2026-02-22 15:30:00"
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None

def calc_ttr_percent(ticket):
    """
    TTR tüketim yüzdesini hesaplar.
    Döndürür: (float percent, datetime ttr_due) veya (None, None)
    """
    created    = parse_glpi_dt(ticket.get("date"))
    ttr_due    = parse_glpi_dt(ticket.get("time_to_resolve"))
    now        = datetime.now(timezone.utc)

    if not created or not ttr_due:
        return None, None

    total_secs   = (ttr_due - created).total_seconds()
    elapsed_secs = (now - created).total_seconds()

    if total_secs <= 0:
        return None, None

    percent = (elapsed_secs / total_secs) * 100
    return round(percent, 1), ttr_due

# ─── Followup Kontrolü ────────────────────────────────────────────────────────
def get_existing_tags(url, headers, ticket_id):
    """Ticket'ın mevcut followup'larından ESK tag'lerini toplar."""
    tags = set()
    try:
        r = requests.get(
            f"{url}/Ticket/{ticket_id}/ITILFollowup",
            headers=headers,
            params={"range": "0-500"},
            verify=False,
            timeout=30,
        )
        if r.status_code in [200, 206]:
            for fu in r.json():
                content = fu.get("content", "")
                for tag in [TAG_WARN, TAG_ESCALATE, TAG_BREACH]:
                    if tag in content:
                        tags.add(tag)
    except Exception:
        pass
    return tags

# ─── Aksiyon Fonksiyonları ────────────────────────────────────────────────────
def add_followup(url, headers, ticket_id, message, dry_run):
    """Ticket'a followup notu ekler."""
    if dry_run:
        return True
    payload = {
        "input": {
            "items_id": ticket_id,
            "itemtype": "Ticket",
            "content": message,
            "is_private": 0,
        }
    }
    try:
        r = requests.post(
            f"{url}/Ticket/{ticket_id}/ITILFollowup",
            headers=headers,
            json=payload,
            verify=False,
            timeout=30,
        )
        return r.status_code in [200, 201]
    except Exception:
        return False

def set_priority(url, headers, ticket_id, new_priority, dry_run):
    """Ticket priority'sini günceller."""
    if dry_run:
        return True
    payload = {"input": {"id": ticket_id, "priority": new_priority}}
    try:
        r = requests.put(
            f"{url}/Ticket/{ticket_id}",
            headers=headers,
            json=payload,
            verify=False,
            timeout=30,
        )
        return r.status_code in [200, 201]
    except Exception:
        return False

# ─── Öncelik Adı ──────────────────────────────────────────────────────────────
PRIORITY_NAMES = {
    1: "Very Low",
    2: "Low",
    3: "Medium",
    4: "High",
    5: "Very High",
    6: "Major",
}

# ─── CSV Log ─────────────────────────────────────────────────────────────────
CSV_HEADER = ["Zaman", "Ticket_ID", "Baslik", "Aksiyon", "TTR_Yuzde", "Oncelik_Once", "Oncelik_Sonra", "Dry_Run"]

def get_csv_path():
    date_str = datetime.now().strftime("%Y%m%d")
    return os.path.join(os.path.dirname(__file__), f"sla_log_{date_str}.csv")

def write_csv_row(row: dict):
    """Günlük CSV dosyasına satır ekler. Dosya yoksa header oluşturur."""
    path = get_csv_path()
    file_exists = os.path.exists(path)
    try:
        with open(path, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADER, delimiter=";")
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    except Exception as e:
        print(f"[CSV] Yazma hatası: {e}")

# ─── Ana İşlem ────────────────────────────────────────────────────────────────
def process_ticket(url, headers, ticket, dry_run, verbose,
                   thr_warn=75, thr_esc=90, thr_breach=100):
    ticket_id = ticket["id"]
    title     = ticket.get("name", "(no title)")[:60]
    priority  = ticket.get("priority", 3)

    percent, ttr_due = calc_ttr_percent(ticket)
    if percent is None:
        return  # Hesaplanamadı

    existing_tags = get_existing_tags(url, headers, ticket_id)

    prefix = "[DRY] " if dry_run else ""

    # ── %100+ → Major ─────────────────────────────────────────────────────────
    if percent >= thr_breach and TAG_BREACH not in existing_tags:
        msg = (
            f"{TAG_BREACH} 🔴 SLA İHLALİ — TTR süresi %{percent:.0f} tüketildi.\n"
            f"Ticket önceliği otomatik olarak Major (6) seviyesine yükseltildi."
        )
        add_followup(url, headers, ticket_id, msg, dry_run)
        set_priority(url, headers, ticket_id, PRIORITY_MAJOR, dry_run)
        print(
            f"{prefix}[BREACH %{percent:.0f}] Ticket #{ticket_id} | Prio: {PRIORITY_NAMES.get(priority,'?')} → Major | {title}"
        )
        write_csv_row({
            "Zaman":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Ticket_ID":      ticket_id,
            "Baslik":         title,
            "Aksiyon":        "BREACH",
            "TTR_Yuzde":      f"{percent:.1f}",
            "Oncelik_Once":   PRIORITY_NAMES.get(priority, "?"),
            "Oncelik_Sonra":  "Major",
            "Dry_Run":        "EVET" if dry_run else "HAYIR",
        })

    # ── %90+ → Priority+1 ─────────────────────────────────────────────────────
    elif percent >= thr_esc and TAG_ESCALATE not in existing_tags:
        new_prio = min(priority + 1, 5)
        msg = (
            f"{TAG_ESCALATE} 🔶 SLA ESKALASYONu — TTR süresi %{percent:.0f} tüketildi.\n"
            f"Ticket önceliği {PRIORITY_NAMES.get(priority,'?')} → {PRIORITY_NAMES.get(new_prio,'?')} seviyesine yükseltildi."
        )
        add_followup(url, headers, ticket_id, msg, dry_run)
        set_priority(url, headers, ticket_id, new_prio, dry_run)
        print(
            f"{prefix}[ESCALATE %{percent:.0f}] Ticket #{ticket_id} | Prio: {PRIORITY_NAMES.get(priority,'?')} → {PRIORITY_NAMES.get(new_prio,'?')} | {title}"
        )
        write_csv_row({
            "Zaman":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Ticket_ID":      ticket_id,
            "Baslik":         title,
            "Aksiyon":        "ESCALATE",
            "TTR_Yuzde":      f"{percent:.1f}",
            "Oncelik_Once":   PRIORITY_NAMES.get(priority, "?"),
            "Oncelik_Sonra":  PRIORITY_NAMES.get(new_prio, "?"),
            "Dry_Run":        "EVET" if dry_run else "HAYIR",
        })

    # ── %75+ → Uyarı followup ─────────────────────────────────────────────────
    elif percent >= thr_warn and TAG_WARN not in existing_tags:
        remaining_min = int((ttr_due - datetime.now(timezone.utc)).total_seconds() / 60)
        msg = (
            f"{TAG_WARN} ⚠️ SLA UYARISI — TTR süresi %{percent:.0f} tüketildi.\n"
            f"Kalan süre: yaklaşık {remaining_min} dakika. Lütfen ticket'ı işleme alın."
        )
        add_followup(url, headers, ticket_id, msg, dry_run)
        print(
            f"{prefix}[WARN %{percent:.0f}] Ticket #{ticket_id} | ~{remaining_min}dk kaldı | {title}"
        )
        write_csv_row({
            "Zaman":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Ticket_ID":      ticket_id,
            "Baslik":         title,
            "Aksiyon":        "WARN",
            "TTR_Yuzde":      f"{percent:.1f}",
            "Oncelik_Once":   PRIORITY_NAMES.get(priority, "?"),
            "Oncelik_Sonra":  PRIORITY_NAMES.get(priority, "?"),
            "Dry_Run":        "EVET" if dry_run else "HAYIR",
        })

    elif verbose and percent >= thr_warn:
        print(
            f"[SKIP] Ticket #{ticket_id} | %{percent:.0f} (zaten işlendi) | {title}"
        )

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    # Use module-level defaults for argparse
    _warn_default     = THRESHOLD_WARN
    _escalate_default = THRESHOLD_ESCALATE

    parser = argparse.ArgumentParser(
        description="GLPI Proaktif SLA Eskalasyon Scripti"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Değişiklikleri uygula (varsayılan: dry-run)"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Detaylı çıktı"
    )
    parser.add_argument(
        "--warn", type=int, default=_warn_default,
        help=f"Uyarı eşiği (varsayılan: {_warn_default})"
    )
    parser.add_argument(
        "--escalate", type=int, default=_escalate_default,
        help=f"Eskalasyon eşiği (varsayılan: {_escalate_default})"
    )
    args = parser.parse_args()

    dry_run    = not args.force
    thr_warn   = args.warn
    thr_esc    = args.escalate
    thr_breach = THRESHOLD_BREACH

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mode    = "DRY-RUN" if dry_run else "LIVE"
    print(f"\n{'='*60}")
    print(f"  GLPI SLA Eskalasyon  [{mode}]  {now_str}")
    print(f"  Eşikler: Uyarı=%{thr_warn} | Eskalasyon=%{thr_esc} | İhlal=%{thr_breach}")
    print(f"{'='*60}\n")

    config   = load_config()
    glpi_url = config["GLPI_URL"].rstrip("/")
    app_tok  = config["GLPI_APP_TOKEN"]
    usr_tok  = config["GLPI_USER_TOKEN"]

    session_token = init_session(glpi_url, app_tok, usr_tok)
    headers = make_headers(app_tok, session_token)

    try:
        tickets = fetch_open_tickets(glpi_url, headers, verbose=args.verbose)

        warn_count     = 0
        escalate_count = 0
        breach_count   = 0
        skip_count     = 0

        for ticket in tickets:
            pct, _ = calc_ttr_percent(ticket)
            if pct is None:
                skip_count += 1
                continue

            existing = get_existing_tags(glpi_url, headers, ticket["id"])

            if pct >= thr_breach and TAG_BREACH not in existing:
                breach_count += 1
            elif pct >= thr_esc and TAG_ESCALATE not in existing:
                escalate_count += 1
            elif pct >= thr_warn and TAG_WARN not in existing:
                warn_count += 1

            process_ticket(glpi_url, headers, ticket, dry_run, args.verbose, thr_warn, thr_esc, thr_breach)

        print(f"\n{'='*60}")
        print(f"  Özet:")
        print(f"    Taranan ticket  : {len(tickets)}")
        print(f"    ⚠️  Yeni uyarı     : {warn_count}")
        print(f"    🔶 Yeni eskalasyon: {escalate_count}")
        print(f"    🔴 Yeni ihlal(Major): {breach_count}")
        print(f"    ↩️  Atlanan (no TTR): {skip_count}")
        if dry_run:
            print(f"\n  DRY-RUN: Hiçbir değişiklik yapılmadı.")
            print(f"  Gerçek değişiklik için: python sla_escalation.py --force")
        print(f"{'='*60}\n")

    except Exception as e:
        import traceback
        print(f"\nKRİTİK HATA: {e}")
        traceback.print_exc()
    finally:
        kill_session(glpi_url, app_tok, session_token)

if __name__ == "__main__":
    main()
