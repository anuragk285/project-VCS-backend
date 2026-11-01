from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.json_column import PydanticJSON
from app.schemas.order_json import Measurements, Notes, OrderLine, StitchingLine

CLOTH_ORDER_HOLD_DAYS = 1  # a booking is held for 24 hours
STITCHING_DEFAULT_DAYS = 5


class ClothOrderStatus(StrEnum):
    order_placed = "order_placed"
    order_confirmed = "order_confirmed"
    ready_for_pickup = "ready_for_pickup"
    completed = "completed"
    cancelled = "cancelled"
    expired = "expired"


class ClothOrderSource(StrEnum):
    webpage = "webpage"
    whatsapp = "whatsapp"
    store = "store"


class StitchingStatus(StrEnum):
    waiting_for_cloth = "waiting_for_cloth"
    queued = "queued"
    in_progress = "in_progress"
    ready = "ready"
    delivered = "delivered"
    cancelled = "cancelled"


def one_of(column: str, values: type[StrEnum]) -> str:
    return f"{column} IN ({', '.join(repr(v.value) for v in values)})"


def days_from_now(days: int) -> datetime:
    return datetime.now(UTC) + timedelta(days=days)


class ClothOrder(Base):
    __tablename__ = "cloth_orders"
    __table_args__ = (
        CheckConstraint(one_of("status", ClothOrderStatus), name="status_valid"),
        CheckConstraint(one_of("source", ClothOrderSource), name="source_valid"),
        CheckConstraint("total_amount >= 0", name="total_not_negative"),
        CheckConstraint("gst_percent >= 0 AND gst_percent <= 100", name="gst_percent_valid"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    customer = relationship("Customer", back_populates="orders")
    
    items: Mapped[list[OrderLine]] = mapped_column(PydanticJSON(list[OrderLine]))
    status: Mapped[str] = mapped_column(String(30), default=ClothOrderStatus.order_placed)
    source: Mapped[str] = mapped_column(String(20), default=ClothOrderSource.webpage)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: days_from_now(CLOTH_ORDER_HOLD_DAYS)
    )

    total_cloth_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal(0))
    gst_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal(0))  
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal(0))


class StitchingOrder(Base):
    __tablename__ = "stitching_orders"
    __table_args__ = (CheckConstraint(one_of("status", StitchingStatus), name="status_valid"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cloth_order_id: Mapped[int] = mapped_column(ForeignKey("cloth_orders.id"), index=True)
    tailor_id: Mapped[int | None] = mapped_column(ForeignKey("tailors.id"), index=True)

    items: Mapped[list[StitchingLine]] = mapped_column(PydanticJSON(list[StitchingLine]))
    cloth_measurements: Mapped[Measurements] = mapped_column(PydanticJSON(Measurements), default=dict)
    stitching_description: Mapped[Notes] = mapped_column(PydanticJSON(Notes), default=dict)
    status: Mapped[str] = mapped_column(String(30), default=StitchingStatus.waiting_for_cloth)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expected_finishing_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: days_from_now(STITCHING_DEFAULT_DAYS)
    )

    cloth_order = relationship("ClothOrder")
    tailor = relationship("Tailor", back_populates="stitching_orders")
    
    @property
    def total_stitching_cost(self) -> Decimal:
        return sum((line.stitching_cost for line in self.items), Decimal(0))
