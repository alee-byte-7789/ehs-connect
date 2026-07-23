"""House model — the root entity every resident belongs to."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class House(Base):
    """
    A single housing unit in the society.

    `house_code` (e.g. "EHS-B-026") is permanent and never reused. Resident
    codes are derived from it (see Resident model / ID generation rule in
    PROJECT_ROADMAP.md Section 6.3).
    """
    __tablename__ = "houses"

    id: Mapped[int] = mapped_column(primary_key=True)
    house_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    block: Mapped[str] = mapped_column(String(10), nullable=False)
    address_meta: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    residents: Mapped[list["Resident"]] = relationship(back_populates="house")
    complaints: Mapped[list["Complaint"]] = relationship(back_populates="house")

    def __repr__(self) -> str:
        return f"<House {self.house_code}>"
