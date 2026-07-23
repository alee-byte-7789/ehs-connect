"""Admin output schema and registration-approval action schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import AdminRole
from app.schemas.resident import ResidentOut


class AdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    role: AdminRole
    created_at: datetime


class RegistrationApprovedOut(BaseModel):
    message: str
    resident: ResidentOut


class RegistrationRejectedOut(BaseModel):
    message: str
    resident_id: int
