"""Resident model — a person living in a house, either its owner or a tenant."""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ResidentType, VerificationStatus


class Resident(Base):
    """
    A registered resident. Fields branch according to the registration flow:

    - Every resident: full_name, phone, optional email, password.
    - AWC employee branch: is_employee=True -> employee_number required.
    - Tenant branch: resident_type=TENANT -> owner_name / owner_cnic /
      owner_phone required (the tenant must identify the house owner).

    `resident_code` (e.g. "EHS-B-026-O" for the owner, "EHS-B-026-T1",
    "EHS-B-026-T2"... for tenants) is generated server-side and ONLY after
    Housing Office approval — never client-side, never pre-verification.
    It is nullable until that approval happens.
    """
    __tablename__ = "residents"

    id: Mapped[int] = mapped_column(primary_key=True)
    resident_code: Mapped[str | None] = mapped_column(String(25), unique=True, index=True, nullable=True)

    house_id: Mapped[int] = mapped_column(ForeignKey("houses.id"), nullable=False)

    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    resident_type: Mapped[ResidentType] = mapped_column(Enum(ResidentType), nullable=False)

    # AWC employee branch
    is_employee: Mapped[bool] = mapped_column(Boolean, default=False)
    employee_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Tenant branch (only populated when resident_type == TENANT)
    owner_house_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    owner_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    owner_cnic: Mapped[str | None] = mapped_column(String(20), nullable=True)
    owner_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False
    )

    # Auto-increments per house for tenants (T1, T2, T3...); unused for owners.
    tenant_sequence: Mapped[int | None] = mapped_column(Integer, nullable=True)

    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    house: Mapped["House"] = relationship(back_populates="residents")
    complaints: Mapped[list["Complaint"]] = relationship(back_populates="resident")
    feedback_entries: Mapped[list["Feedback"]] = relationship(back_populates="resident")
    application_feedback_entries: Mapped[list["ApplicationFeedback"]] = relationship(back_populates="resident")

    def __repr__(self) -> str:
        return f"<Resident {self.resident_code or f'unverified:{self.id}'}>"
