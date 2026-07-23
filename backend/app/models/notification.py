"""Notification model — backs the in-app Notification Center on both frontends.

Actual push delivery (FCM) is a separate concern handled in Module 7; this
table is the durable, queryable record of what was sent and whether it has
been read, independent of whether the push itself succeeded.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import NotificationRecipientType


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipient_type: Mapped[NotificationRecipientType] = mapped_column(
        Enum(NotificationRecipientType), nullable=False
    )
    recipient_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "complaint_status", "registration", "critical_alert"

    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<Notification to={self.recipient_type.value}:{self.recipient_id} '{self.title}'>"
