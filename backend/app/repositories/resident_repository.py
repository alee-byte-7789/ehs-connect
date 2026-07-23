"""Resident repository — plain DB access, no business rules."""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import ResidentType, VerificationStatus
from app.models.resident import Resident


def get_by_id(db: Session, resident_id: int) -> Resident | None:
    return db.query(Resident).filter(Resident.id == resident_id).first()


def get_by_phone_or_email(db: Session, identifier: str) -> Resident | None:
    return (
        db.query(Resident)
        .filter((Resident.phone == identifier) | (Resident.email == identifier))
        .first()
    )


def phone_or_email_taken(db: Session, phone: str, email: str | None) -> bool:
    query = db.query(Resident).filter(Resident.phone == phone)
    if email:
        query = db.query(Resident).filter((Resident.phone == phone) | (Resident.email == email))
    return db.query(query.exists()).scalar()


def list_pending(db: Session) -> list[Resident]:
    return (
        db.query(Resident)
        .filter(Resident.verification_status == VerificationStatus.PENDING)
        .order_by(Resident.created_at)
        .all()
    )


def has_approved_owner(db: Session, house_id: int) -> bool:
    return (
        db.query(Resident)
        .filter(
            Resident.house_id == house_id,
            Resident.resident_type == ResidentType.OWNER,
            Resident.verification_status == VerificationStatus.APPROVED,
        )
        .first()
        is not None
    )


def next_tenant_sequence(db: Session, house_id: int) -> int:
    """Highest existing tenant_sequence for this house (approved or not), plus one.
    Computed from max rather than count so a rejected tenant's number is never reused."""
    current_max = (
        db.query(func.max(Resident.tenant_sequence))
        .filter(Resident.house_id == house_id, Resident.resident_type == ResidentType.TENANT)
        .scalar()
    )
    return (current_max or 0) + 1
