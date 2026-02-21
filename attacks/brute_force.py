"""
attacks/brute_force.py
Brute-force attack using itertools.product over a configurable charset.
Tries all combinations from length 1 up to max_length.
"""

import itertools
import threading
from utils.hash_utils import verify_password
from utils.result import AttackResult

CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# Emit a progress update every N attempts
_CALLBACK_INTERVAL = 5_000


def run_brute_force_attack(
    hash_value: str,
    algorithm: str,
    max_length: int,
    progress_callback=None,
    stop_event: threading.Event | None = None,
) -> AttackResult:
    """
    Generate every combination of CHARSET from length 1 to max_length
    and test each against hash_value.

    Args:
        hash_value:        Target hash string.
        algorithm:         Hash algorithm identifier.
        max_length:        Maximum candidate length (inclusive).
        progress_callback: Optional callable(attempts, total, current_word).
                           total == -1 (unknown).
        stop_event:        Optional threading.Event to abort.

    Returns:
        Populated AttackResult.
    """
    result = AttackResult()
    result.start()

    # ── Local bindings for hot-loop performance ───────────────────────────────
    _verify    = verify_password
    _hash      = hash_value.strip()
    _algo      = algorithm
    _charset   = CHARSET
    _interval  = _CALLBACK_INTERVAL
    _stop      = stop_event
    _cb        = progress_callback
    attempts   = 0

    try:
        for length in range(1, max_length + 1):
            for combo in itertools.product(_charset, repeat=length):
                # ── Stop check ────────────────────────────────────────────────
                if _stop is not None and _stop.is_set():
                    result.error = "Attack stopped by user."
                    result.attempts = attempts
                    result.finish(False)
                    return result

                candidate = "".join(combo)
                attempts += 1

                # ── Progress ──────────────────────────────────────────────────
                if _cb is not None and attempts % _interval == 0:
                    _cb(attempts, -1, candidate)

                # ── Verify ────────────────────────────────────────────────────
                if _verify(candidate, _hash, _algo):
                    result.attempts = attempts
                    result.finish(True, candidate)
                    return result

    except Exception as exc:
        result.error = f"Unexpected error: {exc}"

    result.attempts = attempts
    result.finish(False)
    return result