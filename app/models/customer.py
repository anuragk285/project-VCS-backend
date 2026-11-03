from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.json_column import PydanticJSON
from app.schemas.order_json import CustomerMeasurements


class Customer(Base):
    """Shop details of a customer. The login (email, password) lives in User."""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(String(300))
    # measurements per garment, e.g. {"shirt": {"chest": 40}, "pant": {"waist": 34}}
    measurements: Mapped[CustomerMeasurements] = mapped_column(
        PydanticJSON(CustomerMeasurements), default=dict
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    user = relationship("User")
    # No "orders" column: the link is ClothOrder.customer_id, and this reads it.
    orders = relationship("ClothOrder", back_populates="customer")
