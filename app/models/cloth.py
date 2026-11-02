from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.json_column import PydanticJSON
from app.schemas.cloth_json import BestFor, ImageUrls, MonthlySales


class ClothingCategory(StrEnum):
    shirt = "shirt"
    pant = "pant"
    towel = "towel"


class Cloth(Base):
    __tablename__ = "cloths"
    __table_args__ = (
        CheckConstraint("stock_quantity >= 0", name="stock_not_negative"),
        CheckConstraint("unit_price >= 0", name="price_not_negative"),
        CheckConstraint("clothing_category IN ('shirt', 'pant')", name="category_shirt_or_pant"),
        Index("ix_cloths_category_active", "clothing_category", "is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    brand: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    touch_feel: Mapped[str | None] = mapped_column(Text)

    colour: Mapped[str] = mapped_column(String(40))
    colour_hex: Mapped[str] = mapped_column(String(7))
    pattern: Mapped[str] = mapped_column(String(40))
    best_for: Mapped[BestFor] = mapped_column(PydanticJSON(BestFor), default=list)  # ["wedding", "casual", ...]

    stock_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal(0))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    prev_month_sales: Mapped[MonthlySales] = mapped_column(PydanticJSON(MonthlySales), default=list)  # metres sold, one per month, newest last

    images: Mapped[ImageUrls] = mapped_column(PydanticJSON(ImageUrls), default=list)
    clothing_category: Mapped[str] = mapped_column(String(10))  # "shirt", "pant" or "towel"

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
