from utils.hash_utils import verify_password
from utils.result import AttackResult


SUFFIXES = [
    "1", "12", "123", "1234", "12345", "123456",
    "!", "@", "#", "!!", "@@",
    "0", "00", "01", "99", "2024", "2023",
    "@123", "123!", "!123", "abc", "xyz",
]

PREFIXES = ["!", "@", "#", "1", "123", "000"]

LEET_MAP = str.maketrans("aeiost", "4310$7")


def generate_variants(word: str):
    seen = set()

    def emit(w):
        if w not in seen:
            seen.add(w)
            yield w

    # Original
    yield from emit(word)

    # Capitalization variants
    yield from emit(word.lower())
    yield from emit(word.upper())
    yield from emit(word.capitalize())
    yield from emit(word.swapcase())

    # Title case (each word)
    yield from emit(word.title())

    # Leet speak
    leet = word.translate(LEET_MAP)
    yield from emit(leet)
    yield from emit(leet.capitalize())

    # Suffix combinations
    for suffix in SUFFIXES:
        yield from emit(word + suffix)
        yield from emit(word.lower() + suffix)
        yield from emit(word.capitalize() + suffix)
        yield from emit(word.upper() + suffix)

    # Prefix combinations
    for prefix in PREFIXES:
        yield from emit(prefix + word)
        yield from emit(prefix + word.lower())
        yield from emit(prefix + word.capitalize())

    # Double word
    yield from emit(word + word)
    yield from emit(word.lower() + word.lower())


def run_hybrid_attack(hash_value: str, algorithm: str, wordlist_path: str,
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

    total_words = len(words)
    for i, word in enumerate(words):
        if stop_event and stop_event.is_set():
            result.error = "Attack stopped by user."
            result.finish(False)
            return result

        if progress_callback and i % 10 == 0:
            progress_callback(i, total_words, word)

        for variant in generate_variants(word):
            if stop_event and stop_event.is_set():
                result.error = "Attack stopped by user."
                result.finish(False)
                return result

            result.attempts += 1

            if verify_password(variant, hash_value, algorithm):
                result.finish(True, variant)
                return result

    result.finish(False)
    return result