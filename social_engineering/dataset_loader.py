"""
social_engineering/dataset_loader.py
Loads example email datasets from the data/ folder.
All data is local — no network calls.
"""

import os
import random

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
_PHISHING_FILE   = os.path.join(_DATA_DIR, "phishing_emails.txt")
_LEGITIMATE_FILE = os.path.join(_DATA_DIR, "legitimate_emails.txt")


def _load_file(path: str) -> list[str]:
    """Read a text file and return non-empty stripped lines."""
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def load_phishing_examples() -> list[str]:
    """Return all phishing email examples from the dataset."""
    return _load_file(_PHISHING_FILE)


def load_legitimate_examples() -> list[str]:
    """Return all legitimate email examples from the dataset."""
    return _load_file(_LEGITIMATE_FILE)


def get_random_phishing() -> str:
    """Return one random phishing example."""
    examples = load_phishing_examples()
    return random.choice(examples) if examples else "No phishing examples loaded."


def get_random_legitimate() -> str:
    """Return one random legitimate example."""
    examples = load_legitimate_examples()
    return random.choice(examples) if examples else "No legitimate examples loaded."


def get_dataset_stats() -> dict:
    """Return count stats for both datasets."""
    return {
        "phishing_count":   len(load_phishing_examples()),
        "legitimate_count": len(load_legitimate_examples()),
        "data_dir":         _DATA_DIR,
    }