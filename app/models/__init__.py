# Every model file must be imported here, otherwise Alembic cannot see its table.
# Example, once the model exists:
#   from app.models.cloth import Cloth
from app.models.base import Base

__all__ = ["Base"]
