"""RefreshToken model — durable record of issued refresh tokens, keyed by JWT `jti` claim.

A JWT's signature can't be invalidated early. To support real logout and
rotation (roadmap Section 12: "rotated refresh tokens"), every refresh
token's `jti` is stored here. Refresh requests are only honored if the
`jti` exists, is unexpired, and is not yet revoked. On successful refresh
the old row is marked revoked and a new one is inserted (rotation) — so a
stolen refresh token can only be replayed once before detection.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.security import SubjectType


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    jti: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)

    subject_type: Mapped[SubjectType] = mapped_column(Enum(SubjectType), nullable=False)
    subject_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<RefreshToken jti={self.jti} subject={self.subject_type.value}:{self.subject_id} revoked={self.revoked}>"
