from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import Base, ClothOrder, Customer, User


def test_customer_and_orders():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(User(id=1, role="customer", email="a@b.com", password_hash="x"))
        c = Customer(user_id=1, name="Ravi", measurements={"shirt": {"chest": Decimal(40)}})
        c.orders.append(ClothOrder(items=[]))
        s.add(c)
        s.commit()
        s.expire_all()
        c = s.scalars(select(Customer)).one()
        assert c.measurements["shirt"]["chest"] == Decimal(40)
        assert len(c.orders) == 1 and c.orders[0].customer is c
        assert c.address is None
