"""Security utilities — password hashing (bcrypt) and JWT token management."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings

# ── Password Hashing ─────────────────────────────────────────


def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt with 12 rounds of salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ── JWT Token ─────────────────────────────────────────────────

_ALGORITHM = "HS256"


def create_access_token(user_id: int) -> str:
    """Sign a JWT containing the user ID as subject.

    Payload:
        sub  — user_id (str)
        exp  — expiration timestamp
        iat  — issued-at timestamp
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "exp": now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
        "iat": now,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT.

    Returns the full payload dict on success.

    Raises:
        jwt.ExpiredSignatureError  — token has expired
        jwt.InvalidTokenError      — token is malformed or signature invalid
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[_ALGORITHM])
