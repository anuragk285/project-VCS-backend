from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.models import Base, Cloth
from main import app


def make(name, category="shirt", colour="Navy", pattern="Plain", best_for=None, price="400", stock="10", **extra):
    return Cloth(
        name=name,
        clothing_category=category,
        colour=colour,
        colour_hex="#1F2A44",
        pattern=pattern,
        best_for=best_for or [],
        unit_price=Decimal(price),
        stock_quantity=Decimal(stock),
        **extra,
    )


@pytest.fixture()
def client():
    # One shared in-memory database, so the route and the test see the same rows.
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(
            [
                make("Oxford Blue", colour="Sky Blue", brand="Vinayaka Select", best_for=["office", "daily wear"], price="320"),
                make("Festive Silk", colour="Maroon", pattern="Self design", best_for=["wedding", "festival"], price="720", stock="0"),
                make("Navy Pinstripe", pattern="Pinstripe", best_for=["office", "formal"], price="380", brand="Warangal Weaves"),
                make("Khaki Twill", category="pant", colour="Khaki", pattern="Twill", best_for=["casual"], price="420"),
                make("Black Formal", category="pant", colour="Black", best_for=["formal", "office"], price="520", stock="0"),
                make("Hidden Cloth", is_active=False),
            ]
        )
        session.commit()

        def override():
            yield session

        app.dependency_overrides[get_db] = override
        yield TestClient(app)
        app.dependency_overrides.clear()


def names(response):
    assert response.status_code == 200, response.text
    return sorted(item["name"] for item in response.json()["items"])


def test_no_filters_returns_active_cloths_only(client):
    response = client.get("/cloths")
    assert len(names(response)) == 5
    assert "Hidden Cloth" not in names(response)
    assert response.json()["total_cloths"] == 5


def test_category(client):
    assert names(client.get("/cloths?category=pant")) == ["Black Formal", "Khaki Twill"]


def test_bad_category_is_rejected(client):
    assert client.get("/cloths?category=scarf").status_code == 422


def test_colour_ignores_case(client):
    assert names(client.get("/cloths?colour=navy")) == ["Navy Pinstripe"]


def test_pattern(client):
    assert names(client.get("/cloths?pattern=pinstripe")) == ["Navy Pinstripe"]


def test_best_for(client):
    assert names(client.get("/cloths?best_for=wedding")) == ["Festive Silk"]
    assert names(client.get("/cloths?best_for=office")) == ["Black Formal", "Navy Pinstripe", "Oxford Blue"]


def test_best_for_needs_the_whole_tag(client):
    assert names(client.get("/cloths?best_for=off")) == []


def test_price_range(client):
    assert names(client.get("/cloths?min_price=400&max_price=520")) == ["Black Formal", "Khaki Twill"]


def test_price_range_the_wrong_way_round(client):
    assert client.get("/cloths?min_price=500&max_price=100").status_code == 422


def test_in_stock(client):
    assert names(client.get("/cloths?in_stock=true")) == ["Khaki Twill", "Navy Pinstripe", "Oxford Blue"]
    assert names(client.get("/cloths?in_stock=false")) == ["Black Formal", "Festive Silk"]


def test_search_name_brand_colour(client):
    assert names(client.get("/cloths?search_text=oxford")) == ["Oxford Blue"]
    assert names(client.get("/cloths?search_text=warangal")) == ["Navy Pinstripe"]
    assert names(client.get("/cloths?search_text=maroon")) == ["Festive Silk"]
    assert names(client.get("/cloths?search_text=navy pin")) == ["Navy Pinstripe"]


def test_search_treats_percent_as_text(client):
    assert names(client.get("/cloths?search_text=%25")) == []


def test_filters_combine(client):
    assert names(client.get("/cloths?category=shirt&best_for=office&in_stock=true&max_price=350")) == ["Oxford Blue"]


def test_paging(client):
    first = client.get("/cloths?page_size=2&page_no=1").json()
    last = client.get("/cloths?page_size=2&page_no=3").json()
    assert first["total_cloths"] == 5 and first["total_pages"] == 3 and len(first["items"]) == 2
    assert len(last["items"]) == 1
    assert client.get("/cloths?page_no=0").status_code == 422


def test_item_shape(client):
    item = client.get("/cloths?search_text=oxford").json()["items"][0]
    assert item["in_stock"] is True
    assert "prev_month_sales" not in item
    assert item["clothing_category"] == "shirt"


def test_get_cloth_by_id_success(client):
    # ID 1 ("Oxford Blue") is active and exists
    response = client.get("/cloths/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Oxford Blue"
    assert data["id"] == 1


def test_get_cloth_not_found(client):
    response = client.get("/cloths/999")
    assert response.status_code == 404


def test_get_inactive_cloth_returns_not_found(client):
    response = client.get("/cloths/6")
    assert response.status_code == 404


def test_get_cloth_invalid_id_format(client):
    response = client.get("/cloths/0")
    assert response.status_code == 404

def test_cloth_filters(client):
    response = client.get("/cloths/filters")

    assert response.status_code == 200

    data = response.json()

    assert data["colours"] == ["Black", "Khaki", "Maroon", "Navy", "Sky Blue"]
    assert data["patterns"] == ["Pinstripe", "Plain", "Self design", "Twill"]
    assert data["best_for"] == [
        "casual",
        "daily wear",
        "festival",
        "formal",
        "office",
        "wedding",
    ]

    assert Decimal(data["price_range"]["min"]) == Decimal("320.00")
    assert Decimal(data["price_range"]["max"]) == Decimal("720.00")