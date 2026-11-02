from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.models import Base, Cloth, Customer, Merchant, User
from app.seed import seed


def count(session, model):
    return session.scalar(select(func.count()).select_from(model))


def test_seed_adds_the_sample_data():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        seed(session)
        assert count(session, Cloth) == 15
        assert session.scalar(select(func.count()).select_from(Cloth).where(Cloth.clothing_category == "shirt")) == 8
        assert session.scalar(select(func.count()).select_from(Cloth).where(Cloth.clothing_category == "pant")) == 7
        assert count(session, Merchant) == 1
        assert count(session, Customer) == 1
        assert count(session, User) == 2


def test_running_the_seed_twice_adds_nothing_new():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        seed(session)
        second = seed(session)
        assert second == {"users": 0, "merchants": 0, "customers": 0, "cloths": 0}
        assert count(session, Cloth) == 15
        assert count(session, User) == 2