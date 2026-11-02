"""Shapes of the JSON columns on the cloths table."""

from decimal import Decimal
from typing import Annotated

from pydantic import Field, StringConstraints

# Occasion tags such as "wedding", "casual". Whitespace is trimmed, empty tags are refused.
Occasion = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=40)]
BestFor = Annotated[list[Occasion], Field(max_length=10)]

ImageUrl = Annotated[str, StringConstraints(pattern=r"^https://", max_length=500)]
ImageUrls = Annotated[list[ImageUrl], Field(max_length=10)]

MonthlySales = list[Annotated[Decimal, Field(ge=0)]]
