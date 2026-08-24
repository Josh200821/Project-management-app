"""JWT, password hashing, API key management."""
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

import bcrypt
from jose import JWTError, jwt

from app.config import settings


@lru_cache
def _load_key(path: str) -> str:
    return Path(path).read_text()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(subject: str, extra: dict | None = None) -> str:
    payload = {
        "sub": subject,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access",
        **(extra or {}),
    }
    private_key = _load_key(settings.JWT_PRIVATE_KEY_PATH)
    return jwt.encode(payload, private_key, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    payload = {
        "sub": subject,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
    }
    private_key = _load_key(settings.JWT_PRIVATE_KEY_PATH)
    return jwt.encode(payload, private_key, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decodes and verifies a JWT. Returns None (rather than raising) on any failure
    so callers can use a simple `if not payload:` check."""
    try:
        public_key = _load_key(settings.JWT_PUBLIC_KEY_PATH)
        return jwt.decode(token, public_key, algorithms=[settings.JWT_ALGORITHM])
    except (JWTError, OSError):
        return None


def create_password_reset_token(user_id: str) -> str:
    """Self-contained, stateless reset token — no DB column needed to store it."""
    payload = {
        "sub": user_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "type": "password_reset",
    }
    private_key = _load_key(settings.JWT_PRIVATE_KEY_PATH)
    return jwt.encode(payload, private_key, algorithm=settings.JWT_ALGORITHM)


def decode_password_reset_token(token: str) -> str | None:
    """Returns the user id encoded in a password-reset token, or None if invalid/expired/wrong type."""
    payload = decode_access_token(token)
    if not payload or payload.get("type") != "password_reset":
        return None
    sub = payload.get("sub")
    return sub if isinstance(sub, str) else None


def generate_api_key() -> tuple[str, str, str]:
    """Returns (raw_key, hashed_key, prefix). Store only the hash and prefix."""
    raw = f"sk_{secrets.token_urlsafe(32)}"
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    prefix = raw[:8]
    return raw, hashed, prefix


def verify_api_key(raw: str, stored_hash: str) -> bool:
    return hashlib.sha256(raw.encode()).hexdigest() == stored_hash