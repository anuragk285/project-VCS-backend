from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.cloth import ClothingCategory
from app.schemas.cloth import ClothCreate, ClothResponse


@pytest.fixture
def valid_cloth_data():
    return {
        "name": "Cotton Shirt",
        "brand": "ABC",
        "colour": "Blue",
        "colour_hex": "#0000FF",
        "pattern": "Plain",
        "unit_price": Decimal("499.00"),
        "clothing_category": "shirt",
    }


def test_cloth_create_accepts_valid_data(valid_cloth_data):
    cloth = ClothCreate(**valid_cloth_data)

    assert cloth.name == "Cotton Shirt"
    assert cloth.unit_price == Decimal("499.00")
    assert cloth.clothing_category == ClothingCategory.shirt
    assert cloth.stock_quantity == Decimal(0)
    assert cloth.images == []


def test_cloth_create_rejects_invalid_category(valid_cloth_data):
    valid_cloth_data["clothing_category"] = "shoes"

    with pytest.raises(ValidationError):
        ClothCreate(**valid_cloth_data)


@pytest.mark.parametrize("field", ["unit_price", "stock_quantity"])
def test_cloth_create_rejects_negative_values(valid_cloth_data, field):
    valid_cloth_data[field] = Decimal(-1)

    with pytest.raises(ValidationError):
        ClothCreate(**valid_cloth_data)


def test_cloth_response_accepts_model_attributes():
    now = datetime.now(UTC)

    class ClothObject:
        def __init__(self):
            self.id = 1
            self.name = "Cotton Shirt"
            self.brand = "ABC"
            self.description = None
            self.touch_feel = None
            self.colour = "Blue"
            self.colour_hex = "#0000FF"
            self.pattern = "Plain"
            self.best_for = []
            self.stock_quantity = Decimal(0)
            self.unit_price = Decimal("499.00")
            self.prev_month_sales = []
            self.images = []
            self.clothing_category = "shirt"
            self.is_active = True
            self.created_at = now
            self.updated_at = now

    response = ClothResponse.model_validate(ClothObject())

    assert response.id == 1
    assert response.name == "Cotton Shirt"
    assert response.clothing_category == ClothingCategory.shirt