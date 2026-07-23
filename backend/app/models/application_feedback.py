"""ApplicationFeedback model — feedback about the app itself, not about a specific complaint."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ApplicationFeedbackType


class ApplicationFeedback(Base):
    """Bug reports, suggestions, and feature requests submitted by residents
    about the app itself (distinct from per-complaint Feedback)."""
    __tablename__ = "application_feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    resident_id: Mapped[int] = mapped_column(ForeignKey("residents.id"), nullable=False)
    type: Mapped[ApplicationFeedbackType] = mapped_column(Enum(ApplicationFeedbackType), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    resident: Mapped["Resident"] = relationship(back_populates="application_feedback_entries")

    def __repr__(self) -> str:
        return f"<ApplicationFeedback {self.type.value} by resident={self.resident_id}>"
