from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import RegisteredCustomer, RegisterRequest
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisteredCustomer, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Annotated[Session, Depends(get_db)]):
    try:
        user, customer = auth_service.register_customer(db, data)
    except auth_service.AlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This phone number or email is already registered",
        ) from None
    return RegisteredCustomer(
        user_id=user.id,
        customer_id=customer.id,
        role=user.role,
        name=customer.name,
        email=user.email,
        email_verified=user.email_verified,
    )
