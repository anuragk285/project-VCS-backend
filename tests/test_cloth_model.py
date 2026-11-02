from decimal import Decimal

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Base, Cloth


@pytest.fixture()
def db():
    engine = create_engine("sqlite://")  # in-memory, so tests need no Postgres
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def make_cloth(**changes) -> Cloth:
    data = {
        "name": "Micro Check Shirting · Navy",
        "colour": "Navy",
        "colour_hex": "#2B3A5E",
        "pattern": "checks",
        "best_for": ["formal", "daily work"],
        "stock_quantity": Decimal("36.50"),
        "unit_price": Decimal("380.00"),
        "clothing_category": "shirt",
    }
    data.update(changes)
    return Cloth(**data)


def test_save_and_read_back(db):
    db.add(make_cloth(images=["https://example.com/a.jpg"], prev_month_sales=[12.5, 8.0]))
    db.commit()
    cloth = db.scalars(select(Cloth)).one()
    assert cloth.stock_quantity == Decimal("36.50")
    assert cloth.unit_price == Decimal("380.00")
    assert cloth.best_for == ["formal", "daily work"]
    assert cloth.images == ["https://example.com/a.jpg"]
    assert cloth.prev_month_sales == [12.5, 8.0]
    assert cloth.is_active is True


def test_lists_default_to_empty(db):
    db.add(make_cloth())
    db.commit()
    cloth = db.scalars(select(Cloth)).one()
    assert cloth.images == []
    assert cloth.prev_month_sales == []


@pytest.mark.parametrize(
    "bad",
    [
        {"stock_quantity": Decimal("-0.50")},
        {"unit_price": Decimal(-1)},
        {"clothing_category": "scarf"},
    ],
)
def test_database_rejects_bad_values(db, bad):
    db.add(make_cloth(**bad))
    with pytest.raises(IntegrityError):
        db.commit()


def test_json_columns_are_checked_by_pydantic():
    import pytest
    from pydantic import ValidationError
    from sqlalchemy.exc import StatementError

    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    for bad in [{"images": ["http://insecure.com/a.jpg"]}, {"prev_month_sales": [-1]}, {"best_for": [""]}]:
        with Session(engine) as db:
            db.add(make_cloth(**bad))
            with pytest.raises(StatementError) as err:
                db.commit()
            assert isinstance(err.value.orig, ValidationError)
