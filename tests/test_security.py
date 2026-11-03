from datetime import timedelta

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    TokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


@pytest.fixture(autouse=True)
def long_secret(monkeypatch):
    """A realistic secret, so the tests do not depend on what is in .env."""
    monkeypatch.setattr(settings, "secret_key", "test-secret-" + "x" * 40)


# ---------- passwords ----------
def test_hash_is_not_the_password():
    hashed = hash_password("secret-123")
    assert "secret-123" not in hashed
    assert hashed.startswith("$argon2")


def test_correct_password_is_accepted():
    assert verify_password("secret-123", hash_password("secret-123")) is True


def test_wrong_password_is_rejected():
    assert verify_password("wrong-password", hash_password("secret-123")) is False


def test_same_password_gives_different_hashes():
    assert hash_password("secret-123") != hash_password("secret-123")  # each hash has its own salt


def test_broken_hash_is_rejected_not_crashing():
    assert verify_password("secret-123", "not-a-real-hash") is False
    assert verify_password("secret-123", "") is False


# ---------- tokens ----------
def test_token_round_trip():
    token = create_access_token(user_id=7, role="customer")
    claims = decode_access_token(token)
    assert claims["sub"] == "7"
    assert claims["role"] == "customer"


def test_token_expiry_comes_from_settings():
    claims = decode_access_token(create_access_token(7, "customer"))
    assert claims["exp"] - claims["iat"] == settings.access_token_expire_minutes * 60


def test_expired_token_is_rejected():
    token = create_access_token(7, "customer", expires_delta=timedelta(seconds=-1))
    with pytest.raises(TokenError, match="expired"):
        decode_access_token(token)


def test_token_signed_with_another_secret_is_rejected():
    forged = jwt.encode({"sub": "1", "exp": 9999999999}, "another-secret-" + "y" * 40, algorithm="HS256")
    with pytest.raises(TokenError):
        decode_access_token(forged)


def test_tampered_token_is_rejected():
    header, payload, signature = create_access_token(7, "customer").split(".")
    with pytest.raises(TokenError):
        decode_access_token(f"{header}.{payload}x.{signature}")


def test_token_without_expiry_is_rejected():
    no_expiry = jwt.encode({"sub": "1"}, settings.secret_key, algorithm=settings.jwt_algorithm)
    with pytest.raises(TokenError):
        decode_access_token(no_expiry)


def test_unsigned_token_is_rejected():
    unsigned = jwt.encode({"sub": "1", "exp": 9999999999}, key=None, algorithm="none")
    with pytest.raises(TokenError):
        decode_access_token(unsigned)


def test_garbage_is_rejected():
    with pytest.raises(TokenError):
        decode_access_token("not.a.token")
