"""Complaint model — the central entity of the whole system."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ComplaintCategory, ComplaintStatus


class Complaint(Base):
    """
    A single complaint raised by a resident.

    Status transitions are NOT free-form: they follow the state machine in
    PROJECT_ROADMAP.md Section 7 and are enforced in the service layer, not
    just the UI, so a malicious or buggy client cannot skip steps by calling
    the API directly.

    `close_count` enforces business rule #1: a resident may close a
    complaint exactly once. After a Reopen, only an Admin role may close it
    again (rule #2) — that second close does NOT increment close_count
    further since it is no longer the resident's action.

    `photo_urls` stores a JSON-encoded list of uploaded photo URLs as a
    plain string column to keep this schema portable across SQLite (dev)
    and PostgreSQL (prod) without relying on Postgres-only ARRAY/JSONB types
    at this stage.
    """
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)

    resident_id: Mapped[int] = mapped_column(ForeignKey("residents.id"), nullable=False)
    house_id: Mapped[int] = mapped_column(ForeignKey("houses.id"), nullable=False)

    category: Mapped[ComplaintCategory] = mapped_column(Enum(ComplaintCategory), nullable=False)
    subcategory: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    photo_urls: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON-encoded list

    status: Mapped[ComplaintStatus] = mapped_column(
        Enum(ComplaintStatus), default=ComplaintStatus.PENDING, nullable=False, index=True
    )

    assigned_staff_id: Mapped[int | None] = mapped_column(ForeignKey("staff.id"), nullable=True)

    # Guards business rule: resident may close exactly once.
    close_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    resident: Mapped["Resident"] = relationship(back_populates="complaints")
    house: Mapped["House"] = relationship(back_populates="complaints")
    assigned_staff: Mapped["Staff | None"] = relationship(back_populates="assigned_complaints")
    history: Mapped[list["ComplaintHistory"]] = relationship(
        back_populates="complaint", order_by="ComplaintHistory.timestamp"
    )
    feedback: Mapped["Feedback | None"] = relationship(back_populates="complaint", uselist=False)

    def __repr__(self) -> str:
        return f"<Complaint {self.complaint_code} [{self.status.value}]>"
