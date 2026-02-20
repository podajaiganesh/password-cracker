import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import time

# Ensure parent directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from attacks.dictionary_attack import run_dictionary_attack
from attacks.brute_force import run_brute_force_attack
from attacks.hybrid_attack import run_hybrid_attack


DARK_BG = "#1a1a2e"
PANEL_BG = "#16213e"
CARD_BG = "#0f3460"
ACCENT = "#e94560"
ACCENT2 = "#533483"
SUCCESS_COLOR = "#00d68f"
FAIL_COLOR = "#ff3860"
TEXT_COLOR = "#e0e0e0"
MUTED = "#8892a4"
FONT_MONO = ("Courier New", 10)
FONT_BOLD = ("Helvetica", 10, "bold")
FONT_TITLE = ("Helvetica", 18, "bold")
FONT_LABEL = ("Helvetica", 9)


class PasswordAttackSimulatorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Password Attack Simulator")
        self.root.configure(bg=DARK_BG)
        self.root.geometry("960x720")
        self.root.minsize(800, 600)

        self._stop_event = threading.Event()
        self._attack_thread = None
        self._running = False
        self._start_time = None

        self._build_ui()

    # ─── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        main_frame = tk.Frame(self.root, bg=DARK_BG)
        main_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self._build_left_panel(main_frame)
        self._build_right_panel(main_frame)

    def _build_header(self):
        header = tk.Frame(self.root, bg=CARD_BG, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="🔐 Password Attack Simulator",
                 font=FONT_TITLE, bg=CARD_BG, fg=ACCENT).pack(side="left", padx=20, pady=12)
        tk.Label(header, text="Educational / Cybersecurity Awareness Tool",
                 font=FONT_LABEL, bg=CARD_BG, fg=MUTED).pack(side="left", pady=12)

    def _card(self, parent, title):
        outer = tk.Frame(parent, bg=PANEL_BG, bd=0)
        tk.Label(outer, text=title, font=FONT_BOLD, bg=PANEL_BG, fg=ACCENT).pack(
            anchor="w", padx=12, pady=(10, 2))
        sep = tk.Frame(outer, bg=ACCENT, height=1)
        sep.pack(fill="x", padx=12, pady=(0, 8))
        inner = tk.Frame(outer, bg=PANEL_BG)
        inner.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        return outer, inner

    def _label_entry(self, parent, label_text, default="", width=38):
        tk.Label(parent, text=label_text, font=FONT_LABEL, bg=PANEL_BG, fg=MUTED).pack(anchor="w")
        var = tk.StringVar(value=default)
        entry = tk.Entry(parent, textvariable=var, width=width,
                         bg=CARD_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                         relief="flat", bd=4, font=FONT_MONO)
        entry.pack(fill="x", pady=(2, 8))
        return var, entry

    def _label_combo(self, parent, label_text, values, default=0):
        tk.Label(parent, text=label_text, font=FONT_LABEL, bg=PANEL_BG, fg=MUTED).pack(anchor="w")
        var = tk.StringVar()
        combo = ttk.Combobox(parent, textvariable=var, values=values,
                              state="readonly", font=FONT_MONO)
        combo.current(default)
        combo.pack(fill="x", pady=(2, 8))
        return var

    def _build_left_panel(self, parent):
        frame = tk.Frame(parent, bg=DARK_BG)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=8)
        frame.rowconfigure(99, weight=1)

        # Hash input
        card, inner = self._card(frame, "🎯  Target Hash")
        card.pack(fill="x", pady=(0, 8))
        self.hash_var, _ = self._label_entry(inner, "Hash Value")

        # Algorithm
        card2, inner2 = self._card(frame, "⚙️  Configuration")
        card2.pack(fill="x", pady=(0, 8))
        self.algo_var = self._label_combo(inner2, "Hash Algorithm",
                                          ["md5", "sha256", "bcrypt"])
        self.attack_var = self._label_combo(inner2, "Attack Type",
                                            ["dictionary", "brute_force", "hybrid"])
        self.attack_var.trace_add("write", self._on_attack_change)

        # Wordlist
        card3, inner3 = self._card(frame, "📂  Wordlist")
        card3.pack(fill="x", pady=(0, 8))
        self.wordlist_card = card3

        wl_row = tk.Frame(inner3, bg=PANEL_BG)
        wl_row.pack(fill="x")
        self.wordlist_var = tk.StringVar(value=self._default_wordlist())
        self.wordlist_entry = tk.Entry(wl_row, textvariable=self.wordlist_var,
                                       bg=CARD_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                                       relief="flat", bd=4, font=FONT_MONO)
        self.wordlist_entry.pack(side="left", fill="x", expand=True, pady=(2, 8))
        tk.Button(wl_row, text="Browse", command=self._browse_wordlist,
                  bg=ACCENT2, fg=TEXT_COLOR, relief="flat", bd=0,
                  padx=10, font=FONT_BOLD, cursor="hand2").pack(side="right", padx=(6, 0), pady=(2, 8))

        # Max length
        card4, inner4 = self._card(frame, "🔢  Brute Force Options")
        card4.pack(fill="x", pady=(0, 8))
        self.brute_card = card4
        self.max_len_var = self._label_combo(inner4, "Max Password Length",
                                      ["1", "2", "3", "4", "5", "6"], default=3)

        # Buttons
        btn_frame = tk.Frame(frame, bg=DARK_BG)
        btn_frame.pack(fill="x", pady=4)

        self.start_btn = tk.Button(btn_frame, text="▶  Start Attack",
                                   command=self._start_attack,
                                   bg=ACCENT, fg="white", relief="flat", bd=0,
                                   padx=16, pady=10, font=FONT_BOLD, cursor="hand2")
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.stop_btn = tk.Button(btn_frame, text="⏹  Stop",
                                  command=self._stop_attack,
                                  bg=MUTED, fg="white", relief="flat", bd=0,
                                  padx=16, pady=10, font=FONT_BOLD, cursor="hand2",
                                  state="disabled")
        self.stop_btn.pack(side="right")

        # Hash generator helper
        card5, inner5 = self._card(frame, "🔧  Hash Generator (Testing)")
        card5.pack(fill="x", pady=(8, 0))
        self.gen_pass_var, _ = self._label_entry(inner5, "Password to hash", width=30)
        tk.Button(inner5, text="Generate Hash → Copy to Input",
                  command=self._generate_hash,
                  bg=ACCENT2, fg=TEXT_COLOR, relief="flat", bd=0,
                  padx=10, pady=6, font=FONT_BOLD, cursor="hand2").pack(anchor="w")
        self.gen_result_var = tk.StringVar()
        tk.Label(inner5, textvariable=self.gen_result_var, font=FONT_MONO,
                 bg=PANEL_BG, fg=SUCCESS_COLOR, wraplength=340).pack(anchor="w", pady=(4, 0))

        self._on_attack_change()

    def _build_right_panel(self, parent):
        frame = tk.Frame(parent, bg=DARK_BG)
        frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=8)
        frame.rowconfigure(1, weight=1)

        # Stats
        stats_card, stats_inner = self._card(frame, "📊  Live Statistics")
        stats_card.pack(fill="x", pady=(0, 8))
        stats_inner.columnconfigure((0, 1, 2, 3), weight=1)

        self.stat_status = self._stat_box(stats_inner, "Status", "IDLE", 0)
        self.stat_attempts = self._stat_box(stats_inner, "Attempts", "0", 1)
        self.stat_speed = self._stat_box(stats_inner, "Speed", "—", 2)
        self.stat_time = self._stat_box(stats_inner, "Time", "0.0s", 3)

        # Progress
        prog_card, prog_inner = self._card(frame, "⏳  Progress")
        prog_card.pack(fill="x", pady=(0, 8))
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(prog_inner, variable=self.progress_var,
                                             mode="indeterminate", length=400)
        self.progress_bar.pack(fill="x", pady=(0, 4))
        self.progress_label = tk.Label(prog_inner, text="Ready", font=FONT_LABEL,
                                       bg=PANEL_BG, fg=MUTED)
        self.progress_label.pack(anchor="w")

        # Output log
        log_card, log_inner = self._card(frame, "📋  Attack Log")
        log_card.pack(fill="both", expand=True)
        log_inner.rowconfigure(0, weight=1)
        log_inner.columnconfigure(0, weight=1)

        self.output_box = scrolledtext.ScrolledText(
            log_inner, bg=DARK_BG, fg=TEXT_COLOR,
            font=FONT_MONO, relief="flat", bd=0,
            wrap="word", state="disabled", height=14
        )
        self.output_box.pack(fill="both", expand=True)
        self.output_box.tag_config("success", foreground=SUCCESS_COLOR)
        self.output_box.tag_config("fail", foreground=FAIL_COLOR)
        self.output_box.tag_config("info", foreground="#61dafb")
        self.output_box.tag_config("muted", foreground=MUTED)

        # Clear button
        tk.Button(frame, text="Clear Log", command=self._clear_log,
                  bg=PANEL_BG, fg=MUTED, relief="flat", bd=0,
                  padx=8, pady=4, font=FONT_LABEL, cursor="hand2").pack(anchor="e", pady=(4, 0))

    def _stat_box(self, parent, label, value, col):
        f = tk.Frame(parent, bg=CARD_BG, padx=8, pady=6)
        f.grid(row=0, column=col, padx=4, pady=2, sticky="ew")
        tk.Label(f, text=label, font=FONT_LABEL, bg=CARD_BG, fg=MUTED).pack()
        var = tk.StringVar(value=value)
        tk.Label(f, textvariable=var, font=("Helvetica", 11, "bold"),
                 bg=CARD_BG, fg=TEXT_COLOR).pack()
        return var

    # ─── Logic ──────────────────────────────────────────────────────────────

    def _default_wordlist(self):
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, "wordlists", "common.txt")

    def _on_attack_change(self, *_):
        attack = self.attack_var.get()
        is_brute = attack == "brute_force"
        is_dict_or_hybrid = attack in ("dictionary", "hybrid")

        self.wordlist_card.pack_configure() if is_dict_or_hybrid else None
        if is_brute:
            self.wordlist_card.pack_forget()
            self.brute_card.pack(fill="x", pady=(0, 8))
        else:
            self.brute_card.pack_forget()
            self.wordlist_card.pack(fill="x", pady=(0, 8))

    def _browse_wordlist(self):
        path = filedialog.askopenfilename(
            title="Select Wordlist",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            self.wordlist_var.set(path)

    def _log(self, msg, tag=""):
        self.output_box.configure(state="normal")
        self.output_box.insert("end", msg + "\n", tag)
        self.output_box.see("end")
        self.output_box.configure(state="disabled")

    def _clear_log(self):
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.configure(state="disabled")

    def _generate_hash(self):
        from utils.hash_utils import hash_password
        pw = self.gen_pass_var.get().strip()
        if not pw:
            messagebox.showwarning("Input Required", "Enter a password to hash.")
            return
        algo = self.algo_var.get()
        try:
            h = hash_password(pw, algo)
            self.gen_result_var.set(h)
            self.hash_var.set(h)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _validate_inputs(self):
        h = self.hash_var.get().strip()
        if not h:
            messagebox.showwarning("Missing Input", "Please enter a hash value.")
            return False
        attack = self.attack_var.get()
        if attack in ("dictionary", "hybrid"):
            wl = self.wordlist_var.get().strip()
            if not os.path.isfile(wl):
                messagebox.showerror("File Not Found", f"Wordlist not found:\n{wl}")
                return False
        return True

    def _start_attack(self):
        if self._running:
            return
        if not self._validate_inputs():
            return

        self._stop_event.clear()
        self._running = True
        self._start_time = time.time()
        self.start_btn.configure(state="disabled", bg=MUTED)
        self.stop_btn.configure(state="normal", bg=ACCENT)
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start(12)
        self.stat_status.set("RUNNING")
        self.stat_attempts.set("0")
        self.stat_speed.set("—")
        self.stat_time.set("0.0s")

        self._clear_log()
        self._log("=" * 54, "muted")
        self._log("  PASSWORD ATTACK SIMULATOR", "info")
        self._log("=" * 54, "muted")
        self._log(f"  Algorithm : {self.algo_var.get().upper()}", "info")
        self._log(f"  Attack    : {self.attack_var.get().replace('_', ' ').title()}", "info")
        self._log(f"  Hash      : {self.hash_var.get()[:48]}...", "muted")
        self._log("=" * 54, "muted")
        self._log("  Starting attack...\n", "info")

        self._attack_thread = threading.Thread(target=self._run_attack, daemon=True)
        self._attack_thread.start()
        self._poll_live_stats()

    def _stop_attack(self):
        self._stop_event.set()
        self._log("\n[!] Stop requested by user.", "fail")

    def _poll_live_stats(self):
        if self._running:
            elapsed = time.time() - self._start_time if self._start_time else 0
            self.stat_time.set(f"{elapsed:.1f}s")
            self.root.after(200, self._poll_live_stats)

    def _run_attack(self):
        hash_value = self.hash_var.get().strip()
        algorithm = self.algo_var.get()
        attack = self.attack_var.get()
        wordlist = self.wordlist_var.get().strip()
        max_len = int(self.max_len_var.get())

        attempts_tracker = [0]

        def progress_cb(current, total, current_word):
            attempts_tracker[0] = current
            elapsed = time.time() - self._start_time if self._start_time else 1
            speed = current / elapsed if elapsed > 0 else 0
            self.root.after(0, lambda: self.stat_attempts.set(f"{current:,}"))
            self.root.after(0, lambda: self.stat_speed.set(f"{speed:,.0f}/s"))
            if total > 0:
                pct = (current / total) * 100
                self.root.after(0, lambda: self.progress_label.configure(
                    text=f"Trying: {current_word!r}  ({pct:.1f}%)"))
            else:
                self.root.after(0, lambda: self.progress_label.configure(
                    text=f"Trying: {current_word!r}"))

        try:
            if attack == "dictionary":
                result = run_dictionary_attack(hash_value, algorithm, wordlist,
                                               progress_cb, self._stop_event)
            elif attack == "brute_force":
                result = run_brute_force_attack(hash_value, algorithm, max_len,
                                                progress_cb, self._stop_event)
            else:
                result = run_hybrid_attack(hash_value, algorithm, wordlist,
                                           progress_cb, self._stop_event)
        except Exception as e:
            self.root.after(0, lambda: self._finish_attack_error(str(e)))
            return

        self.root.after(0, lambda: self._finish_attack(result))

    def _finish_attack(self, result):
        self._running = False
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_var.set(100 if result.success else 0)
        self.start_btn.configure(state="normal", bg=ACCENT)
        self.stop_btn.configure(state="disabled", bg=MUTED)

        s = result.summary()
        self.stat_attempts.set(f"{s['attempts']:,}")
        elapsed = result.elapsed_time
        self.stat_time.set(f"{elapsed:.3f}s")
        self.stat_speed.set(s["speed"])

        if result.error and not result.success:
            self.stat_status.set("ERROR")
            self._log(f"\n[ERROR] {result.error}", "fail")
            self.progress_label.configure(text="Error occurred.")
            return

        self._log("\n" + "=" * 54, "muted")
        if result.success:
            self.stat_status.set("SUCCESS ✓")
            self._log("  ✅  CRACK SUCCESSFUL!", "success")
            self._log(f"  Password  : {result.cracked_password}", "success")
        else:
            self.stat_status.set("FAILED ✗")
            self._log("  ❌  CRACK FAILED — password not found.", "fail")
            self._log("  Try a larger wordlist or longer max length.", "muted")

        self._log("=" * 54, "muted")
        self._log(f"  Attempts  : {s['attempts']:,}", "info")
        self._log(f"  Time      : {s['time_taken']}", "info")
        self._log(f"  Speed     : {s['speed']}", "info")
        self._log("=" * 54, "muted")
        self.progress_label.configure(text="Done.")

    def _finish_attack_error(self, msg):
        self._running = False
        self.progress_bar.stop()
        self.start_btn.configure(state="normal", bg=ACCENT)
        self.stop_btn.configure(state="disabled", bg=MUTED)
        self.stat_status.set("ERROR")
        self._log(f"\n[EXCEPTION] {msg}", "fail")
        self.progress_label.configure(text="Error.")


def apply_ttk_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TCombobox",
                    fieldbackground=CARD_BG,
                    background=CARD_BG,
                    foreground=TEXT_COLOR,
                    selectbackground=ACCENT2,
                    selectforeground=TEXT_COLOR,
                    bordercolor=ACCENT2,
                    lightcolor=CARD_BG,
                    darkcolor=CARD_BG,
                    arrowcolor=TEXT_COLOR)
    style.configure("Horizontal.TProgressbar",
                    troughcolor=CARD_BG,
                    background=ACCENT,
                    bordercolor=CARD_BG,
                    lightcolor=ACCENT,
                    darkcolor=ACCENT)