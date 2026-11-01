"""Shapes of the JSON columns on the order tables. One place to change them."""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class OrderLine(BaseModel):
    """One cloth in an order. unit_price is the price at booking time."""
    model_config = ConfigDict(frozen=True)
    cloth_id: int
    length: Decimal = Field(gt=0, description="metres (pieces for towels)")
    unit_price: Decimal = Field(ge=0)


class StitchingLine(BaseModel):
    model_config = ConfigDict(frozen=True)
    cloth_id: int
    garment: str  # "shirt" or "pant"
    length: Decimal = Field(gt=0)
    stitching_cost: Decimal = Field(ge=0, description="rupees, price fixed when the order is made")

Measurements = dict[str, dict[str, Decimal]]  # {"12": {"chest": 40, "waist": 34}}
Notes = dict[str, str]  # {"12": "slim fit, no pocket"}

# A customer's saved measurements, keyed by garment: {"shirt": {"chest": 40}}
CustomerMeasurements = dict[str, dict[str, Decimal]]
