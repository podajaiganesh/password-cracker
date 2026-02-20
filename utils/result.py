import time


class AttackResult:
    def __init__(self):
        self.success = False
        self.cracked_password = None
        self.attempts = 0
        self.start_time = None
        self.end_time = None
        self.elapsed_time = 0.0
        self.speed = 0.0
        self.error = None

    def start(self):
        self.start_time = time.time()

    def finish(self, success: bool, cracked_password=None):
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time if self.start_time else 0
        self.success = success
        self.cracked_password = cracked_password
        self.speed = self.attempts / self.elapsed_time if self.elapsed_time > 0 else 0

    def summary(self) -> dict:
        return {
            "status": "SUCCESS" if self.success else "FAILED",
            "cracked_password": self.cracked_password or "Not found",
            "attempts": self.attempts,
            "time_taken": f"{self.elapsed_time:.4f}s",
            "speed": f"{self.speed:,.0f} attempts/sec",
            "error": self.error,
        }