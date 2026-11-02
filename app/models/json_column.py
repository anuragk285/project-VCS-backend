from typing import Any

from pydantic import TypeAdapter
from sqlalchemy.types import TypeDecorator

from app.models.base import JsonType


class PydanticJSON(TypeDecorator):
    """A JSON column whose content is checked by a pydantic type.

    Column(PydanticJSON(list[OrderLine])): you save and read OrderLine objects,
    the database stores plain JSON. Wrong data fails before it reaches the database.
    """

    impl = JsonType
    cache_ok = True

    def __init__(self, python_type: Any):
        super().__init__()
        self._adapter = TypeAdapter(python_type)
        self._python_type = python_type

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return self._adapter.dump_python(self._adapter.validate_python(value), mode="json")

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self._adapter.validate_python(value)

    @property
    def python_type(self):
        return self._python_type

    # cache_ok needs a stable identity for this type
    def _static_cache_key(self):
        return (type(self), repr(self._python_type))
