import re

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean_phone(value: str | None) -> str | None:
    """Keeps one format for every phone number: 10 digits, no +91, spaces, dashes or leading 0."""
    if value is None or not value.strip():
        return None
    digits = re.sub(r"[\s\-()]", "", value)
    if digits.startswith("+91"):
        digits = digits[3:]
    elif digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]
    if not re.fullmatch(r"[6-9]\d{9}", digits):
        raise ValueError("Enter a valid 10 digit mobile number")
    return digits


def clean_email(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    email = value.strip().lower()
    if len(email) > 255 or not EMAIL_PATTERN.match(email):
        raise ValueError("Enter a valid email address")
    return email


class RegisterRequest(BaseModel):
    """Sign up as a customer. A phone number or an email is needed, and both are allowed."""

    name: str = Field(min_length=1, max_length=100)
    phone: str | None = None
    email: str | None = None
    address: str | None = Field(default=None, max_length=300)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        return value

    @field_validator("phone")
    @classmethod
    def normalise_phone(cls, value: str | None) -> str | None:
        return clean_phone(value)

    @field_validator("email")
    @classmethod
    def normalise_email(cls, value: str | None) -> str | None:
        return clean_email(value)

    @field_validator("address")
    @classmethod
    def blank_address_is_none(cls, value: str | None) -> str | None:
        return value.strip() or None if value else None

    @model_validator(mode="after")
    def phone_or_email_needed(self):
        if self.phone is None and self.email is None:
            raise ValueError("Give a phone number or an email address")
        return self


class RegisteredCustomer(BaseModel):
    """What the API returns after signup. Never includes the password or its hash."""
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    customer_id: int
    role: str
    name: str
    email: str | None
    email_verified: bool
