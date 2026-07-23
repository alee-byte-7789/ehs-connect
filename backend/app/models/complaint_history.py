"""ComplaintHistory model — an append-only audit trail. Rows are never updated or deleted."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ChangedByType, ComplaintStatus


class ComplaintHistory(Base):
    """
    One row per status transition on a complaint. Business rule #3
    (roadmap Section 7): every transition writes a history row, and history
    is never mutated — this is the full audit trail an admin or resident can
    review on the Complaint Detail / Timeline screen.
    """
    __tablename__ = "complaint_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)

    from_status: Mapped[ComplaintStatus | None] = mapped_column(Enum(ComplaintStatus), nullable=True)
    to_status: Mapped[ComplaintStatus] = mapped_column(Enum(ComplaintStatus), nullable=False)

    changed_by_type: Mapped[ChangedByType] = mapped_column(Enum(ChangedByType), nullable=False)
    changed_by_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    complaint: Mapped["Complaint"] = relationship(back_populates="history")

    def __repr__(self) -> str:
        return f"<ComplaintHistory complaint={self.complaint_id} {self.from_status}->{self.to_status}>"
