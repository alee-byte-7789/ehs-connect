"""Staff model — maintenance personnel (electricians, plumbers, etc.) assignable to complaints."""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import StaffCategory


class Staff(Base):
    """A maintenance staff member. Staff never log in via the resident/admin
    auth flow in v1 — they are managed by admins and see assigned work only
    through the Admin Portal's "Maintenance Staff" view (see roadmap Section 9)."""
    __tablename__ = "staff"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[StaffCategory] = mapped_column(Enum(StaffCategory), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    assigned_complaints: Mapped[list["Complaint"]] = relationship(back_populates="assigned_staff")

    def __repr__(self) -> str:
        return f"<Staff {self.full_name} ({self.category.value})>"
