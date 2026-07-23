"""Admin model — staff of the Housing Office with elevated system roles."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import AdminRole


class Admin(Base):
    """
    An administrative user. The `role` field drives every permission check
    against the Role Permissions Matrix in PROJECT_ROADMAP.md Section 11 —
    checked server-side on every protected endpoint, never trusted from the
    JWT claim alone for privilege-sensitive actions.
    """
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[AdminRole] = mapped_column(Enum(AdminRole), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<Admin {self.email} ({self.role.value})>"
