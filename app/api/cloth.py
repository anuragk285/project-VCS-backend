from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import ClothingCategory
from app.schemas.cloth import ClothPage, ClothResponse
from app.schemas.cloth_filters import ClothFiltersResponse
from app.services import cloth as cloth_service

router = APIRouter(prefix="/cloths", tags=["cloths"])


@router.get("", response_model=ClothPage)
def get_cloths(
    db: Annotated[Session, Depends(get_db)],
    category: Annotated[ClothingCategory | None, Query(description="shirt or pant")] = None,
    colour: Annotated[str | None, Query(description="Exact colour name, for example Navy")] = None,
    pattern: Annotated[str | None, Query(description="Exact pattern, for example 'Checks' ")] = None,
    best_for: Annotated[str | None, Query(description="One occasion tag, for example 'wedding' ")] = None,
    min_price: Annotated[Decimal | None, Query(ge=0, description="Lowest price per metre")] = None,
    max_price: Annotated[Decimal | None, Query(ge=0, description="Highest price per metre")] = None,
    in_stock: Annotated[bool | None, Query(description="true: only cloth in stock")] = None,
    search_text: Annotated[str | None, Query(max_length=100, description="Search name, brand and colour")] = None,
    page_no: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 12,
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=422, detail="min_price cannot be more than max_price")
    return cloth_service.list_cloths(
        db,
        category=category,
        colour=colour,
        pattern=pattern,
        best_for=best_for,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        search_text=search_text,
        page_no=page_no,
        page_size=page_size,
    )

@router.get("/filters", response_model=ClothFiltersResponse)
def get_cloth_filters(db: Annotated[Session, Depends(get_db)]):
    return cloth_service.get_cloth_filters(db)


@router.get("/{id}", response_model=ClothResponse)
def get_cloth_(id: int, db: Annotated[Session, Depends(get_db)]):
    cloth = cloth_service.single_cloth(db=db, id=id)

    if not cloth:
        raise HTTPException(
            status_code=404,
            detail=f"No cloth found with id = {id}",
        )

    return cloth