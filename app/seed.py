"""Sample data for development. Safe to run again and again: nothing is added twice.

Run from the backend folder (virtual environment active, database migrated):
    python -m app.seed
"""

from decimal import Decimal

from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import Cloth, Customer, Merchant, User, UserRoles

# Development logins only. Never use these on a real server.
DEMO_PASSWORD = "demo-password-123"
MERCHANT_EMAIL = "merchant@vinayaka.test"
CUSTOMER_EMAIL = "customer@vinayaka.test"


def placeholder(label: str) -> str:
    return f"https://placehold.co/600x800?text={label.replace(' ', '+')}"


def cloth(name, category, brand, colour, hex_, pattern, touch_feel, best_for, price, stock, sales, description):
    return {
        "name": name,
        "clothing_category": category,
        "brand": brand,
        "colour": colour,
        "colour_hex": hex_,
        "pattern": pattern,
        "touch_feel": touch_feel,
        "best_for": best_for,
        "unit_price": Decimal(price),
        "stock_quantity": Decimal(stock),
        "prev_month_sales": [Decimal(x) for x in sales],
        "description": description,
        "images": [placeholder(name), placeholder(name + " close up")],
    }


SHIRT, PANT = "shirt", "pant"

CLOTHS = [
    # 8 shirt cloths
    cloth("Royal Oxford Cotton", SHIRT, "Vinayaka Select", "Sky Blue", "#8DB4E2", "Plain",
          "Crisp and breathable, softens with every wash", ["office", "daily wear"], "320", "120", [38, 42, 45],
          "Classic oxford weave in pure cotton, a dependable office shirt."),
    cloth("Pure Linen Breeze", SHIRT, "Warangal Weaves", "Ivory", "#F2EBDD", "Plain",
          "Light and airy with a natural, relaxed drape", ["summer", "casual", "festival"], "540", "60", [18, 25, 31],
          "Pure linen that keeps you cool in the Warangal heat."),
    cloth("Navy Pinstripe Poplin", SHIRT, "Vinayaka Select", "Navy", "#1F2A44", "Pinstripe",
          "Smooth and cool with a clean, sharp finish", ["office", "formal"], "380", "90", [30, 28, 35],
          "Fine white pinstripes on deep navy for a sharp, formal look."),
    cloth("Festive Silk Blend", SHIRT, "Warangal Weaves", "Maroon", "#7A1F2B", "Self design",
          "Silky smooth with a soft sheen", ["wedding", "festival"], "720", "40", [10, 22, 40],
          "Rich maroon with a subtle woven pattern for weddings and festivals."),
    cloth("Brown Check Flannel", SHIRT, "Vinayaka Select", "Brown", "#8B5E3C", "Checks",
          "Soft and warm with a gentle brushed feel", ["casual", "winter"], "450", "55", [12, 15, 20],
          "Brushed cotton checks, comfortable for cooler months."),
    cloth("Mint Cotton Dobby", SHIRT, "Warangal Weaves", "Mint Green", "#B7DFC9", "Textured",
          "Light and fresh with a fine woven texture", ["casual", "daily wear"], "340", "80", [22, 20, 26],
          "Fresh mint with a small dobby weave, easy for everyday wear."),
    cloth("White Giza Cotton", SHIRT, "Vinayaka Select", "White", "#FAFAF7", "Plain",
          "Silky smooth and cool against the skin", ["formal", "office", "wedding"], "620", "70", [26, 30, 34],
          "Fine long-staple cotton in a clean white."),
    cloth("Charcoal Fil-a-Fil", SHIRT, "Warangal Weaves", "Charcoal", "#3C4048", "Micro stripe",
          "Firm and crisp, holds its shape all day", ["office", "formal"], "400", "65", [20, 24, 22],
          "A fine two-tone weave that looks smart in any office."),
    # 7 pant cloths
    cloth("Classic Navy Terry Rayon", PANT, "Vinayaka Select", "Navy", "#232F4B", "Plain",
          "Smooth and fluid with a clean fall", ["office", "formal"], "480", "100", [34, 38, 40],
          "The everyday trouser fabric, wrinkle resistant and easy to care for."),
    cloth("Charcoal Grey Suiting", PANT, "Warangal Weaves", "Charcoal Grey", "#4A4E57", "Plain",
          "Dense and smooth with a premium hand feel", ["formal", "wedding"], "760", "50", [14, 18, 24],
          "Fine suiting fabric with a rich, even colour."),
    cloth("Khaki Cotton Twill", PANT, "Vinayaka Select", "Khaki", "#B5A27A", "Twill",
          "Sturdy and soft, gets comfortable with wear", ["casual", "daily wear"], "420", "95", [28, 30, 33],
          "Strong cotton twill for relaxed everyday trousers."),
    cloth("Black Formal Blend", PANT, "Warangal Weaves", "Black", "#1C1C1E", "Plain",
          "Smooth and slightly stretchy, easy to move in", ["formal", "office"], "520", "85", [30, 27, 32],
          "A dependable black for formal wear, holds its crease."),
    cloth("Olive Stretch Chino", PANT, "Vinayaka Select", "Olive", "#6B7048", "Plain",
          "Soft with a slight stretch, comfortable all day", ["casual", "travel"], "460", "60", [16, 19, 23],
          "Easy-fit chino cloth with a hint of stretch."),
    cloth("Beige Linen Blend", PANT, "Warangal Weaves", "Beige", "#D8C7A3", "Plain",
          "Light and breathable with a natural texture", ["summer", "casual", "festival"], "560", "45", [9, 14, 21],
          "A linen-cotton mix that stays cool in warm weather."),
    cloth("Grey Pinstripe Suiting", PANT, "Vinayaka Select", "Grey", "#8A8F98", "Pinstripe",
          "Firm and smooth with a fine, tailored look", ["formal", "office"], "680", "40", [11, 13, 17],
          "Subtle stripes on light grey for a polished office look."),
]


def get_or_create_user(session: Session, email: str, role: UserRoles, hasher: PasswordHash) -> tuple[User, bool]:
    user = session.scalars(select(User).where(User.email == email)).first()
    if user:
        return user, False
    user = User(email=email, role=role, password_hash=hasher.hash(DEMO_PASSWORD))
    session.add(user)
    session.flush()  # gives the user an id
    return user, True


def seed(session: Session) -> dict[str, int]:
    """Adds anything missing and returns how many rows were added."""
    added = {"users": 0, "merchants": 0, "customers": 0, "cloths": 0}
    hasher = PasswordHash.recommended()

    merchant_user, new = get_or_create_user(session, MERCHANT_EMAIL, UserRoles.merchant, hasher)
    added["users"] += new
    if not session.scalars(select(Merchant).where(Merchant.user_id == merchant_user.id)).first():
        session.add(
            Merchant(
                user_id=merchant_user.id,
                name="Shop Owner",
                phone="9000000001",
                shop_address="Shivanagar, Warangal",
            )
        )
        added["merchants"] += 1

    customer_user, new = get_or_create_user(session, CUSTOMER_EMAIL, UserRoles.customer, hasher)
    added["users"] += new
    if not session.scalars(select(Customer).where(Customer.user_id == customer_user.id)).first():
        session.add(
            Customer(
                user_id=customer_user.id,
                name="Demo Customer",
                phone="9000000002",
                address="Hanamkonda, Warangal",
            )
        )
        added["customers"] += 1

    # A cloth counts as "already there" when the same name and category exist.
    existing = set(session.execute(select(Cloth.name, Cloth.clothing_category)).all())
    for data in CLOTHS:
        if (data["name"], data["clothing_category"]) not in existing:
            session.add(Cloth(**data))
            added["cloths"] += 1

    session.commit()
    return added


def main() -> None:
    with SessionLocal() as session:
        added = seed(session)
    print("Added:", added)
    if not any(added.values()):
        print("Nothing new. The sample data was already there.")


if __name__ == "__main__":
    main()