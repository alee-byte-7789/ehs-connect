"""RefreshToken repository — plain DB access, no business rules."""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.security import SubjectType
from app.models.refresh_token import RefreshToken


def create(db: Session, jti: str, subject_type: SubjectType, subject_id: int, expires_at: datetime) -> RefreshToken:
    row = RefreshToken(jti=jti, subject_type=subject_type, subject_id=subject_id, expires_at=expires_at)
    db.add(row)
    db.flush()
    return row


def get_by_jti(db: Session, jti: str) -> RefreshToken | None:
    return db.query(RefreshToken).filter(RefreshToken.jti == jti).first()


def revoke(db: Session, row: RefreshToken) -> None:
    row.revoked = True
    db.flush()


def is_valid(row: RefreshToken | None) -> bool:
    if row is None or row.revoked:
        return False
    expires_at = row.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at > datetime.now(timezone.utc)
