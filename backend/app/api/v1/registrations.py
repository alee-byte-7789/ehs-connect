"""Registration approval endpoints — Housing Office Admin and Super Admin only,
per the Role Permissions Matrix (roadmap Section 11)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, require_admin_roles
from app.models.enums import AdminRole
from app.schemas.admin import RegistrationApprovedOut, RegistrationRejectedOut
from app.schemas.resident import ResidentOut
from app.services import registration_service
from app.services.errors import ConflictError, InvalidStateError, NotFoundError

router = APIRouter(prefix="/registrations", tags=["registrations"])

_approver_roles = (AdminRole.HOUSING_OFFICE, AdminRole.SUPER_ADMIN)


@router.get("/pending", response_model=list[ResidentOut])
def list_pending(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin_roles(*_approver_roles)),
) -> list[ResidentOut]:
    return registration_service.list_pending(db)


@router.post("/{resident_id}/approve", response_model=RegistrationApprovedOut)
def approve(
    resident_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin_roles(*_approver_roles)),
) -> RegistrationApprovedOut:
    try:
        resident = registration_service.approve(db, resident_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (ConflictError, InvalidStateError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return RegistrationApprovedOut(
        message=f"Resident approved as {resident.resident_code}.",
        resident=resident,
    )


@router.post("/{resident_id}/reject", response_model=RegistrationRejectedOut)
def reject(
    resident_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin_roles(*_approver_roles)),
) -> RegistrationRejectedOut:
    try:
        resident = registration_service.reject(db, resident_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return RegistrationRejectedOut(message="Registration rejected.", resident_id=resident.id)
