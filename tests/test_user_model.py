import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Base, User, UserRoles


@pytest.fixture()
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def make_user(**changes) -> User:
    data = {"role": UserRoles.customer, "email": "a@example.com", "password_hash": "x" * 100}
    data.update(changes)
    return User(**data)


def test_save_and_read_back(db):
    db.add(make_user())
    db.commit()
    user = db.scalars(select(User)).one()
    assert user.role == "customer"
    assert len(user.password_hash) == 100
    assert user.email_verified is False
    assert user.is_active is True


def test_email_must_be_unique(db):
    db.add_all([make_user(), make_user()])
    with pytest.raises(IntegrityError):
        db.commit()


def test_phone_must_be_unique(db):
    db.add_all([make_user(email=None, phone="9876543210"), make_user(email=None, phone="9876543210")])
    with pytest.raises(IntegrityError):
        db.commit()


def test_role_must_be_valid(db):
    db.add(make_user(role="manager"))
    with pytest.raises(IntegrityError):
        db.commit()


def test_email_only_is_allowed(db):
    db.add(make_user(email="only@example.com", phone=None))
    db.commit()
    assert db.scalars(select(User)).one().phone is None


def test_phone_only_is_allowed(db):
    db.add(make_user(email=None, phone="9876543210"))
    db.commit()
    assert db.scalars(select(User)).one().email is None


def test_both_are_allowed(db):
    db.add(make_user(email="both@example.com", phone="9876543210"))
    db.commit()


@pytest.mark.parametrize("contact", [{"email": None, "phone": None}, {"email": "", "phone": ""}, {"email": None, "phone": ""}])
def test_user_with_no_email_and_no_phone_is_rejected(db, contact):
    db.add(make_user(**contact))
    with pytest.raises(IntegrityError):
        db.commit()


def test_many_users_can_have_no_phone(db):
    db.add_all([make_user(email="one@example.com"), make_user(email="two@example.com")])
    db.commit()  # two missing phones are not "the same phone"
