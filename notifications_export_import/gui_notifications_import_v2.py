"""
gui_notifications_import_v2.py
-------------------------------
GLPI Notification Transfer GUI  —  v2
Yeni işleyiş:
  📤 Export Kaynak  → Kaynaktan CSV'ye export
  📥 Export Hedef   → Hedeften CSV'ye export
  ⚡ Transfer       → Kaynaktan export et, CSV'yi kaydet, Hedefe import et
                      (CSV seçimi gerekmez)
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import queue
import os
import sys
import json
import re
from datetime import datetime

# ─── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVERS_CANDIDATES = [
    os.path.join(SCRIPT_DIR, "servers.json"),
    os.path.join(SCRIPT_DIR, "..", "templates_export", "servers.json"),
]
SERVERS_FILE = next((p for p in SERVERS_CANDIDATES if os.path.exists(p)),
                    SERVERS_CANDIDATES[0])

sys.path.insert(0, SCRIPT_DIR)
import export_notifications as exp
import import_notifications as imp

# ─── Palette ──────────────────────────────────────────────────────────────────
BG        = "#1e1e2e"
BG2       = "#2a2a3e"
BG3       = "#313145"
ACCENT    = "#7c6af7"
ACCENT2   = "#5a4fcf"
TRANSFER  = "#0ea5e9"   # mavi — transfer butonu
TRANSFER2 = "#0284c7"
SUCCESS   = "#4ade80"
WARNING   = "#facc15"
ERROR     = "#f87171"
INFO_C    = "#60a5fa"
TEXT      = "#e2e8f0"
TEXT_DIM  = "#94a3b8"
BORDER    = "#3d3d5c"
FONT      = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_MONO = ("Consolas", 9)
FONT_HEAD = ("Segoe UI", 13, "bold")
FONT_SM   = ("Segoe UI", 9)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def load_servers():
    if not os.path.exists(SERVERS_FILE):
        return {}
    try:
        with open(SERVERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("servers", {})
    except Exception:
        return {}


def save_servers(d):
    data = {"servers": d, "_note": "url, app_token, user_token zorunlu."}
    with open(SERVERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def safe_name(s):
    s = re.sub(r'\W+', '_', s).strip('_')
    return re.sub(r'_+', '_', s)


# ─── Server Dialog ────────────────────────────────────────────────────────────
class ServerDialog(tk.Toplevel):
    def __init__(self, parent, title="Sunucu", name="", data=None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        data = data or {"url": "", "app_token": "", "user_token": "", "description": ""}
        pad  = dict(padx=12, pady=5)

        def lbl(t, r):
            tk.Label(self, text=t, bg=BG, fg=TEXT_DIM, font=FONT,
                     anchor="w", width=14).grid(row=r, column=0, sticky="w", **pad)
        def ent(r, show=None):
            v = tk.StringVar()
            e = tk.Entry(self, textvariable=v, bg=BG3, fg=TEXT, font=FONT,
                         width=44, relief="flat",
                         highlightbackground=BORDER, highlightthickness=1)
            if show:
                e.config(show=show)
            e.grid(row=r, column=1, sticky="ew", **pad)
            return v, e

        lbl("Profil Adı", 0); self.v_name, _ = ent(0); self.v_name.set(name)
        lbl("API URL",    1); self.v_url,  _ = ent(1); self.v_url.set(data.get("url", ""))
        lbl("App-Token",  2); self.v_app,  _ = ent(2); self.v_app.set(data.get("app_token", ""))
        lbl("User-Token", 3); self.v_usr, self._ue = ent(3, show="•"); self.v_usr.set(data.get("user_token", ""))
        lbl("Açıklama",   4); self.v_desc, _ = ent(4); self.v_desc.set(data.get("description", ""))

        self._show = tk.BooleanVar()
        tk.Checkbutton(self, text="Token'ı göster", variable=self._show,
                       command=lambda: self._ue.config(show="" if self._show.get() else "•"),
                       bg=BG, fg=TEXT_DIM, activebackground=BG,
                       selectcolor=BG3, font=FONT_SM).grid(row=5, column=1, sticky="w", padx=12)

        bf = tk.Frame(self, bg=BG)
        bf.grid(row=6, column=0, columnspan=2, pady=12)
        tk.Button(bf, text="💾 Kaydet", command=self._save,
                  bg=ACCENT, fg=TEXT, font=FONT_BOLD, relief="flat",
                  cursor="hand2", padx=14, pady=6).pack(side="left", padx=6)
        tk.Button(bf, text="İptal", command=self.destroy,
                  bg=BG3, fg=TEXT_DIM, font=FONT, relief="flat",
                  cursor="hand2", padx=14, pady=6).pack(side="left")
        self.columnconfigure(1, weight=1)

    def _save(self):
        name = self.v_name.get().strip()
        url  = self.v_url.get().strip().rstrip("/")
        app  = self.v_app.get().strip()
        usr  = self.v_usr.get().strip()
        if not all([name, url, app, usr]):
            messagebox.showwarning("Eksik", "Tüm alanlar zorunludur.", parent=self)
            return
        self.result = (name, {"url": url, "app_token": app,
                              "user_token": usr, "description": self.v_desc.get().strip()})
        self.destroy()


# ─── Main App ─────────────────────────────────────────────────────────────────
class NotifTransferApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GLPI Notification Transfer  v2")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(900, 680)

        self.log_queue = queue.Queue()
        self._running  = False
        self.servers   = load_servers()

        self._build_ui()
        self._refresh_dropdowns()
        self.after(100, self._process_log_queue)

    # ─── UI ───────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=ACCENT2, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⚡  GLPI Notification Transfer  v2",
                 bg=ACCENT2, fg=TEXT, font=FONT_HEAD).pack()
        tk.Label(hdr, text="Export · Export Hedef · Transfer (Kaynak → Hedef)",
                 bg=ACCENT2, fg=TEXT_DIM, font=FONT_SM).pack()

        body = tk.Frame(self, bg=BG, padx=18, pady=14)
        body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg=BG, width=400)
        left.pack(side="left", fill="both", expand=False, padx=(0, 12))
        left.pack_propagate(False)

        right = tk.Frame(body, bg=BG)
        right.pack(side="right", fill="both", expand=True)

        self._build_server_section(left)
        self._build_options_section(left)
        self._build_action_buttons(left)
        self._build_last_csv_info(left)
        self._build_log_panel(right)

    def _section(self, parent, title):
        f = tk.LabelFrame(parent, text=f"  {title}  ", bg=BG, fg=ACCENT,
                          font=FONT_BOLD, bd=0, relief="flat",
                          highlightbackground=BORDER, highlightthickness=1)
        f.pack(fill="x", pady=(0, 10))
        return f

    def _build_server_section(self, parent):
        f = self._section(parent, "Sunucu Profilleri")

        for label, attr in [("📤 Kaynak", "var_src"), ("📥 Hedef", "var_tgt")]:
            row = tk.Frame(f, bg=BG)
            row.pack(fill="x", padx=10, pady=(6, 2))
            tk.Label(row, text=label, bg=BG, fg=TEXT_DIM, font=FONT,
                     width=10, anchor="w").pack(side="left")
            var = tk.StringVar()
            cmb = ttk.Combobox(row, textvariable=var, state="readonly", font=FONT)
            cmb.pack(side="left", fill="x", expand=True, padx=(4, 0))
            setattr(self, attr, var)
            setattr(self, f"cmb_{attr[-3:]}", cmb)

        self.cmb_src.bind("<<ComboboxSelected>>", lambda e: self._on_change())
        self.cmb_tgt.bind("<<ComboboxSelected>>", lambda e: self._on_change())

        self.lbl_src_info = tk.Label(f, text="", bg=BG, fg=TEXT_DIM,
                                     font=FONT_SM, anchor="w", padx=12)
        self.lbl_src_info.pack(fill="x")
        self.lbl_tgt_info = tk.Label(f, text="", bg=BG, fg=TEXT_DIM,
                                     font=FONT_SM, anchor="w", padx=12)
        self.lbl_tgt_info.pack(fill="x")

        btn_row = tk.Frame(f, bg=BG)
        btn_row.pack(fill="x", padx=10, pady=(6, 10))
        for label, cmd, color in [
            ("➕ Ekle",    self._add_server,  BG3),
            ("✏ Düzenle", self._edit_server, BG3),
            ("🗑 Sil",     self._del_server,  "#3d2020"),
        ]:
            tk.Button(btn_row, text=label, command=cmd, bg=color, fg=TEXT,
                      font=FONT_SM, relief="flat", cursor="hand2",
                      padx=8, pady=3).pack(side="left", padx=(0, 4))

        self.btn_test = tk.Button(btn_row, text="🔌 Test", command=self._test_conn,
                                  bg=BG3, fg=TEXT, font=FONT_SM, relief="flat",
                                  cursor="hand2", padx=8, pady=3)
        self.btn_test.pack(side="right")

        self.lbl_conn = tk.Label(f, text="", bg=BG, font=FONT_SM, padx=12)
        self.lbl_conn.pack(anchor="e", pady=(0, 6))

    def _build_options_section(self, parent):
        f = self._section(parent, "Seçenekler")
        row = tk.Frame(f, bg=BG)
        row.pack(fill="x", padx=10, pady=8)
        self.var_dryrun = tk.BooleanVar(value=False)
        tk.Checkbutton(row, text="Dry-Run  (gerçek değişiklik yapma)",
                       variable=self.var_dryrun, bg=BG, fg=TEXT,
                       activebackground=BG, selectcolor=BG3, font=FONT).pack(side="left")

    def _build_action_buttons(self, parent):
        f = self._section(parent, "İşlemler")

        # Row 1: Export buttons
        row1 = tk.Frame(f, bg=BG)
        row1.pack(fill="x", padx=10, pady=(8, 4))

        self.btn_exp_src = tk.Button(row1, text="📤 Export Kaynak",
                                     command=lambda: self._start_export("src"),
                                     bg=BG3, fg=TEXT, font=FONT_BOLD,
                                     relief="flat", cursor="hand2",
                                     padx=12, pady=8, activebackground=ACCENT)
        self.btn_exp_src.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.btn_exp_tgt = tk.Button(row1, text="📥 Export Hedef",
                                     command=lambda: self._start_export("tgt"),
                                     bg=BG3, fg=TEXT, font=FONT_BOLD,
                                     relief="flat", cursor="hand2",
                                     padx=12, pady=8, activebackground=ACCENT)
        self.btn_exp_tgt.pack(side="left", fill="x", expand=True)

        # Row 2: Transfer button
        row2 = tk.Frame(f, bg=BG)
        row2.pack(fill="x", padx=10, pady=(4, 10))

        self.btn_transfer = tk.Button(row2, text="⚡  Transfer  (Kaynak → Hedef)",
                                      command=self._start_transfer,
                                      bg=TRANSFER, fg=TEXT, font=FONT_BOLD,
                                      relief="flat", cursor="hand2",
                                      padx=14, pady=10, activebackground=TRANSFER2)
        self.btn_transfer.pack(fill="x")

        self.lbl_status = tk.Label(f, text="", bg=BG, fg=TEXT_DIM,
                                   font=FONT_SM, pady=4)
        self.lbl_status.pack()

    def _build_last_csv_info(self, parent):
        """Son oluşturulan CSV yolunu gösteren küçük bilgi bandı."""
        f = tk.Frame(parent, bg=BG)
        f.pack(fill="x", pady=(0, 4))
        tk.Label(f, text="Son CSV:", bg=BG, fg=TEXT_DIM, font=FONT_SM).pack(side="left")
        self.lbl_last_csv = tk.Label(f, text="—", bg=BG, fg=INFO_C,
                                     font=FONT_SM, cursor="hand2", anchor="w")
        self.lbl_last_csv.pack(side="left", padx=(4, 0))
        self.lbl_last_csv.bind("<Button-1>", self._open_csv_folder)

    def _build_log_panel(self, parent):
        hdr = tk.Frame(parent, bg=BG)
        hdr.pack(fill="x")
        tk.Label(hdr, text="  İşlem Logu", bg=BG, fg=ACCENT,
                 font=FONT_BOLD, anchor="w").pack(side="left")
        tk.Button(hdr, text="🗑", command=self._clear_log,
                  bg=BG, fg=TEXT_DIM, font=FONT_SM, relief="flat",
                  cursor="hand2", bd=0).pack(side="right")
        self.log_area = scrolledtext.ScrolledText(
            parent, bg=BG2, fg=TEXT, font=FONT_MONO, relief="flat",
            wrap="word", highlightbackground=BORDER, highlightthickness=1,
            state="disabled"
        )
        self.log_area.pack(fill="both", expand=True, pady=(4, 0))
        for tag, color in [("INFO", TEXT), ("OK", SUCCESS), ("ERROR", ERROR),
                            ("WARNING", WARNING), ("DRY", TEXT_DIM),
                            ("HEAD", ACCENT), ("INFO_C", INFO_C)]:
            self.log_area.tag_config(tag, foreground=color)

    # ─── Dropdowns ────────────────────────────────────────────────────────────
    def _refresh_dropdowns(self):
        names = list(self.servers.keys())
        self.cmb_src["values"] = names
        self.cmb_tgt["values"] = names
        if names:
            if self.var_src.get() not in names:
                self.var_src.set(names[0])
            if self.var_tgt.get() not in names:
                self.var_tgt.set(names[min(1, len(names) - 1)])
        self._update_info()

    def _update_info(self):
        src = self.servers.get(self.var_src.get(), {})
        tgt = self.servers.get(self.var_tgt.get(), {})
        self.lbl_src_info.config(
            text=f"  {src.get('description','')}  •  {src.get('url','')}" if src else "")
        self.lbl_tgt_info.config(
            text=f"  {tgt.get('description','')}  •  {tgt.get('url','')}" if tgt else "")

    def _on_change(self):
        self._update_info()
        self.lbl_conn.config(text="")

    # ─── Server CRUD ──────────────────────────────────────────────────────────
    def _add_server(self):
        dlg = ServerDialog(self, "Yeni Sunucu")
        self.wait_window(dlg)
        if dlg.result:
            n, d = dlg.result
            if n in self.servers:
                messagebox.showwarning("Uyarı", f"'{n}' zaten mevcut.", parent=self)
                return
            self.servers[n] = d
            save_servers(self.servers)
            self._refresh_dropdowns()
            self.log_write(f"Sunucu eklendi: {n}", "OK")

    def _edit_server(self):
        n = self.var_tgt.get()
        if not n or n not in self.servers:
            messagebox.showinfo("Bilgi", "Düzenlemek için hedef profili seçin.", parent=self)
            return
        dlg = ServerDialog(self, f"Düzenle: {n}", name=n, data=self.servers[n])
        self.wait_window(dlg)
        if dlg.result:
            new_n, d = dlg.result
            if new_n != n:
                del self.servers[n]
            self.servers[new_n] = d
            save_servers(self.servers)
            self._refresh_dropdowns()
            self.log_write(f"Sunucu güncellendi: {new_n}", "OK")

    def _del_server(self):
        n = self.var_tgt.get()
        if not n or n not in self.servers:
            return
        if messagebox.askyesno("Sil", f"'{n}' silinsin mi?", parent=self):
            del self.servers[n]
            save_servers(self.servers)
            self._refresh_dropdowns()
            self.log_write(f"Sunucu silindi: {n}", "WARNING")

    # ─── Connection Test ──────────────────────────────────────────────────────
    def _test_conn(self):
        p = self.servers.get(self.var_tgt.get())
        if not p:
            messagebox.showwarning("Eksik", "Hedef profil boş.", parent=self)
            return
        self.lbl_conn.config(text="Test ediliyor...", fg=WARNING)
        self.btn_test.config(state="disabled")

        def _do():
            ok, _, ver = imp.test_connection(p["url"], p["app_token"], p["user_token"])
            if ok:
                self.lbl_conn.config(text=f"✓  GLPI {ver}", fg=SUCCESS)
                self.log_write(f"[OK] {self.var_tgt.get()} — GLPI {ver}", "OK")
            else:
                self.lbl_conn.config(text="✗  Hata", fg=ERROR)
                self.log_write(f"[HATA] {self.var_tgt.get()} bağlantısı başarısız.", "ERROR")
            self.btn_test.config(state="normal")

        threading.Thread(target=_do, daemon=True).start()

    # ─── Export (Kaynak veya Hedef) ───────────────────────────────────────────
    def _start_export(self, which):
        """which: 'src' or 'tgt'"""
        if self._running:
            return
        key    = self.var_src.get() if which == "src" else self.var_tgt.get()
        label  = "Kaynak" if which == "src" else "Hedef"
        p      = self.servers.get(key)
        if not p or not p.get("app_token"):
            messagebox.showwarning("Eksik", f"{label} profil eksik.", parent=self)
            return
        if not messagebox.askyesno("Export",
                f"'{key}' ({label}) sunucusundan notification'lar export edilsin mi?"):
            return
        self._running = True
        self._set_buttons_busy()
        self._clear_log()
        threading.Thread(target=self._run_export, args=(p, key), daemon=True).start()

    def _run_export(self, profile, profile_name):
        def qlog(msg, tag="INFO"):
            self.log_queue.put((msg, tag))

        try:
            qlog("=" * 50, "HEAD")
            qlog(f"  EXPORT: {profile_name}", "HEAD")
            qlog("=" * 50, "HEAD")

            ts  = datetime.now().strftime('%Y%m%d_%H%M%S')
            out = os.path.join(SCRIPT_DIR, f"notifications_{safe_name(profile_name)}_{ts}.csv")

            csv_path = exp.export(
                url         = profile["url"].rstrip('/'),
                app_token   = profile["app_token"],
                user_token  = profile["user_token"],
                output_path = out,
                server_name = profile_name,
            )
            qlog(f"\n✅  Export tamamlandı", "OK")
            qlog(f"   {os.path.basename(csv_path)}", "INFO_C")
            self._set_last_csv(csv_path)
            self.log_queue.put(("__DONE__", "OK"))

        except Exception as e:
            import traceback
            qlog(f"\n[HATA] {e}", "ERROR")
            qlog(traceback.format_exc(), "ERROR")
            self.log_queue.put(("__DONE__", "ERROR"))

    # ─── Transfer (src → CSV → tgt) ───────────────────────────────────────────
    def _start_transfer(self):
        if self._running:
            return
        src_name = self.var_src.get()
        tgt_name = self.var_tgt.get()
        src_p    = self.servers.get(src_name)
        tgt_p    = self.servers.get(tgt_name)
        if not src_p or not src_p.get("app_token"):
            messagebox.showwarning("Eksik", "Kaynak profil eksik.", parent=self)
            return
        if not tgt_p or not tgt_p.get("app_token"):
            messagebox.showwarning("Eksik", "Hedef profil eksik.", parent=self)
            return
        dry = self.var_dryrun.get()
        if not messagebox.askyesno("Transfer Onayı",
                f"Kaynak : {src_name}\n"
                f"Hedef  : {tgt_name}\n"
                f"Dry-Run: {'EVET' if dry else 'HAYIR'}\n\n"
                "Kaynaktan export edilip Hedefe aktarılsın mı?"):
            return
        self._running = True
        self._set_buttons_busy()
        self._clear_log()
        threading.Thread(
            target=self._run_transfer,
            args=(src_p, src_name, tgt_p, tgt_name, dry),
            daemon=True
        ).start()

    def _run_transfer(self, src_p, src_name, tgt_p, tgt_name, dry_run):
        def qlog(msg, tag="INFO"):
            self.log_queue.put((msg, tag))

        try:
            # ── 1. Export from source ─────────────────────────────────────────
            qlog("=" * 50, "HEAD")
            qlog(f"  TRANSFER: {src_name}  →  {tgt_name}", "HEAD")
            if dry_run:
                qlog("  [DRY-RUN]", "DRY")
            qlog("=" * 50, "HEAD")

            qlog(f"\n【1/2】 Export: {src_name}", "INFO_C")
            ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_name = f"notifications_{safe_name(src_name)}_to_{safe_name(tgt_name)}_{ts}.csv"
            out      = os.path.join(SCRIPT_DIR, csv_name)

            csv_path = exp.export(
                url         = src_p["url"].rstrip('/'),
                app_token   = src_p["app_token"],
                user_token  = src_p["user_token"],
                output_path = out,
                server_name = src_name,
            )
            qlog(f"  ✅ Export tamamlandı → {os.path.basename(csv_path)}", "OK")
            self._set_last_csv(csv_path)

            # ── 2. Import to target ───────────────────────────────────────────
            qlog(f"\n【2/2】 Import: {tgt_name}", "INFO_C")
            imp.run_import(
                url          = tgt_p["url"].rstrip('/'),
                app_token    = tgt_p["app_token"],
                user_token   = tgt_p["user_token"],
                csv_path     = csv_path,
                dry_run      = dry_run,
                log_callback = qlog,
            )
            self.log_queue.put(("__DONE__", "OK"))

        except Exception as e:
            import traceback
            qlog(f"\n[HATA] {e}", "ERROR")
            qlog(traceback.format_exc(), "ERROR")
            self.log_queue.put(("__DONE__", "ERROR"))

    # ─── UI Helpers ───────────────────────────────────────────────────────────
    def _set_buttons_busy(self):
        self.btn_exp_src.config(state="disabled", text="⏳ Export Kaynak...")
        self.btn_exp_tgt.config(state="disabled", text="⏳ Export Hedef...")
        self.btn_transfer.config(state="disabled", text="⏳ Transfer...")
        self.lbl_status.config(text="İşleniyor...", fg=WARNING)

    def _restore_buttons(self, ok):
        self.btn_exp_src.config(state="normal", text="📤 Export Kaynak")
        self.btn_exp_tgt.config(state="normal", text="📥 Export Hedef")
        self.btn_transfer.config(state="normal", text="⚡  Transfer  (Kaynak → Hedef)")
        self.lbl_status.config(
            text="Tamamlandı ✅" if ok else "Hata oluştu ⚠",
            fg=SUCCESS if ok else ERROR)

    def _set_last_csv(self, path):
        """Son CSV bilgisini günceller (thread-safe via queue)."""
        self.log_queue.put(("__CSV__", path))

    def _open_csv_folder(self, _event=None):
        path = self.lbl_last_csv.cget("text")
        if path and path != "—" and os.path.exists(path):
            os.startfile(os.path.dirname(path))

    # ─── Log ──────────────────────────────────────────────────────────────────
    def log_write(self, msg, tag="INFO"):
        self.log_area.config(state="normal")
        self.log_area.insert("end", msg + "\n", tag)
        self.log_area.see("end")
        self.log_area.config(state="disabled")

    def _clear_log(self):
        self.log_area.config(state="normal")
        self.log_area.delete("1.0", "end")
        self.log_area.config(state="disabled")

    def _process_log_queue(self):
        try:
            while True:
                msg, tag = self.log_queue.get_nowait()
                if msg == "__DONE__":
                    self._running = False
                    self._restore_buttons(tag == "OK")
                elif msg == "__CSV__":
                    self.lbl_last_csv.config(text=tag)
                else:
                    self.log_write(msg, tag)
        except queue.Empty:
            pass
        self.after(100, self._process_log_queue)


# ─── Entry ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = NotifTransferApp()
    app.mainloop()
