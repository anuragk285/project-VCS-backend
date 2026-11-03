import json
import math
from decimal import Decimal

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import Session

from app.models import Cloth, ClothingCategory


def escape_like(text: str) -> str:
    """Stops %, _ and \\ typed by a user from acting as search wildcards."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def list_cloths(
    db: Session,
    *,
    category: ClothingCategory | None = None,
    colour: str | None = None,
    pattern: str | None = None,
    best_for: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    in_stock: bool | None = None,
    search_text: str | None = None,
    page_no: int = 1,
    page_size: int = 12,
) -> dict:
    conditions = [Cloth.is_active.is_(True)]

    if category is not None:
        conditions.append(Cloth.clothing_category == category.value)
    if colour:
        conditions.append(func.lower(Cloth.colour) == colour.strip().lower())
    if pattern:
        conditions.append(func.lower(Cloth.pattern) == pattern.strip().lower())
    if best_for:
        tag = escape_like(json.dumps(best_for.strip().lower()))
        conditions.append(func.lower(cast(Cloth.best_for, String)).like(f"%{tag}%", escape="\\"))
    if min_price is not None:
        conditions.append(Cloth.unit_price >= min_price)
    if max_price is not None:
        conditions.append(Cloth.unit_price <= max_price)
    if in_stock is True:
        conditions.append(Cloth.stock_quantity > 0)
    elif in_stock is False:
        conditions.append(Cloth.stock_quantity <= 0)
    if search_text and search_text.strip():
        for word in search_text.split():
            like = f"%{escape_like(word.lower())}%"
            conditions.append(
                or_(
                    func.lower(Cloth.name).like(like, escape="\\"),
                    func.lower(func.coalesce(Cloth.brand, "")).like(like, escape="\\"),
                    func.lower(Cloth.colour).like(like, escape="\\"),
                    func.lower(func.coalesce(Cloth.pattern, "")).like(like, escape="\\"),
                )
            )

    total_cloths = db.scalar(select(func.count()).select_from(Cloth).where(*conditions)) or 0
    items = db.scalars(
        select(Cloth)
        .where(*conditions)
        .order_by(Cloth.id)
        .limit(page_size)
        .offset((page_no - 1) * page_size)
    ).all()

    return {
        "items": items,
        "total_cloths": total_cloths,
        "page_no": page_no,
        "page_size": page_size,
        "total_pages": math.ceil(total_cloths / page_size) if total_cloths else 0,
    }

def single_cloth(db: Session, *, id: int) -> Cloth | None:
    if id <= 0:
        return None
    stmt = select(Cloth).where(
        Cloth.id == id,
        Cloth.is_active.is_(True),
    )
    return db.scalars(stmt).first()
