"""Feedback model — resident's post-resolution rating for a specific complaint."""
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Feedback(Base):
    """One optional feedback entry per complaint, given only after resolution
    (enforced at the service layer, not the DB — the DB only enforces the
    1:1 relationship via `uselist=False` on the Complaint side)."""
    __tablename__ = "feedback"
    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 5", name="ck_feedback_rating_range"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), unique=True, nullable=False)
    resident_id: Mapped[int] = mapped_column(ForeignKey("residents.id"), nullable=False)

    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    complaint: Mapped["Complaint"] = relationship(back_populates="feedback")
    resident: Mapped["Resident"] = relationship(back_populates="feedback_entries")

    def __repr__(self) -> str:
        return f"<Feedback complaint={self.complaint_id} rating={self.rating}>"
