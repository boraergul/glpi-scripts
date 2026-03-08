"""
gui_sla_escalation.py
---------------------
GLPI SLA Eskalasyon — Grafik Arayüz

  🔍 Dry-Run  → Değişiklik yapmadan simüle eder
  ⚡ Uygula   → Gerçek eskalasyonları uygular
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import subprocess
import sys
import os
from datetime import datetime

# ─── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH  = os.path.join(SCRIPT_DIR, "sla_escalation.py")

# ─── Palette ──────────────────────────────────────────────────────────────────
BG        = "#1e1e2e"
BG2       = "#2a2a3e"
BG3       = "#313145"
ACCENT    = "#7c6af7"
ACCENT2   = "#5a4fcf"
GREEN     = "#4ade80"
GREEN2    = "#22c55e"
WARNING   = "#facc15"
ERROR     = "#f87171"
INFO_C    = "#60a5fa"
TEXT      = "#e2e8f0"
TEXT_DIM  = "#94a3b8"
BORDER    = "#3d3d5c"
FONT      = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_MONO = ("Consolas", 9)
FONT_HEAD = ("Segoe UI", 14, "bold")
FONT_SM   = ("Segoe UI", 9)

# Log color tags
TAG_BREACH   = ("breach",   ERROR,   None)
TAG_ESCALATE = ("escalate", WARNING, None)
TAG_WARN_C   = ("warn",     INFO_C,  None)
TAG_SKIP     = ("skip",     TEXT_DIM, None)
TAG_OK       = ("ok",       GREEN,   None)
TAG_HEAD     = ("head",     ACCENT,  FONT_BOLD)
TAG_DIM      = ("dim",      TEXT_DIM, None)

# ─── App ──────────────────────────────────────────────────────────────────────
class SLAEscalationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GLPI SLA Eskalasyon")
        self.geometry("900x620")
        self.minsize(700, 500)
        self.configure(bg=BG)
        self._running = False
        self._q      = queue.Queue()
        self._build_ui()
        self._setup_tags()
        self._poll()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=BG2, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🔔  GLPI SLA Eskalasyon", font=FONT_HEAD,
                 bg=BG2, fg=ACCENT).pack(side="left", padx=20)
        self._status_lbl = tk.Label(hdr, text="Hazır", font=FONT,
                                    bg=BG2, fg=GREEN)
        self._status_lbl.pack(side="right", padx=20)

        # ── Options row ───────────────────────────────────────────────────────
        opts = tk.Frame(self, bg=BG, pady=10)
        opts.pack(fill="x", padx=20)

        tk.Label(opts, text="Uyarı Eşiği (%)", font=FONT_SM,
                 bg=BG, fg=TEXT_DIM).grid(row=0, column=0, sticky="w", padx=(0,4))
        self._warn_var = tk.IntVar(value=75)
        tk.Spinbox(opts, textvariable=self._warn_var, from_=50, to=99, width=5,
                   bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat",
                   buttonbackground=BG2).grid(row=0, column=1, padx=(0,20))

        tk.Label(opts, text="Eskalasyon Eşiği (%)", font=FONT_SM,
                 bg=BG, fg=TEXT_DIM).grid(row=0, column=2, sticky="w", padx=(0,4))
        self._esc_var = tk.IntVar(value=90)
        tk.Spinbox(opts, textvariable=self._esc_var, from_=51, to=99, width=5,
                   bg=BG3, fg=TEXT, insertbackground=TEXT, relief="flat",
                   buttonbackground=BG2).grid(row=0, column=3, padx=(0,20))

        self._verbose_var = tk.BooleanVar(value=False)
        tk.Checkbutton(opts, text="Verbose (tümünü göster)", var=self._verbose_var,
                       bg=BG, fg=TEXT_DIM, selectcolor=BG3,
                       activebackground=BG, font=FONT_SM).grid(row=0, column=4)

        # ── Buttons ───────────────────────────────────────────────────────────
        btns = tk.Frame(self, bg=BG, pady=4)
        btns.pack(fill="x", padx=20)

        self._dry_btn = tk.Button(
            btns, text="🔍  Dry-Run (Simülasyon)",
            font=FONT_BOLD, bg=ACCENT, fg="white", relief="flat",
            activebackground=ACCENT2, activeforeground="white",
            cursor="hand2", padx=20, pady=8,
            command=lambda: self._run(dry=True)
        )
        self._dry_btn.pack(side="left", padx=(0, 10))

        self._live_btn = tk.Button(
            btns, text="⚡  Uygula (Gerçek)",
            font=FONT_BOLD, bg=GREEN2, fg="#0f172a", relief="flat",
            activebackground=GREEN, activeforeground="#0f172a",
            cursor="hand2", padx=20, pady=8,
            command=lambda: self._run(dry=False)
        )
        self._live_btn.pack(side="left")

        self._stop_btn = tk.Button(
            btns, text="⏹  Durdur",
            font=FONT_BOLD, bg="#475569", fg="white", relief="flat",
            activebackground="#334155", activeforeground="white",
            cursor="hand2", padx=16, pady=8,
            command=self._stop, state="disabled"
        )
        self._stop_btn.pack(side="left", padx=10)

        self._clear_btn = tk.Button(
            btns, text="🗑  Temizle",
            font=FONT_SM, bg=BG3, fg=TEXT_DIM, relief="flat",
            activebackground=BG2, cursor="hand2", padx=12, pady=8,
            command=self._clear_log
        )
        self._clear_btn.pack(side="right")

        # ── Stats bar ─────────────────────────────────────────────────────────
        self._stats_frame = tk.Frame(self, bg=BG2, pady=6)
        self._stats_frame.pack(fill="x", padx=0)

        def stat_lbl(text, color):
            f = tk.Frame(self._stats_frame, bg=BG2)
            f.pack(side="left", padx=20)
            var = tk.StringVar(value="—")
            tk.Label(f, text=text, font=FONT_SM, bg=BG2, fg=TEXT_DIM).pack(side="left")
            lbl = tk.Label(f, textvariable=var, font=FONT_BOLD, bg=BG2, fg=color)
            lbl.pack(side="left", padx=(4,0))
            return var

        self._stat_total   = stat_lbl("Taranan:", TEXT)
        self._stat_warn    = stat_lbl("⚠️ Uyarı:", INFO_C)
        self._stat_esc     = stat_lbl("🔶 Eskalasyon:", WARNING)
        self._stat_breach  = stat_lbl("🔴 İhlal:", ERROR)
        self._stat_skip    = stat_lbl("↩️ Atlanan:", TEXT_DIM)

        # ── Log area ──────────────────────────────────────────────────────────
        log_frame = tk.Frame(self, bg=BG, pady=0)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(8, 16))

        tk.Label(log_frame, text=" ÇALIŞMA LOGU", font=FONT_SM,
                 bg=BORDER, fg=TEXT_DIM, anchor="w").pack(fill="x")

        self._log = scrolledtext.ScrolledText(
            log_frame, bg=BG3, fg=TEXT, font=FONT_MONO,
            relief="flat", bd=0, wrap="word",
            state="disabled", padx=10, pady=8
        )
        self._log.pack(fill="both", expand=True)

    def _setup_tags(self):
        for name, fg, font in [TAG_BREACH, TAG_ESCALATE, TAG_WARN_C,
                                TAG_SKIP, TAG_OK, TAG_HEAD, TAG_DIM]:
            kwargs = {"foreground": fg}
            if font:
                kwargs["font"] = font
            self._log.tag_config(name, **kwargs)

    # ── Log helpers ───────────────────────────────────────────────────────────
    def _clear_log(self):
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")
        for v in [self._stat_total, self._stat_warn,
                  self._stat_esc, self._stat_breach, self._stat_skip]:
            v.set("—")

    def _append(self, text, tag=None):
        self._log.configure(state="normal")
        if tag:
            self._log.insert("end", text + "\n", tag)
        else:
            self._log.insert("end", text + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def _tag_for_line(self, line):
        if "[BREACH"   in line: return "breach"
        if "[ESCALATE" in line: return "escalate"
        if "[WARN"     in line: return "warn"
        if "[SKIP"     in line: return "skip"
        if "==="       in line or "---" in line: return "head"
        if "Özet"      in line or "DRY-RUN" in line: return "dim"
        if "✓" in line or "✅" in line: return "ok"
        return None

    # ── Run logic ─────────────────────────────────────────────────────────────
    def _run(self, dry: bool):
        if self._running:
            return

        self._running = True
        self._dry_btn.configure(state="disabled")
        self._live_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")

        mode_str = "DRY-RUN" if dry else "⚡ GERÇEK"
        self._status_lbl.configure(text=f"Çalışıyor — {mode_str}", fg=WARNING)

        ts = datetime.now().strftime("%H:%M:%S")
        self._append(f"\n{'─'*70}", "head")
        self._append(f"  {ts}  |  {mode_str}  |  Uyarı={self._warn_var.get()}%  Eskalasyon={self._esc_var.get()}%", "head")
        self._append(f"{'─'*70}", "head")

        threading.Thread(target=self._worker, args=(dry,), daemon=True).start()

    def _worker(self, dry: bool):
        cmd = [sys.executable, SCRIPT_PATH,
               "--warn",     str(self._warn_var.get()),
               "--escalate", str(self._esc_var.get())]
        if not dry:
            cmd.append("--force")
        if self._verbose_var.get():
            cmd.append("--verbose")

        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
                cwd=SCRIPT_DIR
            )
            self._proc = proc
            for line in proc.stdout:
                self._q.put(("line", line.rstrip()))
            proc.wait()
            self._q.put(("done", proc.returncode))
        except Exception as e:
            self._q.put(("line", f"HATA: {e}"))
            self._q.put(("done", -1))

    def _stop(self):
        if hasattr(self, "_proc") and self._proc:
            try:
                self._proc.terminate()
            except Exception:
                pass
        self._q.put(("done", -2))

    def _poll(self):
        # Parse stats from log lines
        try:
            while True:
                msg_type, payload = self._q.get_nowait()
                if msg_type == "line":
                    tag = self._tag_for_line(payload)
                    self._append(payload, tag)
                    # Parse summary lines
                    p = payload.strip()
                    if "Taranan ticket" in p:
                        self._stat_total.set(p.split(":")[-1].strip())
                    elif "Yeni uyarı" in p:
                        self._stat_warn.set(p.split(":")[-1].strip())
                    elif "Yeni eskalasyon" in p:
                        self._stat_esc.set(p.split(":")[-1].strip())
                    elif "Yeni ihlal" in p:
                        self._stat_breach.set(p.split(":")[-1].strip())
                    elif "Atlanan" in p:
                        self._stat_skip.set(p.split(":")[-1].strip())

                elif msg_type == "done":
                    rc = payload
                    if rc == 0:
                        self._status_lbl.configure(text="✅ Tamamlandı", fg=GREEN)
                    elif rc == -2:
                        self._status_lbl.configure(text="⏹ Durduruldu", fg=TEXT_DIM)
                    else:
                        self._status_lbl.configure(text="❌ Hata", fg=ERROR)
                    self._running = False
                    self._dry_btn.configure(state="normal")
                    self._live_btn.configure(state="normal")
                    self._stop_btn.configure(state="disabled")

        except queue.Empty:
            pass
        self.after(100, self._poll)


# ─── Entry ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = SLAEscalationApp()
    app.mainloop()
