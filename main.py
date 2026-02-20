#!/usr/bin/env python3
"""
Password Attack Simulator
Educational / Cybersecurity Awareness Tool

Usage:
    python main.py

Optional (for bcrypt support):
    pip install bcrypt
"""

import os
import sys

# Ensure the package root is on sys.path so all submodules resolve correctly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import tkinter as tk
from gui import PasswordAttackSimulatorGUI, apply_ttk_style


def main():
    root = tk.Tk()
    root.resizable(True, True)
    apply_ttk_style()
    app = PasswordAttackSimulatorGUI(root)  # noqa: F841
    root.mainloop()


if __name__ == "__main__":
    main()