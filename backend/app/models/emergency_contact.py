"""EmergencyContact model — quick-dial numbers shown on the resident app's Emergency screen."""
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EmergencyContact(Base):
    """A single emergency contact entry (e.g. "Fire", "Ambulance", "Security
    Gate"). Managed by admins, read-only for residents."""
    __tablename__ = "emergency_contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(60), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<EmergencyContact {self.label}: {self.phone_number}>"
