from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, false, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserRoles(StrEnum):
    admin = "admin"
    merchant = "merchant"
    tailor = "tailor"
    customer = "customer"


class User(Base):
    """A login. A user needs an email, a phone number, or both.

    Email is verified by a link (email_verified). A phone number is accepted without OTP for now.
    Signup code must store emails in lower case and phone numbers in one fixed format, and use
    None, never "", for a missing value.
    """

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            f"role IN ({', '.join(repr(role.value) for role in UserRoles)})",
            name="role_valid",
        ),
        CheckConstraint(
            "COALESCE(email, '') <> '' OR COALESCE(phone, '') <> ''",
            name="email_or_phone_required",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(String(20), default=UserRoles.customer)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(15), unique=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    password_hash: Mapped[str] = mapped_column(String(255))  # argon2 hashes are about 100 characters
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )