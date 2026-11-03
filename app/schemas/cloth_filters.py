from decimal import Decimal

from pydantic import BaseModel


class PriceRange(BaseModel):
    min: Decimal | None
    max: Decimal | None


class ClothFiltersResponse(BaseModel):
    colours: list[str]
    patterns: list[str]
    best_for: list[str]
    price_range: PriceRange