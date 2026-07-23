"""
Password hashing and JWT helpers.

This is the ONLY module that touches passlib/jose directly — every other
layer (services, routers) calls these functions instead of rolling its own
hashing or token logic, so there is exactly one place to audit or rotate
algorithms.
"""
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Password hashing ---

def hash_password(plain_password: str) -> str:
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return _pwd_context.verify(plain_password, password_hash)


# --- JWT ---

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class SubjectType(str, Enum):
    RESIDENT = "resident"
    ADMIN = "admin"


class InvalidTokenError(Exception):
    """Raised for any token that fails to decode, is malformed, or is expired."""


def create_access_token(subject_id: int, subject_type: SubjectType, role: str) -> str:
    """
    `role` is `resident_type` ("owner"/"tenant") for residents, or the admin
    `AdminRole` value for admins. It rides in the token so every protected
    endpoint can check permissions from the token claims first, then
    re-verify against the DB for privilege-sensitive actions (never trust
    the token alone for those — see roadmap Section 2, "Auth").
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(subject_id),
        "type": subject_type.value,
        "role": role,
        "token_type": TokenType.ACCESS.value,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject_id: int, subject_type: SubjectType, jti: str | None = None) -> tuple[str, str, datetime]:
    """
    Returns (token, jti, expires_at). The caller (auth service) persists
    `jti` in the `refresh_tokens` table so it can be revoked/rotated —
    the JWT signature alone can't be invalidated before its natural expiry.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.refresh_token_expire_days)
    jti = jti or str(uuid.uuid4())
    payload = {
        "sub": str(subject_id),
        "type": subject_type.value,
        "token_type": TokenType.REFRESH.value,
        "jti": jti,
        "iat": now,
        "exp": expire,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, jti, expire


def decode_token(token: str) -> dict[str, Any]:
    """Decodes and verifies signature + expiry. Raises InvalidTokenError on any failure."""
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise InvalidTokenError(str(exc)) from exc
