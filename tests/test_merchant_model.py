import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Base, Merchant, User


@pytest.fixture()
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(User(id=1, role="merchant", email="owner@shop.com", password_hash="x"))
        session.commit()
        yield session


def test_merchant_is_saved_with_defaults(db):
    db.add(Merchant(user_id=1, name="Owner", phone="9999999999"))
    db.commit()
    merchant = db.scalars(select(Merchant)).one()
    assert merchant.shop_name == "Vinayaka Cloth Store"
    assert merchant.is_active is True
    assert merchant.gstin is None
    assert merchant.created_at is not None


def test_one_merchant_per_user(db):
    db.add(Merchant(user_id=1, name="Owner", phone="9999999999"))
    db.commit()
    db.add(Merchant(user_id=1, name="Copy", phone="8888888888"))
    with pytest.raises(IntegrityError):
        db.commit()
