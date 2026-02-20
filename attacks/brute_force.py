import string
import itertools
from utils.hash_utils import verify_password
from utils.result import AttackResult

CHARSET = string.ascii_lowercase + string.ascii_uppercase + string.digits


def run_brute_force_attack(hash_value: str, algorithm: str, max_length: int,
                            progress_callback=None, stop_event=None) -> AttackResult:
    result = AttackResult()
    result.start()

    for length in range(1, max_length + 1):
        for combo in itertools.product(CHARSET, repeat=length):
            if stop_event and stop_event.is_set():
                result.error = "Attack stopped by user."
                result.finish(False)
                return result

            candidate = "".join(combo)
            result.attempts += 1

            if progress_callback and result.attempts % 5000 == 0:
                progress_callback(result.attempts, -1, candidate)

            if verify_password(candidate, hash_value, algorithm):
                result.finish(True, candidate)
                return result

    result.finish(False)
    return result