# Every model file must be imported here, otherwise Alembic cannot see its table.
from app.models.base import Base
from app.models.cloth import Cloth, ClothingCategory

__all__ = ["Base", "Cloth", "ClothingCategory"]