"""
home.py  —  CyberSim Suite  |  Home Dashboard
Run:  python3 home.py
Requires:  pip install customtkinter
"""

import customtkinter as ctk
import os, sys, subprocess

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Brand colours ─────────────────────────────────────────────────────────────
BG          = "#0a0a0a"
SURFACE     = "#111111"
CARD        = "#141414"
CARD_HOVER  = "#1a1a1a"
BORDER      = "#222222"
RED         = "#e63946"
CYAN        = "#00b4d8"
AMBER       = "#f4a261"
GREEN       = "#2dc653"
TEXT        = "#f0f0f0"
TEXT_MID    = "#777777"
TEXT_DIM    = "#444444"

MODULES = [
    {
        "title":   "Password Attack\nSimulator",
        "sub":     "Dictionary · Brute Force · Hybrid\nMD5  SHA1/256/512  bcrypt",
        "tag":     "ACTIVE",
        "accent":  RED,
        "tag_fg":  RED,
        "tag_bg":  "#1f0a0b",
        "script":  "gui.py",
    },
    {
        "title":   "Social Engineering\nSimulator",
        "sub":     "Phishing · Pretexting · Vishing\nAwareness training scenarios",
        "tag":     "ACTIVE",
        "accent":  AMBER,
        "tag_fg":  AMBER,
        "tag_bg":  "#1a1000",
        "script":  "social_engineering_gui.py",
    },
    {
        "title":   "Domain Spoof\nDetector",
        "sub":     "SSL validation · DNS lookup\nHomograph & TLD risk analysis",
        "tag":     "ACTIVE",
        "accent":  CYAN,
        "tag_fg":  CYAN,
        "tag_bg":  "#001519",
        "script":  "domain_gui.py",
    },
    {
        "title":   "Security Awareness\nTraining",
        "sub":     "Interactive lessons · Quizzes\nDaily security tips feed",
        "tag":     "ACTIVE",
        "accent":  GREEN,
        "tag_fg":  GREEN,
        "tag_bg":  "#041209",
        "script":  "training_gui.py",
    },
    {
        "title":   "Risk & Analytics\nDashboard",
        "sub":     "Attack metrics · Charts\nPDF/JSON export · Timeline",
        "tag":     "ACTIVE",
        "accent":  "#9d4edd",
        "tag_fg":  "#9d4edd",
        "tag_bg":  "#130a18",
        "script":  "dashboard_gui.py",
    },
    {
        "title":   "2FA Login\nSystem",
        "sub":     "OTP verification · Session mgmt\nPassword strength meter",
        "tag":     "ACTIVE",
        "accent":  "#ff006e",
        "tag_fg":  "#ff006e",
        "tag_bg":  "#1a0009",
        "script":  "auth_gui.py",
    },
    {
        "title":   "Network Traffic\nAnalyzer",
        "sub":     "Packet inspection · Protocol analysis\nAnomaly detection",
        "tag":     "COMING SOON",
        "accent":  "#06ffa5",
        "tag_fg":  "#06ffa5",
        "tag_bg":  "#001a11",
        "script":  None,
    },
    {
        "title":   "Vulnerability\nScanner",
        "sub":     "Port scanning · CVE lookup\nRisk assessment reports",
        "tag":     "COMING SOON",
        "accent":  "#ffbe0b",
        "tag_fg":  "#ffbe0b",
        "tag_bg":  "#1a1500",
        "script":  None,
    },
]


class ModuleCard(ctk.CTkFrame):
    def __init__(self, parent, data: dict, **kw):
        super().__init__(parent,
                         fg_color=CARD,
                         corner_radius=6,
                         border_width=1,
                         border_color=BORDER,
                         **kw)
        self._data   = data
        self._active = data["script"] is not None
        self._accent = data["accent"]
        self._build()
        if self._active:
            self.bind("<Button-1>", self._launch)
            self.bind("<Enter>",    self._hover_on)
            self.bind("<Leave>",    self._hover_off)
            self.configure(cursor="hand2")

    def _build(self):
        # Top accent stripe
        stripe = ctk.CTkFrame(self, fg_color=self._accent if self._active else BORDER,
                               height=3, corner_radius=0)
        stripe.pack(fill="x")
        stripe.pack_propagate(False)
        self._stripe = stripe

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=18, pady=16)

        # Tag pill
        tag_frame = ctk.CTkFrame(body,
                                  fg_color=self._data["tag_bg"],
                                  corner_radius=4,
                                  border_width=1,
                                  border_color=self._accent if self._active else BORDER)
        tag_frame.pack(anchor="w")
        ctk.CTkLabel(tag_frame,
                     text=self._data["tag"],
                     font=ctk.CTkFont("Courier New", 10, "bold"),
                     text_color=self._data["tag_fg"] if self._active else TEXT_DIM,
                     fg_color="transparent").pack(padx=8, pady=3)

        ctk.CTkFrame(body, fg_color="transparent", height=12).pack()

        # Title
        ctk.CTkLabel(body,
                     text=self._data["title"],
                     font=ctk.CTkFont("Courier New", 15, "bold"),
                     text_color=TEXT if self._active else TEXT_DIM,
                     justify="left",
                     anchor="w").pack(fill="x")

        ctk.CTkFrame(body, fg_color=BORDER, height=1).pack(fill="x", pady=12)

        # Description
        ctk.CTkLabel(body,
                     text=self._data["sub"],
                     font=ctk.CTkFont("Courier New", 10),
                     text_color=TEXT_MID if self._active else TEXT_DIM,
                     justify="left",
                     anchor="w").pack(fill="x")

        ctk.CTkFrame(body, fg_color="transparent", height=14).pack()

        # Launch label
        if self._active:
            self._launch_lbl = ctk.CTkLabel(body,
                                             text="LAUNCH  →",
                                             font=ctk.CTkFont("Courier New", 10, "bold"),
                                             text_color=self._accent,
                                             anchor="w")
            self._launch_lbl.pack(anchor="w")

    def _hover_on(self, _=None):
        self.configure(fg_color=CARD_HOVER, border_color=self._accent)
        self._stripe.configure(fg_color=self._accent)

    def _hover_off(self, _=None):
        self.configure(fg_color=CARD, border_color=BORDER)
        self._stripe.configure(fg_color=self._accent)

    def _launch(self, _=None):
        script = os.path.join(BASE, self._data["script"])
        if os.path.isfile(script):
            subprocess.Popen([sys.executable, script])


class CyberSimHome(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SECURENETRA - Offensive AI Simulator")
        self.geometry("1100x660")
        self.minsize(900, 560)
        self.configure(fg_color=BG)
        self._build()

    def _build(self):
        self._topbar()
        self._body()
        self._footer()

    def _topbar(self):
        bar = ctk.CTkFrame(self, fg_color=SURFACE, height=52, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        ctk.CTkLabel(bar,
                     text="◈ SECURENETRA",
                     font=ctk.CTkFont("Courier New", 15, "bold"),
                     text_color=RED).pack(side="left", padx=24, pady=14)

        ctk.CTkFrame(bar, fg_color=BORDER, width=1, height=28,
                     corner_radius=0).pack(side="left", pady=12)

        ctk.CTkLabel(bar,
                     text="  Offensive AI Simulator",
                     font=ctk.CTkFont("Courier New", 10),
                     text_color=TEXT_DIM).pack(side="left")

        # Status indicator
        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.pack(side="right", padx=24)
        ctk.CTkLabel(right, text="●  SYSTEM READY",
                     font=ctk.CTkFont("Courier New", 9),
                     text_color=GREEN).pack()

        ctk.CTkFrame(self, fg_color=BORDER, height=1,
                     corner_radius=0).pack(fill="x")

    def _body(self):
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=40, pady=0)

        # Section header row
        hdr = ctk.CTkFrame(body, fg_color="transparent")
        hdr.pack(fill="x", pady=(32, 0))
        ctk.CTkLabel(hdr, text="SELECT MODULE",
                     font=ctk.CTkFont("Courier New", 9, "bold"),
                     text_color=TEXT_DIM).pack(side="left")
        ctk.CTkFrame(hdr, fg_color=BORDER, height=1,
                     corner_radius=0).pack(side="left", fill="x",
                                           expand=True, padx=(14, 0), pady=6)

        # Cards - 2x4 grid
        grid = ctk.CTkFrame(body, fg_color="transparent")
        grid.pack(fill="both", expand=True, pady=(18, 0))
        grid.columnconfigure((0, 1, 2, 3), weight=1, uniform="col")
        grid.rowconfigure((0, 1), weight=1, uniform="row")

        for i, mod in enumerate(MODULES):
            row = i // 4
            col = i % 4
            card = ModuleCard(grid, mod)
            card.grid(row=row, column=col, sticky="nsew",
                      padx=(0 if col == 0 else 10, 0),
                      pady=(0 if row == 0 else 10, 0))

    def _footer(self):
        ctk.CTkFrame(self, fg_color=BORDER, height=1,
                     corner_radius=0).pack(fill="x")
        bar = ctk.CTkFrame(self, fg_color=SURFACE, height=32, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        ctk.CTkLabel(bar,
                     text="FOR EDUCATIONAL & CYBERSECURITY AWARENESS USE ONLY",
                     font=ctk.CTkFont("Courier New", 8),
                     text_color=TEXT_DIM).pack(side="left", padx=20, pady=8)
        ctk.CTkLabel(bar, text="v2.0.0",
                     font=ctk.CTkFont("Courier New", 8),
                     text_color=TEXT_DIM).pack(side="right", padx=20)


if __name__ == "__main__":
    CyberSimHome().mainloop()