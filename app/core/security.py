"""
Security utilities: password hashing with bcrypt and JWT creation/verification.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Union

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


# ── Password hashing ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Return bcrypt hash of the plain-text password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify plain-text password against stored bcrypt hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ── JWT ───────────────────────────────────────────────────────────────────────

def _create_token(
    subject: Union[str, int],
    token_type: str,
    expires_delta: timedelta,
    extra_claims: Optional[dict] = None,
) -> str:
    """Internal: build and sign a JWT with the given claims."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        **(extra_claims or {}),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: int, email: str) -> str:
    """Create a short-lived JWT access token."""
    return _create_token(
        subject=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims={"email": email},
    )


def create_refresh_token(user_id: int) -> str:
    """Create a long-lived JWT refresh token."""
    return _create_token(
        subject=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT. Raises JWTError on failure.
    Returns the raw payload dict.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def get_user_id_from_token(token: str) -> Optional[int]:
    """Extract the integer user id from a valid access token, or None."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None
