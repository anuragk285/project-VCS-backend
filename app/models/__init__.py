# Every model file must be imported here, otherwise Alembic cannot see its table.
from app.models.admin import Admin
from app.models.base import Base
from app.models.cloth import Cloth, ClothingCategory
from app.models.customer import Customer
from app.models.merchant import Merchant
from app.models.orders import (
    ClothOrder,
    ClothOrderSource,
    ClothOrderStatus,
    StitchingOrder,
    StitchingStatus,
)
from app.models.tailor import Tailor
from app.models.user import User, UserRoles

__all__ = [
    "Admin",
    "Base",
    "Cloth",
    "ClothOrder",
    "ClothOrderSource",
    "ClothOrderStatus",
    "ClothingCategory",
    "Customer",
    "Merchant",
    "StitchingOrder",
    "StitchingStatus",
    "Tailor",
    "User",
    "UserRoles",
]
