"""
Auth service — all authentication business logic lives here, not in the
routers. Routers only translate HTTP <-> service calls and map exceptions
to status codes.
"""
from sqlalchemy.orm import Session

from app.core.security import (
    SubjectType,
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
    InvalidTokenError,
)
from app.models.enums import ResidentType, VerificationStatus
from app.models.resident import Resident
from app.models.admin import Admin
from app.repositories import (
    admin_repository,
    house_repository,
    refresh_token_repository,
    resident_repository,
)
from app.schemas.auth import RegisterRequest, TokenPair
from app.services.errors import AuthenticationError, ConflictError
from app.services.id_generation import build_house_code


def register_resident(db: Session, req: RegisterRequest) -> Resident:
    """
    Creates the House (if it doesn't exist yet) and a Resident row in
    `pending` status. No resident_code is assigned here — that only
    happens on admin approval (see registration_service.approve).
    """
    if resident_repository.phone_or_email_taken(db, req.mobile_number, req.email):
        raise ConflictError("A resident with this phone or email is already registered.")

    house_code, block = build_house_code(req.house_number)
    house = house_repository.get_or_create(db, house_code=house_code, block=block)

    resident_type = ResidentType.TENANT if req.is_tenant else ResidentType.OWNER

    resident = Resident(
        house_id=house.id,
        full_name=req.full_name,
        phone=req.mobile_number,
        email=req.email,
        password_hash=hash_password(req.password),
        resident_type=resident_type,
        is_employee=req.is_awc_employee,
        employee_number=req.employee_number,
        owner_house_number=req.owner_house_number,
        owner_name=req.owner_name,
        owner_cnic=req.owner_cnic,
        owner_phone=req.owner_mobile_number,
        verification_status=VerificationStatus.PENDING,
    )
    db.add(resident)
    db.commit()
    db.refresh(resident)
    return resident


def authenticate_resident(db: Session, identifier: str, password: str) -> Resident:
    resident = resident_repository.get_by_phone_or_email(db, identifier)
    if not resident or not verify_password(password, resident.password_hash):
        raise AuthenticationError("Invalid credentials.")

    if resident.verification_status == VerificationStatus.PENDING:
        raise AuthenticationError("Registration is still pending Housing Office verification.")
    if resident.verification_status == VerificationStatus.REJECTED:
        raise AuthenticationError("Registration was rejected. Contact the Housing Office.")

    return resident


def authenticate_admin(db: Session, email: str, password: str) -> Admin:
    admin = admin_repository.get_by_email(db, email)
    if not admin or not verify_password(password, admin.password_hash):
        raise AuthenticationError("Invalid credentials.")
    return admin


def issue_token_pair(db: Session, subject_id: int, subject_type: SubjectType, role: str) -> TokenPair:
    access_token = create_access_token(subject_id, subject_type, role)
    refresh_token, jti, expires_at = create_refresh_token(subject_id, subject_type)
    refresh_token_repository.create(db, jti=jti, subject_type=subject_type, subject_id=subject_id, expires_at=expires_at)
    db.commit()
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


def refresh_token_pair(db: Session, refresh_token: str) -> TokenPair:
    """
    Verifies the refresh token, checks it against the DB (not revoked, not
    expired), then ROTATES it: the old jti is revoked and a brand new
    access+refresh pair is issued. If a stolen refresh token is replayed
    after the legitimate client already rotated it, this will fail because
    the old jti is already revoked.
    """
    try:
        payload = decode_token(refresh_token)
    except InvalidTokenError as exc:
        raise AuthenticationError("Invalid or expired refresh token.") from exc

    if payload.get("token_type") != TokenType.REFRESH.value:
        raise AuthenticationError("Token is not a refresh token.")

    jti = payload.get("jti")
    row = refresh_token_repository.get_by_jti(db, jti) if jti else None
    if not refresh_token_repository.is_valid(row):
        raise AuthenticationError("Refresh token has been revoked or has expired.")

    subject_id = int(payload["sub"])
    subject_type = SubjectType(payload["type"])

    role = _current_role(db, subject_type, subject_id)

    refresh_token_repository.revoke(db, row)
    new_pair = issue_token_pair(db, subject_id, subject_type, role)
    return new_pair


def revoke_refresh_token(db: Session, refresh_token: str) -> None:
    """Used by /auth/logout. Silently no-ops on an already-invalid token —
    logout should never fail from the client's point of view."""
    try:
        payload = decode_token(refresh_token)
    except InvalidTokenError:
        return

    jti = payload.get("jti")
    if not jti:
        return

    row = refresh_token_repository.get_by_jti(db, jti)
    if row and not row.revoked:
        refresh_token_repository.revoke(db, row)
        db.commit()


def _current_role(db: Session, subject_type: SubjectType, subject_id: int) -> str:
    """Re-reads the role from the DB (not from the old token) so a role
    change or de-activation takes effect on the very next refresh."""
    if subject_type == SubjectType.RESIDENT:
        resident = resident_repository.get_by_id(db, subject_id)
        if not resident or resident.verification_status != VerificationStatus.APPROVED:
            raise AuthenticationError("Account is no longer active.")
        return resident.resident_type.value

    admin = admin_repository.get_by_id(db, subject_id)
    if not admin:
        raise AuthenticationError("Account is no longer active.")
    return admin.role.value
