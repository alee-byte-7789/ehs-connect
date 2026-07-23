"""Admin repository — plain DB access, no business rules."""
from sqlalchemy.orm import Session

from app.models.admin import Admin


def get_by_id(db: Session, admin_id: int) -> Admin | None:
    return db.query(Admin).filter(Admin.id == admin_id).first()


def get_by_email(db: Session, email: str) -> Admin | None:
    return db.query(Admin).filter(Admin.email == email).first()
