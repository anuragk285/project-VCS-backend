import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    Base,
    ClothOrder,
    Customer,
    StitchingOrder,
    StitchingStatus,
    Tailor,
    User,
)


@pytest.fixture()
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(
            [
                User(id=1, role="customer", email="c@shop.com", password_hash="x"),
                User(id=2, role="tailor", email="t@shop.com", password_hash="x"),
                User(id=3, role="tailor", email="t2@shop.com", password_hash="x"),
            ]
        )
        session.add(Customer(id=1, user_id=1, name="Ravi"))
        session.add(ClothOrder(id=1, customer_id=1, items=[]))
        session.commit()
        yield session


def make_tailor(**changes):
    values = {"user_id": 2, "name": "Suresh", "phone": "8888888888", "tailoring_shop_name": "Suresh Tailors"}
    values.update(changes)
    return Tailor(**values)


def test_tailor_is_saved_with_defaults(db):
    db.add(make_tailor())
    db.commit()
    tailor = db.scalars(select(Tailor)).one()
    assert tailor.is_active is True
    assert tailor.created_at is not None
    assert tailor.tailoring_shop_name == "Suresh Tailors"


def test_shop_name_is_optional(db):
    db.add(make_tailor(tailoring_shop_name=None))
    db.commit()
    assert db.scalars(select(Tailor)).one().tailoring_shop_name is None


def test_one_tailor_per_user(db):
    db.add(make_tailor())
    db.commit()
    db.add(make_tailor(name="Another"))  # same user_id
    with pytest.raises(IntegrityError):
        db.commit()


def test_stitching_orders_are_found_through_the_tailor(db):
    tailor = make_tailor()
    tailor.stitching_orders.append(StitchingOrder(cloth_order_id=1, items=[]))
    tailor.stitching_orders.append(
        StitchingOrder(cloth_order_id=1, items=[], status=StitchingStatus.delivered)
    )
    db.add(tailor)
    db.commit()
    db.expire_all()

    tailor = db.scalars(select(Tailor)).one()
    assert len(tailor.stitching_orders) == 2
    assert tailor.stitching_orders[0].tailor is tailor

    current = [
        order
        for order in tailor.stitching_orders
        if order.status in (StitchingStatus.waiting_for_cloth, StitchingStatus.queued, StitchingStatus.in_progress)
    ]
    previous = [o for o in tailor.stitching_orders if o.status == StitchingStatus.delivered]
    assert len(current) == 1
    assert len(previous) == 1


def test_stitching_order_can_exist_without_a_tailor(db):
    db.add(StitchingOrder(cloth_order_id=1, items=[]))  # not assigned yet
    db.commit()
    assert db.scalars(select(StitchingOrder)).one().tailor is None