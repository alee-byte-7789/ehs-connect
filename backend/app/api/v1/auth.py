"""Auth endpoints: registration, login (resident + admin), refresh, logout."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.core.security import SubjectType
from app.schemas.auth import (
    AdminLoginRequest,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenPair,
)
from app.services import auth_service
from app.services.errors import AuthenticationError, ConflictError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    try:
        resident = auth_service.register_resident(db, req)
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return RegisterResponse(
        message="Registration submitted. Awaiting Housing Office verification.",
        resident_id=resident.id,
        verification_status=resident.verification_status,
    )


@router.post("/login", response_model=TokenPair)
def login(req: LoginRequest, db: Session = Depends(get_db)) -> TokenPair:
    try:
        resident = auth_service.authenticate_resident(db, req.identifier, req.password)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    return auth_service.issue_token_pair(db, resident.id, SubjectType.RESIDENT, resident.resident_type.value)


@router.post("/admin/login", response_model=TokenPair)
def admin_login(req: AdminLoginRequest, db: Session = Depends(get_db)) -> TokenPair:
    try:
        admin = auth_service.authenticate_admin(db, req.email, req.password)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    return auth_service.issue_token_pair(db, admin.id, SubjectType.ADMIN, admin.role.value)


@router.post("/refresh", response_model=TokenPair)
def refresh(req: RefreshRequest, db: Session = Depends(get_db)) -> TokenPair:
    try:
        return auth_service.refresh_token_pair(db, req.refresh_token)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/logout", response_model=MessageResponse)
def logout(req: LogoutRequest, db: Session = Depends(get_db)) -> MessageResponse:
    # Always succeeds from the client's point of view, even if the token was
    # already invalid/expired — logout should never surface an error.
    auth_service.revoke_refresh_token(db, req.refresh_token)
    return MessageResponse(message="Logged out.")
