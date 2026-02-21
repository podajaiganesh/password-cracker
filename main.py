#!/usr/bin/env python3
"""
main.py — SECURENETRA entry point
Run:  python3 main.py
Requires:  pip install customtkinter
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import customtkinter as ctk
except ImportError:
    print("[ERROR] CustomTkinter not installed.")
    print("        Run:  pip install customtkinter")
    sys.exit(1)

from utils import db
from auth_gui import AuthWindow
from home import CyberSimHome

def show_home():
    root.deiconify()
    CyberSimHome().mainloop()

if __name__ == "__main__":
    # Initialize database
    db.init_db()
    
    # Create hidden root window
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.withdraw()
    
    # Show auth window first
    auth = AuthWindow(root, show_home)
    auth.mainloop()