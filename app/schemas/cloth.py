from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.models.cloth import ClothingCategory


class ClothCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    brand: str | None = Field(default=None, max_length=100)
    description: str | None = None
    touch_feel: str | None = None

    colour: str = Field(min_length=1, max_length=40)
    colour_hex: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    pattern: str = Field(min_length=1, max_length=40)
    best_for: list[str] = Field(default_factory=list)

    stock_quantity: Decimal = Field(
        default=Decimal(0), ge=0, max_digits=10, decimal_places=2
    )
    unit_price: Decimal = Field(
        ge=0, max_digits=12, decimal_places=2
    )
    prev_month_sales: list[float] = Field(default_factory=list)

    images: list[str] = Field(default_factory=list)
    clothing_category: ClothingCategory

    is_active: bool = True


class ClothResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    brand: str | None
    description: str | None
    touch_feel: str | None

    colour: str
    colour_hex: str
    pattern: str
    best_for: list[str]

    stock_quantity: Decimal
    unit_price: Decimal

    images: list[str]
    clothing_category: ClothingCategory
    is_active: bool

    @computed_field
    @property
    def in_stock(self) -> bool:
        return self.stock_quantity > 0
    

class ClothPage(BaseModel):
    items: list[ClothResponse]
    total_cloths: int
    page_size: int
    page_no: int
    total_pages: int