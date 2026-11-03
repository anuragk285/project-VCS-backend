from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import Customer, User, UserRoles
from app.schemas.auth import RegisterRequest


class AlreadyRegisteredError(Exception):
    """The phone number or email already belongs to another user."""


def find_existing(db: Session, phone: str | None, email: str | None) -> User | None:
    conditions = []
    if phone:
        conditions.append(User.phone == phone)
    if email:
        conditions.append(User.email == email)
    return db.scalars(select(User).where(or_(*conditions))).first()


def register_customer(db: Session, data: RegisterRequest) -> tuple[User, Customer]:
    """Creates the User and the Customer together. Both are saved, or neither is."""
    if find_existing(db, data.phone, data.email):
        raise AlreadyRegisteredError

    user = User(
        role=UserRoles.customer,
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password),
    )
    try:
        db.add(user)
        db.flush() 
        customer = Customer(user_id=user.id, name=data.name, address=data.address)
        db.add(customer)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise AlreadyRegisteredError from error
    except Exception:
        db.rollback()
        raise
    return user, customer
