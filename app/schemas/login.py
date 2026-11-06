from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """identifier is whatever the person typed: an email or a phone number."""

    identifier: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    expires_in: int  # seconds until the token stops working


class CustomerProfile(BaseModel):
    id: int
    name: str
    address: str | None


class MerchantProfile(BaseModel):
    id: int
    name: str
    phone: str
    shop_name: str
    shop_address: str | None
    gstin: str | None


class TailorProfile(BaseModel):
    id: int
    name: str
    phone: str
    tailoring_shop_name: str | None


class AdminProfile(BaseModel):
    id: int
    name: str
    phone: str | None


class MeResponse(BaseModel):
    """The signed-in person. Never includes the password hash."""

    user_id: int
    role: str
    email: str | None
    phone: str | None
    email_verified: bool
    profile: CustomerProfile | MerchantProfile | TailorProfile | AdminProfile | None
