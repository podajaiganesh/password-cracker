"""
utils/result.py
AttackResult — stores outcome of any attack and provides a summary.
"""

import time


class AttackResult:
    """Stores the outcome of a password attack run."""

    def __init__(self):
        self.success: bool = False
        self.cracked_password: str | None = None
        self.attempts: int = 0
        self.elapsed_time: float = 0.0
        self.error: str | None = None

        self._start_time: float | None = None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Call once when the attack begins."""
        self._start_time = time.perf_counter()

    def finish(self, success: bool, cracked_password: str | None = None) -> None:
        """Call once when the attack ends (found or exhausted)."""
        end = time.perf_counter()
        self.elapsed_time = end - self._start_time if self._start_time else 0.0
        self.success = success
        self.cracked_password = cracked_password

    # ── Summary ───────────────────────────────────────────────────────────────

    @property
    def speed(self) -> float:
        """Attempts per second."""
        return self.attempts / self.elapsed_time if self.elapsed_time > 0 else 0.0

    def summary(self) -> dict:
        """
        Returns a plain-dict summary suitable for display in the GUI.
        Keys: status, cracked_password, attempts, time_taken, speed, error
        """
        spd = self.speed
        if spd >= 1_000_000:
            speed_str = f"{spd / 1_000_000:.2f}M/s"
        elif spd >= 1_000:
            speed_str = f"{spd / 1_000:.1f}K/s"
        else:
            speed_str = f"{spd:.0f}/s"

        return {
            "status":           "SUCCESS" if self.success else "FAILED",
            "cracked_password": self.cracked_password or "Not found",
            "attempts":         self.attempts,
            "time_taken":       f"{self.elapsed_time:.4f}s",
            "speed":            speed_str,
            "error":            self.error,
        }

    def __repr__(self) -> str:  # handy for debugging
        s = self.summary()
        return (f"<AttackResult status={s['status']} "
                f"attempts={s['attempts']} time={s['time_taken']} "
                f"speed={s['speed']} pw={self.cracked_password!r}>")