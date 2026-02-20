import hashlib

# Optional bcrypt support
try:
    import bcrypt as _bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    try:
        from passlib.hash import bcrypt as _bcrypt_passlib
        BCRYPT_AVAILABLE = "passlib"
    except ImportError:
        BCRYPT_AVAILABLE = False


def hash_password(password: str, algorithm: str) -> str:
    """Hash a password using the specified algorithm."""
    if algorithm == "md5":
        return hashlib.md5(password.encode()).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(password.encode()).hexdigest()
    elif algorithm == "bcrypt":
        if BCRYPT_AVAILABLE is True:
            salt = _bcrypt.gensalt()
            return _bcrypt.hashpw(password.encode(), salt).decode()
        elif BCRYPT_AVAILABLE == "passlib":
            return _bcrypt_passlib.hash(password)
        else:
            raise RuntimeError("bcrypt not available. Install with: pip install bcrypt")
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def verify_password(password: str, hash_value: str, algorithm: str) -> bool:
    """Verify a password against a hash."""
    try:
        if algorithm == "md5":
            return hashlib.md5(password.encode()).hexdigest() == hash_value.lower().strip()
        elif algorithm == "sha256":
            return hashlib.sha256(password.encode()).hexdigest() == hash_value.lower().strip()
        elif algorithm == "bcrypt":
            if BCRYPT_AVAILABLE is True:
                return _bcrypt.checkpw(password.encode(), hash_value.encode())
            elif BCRYPT_AVAILABLE == "passlib":
                return _bcrypt_passlib.verify(password, hash_value)
            else:
                raise RuntimeError("bcrypt not available. Install with: pip install bcrypt")
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    except RuntimeError:
        raise
    except Exception:
        return False


def bcrypt_available() -> bool:
    return BCRYPT_AVAILABLE is not False