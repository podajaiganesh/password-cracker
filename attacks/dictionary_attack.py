"""
attacks/dictionary_attack.py
Efficient dictionary attack — reads the wordlist line-by-line (no full load),
so it works with multi-million-entry files like rockyou.txt without OOM issues.
"""

import threading
from utils.hash_utils import verify_password
from utils.result import AttackResult

# Progress callback is invoked every N lines to keep GUI responsive
_CALLBACK_INTERVAL = 500


def run_dictionary_attack(
    hash_value: str,
    algorithm: str,
    wordlist_path: str,
    progress_callback=None,
    stop_event: threading.Event | None = None,
) -> AttackResult:
    """
    Iterate over *wordlist_path* line by line and compare each candidate
    against *hash_value* using *algorithm*.

    Args:
        hash_value:        The hash string to crack.
        algorithm:         One of md5 | sha1 | sha256 | sha512 | bcrypt | pbkdf2_sha256.
        wordlist_path:     Path to a plain-text wordlist (one password per line).
        progress_callback: Optional callable(attempts, total, current_word).
                           total == -1 when file size is unknown.
        stop_event:        Optional threading.Event; attack aborts when set.

    Returns:
        AttackResult with all fields populated.
    """
    result = AttackResult()
    result.start()

    # ── Open file ─────────────────────────────────────────────────────────────
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

    # ── Pre-cache local references for tight loop performance ─────────────────
    _verify    = verify_password
    _algorithm = algorithm
    _hash      = hash_value.strip()
    _interval  = _CALLBACK_INTERVAL
    _stop      = stop_event
    _cb        = progress_callback
    attempts   = 0

    try:
        for raw_line in f:
            # ── Stop check ────────────────────────────────────────────────────
            if _stop is not None and _stop.is_set():
                result.error = "Attack stopped by user."
                break

            candidate = raw_line.rstrip("\n\r")
            if not candidate:
                continue

            attempts += 1

            # ── Progress callback (throttled) ─────────────────────────────────
            if _cb is not None and attempts % _interval == 0:
                _cb(attempts, -1, candidate)

            # ── Verify ────────────────────────────────────────────────────────
            if _verify(candidate, _hash, _algorithm):
                result.attempts = attempts
                result.finish(True, candidate)
                return result

    except Exception as exc:
        result.error = f"Unexpected error during attack: {exc}"
    finally:
        f.close()

    result.attempts = attempts
    result.finish(False)
    return result