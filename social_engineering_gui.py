"""
social_engineering_gui.py  —  Social Engineering Simulator Module
CustomTkinter UI.  Run standalone:  python3 social_engineering_gui.py
Requires:  pip install customtkinter
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading, os, sys, time, datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from social_engineering.phishing_simulator import (
    generate_phishing_email, get_scenarios, get_urgency_levels,
)
from social_engineering.email_analyzer import analyze_email
from social_engineering.dataset_loader import (
    get_random_phishing, get_random_legitimate, get_dataset_stats,
)

# ── Palette (matches suite) ───────────────────────────────────────────────────
BG       = "#0a0a0a"
SURFACE  = "#111111"
CARD     = "#141414"
CARD2    = "#181818"
BORDER   = "#222222"
BORDER2  = "#2a2a2a"
INPUT_BG = "#0f0f0f"
AMBER    = "#f4a261"
AMBER_D  = "#7a3d10"
GREEN    = "#2dc653"
RED      = "#e63946"
CYAN     = "#00b4d8"
TEXT     = "#f0f0f0"
TEXT_MID = "#777777"
TEXT_DIM = "#3a3a3a"

SCORE_SAFE       = GREEN
SCORE_SUSPICIOUS = AMBER
SCORE_PHISHING   = RED

LABEL_COLORS = {"SAFE": GREEN, "SUSPICIOUS": AMBER, "PHISHING": RED}


def fmono(size=11, weight="normal"):
    return ctk.CTkFont("Courier New", size, weight)

def flabel():
    return ctk.CTkFont("Courier New", 9)


# ── Shared widgets ────────────────────────────────────────────────────────────

class SectionHeader(ctk.CTkFrame):
    def __init__(self, parent, title: str, **kw):
        super().__init__(parent, fg_color="transparent", **kw)
        ctk.CTkLabel(self, text=title, font=flabel(),
                     text_color=TEXT_MID).pack(side="left")
        ctk.CTkFrame(self, fg_color=BORDER2, height=1,
                     corner_radius=0).pack(side="left", fill="x",
                                           expand=True, padx=(10, 0), pady=5)


class LogBox(ctk.CTkTextbox):
    TAGS = {"ok": GREEN, "err": RED, "warn": AMBER, "cyan": CYAN,
            "dim": TEXT_MID, "mid": "#aaaaaa", "bold_ok": GREEN,
            "bold_err": RED, "bold_warn": AMBER}

    def __init__(self, parent, **kw):
        super().__init__(parent, fg_color=INPUT_BG, text_color=TEXT,
                         font=fmono(10), corner_radius=6,
                         border_width=1, border_color=BORDER,
                         wrap="word", state="disabled", **kw)

    def write(self, msg: str, tag: str = "", newline: bool = True):
        self.configure(state="normal")
        color = self.TAGS.get(tag, TEXT)
        end_char = "\n" if newline else ""
        start = self._textbox.index("end-1c")
        self._textbox.insert("end", msg + end_char)
        if tag:
            end = self._textbox.index("end-1c")
            self._textbox.tag_add(tag, start, end)
            self._textbox.tag_config(tag, foreground=color,
                                     font=("Courier New", 10,
                                           "bold" if "bold" in tag else "normal"))
        self._textbox.see("end")
        self.configure(state="disabled")

    def clear(self):
        self.configure(state="normal")
        self.delete("0.0", "end")
        self.configure(state="disabled")


class ScoreMeter(ctk.CTkFrame):
    """Visual risk score bar + label."""
    def __init__(self, parent, **kw):
        super().__init__(parent, fg_color=CARD, corner_radius=6,
                         border_width=1, border_color=BORDER, **kw)
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=14)

        # Top row: RISK SCORE label + numeric value
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text="RISK SCORE", font=flabel(),
                     text_color=TEXT_MID).pack(side="left")
        self._score_var = ctk.StringVar(value="—")
        self._score_lbl = ctk.CTkLabel(top, textvariable=self._score_var,
                                        font=fmono(18, "bold"),
                                        text_color=TEXT_MID)
        self._score_lbl.pack(side="right")

        ctk.CTkFrame(inner, fg_color="transparent", height=6).pack()

        # Progress bar
        self._bar = ctk.CTkProgressBar(inner, fg_color=BORDER2,
                                        progress_color=TEXT_MID,
                                        corner_radius=2, height=6)
        self._bar.set(0)
        self._bar.pack(fill="x")

        ctk.CTkFrame(inner, fg_color="transparent", height=8).pack()

        # Label pill
        self._label_var = ctk.StringVar(value="AWAITING INPUT")
        self._label_frame = ctk.CTkFrame(inner, fg_color=BORDER,
                                          corner_radius=4)
        self._label_frame.pack(anchor="w")
        self._label_lbl = ctk.CTkLabel(self._label_frame,
                                        textvariable=self._label_var,
                                        font=fmono(11, "bold"),
                                        text_color=TEXT_MID)
        self._label_lbl.pack(padx=12, pady=5)

    def update(self, score: int, label: str):
        color = LABEL_COLORS.get(label, TEXT_MID)
        self._score_var.set(f"{score}/100")
        self._score_lbl.configure(text_color=color)
        self._bar.set(score / 100)
        self._bar.configure(progress_color=color)
        self._label_var.set(f"  {label}  ")
        self._label_frame.configure(fg_color=color)
        self._label_lbl.configure(text_color=BG, fg_color=color)

    def reset(self):
        self._score_var.set("—")
        self._score_lbl.configure(text_color=TEXT_MID)
        self._bar.set(0)
        self._bar.configure(progress_color=TEXT_MID)
        self._label_var.set("AWAITING INPUT")
        self._label_frame.configure(fg_color=BORDER)
        self._label_lbl.configure(text_color=TEXT_MID, fg_color=BORDER)


# ── Main window ───────────────────────────────────────────────────────────────

class SocialEngineeringGUI(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Social Engineering Simulator")
        self.geometry("1200x800")
        self.minsize(1000, 680)
        self.configure(fg_color=BG)

        self._build()
        self._load_stats()

    # ── Skeleton ──────────────────────────────────────────────────────────────

    def _build(self):
        self._topbar()
        # Tab view
        self._tabs = ctk.CTkTabview(self,
                                     fg_color=BG,
                                     segmented_button_fg_color=SURFACE,
                                     segmented_button_selected_color=AMBER,
                                     segmented_button_selected_hover_color="#c07830",
                                     segmented_button_unselected_color=SURFACE,
                                     segmented_button_unselected_hover_color=CARD,
                                     text_color=TEXT,
                                     text_color_disabled=TEXT_MID,
                                     border_color=BORDER,
                                     border_width=1,
                                     corner_radius=6)
        self._tabs.pack(fill="both", expand=True, padx=20, pady=(14, 0))

        self._tabs.add("⚠   Phishing Generator")
        self._tabs.add("🔍  Email Analyser")
        self._tabs.add("📊  Dataset Explorer")

        self._build_generator(self._tabs.tab("⚠   Phishing Generator"))
        self._build_analyser(self._tabs.tab("🔍  Email Analyser"))
        self._build_dataset(self._tabs.tab("📊  Dataset Explorer"))

        self._statusbar()

    # ── Top bar ───────────────────────────────────────────────────────────────

    def _topbar(self):
        bar = ctk.CTkFrame(self, fg_color=SURFACE, height=50, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        ctk.CTkButton(bar, text="← HOME", font=flabel(),
                      fg_color="transparent", hover_color=BORDER2,
                      text_color=TEXT_MID, width=80, height=32,
                      corner_radius=4, command=self._go_home).pack(
            side="left", padx=(14, 0), pady=9)

        ctk.CTkFrame(bar, fg_color=BORDER, width=1, height=28,
                     corner_radius=0).pack(side="left", pady=11, padx=6)

        ctk.CTkLabel(bar, text="SOCIAL ENGINEERING SIMULATOR",
                     font=fmono(12, "bold"), text_color=AMBER).pack(
            side="left", padx=8)

        ctk.CTkLabel(bar, text="⚠  SIMULATION ONLY — No real attacks performed",
                     font=flabel(), text_color=TEXT_MID).pack(
            side="right", padx=20)

        ctk.CTkFrame(self, fg_color=BORDER, height=1,
                     corner_radius=0).pack(fill="x")

    # ── TAB 1: Phishing Generator ─────────────────────────────────────────────

    def _build_generator(self, parent):
        parent.configure(fg_color=BG)

        # Two columns
        parent.grid_columnconfigure(0, weight=0, minsize=320)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        # ── Left controls ─────────────────────────────────────────────────────
        left = ctk.CTkScrollableFrame(parent, fg_color=BG, corner_radius=0,
                                       border_width=0,
                                       scrollbar_button_color=BORDER2,
                                       scrollbar_button_hover_color=BORDER,
                                       width=320)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 0))
        P = {"padx": 20}

        ctk.CTkFrame(left, fg_color="transparent", height=16).pack()
        SectionHeader(left, "GENERATE PHISHING EMAIL").pack(fill="x", **P)
        ctk.CTkFrame(left, fg_color="transparent", height=10).pack()

        # Target name
        ctk.CTkLabel(left, text="TARGET NAME", font=flabel(),
                     text_color=TEXT_MID).pack(anchor="w", **P)
        self._gen_name = ctk.StringVar(value="Employee")
        ctk.CTkEntry(left, textvariable=self._gen_name,
                     fg_color=INPUT_BG, border_color=BORDER2, border_width=1,
                     text_color=TEXT, font=fmono(10), corner_radius=5,
                     height=36).pack(fill="x", **P, pady=(4, 12))

        # Scenario
        ctk.CTkLabel(left, text="SCENARIO", font=flabel(),
                     text_color=TEXT_MID).pack(anchor="w", **P)
        self._gen_scenario = ctk.StringVar(value=get_scenarios()[0])
        ctk.CTkOptionMenu(left, variable=self._gen_scenario,
                          values=get_scenarios(),
                          fg_color=CARD, button_color=BORDER2,
                          button_hover_color=BORDER, dropdown_fg_color=CARD2,
                          dropdown_hover_color=BORDER, text_color=TEXT,
                          font=fmono(10), corner_radius=5,
                          height=36).pack(fill="x", **P, pady=(4, 12))

        # Urgency
        ctk.CTkLabel(left, text="URGENCY LEVEL", font=flabel(),
                     text_color=TEXT_MID).pack(anchor="w", **P)
        self._gen_urgency = ctk.StringVar(value="High")
        ctk.CTkOptionMenu(left, variable=self._gen_urgency,
                          values=get_urgency_levels(),
                          fg_color=CARD, button_color=BORDER2,
                          button_hover_color=BORDER, dropdown_fg_color=CARD2,
                          dropdown_hover_color=BORDER, text_color=TEXT,
                          font=fmono(10), corner_radius=5,
                          height=36).pack(fill="x", **P, pady=(4, 16))

        ctk.CTkFrame(left, fg_color=BORDER, height=1,
                     corner_radius=0).pack(fill="x", **P)
        ctk.CTkFrame(left, fg_color="transparent", height=12).pack()

        # Generate button
        ctk.CTkButton(left, text="⚠   GENERATE PHISHING EMAIL",
                      font=fmono(11, "bold"), fg_color=AMBER,
                      hover_color="#c07830", text_color=BG,
                      height=42, corner_radius=5,
                      command=self._do_generate).pack(fill="x", **P)

        ctk.CTkFrame(left, fg_color="transparent", height=10).pack()

        # Send to analyser
        ctk.CTkButton(left, text="→  SEND TO ANALYSER",
                      font=flabel(), fg_color="transparent",
                      hover_color=BORDER2, text_color=CYAN,
                      border_color=BORDER2, border_width=1,
                      height=32, corner_radius=5,
                      command=self._send_to_analyser).pack(fill="x", **P)

        ctk.CTkFrame(left, fg_color="transparent", height=10).pack()

        # Export
        ctk.CTkButton(left, text="💾  EXPORT EMAIL",
                      font=flabel(), fg_color="transparent",
                      hover_color=BORDER2, text_color=TEXT_MID,
                      border_color=BORDER2, border_width=1,
                      height=32, corner_radius=5,
                      command=self._export_email).pack(fill="x", **P)

        ctk.CTkFrame(left, fg_color="transparent", height=20).pack()
        SectionHeader(left, "PHISHING TRAITS DETECTED").pack(fill="x", **P)
        ctk.CTkFrame(left, fg_color="transparent", height=8).pack()

        self._traits_box = ctk.CTkTextbox(left, fg_color=INPUT_BG,
                                           text_color=AMBER,
                                           font=fmono(9),
                                           corner_radius=5,
                                           border_width=1, border_color=BORDER,
                                           height=140, state="disabled")
        self._traits_box.pack(fill="x", **P)
        ctk.CTkFrame(left, fg_color="transparent", height=20).pack()

        # Right border
        ctk.CTkFrame(parent, fg_color=BORDER, width=1,
                     corner_radius=0).grid(row=0, column=0,
                                           sticky="nse", padx=(319, 0))

        # ── Right: output ──────────────────────────────────────────────────────
        right = ctk.CTkFrame(parent, fg_color=BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(20, 0))
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(right, fg_color="transparent", height=16).grid(
            row=0, column=0)

        # Subject display
        subj_row = ctk.CTkFrame(right, fg_color="transparent")
        subj_row.grid(row=1, column=0, sticky="ew")
        subj_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(subj_row, text="SUBJECT:", font=flabel(),
                     text_color=TEXT_MID).grid(row=0, column=0, padx=(0, 8))
        self._subj_var = ctk.StringVar(value="—")
        ctk.CTkLabel(subj_row, textvariable=self._subj_var,
                     font=fmono(10, "bold"), text_color=AMBER,
                     anchor="w").grid(row=0, column=1, sticky="ew")

        ctk.CTkFrame(right, fg_color="transparent", height=8).grid(row=2, column=0)

        # Email body output
        SectionHeader(right, "EMAIL BODY (SIMULATION)").grid(
            row=3, column=0, sticky="ew")
        self._gen_output = LogBox(right)
        self._gen_output.grid(row=4, column=0, sticky="nsew",
                               pady=(8, 0), padx=(0, 4))
        right.grid_rowconfigure(4, weight=1)

        self._last_generated = {}

    # ── TAB 2: Email Analyser ─────────────────────────────────────────────────

    def _build_analyser(self, parent):
        parent.configure(fg_color=BG)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=0, minsize=340)
        parent.grid_rowconfigure(0, weight=1)

        # ── Left: input ────────────────────────────────────────────────────────
        left = ctk.CTkFrame(parent, fg_color=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        left.grid_rowconfigure(3, weight=1)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(left, fg_color="transparent", height=16).grid(row=0, column=0)

        # Subject input
        subj_frame = ctk.CTkFrame(left, fg_color="transparent")
        subj_frame.grid(row=1, column=0, sticky="ew")
        ctk.CTkLabel(subj_frame, text="SUBJECT (optional)", font=flabel(),
                     text_color=TEXT_MID).pack(anchor="w")
        self._ana_subject = ctk.StringVar()
        ctk.CTkEntry(subj_frame, textvariable=self._ana_subject,
                     fg_color=INPUT_BG, border_color=BORDER2, border_width=1,
                     text_color=TEXT, font=fmono(10), corner_radius=5,
                     height=34,
                     placeholder_text="Optional: paste subject line…",
                     placeholder_text_color=TEXT_DIM).pack(
            fill="x", pady=(4, 0))

        ctk.CTkFrame(left, fg_color="transparent", height=10).grid(row=2, column=0)

        # Body input
        body_frame = ctk.CTkFrame(left, fg_color="transparent")
        body_frame.grid(row=3, column=0, sticky="nsew")
        body_frame.grid_rowconfigure(1, weight=1)
        body_frame.grid_columnconfigure(0, weight=1)

        hdr_row = ctk.CTkFrame(body_frame, fg_color="transparent")
        hdr_row.grid(row=0, column=0, sticky="ew")
        SectionHeader(hdr_row, "EMAIL BODY TO ANALYSE").pack(side="left",
                                                              fill="x", expand=True)
        ctk.CTkButton(hdr_row, text="CLEAR", font=flabel(),
                      fg_color="transparent", hover_color=BORDER2,
                      text_color=TEXT_MID, width=60, height=22,
                      corner_radius=4,
                      command=lambda: self._ana_input.delete(
                          "0.0", "end")).pack(side="right")

        self._ana_input = ctk.CTkTextbox(body_frame, fg_color=INPUT_BG,
                                          text_color=TEXT, font=fmono(10),
                                          corner_radius=6, border_width=1,
                                          border_color=BORDER, wrap="word")
        self._ana_input.grid(row=1, column=0, sticky="nsew", pady=(6, 0))

        ctk.CTkFrame(left, fg_color="transparent", height=10).grid(row=4, column=0)

        # Buttons row
        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.grid(row=5, column=0, sticky="ew")
        btn_row.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(btn_row, text="🔍  ANALYSE EMAIL",
                      font=fmono(11, "bold"), fg_color=AMBER,
                      hover_color="#c07830", text_color=BG,
                      height=42, corner_radius=5,
                      command=self._do_analyse).grid(
            row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(btn_row, text="📋  LOAD RANDOM PHISHING",
                      font=flabel(), fg_color="transparent",
                      hover_color=BORDER2, text_color=RED,
                      border_color=BORDER2, border_width=1,
                      height=42, corner_radius=5,
                      command=self._load_random_phishing).grid(row=0, column=1)

        ctk.CTkButton(btn_row, text="📋  LOAD RANDOM LEGIT",
                      font=flabel(), fg_color="transparent",
                      hover_color=BORDER2, text_color=GREEN,
                      border_color=BORDER2, border_width=1,
                      height=42, corner_radius=5,
                      command=self._load_random_legit).grid(
            row=0, column=2, padx=(8, 0))

        ctk.CTkFrame(left, fg_color="transparent", height=16).grid(row=6, column=0)

        # Right border
        ctk.CTkFrame(parent, fg_color=BORDER, width=1,
                     corner_radius=0).grid(row=0, column=0,
                                           sticky="nse")

        # ── Right: results ─────────────────────────────────────────────────────
        right = ctk.CTkScrollableFrame(parent, fg_color=BG, corner_radius=0,
                                        border_width=0,
                                        scrollbar_button_color=BORDER2,
                                        scrollbar_button_hover_color=BORDER,
                                        width=340)
        right.grid(row=0, column=1, sticky="nsew", padx=(16, 0))
        P = {"padx": 4}

        ctk.CTkFrame(right, fg_color="transparent", height=16).pack()

        # Score meter
        self._score_meter = ScoreMeter(right)
        self._score_meter.pack(fill="x", **P)

        ctk.CTkFrame(right, fg_color="transparent", height=14).pack()
        SectionHeader(right, "DETECTION REASONS").pack(fill="x", **P)
        ctk.CTkFrame(right, fg_color="transparent", height=6).pack()

        self._reasons_box = ctk.CTkTextbox(right, fg_color=INPUT_BG,
                                            text_color=TEXT, font=fmono(9),
                                            corner_radius=5, border_width=1,
                                            border_color=BORDER, height=200,
                                            state="disabled")
        self._reasons_box.pack(fill="x", **P)

        ctk.CTkFrame(right, fg_color="transparent", height=14).pack()
        SectionHeader(right, "AWARENESS TIPS").pack(fill="x", **P)
        ctk.CTkFrame(right, fg_color="transparent", height=6).pack()

        self._tips_box = ctk.CTkTextbox(right, fg_color=INPUT_BG,
                                         text_color=TEXT, font=fmono(9),
                                         corner_radius=5, border_width=1,
                                         border_color=BORDER, height=200,
                                         state="disabled")
        self._tips_box.pack(fill="x", **P)

        ctk.CTkFrame(right, fg_color="transparent", height=14).pack()
        ctk.CTkButton(right, text="💾  EXPORT REPORT",
                      font=flabel(), fg_color="transparent",
                      hover_color=BORDER2, text_color=TEXT_MID,
                      border_color=BORDER2, border_width=1,
                      height=32, corner_radius=5,
                      command=self._export_report).pack(fill="x", **P)

        ctk.CTkFrame(right, fg_color="transparent", height=20).pack()
        self._last_result = None

    # ── TAB 3: Dataset Explorer ───────────────────────────────────────────────

    def _build_dataset(self, parent):
        parent.configure(fg_color=BG)
        parent.grid_columnconfigure((0, 1), weight=1)
        parent.grid_rowconfigure(1, weight=1)

        ctk.CTkFrame(parent, fg_color="transparent", height=16).grid(
            row=0, column=0, columnspan=2)

        # Stats bar
        stats_frame = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=6,
                                    border_width=1, border_color=BORDER)
        stats_frame.grid(row=0, column=0, columnspan=2, sticky="ew",
                          padx=0, pady=(16, 12))
        stats_inner = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_inner.pack(fill="x", padx=20, pady=12)

        self._stat_phishing_var = ctk.StringVar(value="—")
        self._stat_legit_var    = ctk.StringVar(value="—")

        for label, var, color in [
            ("PHISHING EXAMPLES", self._stat_phishing_var, RED),
            ("LEGITIMATE EXAMPLES", self._stat_legit_var, GREEN),
        ]:
            col = ctk.CTkFrame(stats_inner, fg_color="transparent")
            col.pack(side="left", padx=(0, 40))
            ctk.CTkLabel(col, text=label, font=flabel(),
                         text_color=TEXT_MID).pack(anchor="w")
            ctk.CTkLabel(col, textvariable=var, font=fmono(18, "bold"),
                         text_color=color).pack(anchor="w")

        # Phishing examples column
        p_frame = ctk.CTkFrame(parent, fg_color=BG)
        p_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        p_frame.grid_rowconfigure(1, weight=1)
        p_frame.grid_columnconfigure(0, weight=1)

        p_hdr = ctk.CTkFrame(p_frame, fg_color="transparent")
        p_hdr.grid(row=0, column=0, sticky="ew")
        SectionHeader(p_hdr, "PHISHING EXAMPLES").pack(side="left",
                                                        fill="x", expand=True)
        ctk.CTkButton(p_hdr, text="SEND TO ANALYSER →",
                      font=flabel(), fg_color="transparent",
                      hover_color=BORDER2, text_color=AMBER,
                      width=140, height=22, corner_radius=4,
                      command=lambda: self._send_dataset_to_analyser("phishing")
                      ).pack(side="right")

        self._phishing_list = ctk.CTkTextbox(p_frame, fg_color=INPUT_BG,
                                              text_color=TEXT, font=fmono(9),
                                              corner_radius=6, border_width=1,
                                              border_color=BORDER, wrap="word",
                                              state="disabled")
        self._phishing_list.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        # Legit examples column
        l_frame = ctk.CTkFrame(parent, fg_color=BG)
        l_frame.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        l_frame.grid_rowconfigure(1, weight=1)
        l_frame.grid_columnconfigure(0, weight=1)

        l_hdr = ctk.CTkFrame(l_frame, fg_color="transparent")
        l_hdr.grid(row=0, column=0, sticky="ew")
        SectionHeader(l_hdr, "LEGITIMATE EXAMPLES").pack(side="left",
                                                          fill="x", expand=True)
        ctk.CTkButton(l_hdr, text="SEND TO ANALYSER →",
                      font=flabel(), fg_color="transparent",
                      hover_color=BORDER2, text_color=GREEN,
                      width=140, height=22, corner_radius=4,
                      command=lambda: self._send_dataset_to_analyser("legit")
                      ).pack(side="right")

        self._legit_list = ctk.CTkTextbox(l_frame, fg_color=INPUT_BG,
                                           text_color=TEXT, font=fmono(9),
                                           corner_radius=6, border_width=1,
                                           border_color=BORDER, wrap="word",
                                           state="disabled")
        self._legit_list.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

    # ── Status bar ────────────────────────────────────────────────────────────

    def _statusbar(self):
        ctk.CTkFrame(self, fg_color=BORDER, height=1,
                     corner_radius=0).pack(fill="x")
        sb = ctk.CTkFrame(self, fg_color=SURFACE, height=28, corner_radius=0)
        sb.pack(fill="x")
        sb.pack_propagate(False)
        ctk.CTkLabel(sb,
                     text="FOR EDUCATIONAL USE ONLY  ·  Social Engineering Simulator  v2.0",
                     font=flabel(), text_color=TEXT_DIM).pack(
            side="left", padx=18, pady=5)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _do_generate(self):
        name     = self._gen_name.get().strip() or "Employee"
        scenario = self._gen_scenario.get()
        urgency  = self._gen_urgency.get()

        result = generate_phishing_email(name, scenario, urgency)
        self._last_generated = result

        # Subject
        self._subj_var.set(result["subject"])

        # Body output
        self._gen_output.clear()
        self._gen_output.write(f"Subject: {result['subject']}", "warn")
        self._gen_output.write("─" * 56, "dim")
        self._gen_output.write(result["body"])
        self._gen_output.write(result["disclaimer"], "dim")

        # Traits
        self._traits_box.configure(state="normal")
        self._traits_box.delete("0.0", "end")
        for trait in result["traits"]:
            self._traits_box.insert("end", trait + "\n")
        self._traits_box.configure(state="disabled")

    def _send_to_analyser(self):
        if not self._last_generated:
            messagebox.showinfo("Nothing Generated", "Generate an email first.")
            return
        body = self._last_generated.get("body", "")
        subj = self._last_generated.get("subject", "")
        self._ana_input.delete("0.0", "end")
        self._ana_input.insert("0.0", body)
        self._ana_subject.set(subj)
        self._tabs.set("🔍  Email Analyser")

    def _do_analyse(self):
        text = self._ana_input.get("0.0", "end").strip()
        subj = self._ana_subject.get().strip()

        if not text:
            messagebox.showwarning("Empty", "Paste an email body to analyse.")
            return

        # Fake brief progress feel
        self._score_meter.reset()

        def run():
            time.sleep(0.4)  # simulated analysis delay
            result = analyze_email(text, subj)
            self.after(0, lambda r=result: self._show_analysis(r))

        threading.Thread(target=run, daemon=True).start()

    def _show_analysis(self, result):
        self._last_result = result
        self._score_meter.update(result.risk_score, result.label)

        # Reasons
        self._reasons_box.configure(state="normal")
        self._reasons_box.delete("0.0", "end")
        if result.reasons:
            for r in result.reasons:
                self._reasons_box.insert("end", f"• {r}\n\n")
        else:
            self._reasons_box.insert("end", "No phishing indicators detected.")
        self._reasons_box.configure(state="disabled")

        # Tips
        self._tips_box.configure(state="normal")
        self._tips_box.delete("0.0", "end")
        for tip in result.tips:
            self._tips_box.insert("end", f"{tip}\n\n")
        self._tips_box.configure(state="disabled")

    def _load_random_phishing(self):
        email = get_random_phishing()
        self._ana_input.delete("0.0", "end")
        self._ana_input.insert("0.0", email)
        self._ana_subject.set("")

    def _load_random_legit(self):
        email = get_random_legitimate()
        self._ana_input.delete("0.0", "end")
        self._ana_input.insert("0.0", email)
        self._ana_subject.set("")

    def _load_stats(self):
        stats = get_dataset_stats()
        self._stat_phishing_var.set(str(stats["phishing_count"]))
        self._stat_legit_var.set(str(stats["legitimate_count"]))

        from social_engineering.dataset_loader import (
            load_phishing_examples, load_legitimate_examples)

        ph = load_phishing_examples()
        le = load_legitimate_examples()

        self._phishing_list.configure(state="normal")
        self._phishing_list.delete("0.0", "end")
        for i, ex in enumerate(ph, 1):
            self._phishing_list.insert("end", f"[{i:02d}]  {ex}\n\n")
        self._phishing_list.configure(state="disabled")

        self._legit_list.configure(state="normal")
        self._legit_list.delete("0.0", "end")
        for i, ex in enumerate(le, 1):
            self._legit_list.insert("end", f"[{i:02d}]  {ex}\n\n")
        self._legit_list.configure(state="disabled")

    def _send_dataset_to_analyser(self, kind: str):
        if kind == "phishing":
            email = get_random_phishing()
        else:
            email = get_random_legitimate()
        self._ana_input.delete("0.0", "end")
        self._ana_input.insert("0.0", email)
        self._ana_subject.set("")
        self._tabs.set("🔍  Email Analyser")

    def _export_email(self):
        if not self._last_generated:
            messagebox.showinfo("Nothing to Export", "Generate an email first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt")],
            initialfile="simulated_phishing_email.txt")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Subject: {self._last_generated['subject']}\n")
            f.write("=" * 60 + "\n")
            f.write(self._last_generated["body"])
            f.write("\n" + "=" * 60 + "\n")
            f.write("\nPHISHING TRAITS ANNOTATED:\n")
            for t in self._last_generated["traits"]:
                f.write(f"  {t}\n")
            f.write(self._last_generated["disclaimer"])
        messagebox.showinfo("Exported", f"Email saved to:\n{path}")

    def _export_report(self):
        if not self._last_result:
            messagebox.showinfo("No Analysis", "Analyse an email first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt")],
            initialfile="phishing_analysis_report.txt")
        if not path:
            return
        r = self._last_result
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(path, "w", encoding="utf-8") as f:
            f.write("CYBERSIM SUITE — PHISHING ANALYSIS REPORT\n")
            f.write(f"Generated: {ts}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"RISK SCORE  :  {r.risk_score}/100\n")
            f.write(f"LABEL       :  {r.label}\n\n")
            f.write("DETECTION REASONS:\n")
            for reason in r.reasons:
                f.write(f"  • {reason}\n")
            f.write("\nAWARENESS TIPS:\n")
            for tip in r.tips:
                f.write(f"  {tip}\n")
            if r.urls_found:
                f.write("\nURLs FOUND IN EMAIL:\n")
                for url in r.urls_found:
                    f.write(f"  {url}\n")
            f.write("\n" + "=" * 60 + "\n")
            f.write("FOR EDUCATIONAL USE ONLY — CyberSim Suite v2.0\n")
        messagebox.showinfo("Exported", f"Report saved to:\n{path}")

    def _go_home(self):
        import subprocess
        script = os.path.join(BASE, "home.py")
        if os.path.isfile(script):
            subprocess.Popen([sys.executable, script])
        self.destroy()

    def _export_report(self):
        if not self._last_result:
            messagebox.showinfo("No Analysis", "Analyse an email first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt")],
            initialfile="phishing_analysis_report.txt")
        if not path:
            return
        r = self._last_result
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(path, "w", encoding="utf-8") as f:
            f.write("CYBERSIM — PHISHING ANALYSIS REPORT\n")
            f.write(f"Generated: {ts}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"RISK SCORE : {r.risk_score}/100\n")
            f.write(f"LABEL      : {r.label}\n\n")
            f.write("REASONS:\n")
            for reason in r.reasons:
                f.write(f"  • {reason}\n")
            f.write("\nTIPS:\n")
            for tip in r.tips:
                f.write(f"  {tip}\n")
        messagebox.showinfo("Exported", f"Saved to:\n{path}")


if __name__ == "__main__":
    SocialEngineeringGUI().mainloop()