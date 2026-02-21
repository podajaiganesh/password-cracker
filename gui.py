"""
gui.py  —  CyberSim Suite  |  Password Attack Simulator
Requires:  pip install customtkinter
"""

import os, sys, threading, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk

from attacks.dictionary_attack import run_dictionary_attack
from attacks.brute_force import run_brute_force_attack
from attacks.hybrid_attack import run_hybrid_attack
from utils.hash_utils import hash_password, algorithm_available, SUPPORTED_ALGORITHMS
from utils.result import AttackResult

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BASE        = os.path.dirname(os.path.abspath(__file__))

BG          = "#0a0a0a"
SURFACE     = "#111111"
CARD        = "#141414"
BORDER      = "#222222"
BORDER2     = "#2a2a2a"
INPUT_BG    = "#0f0f0f"
RED         = "#e63946"
GREEN       = "#2dc653"
CYAN        = "#00b4d8"
AMBER       = "#f4a261"
TEXT        = "#f0f0f0"
TEXT_MID    = "#777777"
TEXT_DIM    = "#444444"

FONT_MONO   = "Courier New"


# ── Helper widgets ────────────────────────────────────────────────────────────

class SectionHeader(ctk.CTkFrame):
    def __init__(self, parent, text, **kw):
        super().__init__(parent, fg_color="transparent", **kw)
        ctk.CTkLabel(self, text=text,
                     font=ctk.CTkFont(FONT_MONO, 9, "bold"),
                     text_color=TEXT_DIM).pack(side="left")
        ctk.CTkFrame(self, fg_color=BORDER, height=1,
                     corner_radius=0).pack(side="left", fill="x",
                                           expand=True, padx=(10, 0), pady=5)


class StatTile(ctk.CTkFrame):
    def __init__(self, parent, label, accent=CYAN, **kw):
        super().__init__(parent, fg_color=CARD, corner_radius=6,
                         border_width=1, border_color=BORDER, **kw)
        ctk.CTkLabel(self, text=label,
                     font=ctk.CTkFont(FONT_MONO, 8),
                     text_color=TEXT_DIM).pack(pady=(10, 2))
        self._val = ctk.CTkLabel(self, text="—",
                                  font=ctk.CTkFont(FONT_MONO, 16, "bold"),
                                  text_color=accent)
        self._val.pack(pady=(0, 10))

    def set(self, value):
        self._val.configure(text=value)


class LogBox(ctk.CTkFrame):
    def __init__(self, parent, **kw):
        super().__init__(parent, fg_color=INPUT_BG,
                         corner_radius=6, border_width=1,
                         border_color=BORDER, **kw)
        self._text = ctk.CTkTextbox(self,
                                     fg_color="transparent",
                                     font=ctk.CTkFont(FONT_MONO, 10),
                                     text_color=TEXT_MID,
                                     wrap="word",
                                     activate_scrollbars=True)
        self._text.pack(fill="both", expand=True, padx=4, pady=4)
        self._text.configure(state="disabled")

    def append(self, msg, color=None):
        self._text.configure(state="normal")
        self._text.insert("end", msg + "\n")
        self._text.see("end")
        self._text.configure(state="disabled")

    def clear(self):
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")


class ResultBanner(ctk.CTkFrame):
    def __init__(self, parent, **kw):
        super().__init__(parent, fg_color=CARD, corner_radius=6,
                         border_width=1, border_color=BORDER,
                         height=56, **kw)
        self.pack_propagate(False)
        self._lbl = ctk.CTkLabel(self, text="AWAITING ATTACK",
                                  font=ctk.CTkFont(FONT_MONO, 13, "bold"),
                                  text_color=TEXT_DIM)
        self._lbl.pack(expand=True)

    def set(self, text, color=TEXT_DIM):
        self._lbl.configure(text=text, text_color=color)
        self.configure(border_color=color if color != TEXT_DIM else BORDER)


# ── Main GUI ──────────────────────────────────────────────────────────────────

class PasswordAttackSimulatorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Password Attack Simulator — CyberSim Suite")
        self.geometry("1140x700")
        self.minsize(960, 600)
        self.configure(fg_color=BG)

        self._stop_event   = threading.Event()
        self._attack_thread = None
        self._running      = False

        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        self._topbar()
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(12, 20))
        content.columnconfigure(0, weight=0, minsize=360)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        self._left_panel(content)
        self._right_panel(content)

    def _topbar(self):
        bar = ctk.CTkFrame(self, fg_color=SURFACE, height=52, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Home button
        home_btn = ctk.CTkButton(bar, text="← HOME",
                                  font=ctk.CTkFont(FONT_MONO, 9, "bold"),
                                  fg_color="transparent",
                                  hover_color=BORDER2,
                                  text_color=TEXT_MID,
                                  border_width=1,
                                  border_color=BORDER,
                                  corner_radius=4,
                                  width=80, height=28,
                                  command=self._go_home)
        home_btn.pack(side="left", padx=16, pady=12)

        ctk.CTkFrame(bar, fg_color=BORDER, width=1, height=28,
                     corner_radius=0).pack(side="left", pady=12)

        ctk.CTkLabel(bar, text="  [ CYBERSIM ]",
                     font=ctk.CTkFont(FONT_MONO, 14, "bold"),
                     text_color=RED).pack(side="left")

        ctk.CTkLabel(bar, text="  //  Password Attack Simulator",
                     font=ctk.CTkFont(FONT_MONO, 10),
                     text_color=TEXT_DIM).pack(side="left")

        ctk.CTkLabel(bar, text="●  READY",
                     font=ctk.CTkFont(FONT_MONO, 9),
                     text_color=GREEN).pack(side="right", padx=20)

        ctk.CTkFrame(self, fg_color=BORDER, height=1,
                     corner_radius=0).pack(fill="x")

    # ── Left (controls) ───────────────────────────────────────────────────────

    def _left_panel(self, parent):
        outer = ctk.CTkFrame(parent, fg_color=SURFACE, corner_radius=6,
                              border_width=1, border_color=BORDER,
                              width=360)
        outer.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        outer.grid_propagate(False)

        scroll = ctk.CTkScrollableFrame(outer, fg_color="transparent",
                                         scrollbar_button_color=BORDER2,
                                         scrollbar_button_hover_color=BORDER)
        scroll.pack(fill="both", expand=True, padx=2, pady=2)

        pad = {"padx": 16, "pady": (0, 10)}

        # ── Target hash ──
        SectionHeader(scroll, "TARGET HASH").pack(fill="x", padx=16, pady=(18, 8))

        ctk.CTkLabel(scroll, text="Hash Value",
                     font=ctk.CTkFont(FONT_MONO, 9),
                     text_color=TEXT_MID,
                     anchor="w").pack(fill="x", **pad)

        self._hash_entry = ctk.CTkEntry(scroll,
                                         fg_color=INPUT_BG,
                                         border_color=BORDER,
                                         border_width=1,
                                         font=ctk.CTkFont(FONT_MONO, 10),
                                         text_color=TEXT,
                                         placeholder_text="Paste hash here…",
                                         height=34)
        self._hash_entry.pack(fill="x", **pad)

        ctk.CTkLabel(scroll, text="Algorithm",
                     font=ctk.CTkFont(FONT_MONO, 9),
                     text_color=TEXT_MID,
                     anchor="w").pack(fill="x", **pad)

        self._algo_var = ctk.StringVar(value="md5")
        self._algo_menu = ctk.CTkOptionMenu(scroll,
                                             values=SUPPORTED_ALGORITHMS,
                                             variable=self._algo_var,
                                             fg_color=INPUT_BG,
                                             button_color=BORDER2,
                                             button_hover_color=BORDER,
                                             dropdown_fg_color=CARD,
                                             dropdown_hover_color=BORDER2,
                                             text_color=TEXT,
                                             font=ctk.CTkFont(FONT_MONO, 10),
                                             height=34)
        self._algo_menu.pack(fill="x", **pad)

        # ── Quick hash generator ──
        SectionHeader(scroll, "HASH GENERATOR").pack(fill="x", padx=16, pady=(8, 8))

        ctk.CTkLabel(scroll, text="Password to hash",
                     font=ctk.CTkFont(FONT_MONO, 9),
                     text_color=TEXT_MID,
                     anchor="w").pack(fill="x", **pad)

        self._gen_entry = ctk.CTkEntry(scroll,
                                        fg_color=INPUT_BG,
                                        border_color=BORDER,
                                        border_width=1,
                                        font=ctk.CTkFont(FONT_MONO, 10),
                                        text_color=TEXT,
                                        placeholder_text="e.g. password123",
                                        height=34)
        self._gen_entry.pack(fill="x", **pad)

        ctk.CTkButton(scroll, text="GENERATE & FILL",
                       font=ctk.CTkFont(FONT_MONO, 9, "bold"),
                       fg_color=BORDER2,
                       hover_color=BORDER,
                       text_color=CYAN,
                       height=30,
                       corner_radius=4,
                       command=self._generate_hash).pack(fill="x", **pad)

        # ── Attack type ──
        SectionHeader(scroll, "ATTACK TYPE").pack(fill="x", padx=16, pady=(8, 8))

        self._attack_var = ctk.StringVar(value="Dictionary")
        for label, desc in [
            ("Dictionary", "Wordlist-based lookup"),
            ("Brute Force", "Exhaustive character search"),
            ("Hybrid",      "Dictionary + mutations"),
        ]:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=2)
            ctk.CTkRadioButton(row, text=label,
                                font=ctk.CTkFont(FONT_MONO, 10),
                                text_color=TEXT,
                                fg_color=RED,
                                border_color=BORDER,
                                variable=self._attack_var,
                                value=label,
                                command=self._update_attack_options).pack(side="left")
            ctk.CTkLabel(row, text=f"  {desc}",
                          font=ctk.CTkFont(FONT_MONO, 8),
                          text_color=TEXT_DIM).pack(side="left")

        ctk.CTkFrame(scroll, fg_color="transparent", height=8).pack()

        # ── Wordlist ──
        self._wordlist_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self._wordlist_frame.pack(fill="x")

        SectionHeader(self._wordlist_frame, "WORDLIST").pack(fill="x", padx=16, pady=(8, 8))

        ctk.CTkLabel(self._wordlist_frame, text="Wordlist path",
                     font=ctk.CTkFont(FONT_MONO, 9),
                     text_color=TEXT_MID,
                     anchor="w").pack(fill="x", **pad)

        wl_row = ctk.CTkFrame(self._wordlist_frame, fg_color="transparent")
        wl_row.pack(fill="x", padx=16, pady=(0, 10))

        self._wordlist_entry = ctk.CTkEntry(wl_row,
                                             fg_color=INPUT_BG,
                                             border_color=BORDER,
                                             border_width=1,
                                             font=ctk.CTkFont(FONT_MONO, 9),
                                             text_color=TEXT,
                                             placeholder_text="wordlists/common.txt",
                                             height=32)
        default_wl = os.path.join(BASE, "wordlists", "common.txt")
        self._wordlist_entry.insert(0, default_wl)
        self._wordlist_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(wl_row, text="…",
                       font=ctk.CTkFont(FONT_MONO, 10),
                       fg_color=BORDER2,
                       hover_color=BORDER,
                       text_color=TEXT,
                       width=32, height=32,
                       corner_radius=4,
                       command=self._browse_wordlist).pack(side="left")

        # ── Brute force options ──
        self._brute_frame = ctk.CTkFrame(scroll, fg_color="transparent")

        SectionHeader(self._brute_frame, "BRUTE FORCE OPTIONS").pack(fill="x", padx=16, pady=(8, 8))

        ctk.CTkLabel(self._brute_frame, text="Max password length",
                     font=ctk.CTkFont(FONT_MONO, 9),
                     text_color=TEXT_MID,
                     anchor="w").pack(fill="x", **pad)

        self._maxlen_var = ctk.IntVar(value=4)
        row = ctk.CTkFrame(self._brute_frame, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 10))

        self._maxlen_slider = ctk.CTkSlider(row,
                                             from_=1, to=8,
                                             number_of_steps=7,
                                             variable=self._maxlen_var,
                                             fg_color=BORDER,
                                             progress_color=RED,
                                             button_color=RED,
                                             button_hover_color="#c1121f",
                                             command=self._update_maxlen_label)
        self._maxlen_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._maxlen_label = ctk.CTkLabel(row, text="4",
                                           font=ctk.CTkFont(FONT_MONO, 11, "bold"),
                                           text_color=RED,
                                           width=24)
        self._maxlen_label.pack(side="left")

        # ── Launch controls ──
        SectionHeader(scroll, "CONTROLS").pack(fill="x", padx=16, pady=(8, 8))

        self._launch_btn = ctk.CTkButton(scroll,
                                          text="▶  LAUNCH ATTACK",
                                          font=ctk.CTkFont(FONT_MONO, 11, "bold"),
                                          fg_color=RED,
                                          hover_color="#c1121f",
                                          text_color=TEXT,
                                          height=40,
                                          corner_radius=4,
                                          command=self._start_attack)
        self._launch_btn.pack(fill="x", padx=16, pady=(0, 8))

        self._stop_btn = ctk.CTkButton(scroll,
                                        text="■  STOP",
                                        font=ctk.CTkFont(FONT_MONO, 11, "bold"),
                                        fg_color=BORDER2,
                                        hover_color=BORDER,
                                        text_color=TEXT_MID,
                                        height=40,
                                        corner_radius=4,
                                        state="disabled",
                                        command=self._stop_attack)
        self._stop_btn.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkButton(scroll, text="CLEAR LOG",
                       font=ctk.CTkFont(FONT_MONO, 9),
                       fg_color="transparent",
                       hover_color=BORDER,
                       text_color=TEXT_DIM,
                       border_width=1,
                       border_color=BORDER,
                       height=28,
                       corner_radius=4,
                       command=self._clear).pack(fill="x", padx=16, pady=(0, 18))

    # ── Right (output) ────────────────────────────────────────────────────────

    def _right_panel(self, parent):
        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure((0, 1, 2, 3), weight=1, uniform="tile")
        right.rowconfigure(2, weight=1)

        # Stat tiles
        self._tile_status   = StatTile(right, "STATUS",   accent=RED)
        self._tile_attempts = StatTile(right, "ATTEMPTS", accent=AMBER)
        self._tile_time     = StatTile(right, "TIME",     accent=CYAN)
        self._tile_speed    = StatTile(right, "SPEED",    accent=GREEN)

        for i, tile in enumerate([self._tile_status, self._tile_attempts,
                                   self._tile_time, self._tile_speed]):
            tile.grid(row=0, column=i,
                      sticky="ew",
                      padx=(0 if i == 0 else 8, 0))

        # Progress bar
        self._progress = ctk.CTkProgressBar(right,
                                              fg_color=BORDER,
                                              progress_color=RED,
                                              height=4,
                                              corner_radius=2)
        self._progress.set(0)
        self._progress.grid(row=1, column=0, columnspan=4,
                             sticky="ew", pady=(10, 8))

        # Result banner
        self._banner = ResultBanner(right)
        self._banner.grid(row=2, column=0, columnspan=4,
                           sticky="ew", pady=(0, 8))

        # Log
        self._log = LogBox(right)
        self._log.grid(row=3, column=0, columnspan=4, sticky="nsew")
        right.rowconfigure(3, weight=1)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _go_home(self):
        script = os.path.join(BASE, "home.py")
        if os.path.isfile(script):
            subprocess.Popen([sys.executable, script])
        self.destroy()

    def _generate_hash(self):
        pw = self._gen_entry.get().strip()
        if not pw:
            self._log.append("[WARN] Enter a password to hash.")
            return
        algo = self._algo_var.get()
        ok, msg = algorithm_available(algo)
        if not ok:
            self._log.append(f"[ERROR] {msg}")
            return
        try:
            h = hash_password(pw, algo)
            self._hash_entry.delete(0, "end")
            self._hash_entry.insert(0, h)
            self._log.append(f"[GEN] {algo.upper()}({pw!r}) = {h}")
        except Exception as e:
            self._log.append(f"[ERROR] {e}")

    def _browse_wordlist(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Select wordlist",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self._wordlist_entry.delete(0, "end")
            self._wordlist_entry.insert(0, path)

    def _update_attack_options(self):
        mode = self._attack_var.get()
        if mode == "Brute Force":
            self._wordlist_frame.pack_forget()
            self._brute_frame.pack(fill="x")
        else:
            self._brute_frame.pack_forget()
            self._wordlist_frame.pack(fill="x")

    def _update_maxlen_label(self, val=None):
        self._maxlen_label.configure(text=str(int(self._maxlen_var.get())))

    def _clear(self):
        self._log.clear()
        self._banner.set("AWAITING ATTACK", TEXT_DIM)
        for tile in [self._tile_status, self._tile_attempts,
                     self._tile_time, self._tile_speed]:
            tile.set("—")
        self._progress.set(0)

    # ── Attack orchestration ──────────────────────────────────────────────────

    def _start_attack(self):
        if self._running:
            return
        hash_val = self._hash_entry.get().strip()
        if not hash_val:
            self._log.append("[ERROR] Paste a hash value first.")
            return

        algo = self._algo_var.get()
        ok, msg = algorithm_available(algo)
        if not ok:
            self._log.append(f"[ERROR] Algorithm unavailable — {msg}")
            return

        mode = self._attack_var.get()

        if mode in ("Dictionary", "Hybrid"):
            wl = self._wordlist_entry.get().strip()
            if not os.path.isfile(wl):
                self._log.append(f"[ERROR] Wordlist not found: {wl}")
                return
        else:
            wl = None

        self._running = True
        self._stop_event.clear()
        self._launch_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal", text_color=TEXT)
        self._progress.configure(progress_color=RED)
        self._progress.set(0)
        self._banner.set("● ATTACK IN PROGRESS …", AMBER)
        self._tile_status.set("RUNNING")

        self._log.append(f"\n[START] Mode: {mode} | Algorithm: {algo.upper()}")
        if wl:
            self._log.append(f"[INFO]  Wordlist: {wl}")

        def worker():
            try:
                def cb(attempts, total, current):
                    self.after(0, lambda: self._on_progress(attempts, current))

                if mode == "Dictionary":
                    result = run_dictionary_attack(hash_val, algo, wl,
                                                    progress_callback=cb,
                                                    stop_event=self._stop_event)
                elif mode == "Brute Force":
                    maxlen = int(self._maxlen_var.get())
                    result = run_brute_force_attack(hash_val, algo, maxlen,
                                                     progress_callback=cb,
                                                     stop_event=self._stop_event)
                else:
                    result = run_hybrid_attack(hash_val, algo, wl,
                                                progress_callback=cb,
                                                stop_event=self._stop_event)
                self.after(0, lambda: self._on_complete(result))
            except Exception as e:
                self.after(0, lambda: self._on_error(str(e)))

        self._attack_thread = threading.Thread(target=worker, daemon=True)
        self._attack_thread.start()

        # Animate progress bar while running
        self._animate_progress()

    def _animate_progress(self):
        if not self._running:
            return
        cur = self._progress.get()
        next_val = (cur + 0.005) % 1.0
        self._progress.set(next_val)
        self.after(30, self._animate_progress)

    def _on_progress(self, attempts, current):
        self._tile_attempts.set(f"{attempts:,}")
        self._log.append(f"[TRY]  #{attempts:,}  → {current!r}")

    def _on_complete(self, result):
        self._running = False
        self._launch_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled", text_color=TEXT_MID)
        self._progress.set(1.0 if result.success else 0.0)

        summ = result.summary()
        self._tile_attempts.set(f"{summ['attempts']:,}")
        self._tile_time.set(summ["time_taken"])
        self._tile_speed.set(summ["speed"])

        if result.success:
            self._tile_status.set("CRACKED")
            self._banner.set(f"✓  PASSWORD FOUND:  {result.cracked_password}", GREEN)
            self._progress.configure(progress_color=GREEN)
            self._log.append(f"\n[SUCCESS] Password cracked: {result.cracked_password!r}")
            self._log.append(f"[STATS]   Attempts: {summ['attempts']:,} | Time: {summ['time_taken']} | Speed: {summ['speed']}")
        else:
            reason = result.error or "Password not found."
            self._tile_status.set("FAILED")
            self._banner.set(f"✗  {reason}", RED)
            self._progress.configure(progress_color=BORDER)
            self._log.append(f"\n[FAILED] {reason}")
            self._log.append(f"[STATS]  Attempts: {summ['attempts']:,} | Time: {summ['time_taken']}")

    def _on_error(self, msg):
        self._running = False
        self._launch_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled", text_color=TEXT_MID)
        self._banner.set(f"[ERROR] {msg}", RED)
        self._tile_status.set("ERROR")
        self._log.append(f"\n[ERROR] {msg}")

    def _stop_attack(self):
        if self._running:
            self._stop_event.set()
            self._log.append("[STOP] Stopping…")
            self._banner.set("■  STOPPED BY USER", AMBER)
            self._running = False
            self._launch_btn.configure(state="normal")
            self._stop_btn.configure(state="disabled", text_color=TEXT_MID)


if __name__ == "__main__":
    PasswordAttackSimulatorGUI().mainloop()