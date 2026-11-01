from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

JsonType = JSON().with_variant(JSONB(), "postgresql")

class ClothingCategory(StrEnum):
    shirt = "shirt"
    pant = "pant"
    towel = "towel"

class Cloth(Base):
    __tablename__ = "cloths"
    __table_args__ = (
        CheckConstraint("stock_quantity >= 0", name="stock_not_negative"),
        CheckConstraint("unit_price >= 0", name="price_not_negative"),
        CheckConstraint("clothing_category IN ('shirt', 'pant', 'towel')", name="category_shirt_or_pant"),
        Index("ix_cloths_category_active", "clothing_category", "is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    brand: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    touch_feel: Mapped[str | None] = mapped_column(Text)

    colour: Mapped[str] = mapped_column(String(40))
    colour_hex: Mapped[str] = mapped_column(String(7))  # used for swatches and the 3D model
    pattern: Mapped[str] = mapped_column(String(40))  # plain, checks, stripes, printed design etc...
    best_for: Mapped[list[str]] = mapped_column(JsonType, default=list)  # ["wedding", "casual", etc...]

    stock_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal(0))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    prev_month_sales: Mapped[list[float]] = mapped_column(JsonType, default=list)  # metres sold in a month list, one per month, newest last at index = -1

    images: Mapped[list[str]] = mapped_column(JsonType, default=list)
    clothing_category: Mapped[str] = mapped_column(String(10))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
