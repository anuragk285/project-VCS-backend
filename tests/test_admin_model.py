import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Admin, Base, User


@pytest.fixture()
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(User(id=1, role="admin", email="admin@shop.com", password_hash="x"))
        session.commit()
        yield session


def test_admin_is_saved_with_defaults(db):
    db.add(Admin(user_id=1, name="Owner"))
    db.commit()
    admin = db.scalars(select(Admin)).one()
    assert admin.is_active is True
    assert admin.phone is None
    assert admin.created_at is not None


def test_one_admin_per_user(db):
    db.add(Admin(user_id=1, name="Owner"))
    db.commit()
    db.add(Admin(user_id=1, name="Copy"))
    with pytest.raises(IntegrityError):
        db.commit()

