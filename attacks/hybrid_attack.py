"""
attacks/hybrid_attack.py
Hybrid attack: applies a set of mutation rules to each word in a wordlist
to produce realistic password candidates (word + number, leet, symbols, etc.).

Reads the wordlist line-by-line to handle large files (rockyou.txt etc.).
"""

import threading
from utils.hash_utils import verify_password
from utils.result import AttackResult

# ── Mutation tables ───────────────────────────────────────────────────────────

_SUFFIXES = (
    "1", "12", "123", "1234", "12345", "123456",
    "!", "@", "#", "$", "!!", "@@",
    "0", "00", "01", "99", "007", "786", "143",
    "2020", "2021", "2022", "2023", "2024", "2025",
    "@123", "123!", "!123", "@2024", "@2025",
    "abc", "pass", "pwd",
)

_PREFIXES = ("1", "123", "!", "@", "#", "my", "the", "new", "old")

_LEET = str.maketrans("aeiostb", "4310$7b".replace("b", "6"))

_CALLBACK_INTERVAL = 200   # emit progress every N base-words


def _variants(word: str):
    """
    Yield all mutation variants of *word*.
    Uses a local seen-set so no duplicate candidates escape this function.
    """
    seen = set()

    def _e(w):
        if w and w not in seen:
            seen.add(w)
            return w
        return None

    lower = word.lower()
    cap   = word.capitalize()
    upper = word.upper()
    swap  = word.swapcase()
    leet  = lower.translate(_LEET)

    # Base forms
    for base in (word, lower, cap, upper, swap, leet, leet.capitalize()):
        v = _e(base)
        if v:
            yield v

    # base + suffix
    for base in (lower, cap, word):
        for suf in _SUFFIXES:
            v = _e(base + suf)
            if v:
                yield v

    # prefix + base
    for pre in _PREFIXES:
        for base in (lower, cap):
            v = _e(pre + base)
            if v:
                yield v

    # doubled word
    for base in (lower, cap):
        v = _e(base + base)
        if v:
            yield v
        v = _e(base + base + "123")
        if v:
            yield v

    # symbol replacements
    replacements = (
        lower.replace("a", "@"),
        lower.replace("o", "0"),
        lower.replace("i", "1"),
        lower.replace("s", "$"),
        lower.replace("a", "@").replace("o", "0"),
        lower.replace("i", "1").replace("s", "$"),
        lower.replace("a", "@").replace("s", "$").replace("i", "1"),
    )
    for r in replacements:
        if r != lower:
            v = _e(r)
            if v:
                yield v
            v = _e(r.capitalize())
            if v:
                yield v


def run_hybrid_attack(
    hash_value: str,
    algorithm: str,
    wordlist_path: str,
    progress_callback=None,
    stop_event: threading.Event | None = None,
) -> AttackResult:
    """
    For every word in *wordlist_path*, generate mutation variants and test
    each against *hash_value*.  Reads line-by-line for memory efficiency.

    Args:
        hash_value:        Target hash string.
        algorithm:         Hash algorithm identifier.
        wordlist_path:     Path to plaintext wordlist.
        progress_callback: Optional callable(attempts, total, current_word).
        stop_event:        Optional threading.Event to abort.

    Returns:
        Populated AttackResult.
    """
    result = AttackResult()
    result.start()

    try:
        f = open(wordlist_path, "r", encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        result.error = f"Wordlist not found: {wordlist_path}"
        result.finish(False)
        return result
    except OSError as exc:
        result.error = f"Cannot open wordlist: {exc}"
        result.finish(False)
        return result

    _verify   = verify_password
    _hash     = hash_value.strip()
    _algo     = algorithm
    _stop     = stop_event
    _cb       = progress_callback
    _interval = _CALLBACK_INTERVAL
    attempts  = 0
    word_no   = 0

    try:
        for raw_line in f:
            if _stop is not None and _stop.is_set():
                result.error = "Attack stopped by user."
                break

            base_word = raw_line.rstrip("\n\r")
            if not base_word:
                continue

            word_no += 1
            if _cb is not None and word_no % _interval == 0:
                _cb(attempts, -1, base_word)

            for candidate in _variants(base_word):
                if _stop is not None and _stop.is_set():
                    result.error = "Attack stopped by user."
                    result.attempts = attempts
                    result.finish(False)
                    return result

                attempts += 1

                if _verify(candidate, _hash, _algo):
                    result.attempts = attempts
                    result.finish(True, candidate)
                    return result

    except Exception as exc:
        result.error = f"Unexpected error: {exc}"
    finally:
        f.close()

    result.attempts = attempts
    result.finish(False)
    return result