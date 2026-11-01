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


def test_email_must_be_unique(db):
    db.add_all([make_user(), make_user()])
    with pytest.raises(IntegrityError):
        db.commit()


def test_role_must_be_valid(db):
    db.add(make_user(role="manager"))
    with pytest.raises(IntegrityError):
        db.commit()
