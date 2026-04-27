"""Integration tests for SelectWithSearchFilterInList chained-attribute string paths."""

import pytest
from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy_lite import SQLAlchemy
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from xgovuk_flask_admin import XGovukFlaskAdmin, XGovukModelView
from xgovuk_flask_admin.filters import (
    SelectWithSearchFilterInList,
    SelectWithSearchFilterNotInList,
)
from xgovuk_flask_admin.theme import XGovukFrontendTheme


class ChainBase(DeclarativeBase):
    pass


class Continent(ChainBase):
    __tablename__ = "swsf_continent"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class Country(ChainBase):
    __tablename__ = "swsf_country"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    continent_id: Mapped[int] = mapped_column(ForeignKey(Continent.id))
    continent: Mapped[Continent] = relationship()


class City(ChainBase):
    __tablename__ = "swsf_city"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    country_id: Mapped[int] = mapped_column(ForeignKey(Country.id))
    country: Mapped[Country] = relationship()


@pytest.fixture
def chain_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret"
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_ENGINES"] = {"default": "sqlite:///:memory:"}

    app.jinja_options = {
        "loader": ChoiceLoader(
            [
                PrefixLoader(
                    {"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}
                ),
                PrefixLoader(
                    {"govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf")}
                ),
                PackageLoader("xgovuk_flask_admin"),
            ]
        )
    }

    admin = Admin(app, theme=XGovukFrontendTheme())
    XGovukFlaskAdmin(app, service_name="Test")
    db = SQLAlchemy(app)

    class CityView(XGovukModelView):
        column_filters = [
            SelectWithSearchFilterInList(
                "country.continent.name",
                "Continent",
                options=lambda: [
                    (c.name, c.name)
                    for c in db.session.scalars(
                        select(Continent).order_by(Continent.name)
                    )
                ],
                multiple=True,
            ),
            SelectWithSearchFilterInList(
                "country.name",
                "Country",
                options=lambda: [
                    (c.name, c.name)
                    for c in db.session.scalars(select(Country).order_by(Country.name))
                ],
            ),
            SelectWithSearchFilterNotInList(
                "country.name",
                "Country (exclude)",
                options=lambda: [
                    (c.name, c.name)
                    for c in db.session.scalars(select(Country).order_by(Country.name))
                ],
                multiple=True,
            ),
        ]

    with app.app_context():
        ChainBase.metadata.create_all(db.engine)
        admin.add_view(CityView(City, db))

        africa = Continent(name="Africa")
        europe = Continent(name="Europe")
        db.session.add_all([africa, europe])
        db.session.flush()

        kenya = Country(name="Kenya", continent_id=africa.id)
        france = Country(name="France", continent_id=europe.id)
        spain = Country(name="Spain", continent_id=europe.id)
        db.session.add_all([kenya, france, spain])
        db.session.flush()

        db.session.add_all(
            [
                City(name="Nairobi", country_id=kenya.id),
                City(name="Paris", country_id=france.id),
                City(name="Lyon", country_id=france.id),
                City(name="Madrid", country_id=spain.id),
            ]
        )
        db.session.commit()

    yield app, db


@pytest.mark.integration
class TestSelectWithSearchFilterInListStringPath:
    def test_three_deep_filter_returns_correct_rows(self, chain_app):
        app, db = chain_app
        with app.test_client() as client:
            response = client.get("/admin/city/?flt0_0=Europe")
            assert response.status_code == 200
            html = response.data.decode("utf-8")

            assert "Paris" in html
            assert "Lyon" in html
            assert "Madrid" in html
            assert "Nairobi" not in html

    def test_two_deep_filter_returns_correct_rows(self, chain_app):
        app, db = chain_app
        with app.test_client() as client:
            response = client.get("/admin/city/?flt1_1=France")
            assert response.status_code == 200
            html = response.data.decode("utf-8")

            assert "Paris" in html
            assert "Lyon" in html
            assert "Madrid" not in html
            assert "Nairobi" not in html

    def test_options_render_in_filter_form(self, chain_app):
        app, db = chain_app
        with app.test_client() as client:
            response = client.get("/admin/city/")
            assert response.status_code == 200
            html = response.data.decode("utf-8")

            assert "Africa" in html
            assert "Europe" in html
            assert "France" in html
            assert "Kenya" in html

    def test_active_filter_tag_shows_label(self, chain_app):
        app, db = chain_app
        with app.test_client() as client:
            response = client.get("/admin/city/?flt0_0=Europe")
            html = response.data.decode("utf-8")

            tag_start = html.find('class="moj-filter__tag"')
            assert tag_start > 0
            tag_html = html[tag_start : html.find("</a>", tag_start)]
            assert "Europe" in tag_html

    def test_not_in_list_filter_excludes_selected_values(self, chain_app):
        app, db = chain_app
        with app.test_client() as client:
            response = client.get("/admin/city/?flt0_2=France")
            assert response.status_code == 200
            html = response.data.decode("utf-8")

            assert "Paris" not in html
            assert "Lyon" not in html
            assert "Madrid" in html
            assert "Nairobi" in html

    def test_unresolvable_path_raises(self):
        app = Flask(__name__)
        app.config["SECRET_KEY"] = "test-secret"
        app.config["SQLALCHEMY_ENGINES"] = {"default": "sqlite:///:memory:"}
        app.jinja_options = {
            "loader": ChoiceLoader(
                [
                    PrefixLoader(
                        {"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}
                    ),
                    PrefixLoader(
                        {"govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf")}
                    ),
                    PackageLoader("xgovuk_flask_admin"),
                ]
            )
        }
        Admin(app, theme=XGovukFrontendTheme())
        XGovukFlaskAdmin(app, service_name="Test")
        db = SQLAlchemy(app)

        class BadCityView(XGovukModelView):
            column_filters = [
                SelectWithSearchFilterInList(
                    "country.continent.does_not_exist",
                    "Bad",
                    options=lambda: [],
                ),
            ]

        with app.app_context():
            ChainBase.metadata.create_all(db.engine)
            with pytest.raises((AttributeError, ValueError)):
                BadCityView(City, db)
