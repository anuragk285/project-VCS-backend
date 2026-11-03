from decimal import Decimal

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import Session

from app.models import Base, ClothOrder, Customer, StitchingOrder, User
from app.schemas.order_json import OrderLine, StitchingLine


@pytest.fixture()
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(User(id=1, role="customer", email="a@b.com", password_hash="x"))
        s.add(Customer(id=1, user_id=1, name="Ravi"))
        s.commit()
        yield s


def test_items_come_back_as_objects(db):
    db.add(ClothOrder(customer_id=1, items=[OrderLine(cloth_id=12, length=Decimal("2.2"), unit_price=Decimal(380))]))
    db.commit()
    db.expire_all()
    line = db.scalars(select(ClothOrder)).one().items[0]
    assert isinstance(line, OrderLine)
    assert line.length == Decimal("2.2") and line.cloth_id == 12


def test_plain_dicts_are_accepted_and_checked(db):
    db.add(ClothOrder(customer_id=1, items=[{"cloth_id": 1, "length": 1, "unit_price": 100}]))
    db.commit()


@pytest.mark.parametrize("bad", [{"cloth_id": 1, "length": 0, "unit_price": 100}, {"cloth_id": "x", "length": 1, "unit_price": 1}, {"length": 1}])
def test_bad_lines_rejected_before_database(db, bad):
    db.add(ClothOrder(customer_id=1, items=[bad]))
    with pytest.raises(StatementError) as err:  # SQLAlchemy wraps the pydantic error
        db.commit()
    assert isinstance(err.value.orig, ValidationError)


def test_stitching_json(db):
    db.add(ClothOrder(customer_id=1, items=[]))
    db.commit()
    db.add(
        StitchingOrder(
            cloth_order_id=1,
            items=[StitchingLine(cloth_id=12, garment="shirt", length=Decimal("2.2"), stitching_cost=Decimal(450))],
            cloth_measurements={"12": {"chest": Decimal(40)}},
            stitching_description={"12": "slim fit"},
        )
    )
    db.commit()
    db.expire_all()
    s = db.scalars(select(StitchingOrder)).one()
    assert s.cloth_measurements["12"]["chest"] == Decimal(40)
    assert s.items[0].garment == "shirt"


def test_stitching_cost_total(db):
    db.add(ClothOrder(customer_id=1, items=[]))
    db.commit()
    lines = [
        StitchingLine(cloth_id=1, garment="shirt", length=Decimal("2.2"), stitching_cost=Decimal(450)),
        StitchingLine(cloth_id=2, garment="pant", length=Decimal("1.2"), stitching_cost=Decimal("550.50")),
    ]
    db.add(StitchingOrder(cloth_order_id=1, items=lines))
    db.commit()
    db.expire_all()
    assert db.scalars(select(StitchingOrder)).one().total_stitching_cost == Decimal("1000.50")


def test_negative_stitching_cost_rejected(db):
    db.add(ClothOrder(customer_id=1, items=[]))
    db.commit()
    db.add(StitchingOrder(cloth_order_id=1, items=[{"cloth_id": 1, "garment": "shirt", "length": 1, "stitching_cost": -5}]))
    with pytest.raises(StatementError):
        db.commit()
