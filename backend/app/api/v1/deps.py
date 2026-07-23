"""
Shared FastAPI dependencies: DB session + auth extraction + RBAC.

`require_admin_roles(...)` re-checks the admin's role against the live DB
row (via `get_current_admin`) on every call — the JWT's `role` claim is
convenient for the client, but privilege-sensitive endpoints never trust it
alone, per roadmap Section 2.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import InvalidTokenError, SubjectType, TokenType, decode_token
from app.models.admin import Admin
from app.models.enums import AdminRole, VerificationStatus
from app.models.resident import Resident
from app.repositories import admin_repository, resident_repository

__all__ = ["get_db", "get_current_resident", "get_current_admin", "require_admin_roles"]

_bearer_scheme = HTTPBearer(auto_error=True)


def _decode_access_token(credentials: HTTPAuthorizationCredentials) -> dict:
    try:
        payload = decode_token(credentials.credentials)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if payload.get("token_type") != TokenType.ACCESS.value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not an access token.")

    return payload


def get_current_resident(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> Resident:
    payload = _decode_access_token(credentials)
    if payload.get("type") != SubjectType.RESIDENT.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="A resident account is required.")

    resident = resident_repository.get_by_id(db, int(payload["sub"]))
    if not resident or resident.verification_status != VerificationStatus.APPROVED:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account not found or not active.")

    return resident


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> Admin:
    payload = _decode_access_token(credentials)
    if payload.get("type") != SubjectType.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="An admin account is required.")

    admin = admin_repository.get_by_id(db, int(payload["sub"]))
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account not found.")

    return admin


def require_admin_roles(*roles: AdminRole):
    """Dependency factory: only admins whose (DB-verified) role is in `roles` may proceed.

    Usage: `Depends(require_admin_roles(AdminRole.IT_ADMIN, AdminRole.SUPER_ADMIN))`
    """
    def _dependency(admin: Admin = Depends(get_current_admin)) -> Admin:
        if admin.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {[r.value for r in roles]}",
            )
        return admin

    return _dependency
