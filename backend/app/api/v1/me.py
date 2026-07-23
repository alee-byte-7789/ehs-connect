"""Small `/me` endpoints — mainly exist so the auth dependencies have a
protected route to be exercised against in tests. Real profile screens
land properly in Module 4/5."""
from fastapi import APIRouter, Depends

from app.api.v1.deps import get_current_admin, get_current_resident
from app.models.admin import Admin
from app.models.resident import Resident
from app.schemas.admin import AdminOut
from app.schemas.resident import ResidentOut

router = APIRouter(tags=["me"])


@router.get("/residents/me", response_model=ResidentOut)
def resident_me(resident: Resident = Depends(get_current_resident)) -> ResidentOut:
    return resident


@router.get("/admins/me", response_model=AdminOut)
def admin_me(admin: Admin = Depends(get_current_admin)) -> AdminOut:
    return admin
