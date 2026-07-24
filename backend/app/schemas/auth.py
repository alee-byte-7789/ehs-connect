"""
Auth-related Pydantic schemas.

`RegisterRequest` encodes the registration flow's two independent facts
about a resident:

    Are you an AWC Employee?           (affects: employee_number required)
      YES -> collect employee_number
      NO  -> employee_number omitted

    Are you a tenant?                  (affects: resident_type + owner fields)
      YES -> collect owner_house_number, owner_name,
             owner_cnic, owner_mobile_number   (resident_type = TENANT)
      NO  -> no extra fields                    (resident_type = OWNER)

These two questions are independent — an AWC employee can also be a
tenant (e.g. an employee who rents rather than owns their house). Earlier
drafts of this schema incorrectly treated "employee" as implying "owner";
that was a real modeling mistake, not a deliberate business rule, and has
been removed.

`resident_type` is derived server-side from `is_tenant` alone, rather than
accepted directly from the client, so a client can't submit
`resident_type=owner` while also sending tenant-only fields (or vice versa)
and end up in an inconsistent state.
"""
from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.enums import VerificationStatus


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    house_number: str = Field(min_length=1, max_length=20, description='e.g. "B-026"')
    mobile_number: str = Field(min_length=7, max_length=20)
    email: str | None = None
    password: str = Field(min_length=8, max_length=128)

    is_awc_employee: bool
    employee_number: str | None = None

    is_tenant: bool = False
    owner_house_number: str | None = None
    owner_name: str | None = None
    owner_cnic: str | None = None
    owner_mobile_number: str | None = None

    @field_validator("house_number")
    @classmethod
    def normalize_house_number(cls, v: str) -> str:
        return v.strip().upper()

    @model_validator(mode="after")
    def validate_branches(self) -> "RegisterRequest":
        if self.is_awc_employee and not self.employee_number:
            raise ValueError("employee_number is required when is_awc_employee is true.")

        if not self.is_awc_employee and self.employee_number:
            raise ValueError("employee_number must be omitted unless is_awc_employee is true.")

        if self.is_tenant:
            required = {
                "owner_house_number": self.owner_house_number,
                "owner_name": self.owner_name,
                "owner_cnic": self.owner_cnic,
                "owner_mobile_number": self.owner_mobile_number,
            }
            missing = [name for name, value in required.items() if not value]
            if missing:
                raise ValueError(f"Tenant registration requires: {', '.join(missing)}")
        else:
            if any([self.owner_house_number, self.owner_name, self.owner_cnic, self.owner_mobile_number]):
                raise ValueError("Owner details must be omitted unless is_tenant is true.")

        return self


class RegisterResponse(BaseModel):
    message: str
    resident_id: int
    verification_status: VerificationStatus


class LoginRequest(BaseModel):
    """`identifier` accepts either the resident's phone or email."""
    identifier: str
    password: str


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class MessageResponse(BaseModel):
    message: str
