from app.models.base import Base

from enum import StrEnum
from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

class UserRoles(StrEnum):
    admin = "admin"
    merchant = "merchant"
    tailor = "tailor"
    customer = "customer"

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'merchant', 'tailor', 'customer')",name="role_valid",),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
