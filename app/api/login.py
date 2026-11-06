from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.login import LoginRequest, MeResponse, TokenResponse
from app.services import login as login_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    user = login_service.authenticate_user(db, data.identifier, data.password)
    if user is None:
        # One message for every failure, so nobody can find out which accounts exist.
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Incorrect phone, email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(
        access_token=create_access_token(user.id, user.role),
        role=user.role,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=MeResponse)
def me(user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return MeResponse(
        user_id=user.id,
        role=user.role,
        email=user.email,
        phone=user.phone,
        email_verified=user.email_verified,
        profile=login_service.get_profile(db, user),
    )
