from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, decode_access_token, hash_password
from app.models import Base, Merchant, User
from main import app

PASSWORD = "strong-pass-1"
SIGNUP = {"name": "Ravi Kumar", "phone": "9876543210", "email": "ravi@example.com", "address": "Hanamkonda", "password": PASSWORD}
BAD_LOGIN = "Incorrect phone, email or password"


@pytest.fixture(autouse=True)
def long_secret(monkeypatch):
    monkeypatch.setattr(settings, "secret_key", "test-secret-" + "x" * 40)


@pytest.fixture()
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture()
def client(session):
    app.dependency_overrides[get_db] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def registered(client):
    assert client.post("/auth/register", json=SIGNUP).status_code == 201


def login(client, identifier, password=PASSWORD):
    return client.post("/auth/login", json={"identifier": identifier, "password": password})


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# ---------- login ----------
@pytest.mark.parametrize("identifier", ["ravi@example.com", "RAVI@Example.com", "9876543210", "+91 98765 43210", "09876543210"])
def test_login_with_email_or_phone(client, registered, identifier):
    response = login(client, identifier)
    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "customer"
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == settings.access_token_expire_minutes * 60
    assert decode_access_token(body["access_token"])["role"] == "customer"


def test_wrong_password_is_rejected(client, registered):
    response = login(client, "ravi@example.com", "wrong-password")
    assert response.status_code == 401
    assert response.json()["detail"] == BAD_LOGIN


def test_unknown_account_gives_the_same_message(client, registered):
    wrong_password = login(client, "ravi@example.com", "wrong-password")
    unknown = login(client, "nobody@example.com")
    assert unknown.status_code == 401
    assert unknown.json() == wrong_password.json()


@pytest.mark.parametrize("identifier", ["not a phone", "12345", "@", "x@y"])
def test_unusable_identifier_is_just_a_failed_login(client, registered, identifier):
    response = login(client, identifier)
    assert response.status_code == 401
    assert response.json()["detail"] == BAD_LOGIN


def test_disabled_user_cannot_log_in(client, session, registered):
    session.query(User).update({"is_active": False})
    session.commit()
    response = login(client, "ravi@example.com")
    assert response.status_code == 401
    assert response.json()["detail"] == BAD_LOGIN


def test_missing_fields_are_rejected(client):
    assert client.post("/auth/login", json={"identifier": "ravi@example.com"}).status_code == 422
    assert client.post("/auth/login", json={}).status_code == 422


def test_login_response_has_no_password_data(client, registered):
    text = login(client, "ravi@example.com").text
    assert PASSWORD not in text and "argon2" not in text


# ---------- /auth/me ----------
def test_me_returns_the_signed_in_customer(client, registered):
    token = login(client, "9876543210").json()["access_token"]
    response = client.get("/auth/me", headers=auth(token))
    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "customer"
    assert body["email"] == "ravi@example.com" and body["phone"] == "9876543210"
    assert body["email_verified"] is False
    assert body["profile"]["name"] == "Ravi Kumar"
    assert body["profile"]["address"] == "Hanamkonda"
    assert "password_hash" not in response.text


def test_me_returns_the_merchant_profile(client, session):
    user = User(role="merchant", email="owner@vinayaka.test", password_hash=hash_password(PASSWORD))
    session.add(user)
    session.flush()
    session.add(Merchant(user_id=user.id, name="Shop Owner", phone="9000000001"))
    session.commit()
    token = login(client, "owner@vinayaka.test").json()["access_token"]
    body = client.get("/auth/me", headers=auth(token)).json()
    assert body["role"] == "merchant"
    assert body["profile"]["shop_name"] == "Vinayaka Cloth Store"


def test_me_without_a_token_is_rejected(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_with_a_garbage_token_is_rejected(client):
    assert client.get("/auth/me", headers=auth("not.a.token")).status_code == 401


def test_me_with_an_expired_token_is_rejected(client, registered, session):
    user_id = session.query(User).one().id
    token = create_access_token(user_id, "customer", expires_delta=timedelta(seconds=-1))
    response = client.get("/auth/me", headers=auth(token))
    assert response.status_code == 401
    assert "expired" in response.json()["detail"]


def test_me_for_a_user_who_no_longer_exists_is_rejected(client):
    token = create_access_token(999, "customer")
    assert client.get("/auth/me", headers=auth(token)).status_code == 401


def test_me_stops_working_when_the_user_is_disabled(client, session, registered):
    token = login(client, "ravi@example.com").json()["access_token"]
    session.query(User).update({"is_active": False})
    session.commit()
    assert client.get("/auth/me", headers=auth(token)).status_code == 401
