from utils.hash_utils import verify_password
from utils.result import AttackResult


def run_dictionary_attack(hash_value: str, algorithm: str, wordlist_path: str,
                           progress_callback=None, stop_event=None) -> AttackResult:
    result = AttackResult()
    result.start()

    try:
        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            words = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        result.error = f"Wordlist file not found: {wordlist_path}"
        result.finish(False)
        return result
    except Exception as e:
        result.error = f"Error reading wordlist: {e}"
        result.finish(False)
        return result

    total = len(words)
    for i, word in enumerate(words):
        if stop_event and stop_event.is_set():
            result.error = "Attack stopped by user."
            result.finish(False)
            return result

        result.attempts += 1

        if progress_callback and i % 100 == 0:
            progress_callback(i, total, word)

        if verify_password(word, hash_value, algorithm):
            result.finish(True, word)
            return result

    result.finish(False)
    return result