from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.models import Base, Cloth, ClothingCategory
from app.services.cloth import list_cloths, single_cloth


def make(name, category=ClothingCategory.shirt, colour="Navy", pattern="Plain", best_for=None, price="400", stock="10", **extra):
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
def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(
            [
                make("Oxford Blue", id=1, colour="Sky Blue", brand="Vinayaka Select", best_for=["office", "daily wear"], price="320"),
                make("Festive Silk", id=2, colour="Maroon", pattern="Self design", best_for=["wedding", "festival"], price="720", stock="0"),
                make("Navy Pinstripe", id=3, pattern="Pinstripe", best_for=["office", "formal"], price="380", brand="Warangal Weaves"),
                make("Khaki Twill", id=4, category=ClothingCategory.pant, colour="Khaki", pattern="Twill", best_for=["casual"], price="420", stock="2"),
                make("Hidden Cloth", id=5, colour="Black", is_active=False),
            ]
        )
        session.commit()
        yield session


def test_list_cloths_defaults(db_session):
    result = list_cloths(db_session)
    assert result["total_cloths"] == 4
    assert len(result["items"]) == 4
    assert result["page_no"] == 1
    assert result["page_size"] == 12
    assert result["total_pages"] == 1


def test_list_cloths_filter_category(db_session):
    result = list_cloths(db_session, category=ClothingCategory.pant)
    assert result["total_cloths"] == 1
    assert result["items"][0].name == "Khaki Twill"


def test_list_cloths_filter_colour(db_session):
    result = list_cloths(db_session, colour="  NAVY ")
    assert result["total_cloths"] == 1
    assert result["items"][0].name == "Navy Pinstripe"


def test_list_cloths_filter_pattern(db_session):
    result = list_cloths(db_session, pattern="pinstripe")
    assert result["total_cloths"] == 1
    assert result["items"][0].name == "Navy Pinstripe"


def test_list_cloths_filter_best_for(db_session):
    result = list_cloths(db_session, best_for="office")
    names = [c.name for c in result["items"]]
    assert sorted(names) == ["Navy Pinstripe", "Oxford Blue"]


def test_list_cloths_filter_price_range(db_session):
    result = list_cloths(db_session, min_price=350, max_price=500)
    names = [c.name for c in result["items"]]
    assert sorted(names) == ["Khaki Twill", "Navy Pinstripe"]


def test_list_cloths_filter_in_stock(db_session):
    in_stock_res = list_cloths(db_session, in_stock=True)
    assert len(in_stock_res["items"]) == 3  

    out_of_stock_res = list_cloths(db_session, in_stock=False)
    assert len(out_of_stock_res["items"]) == 1 


def test_list_cloths_search_text(db_session):
    result = list_cloths(db_session, search_text="warangal")
    assert result["total_cloths"] == 1
    assert result["items"][0].name == "Navy Pinstripe"


def test_list_cloths_pagination(db_session):
    result = list_cloths(db_session, page_no=1, page_size=2)
    assert result["total_cloths"] == 4
    assert result["total_pages"] == 2
    assert len(result["items"]) == 2

    page_2 = list_cloths(db_session, page_no=2, page_size=2)
    assert len(page_2["items"]) == 2


def test_single_cloth_found(db_session):
    cloth = single_cloth(db_session, id=1)
    assert cloth is not None
    assert cloth.name == "Oxford Blue"


def test_single_cloth_inactive_returns_none(db_session):
    cloth = single_cloth(db_session, id=5)
    assert cloth is None


def test_single_cloth_not_found(db_session):
    cloth = single_cloth(db_session, id=999)
    assert cloth is None


def test_single_cloth_invalid_id(db_session):
    cloth = single_cloth(db_session, id=0)
    assert cloth is None