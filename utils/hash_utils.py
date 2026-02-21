"""
utils/hash_utils.py
Supports: md5, sha1, sha256, sha512, bcrypt, pbkdf2_sha256
Uses hashlib for simple hashes and passlib for advanced ones.
"""

import hashlib

# ── Optional library detection ────────────────────────────────────────────────
_BCRYPT_BACKEND = None
_PBKDF2_BACKEND = None

try:
    from passlib.hash import bcrypt as _passlib_bcrypt
    from passlib.hash import pbkdf2_sha256 as _passlib_pbkdf2
    _BCRYPT_BACKEND  = "passlib"
    _PBKDF2_BACKEND  = "passlib"
except ImportError:
    pass

if _BCRYPT_BACKEND is None:
    try:
        import bcrypt as _bcrypt_lib
        _BCRYPT_BACKEND = "bcrypt"
    except ImportError:
        pass

# ── Supported algorithms ──────────────────────────────────────────────────────
SUPPORTED_ALGORITHMS = ["md5", "sha1", "sha256", "sha512", "bcrypt", "pbkdf2_sha256"]

_HASHLIB_MAP = {
    "md5":    hashlib.md5,
    "sha1":   hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
}


# ── Public API ────────────────────────────────────────────────────────────────

def hash_password(password: str, algorithm: str) -> str:
    """
    Hash password using algorithm.
    Returns hex digest (hashlib) or encoded hash string (passlib/bcrypt).
    Raises ValueError for unsupported algorithms.
    Raises RuntimeError if a required optional library is missing.
    """
    algo = algorithm.lower().strip()

    if algo in _HASHLIB_MAP:
        return _HASHLIB_MAP[algo](password.encode("utf-8")).hexdigest()

    if algo == "bcrypt":
        if _BCRYPT_BACKEND == "passlib":
            return _passlib_bcrypt.hash(password)
        if _BCRYPT_BACKEND == "bcrypt":
            salt = _bcrypt_lib.gensalt()
            return _bcrypt_lib.hashpw(password.encode(), salt).decode()
        raise RuntimeError(
            "bcrypt support requires 'passlib' or 'bcrypt'.\n"
            "Install with: pip install passlib bcrypt"
        )

    if algo == "pbkdf2_sha256":
        if _PBKDF2_BACKEND == "passlib":
            return _passlib_pbkdf2.hash(password)
        import os, base64
        salt = os.urandom(16)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260000)
        return "pbkdf2:" + base64.b64encode(salt).decode() + ":" + base64.b64encode(dk).decode()

    raise ValueError(
        f"Unsupported algorithm '{algorithm}'. "
        f"Choose from: {', '.join(SUPPORTED_ALGORITHMS)}"
    )


def verify_password(password: str, hash_value: str, algorithm: str) -> bool:
    """
    Verify password against hash_value using algorithm.
    Returns True on match, False otherwise.
    """
    algo = algorithm.lower().strip()
    hash_value = hash_value.strip()

    try:
        if algo in _HASHLIB_MAP:
            return _HASHLIB_MAP[algo](password.encode("utf-8")).hexdigest() == hash_value.lower()

        if algo == "bcrypt":
            if _BCRYPT_BACKEND == "passlib":
                return _passlib_bcrypt.verify(password, hash_value)
            if _BCRYPT_BACKEND == "bcrypt":
                return _bcrypt_lib.checkpw(password.encode(), hash_value.encode())
            raise RuntimeError("bcrypt library not available")

        if algo == "pbkdf2_sha256":
            if _PBKDF2_BACKEND == "passlib":
                return _passlib_pbkdf2.verify(password, hash_value)
            if hash_value.startswith("pbkdf2:"):
                import base64
                _, b64_salt, b64_dk = hash_value.split(":")
                salt = base64.b64decode(b64_salt)
                stored_dk = base64.b64decode(b64_dk)
                new_dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260000)
                return new_dk == stored_dk
            return False

        raise ValueError(f"Unsupported algorithm: {algorithm}")

    except (ValueError, RuntimeError):
        raise
    except Exception:
        return False


def algorithm_available(algorithm: str) -> tuple:
    """Returns (available: bool, reason: str)."""
    algo = algorithm.lower().strip()
    if algo in _HASHLIB_MAP:
        return True, "ok"
    if algo == "bcrypt":
        if _BCRYPT_BACKEND:
            return True, "ok"
        return False, "Install passlib or bcrypt: pip install passlib"
    if algo == "pbkdf2_sha256":
        return True, "ok"
    return False, f"Unknown algorithm: {algorithm}"