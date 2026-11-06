from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import Admin, Customer, Merchant, Tailor, User, UserRoles
from app.schemas.auth import clean_email, clean_phone
from app.schemas.login import (
    AdminProfile,
    CustomerProfile,
    MerchantProfile,
    TailorProfile,
)

# Checked when no user is found, so a wrong email takes as long as a wrong password.
DUMMY_HASH = hash_password("a-password-nobody-uses")


def find_user(db: Session, identifier: str) -> User | None:
    """Finds a user by email (if the text has an @) or by phone number."""
    try:
        if "@" in identifier:
            email = clean_email(identifier)
            return db.scalars(select(User).where(User.email == email)).first() if email else None
        phone = clean_phone(identifier)
        return db.scalars(select(User).where(User.phone == phone)).first() if phone else None
    except ValueError:  # not a valid email or phone, so no account can match
        return None


def authenticate_user(db: Session, identifier: str, password: str) -> User | None:
    """The user when the details are right and the account is active, otherwise None."""
    user = find_user(db, identifier)
    password_ok = False
    if user:
        password_ok = verify_password(password, user.password_hash)
    if user is None or not password_ok or not user.is_active:
        return None
    return user


def get_profile(db: Session, user: User):
    """The shop details that go with this login, depending on its role."""
    if user.role == UserRoles.customer:
        row = db.scalars(select(Customer).where(Customer.user_id == user.id)).first()
        return CustomerProfile(id=row.id, name=row.name, address=row.address) if row else None
    if user.role == UserRoles.merchant:
        row = db.scalars(select(Merchant).where(Merchant.user_id == user.id)).first()
        if row:
            return MerchantProfile(
                id=row.id,
                name=row.name,
                phone=row.phone,
                shop_name=row.shop_name,
                shop_address=row.shop_address,
                gstin=row.gstin,
            )
    if user.role == UserRoles.tailor:
        row = db.scalars(select(Tailor).where(Tailor.user_id == user.id)).first()
        if row:
            return TailorProfile(
                id=row.id, name=row.name, phone=row.phone, tailoring_shop_name=row.tailoring_shop_name
            )
    if user.role == UserRoles.admin:
        row = db.scalars(select(Admin).where(Admin.user_id == user.id)).first()
        if row:
            return AdminProfile(id=row.id, name=row.name, phone=row.phone)
    return None
