"""Password hashing and login tokens (JWT).

Passwords: hashed with argon2 (through pwdlib). The plain password is never stored or logged.
Tokens: signed with SECRET_KEY from .env. They carry the user id ("sub"), the role and an expiry.
"""

from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from app.core.config import settings

_password_hash = PasswordHash.recommended()  # argon2id


class TokenError(Exception):
    """The token is missing, expired, tampered with, or otherwise not acceptable."""


def hash_password(plain_password: str) -> str:
    return _password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """True only when the password matches. A broken or unknown hash counts as no match."""
    try:
        return _password_hash.verify(plain_password, hashed_password)
    except UnknownHashError:
        return False


def create_access_token(user_id: int, role: str, expires_delta: timedelta | None = None) -> str:
    now = datetime.now(UTC)
    lifetime = expires_delta if expires_delta is not None else timedelta(minutes=settings.access_token_expire_minutes)
    claims = {
        "sub": str(user_id),  # JWT wants the subject as text
        "role": role,
        "iat": now,
        "exp": now + lifetime,
    }
    return jwt.encode(claims, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Returns the claims, or raises TokenError (expired, wrong signature, no expiry, and so on)."""
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],  # a fixed list: tokens cannot pick their own algorithm
            options={"require": ["exp", "sub"]},
        )
    except jwt.ExpiredSignatureError as error:
        raise TokenError("Token has expired") from error
    except jwt.PyJWTError as error:
        raise TokenError("Token is not valid") from error
