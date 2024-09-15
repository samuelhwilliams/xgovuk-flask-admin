"""Integration tests for list view rendering and functionality."""

import pytest
from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy_lite import SQLAlchemy
from jinja2 import PackageLoader, ChoiceLoader, PrefixLoader

from xgov_flask_admin import XGovFrontendTheme, XGovModelView, XGovFlaskAdmin
from example.models import Base, User
from tests.factories import UserFactory


@pytest.mark.integration
class TestListViewRendering:
    """Test list view renders correctly with GOV.UK components."""

    @pytest.mark.xfail(reason="Not implemented: Assert table has govuk-table class")
    def test_renders_govuk_table(self, client):
        """Test list view renders GOV.UK table component."""
        response = client.get("/admin/user/")
        assert response.status_code == 200
        # TODO: Assert table has govuk-table class
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(reason="Not implemented: Assert column headers present")
    def test_displays_column_headers(self, client):
        """Test column headers are displayed."""
        client.get("/admin/user/")
        # TODO: Assert column headers present
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(reason="Not implemented: Assert correct number of rows")
    def test_displays_data_rows(self, client):
        """Test data rows are displayed."""
        client.get("/admin/user/")
        # TODO: Assert correct number of rows
        raise NotImplementedError("Test not implemented")

    def test_first_column_is_link_when_can_edit(self, client, db_session):
        """Test first column contains edit link when can_edit is True."""
        UserFactory.create_batch(5)
        response = client.get("/admin/user/")
        assert response.status_code == 200
        html = response.data.decode("utf-8")

        # Check that first column has edit link
        assert 'href="/admin/user/edit/' in html
        assert "govuk-link govuk-link--no-visited-state" in html
        assert "(view and edit)" in html

    @pytest.mark.xfail(reason="Not implemented: Assert column descriptions present")
    def test_displays_column_descriptions(self, client):
        """Test column descriptions are shown as hints."""
        client.get("/admin/user/")
        # TODO: Assert column descriptions present
        raise NotImplementedError("Test not implemented")


@pytest.mark.integration
class TestListViewPagination:
    """Test list view pagination."""

    @pytest.mark.xfail(
        reason="Not implemented: Create more records than page size, Assert pagination component present"
    )
    def test_pagination_shown_when_needed(self, client):
        """Test pagination appears when results exceed page size."""
        # TODO: Create more records than page size
        # TODO: Assert pagination component present
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(reason="Not implemented: Assert pagination not present")
    def test_pagination_hidden_single_page(self, client):
        """Test pagination hidden with single page of results."""
        # TODO: Assert pagination not present
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(reason='Not implemented: Assert "Showing X results" text')
    def test_result_count_displayed(self, client):
        """Test result count is displayed."""
        client.get("/admin/user/")
        # TODO: Assert "Showing X results" text
        raise NotImplementedError("Test not implemented")


@pytest.mark.integration
class TestListViewEmpty:
    """Test list view with no data."""

    @pytest.mark.xfail(reason="Not implemented: Assert empty message present")
    def test_empty_message_displayed(self, client):
        """Test empty list message is shown when no records."""
        client.get("/admin/user/")
        # TODO: Assert empty message present
        raise NotImplementedError("Test not implemented")


@pytest.mark.integration
class TestListViewCanEdit:
    """Test list view respects can_edit setting."""

    @pytest.fixture
    def app_with_readonly_view(self):
        """Create app with a read-only model view."""
        app = Flask(__name__)
        app.config["SECRET_KEY"] = "test-secret"
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_ENGINES"] = {"default": "sqlite:///:memory:"}

        # Configure Jinja2 loaders
        app.jinja_options = {
            "loader": ChoiceLoader(
                [
                    PrefixLoader(
                        {"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}
                    ),
                    PrefixLoader(
                        {"govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf")}
                    ),
                    PackageLoader("xgov_flask_admin"),
                ]
            )
        }

        # Initialize extensions
        admin = Admin(app, theme=XGovFrontendTheme())
        XGovFlaskAdmin(app, service_name="Test Service")
        db = SQLAlchemy(app)

        # Create tables and add views
        with app.app_context():
            Base.metadata.create_all(db.engine)

            # Add read-only view (can_edit=False)
            class ReadOnlyUserView(XGovModelView):
                can_edit = False

            admin.add_view(ReadOnlyUserView(User, db.session))

        yield app, db

        with app.app_context():
            db.engine.dispose()

    def test_first_column_not_link_when_can_edit_false_and_no_view_details(
        self, app_with_readonly_view
    ):
        """Test first column does NOT contain any link when can_edit and can_view_details are False."""
        app, db = app_with_readonly_view

        with app.app_context():
            # Create a test user
            import datetime

            user = User(
                email="test@example.com",
                name="Test User",
                age=30,
                job="Test Job",
                favourite_colour=list(
                    User.__table__.c.favourite_colour.type.enum_class
                )[0],
                created_at=datetime.date.today(),
            )
            db.session.add(user)
            db.session.commit()

            client = app.test_client()
            response = client.get("/admin/user/")
            assert response.status_code == 200
            html = response.data.decode("utf-8")

            # Check that edit links are NOT present
            assert 'href="/admin/user/edit/' not in html
            # Check that details links are NOT present (can_view_details is False by default)
            assert 'href="/admin/user/details/' not in html
            # The first column should just contain plain text
            assert "Test User" in html
            # The visually hidden "(view and edit)" text should not be present
            assert "(view and edit)" not in html
            # The visually hidden "(view details)" text should not be present
            assert "(view details)" not in html

    @pytest.fixture
    def app_with_details_view(self):
        """Create app with a view-only model view (can_view_details=True, can_edit=False)."""
        app = Flask(__name__)
        app.config["SECRET_KEY"] = "test-secret"
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_ENGINES"] = {"default": "sqlite:///:memory:"}

        # Configure Jinja2 loaders
        app.jinja_options = {
            "loader": ChoiceLoader(
                [
                    PrefixLoader(
                        {"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}
                    ),
                    PrefixLoader(
                        {"govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf")}
                    ),
                    PackageLoader("xgov_flask_admin"),
                ]
            )
        }

        # Initialize extensions
        admin = Admin(app, theme=XGovFrontendTheme())
        XGovFlaskAdmin(app, service_name="Test Service")
        db = SQLAlchemy(app)

        # Create tables and add views
        with app.app_context():
            Base.metadata.create_all(db.engine)

            # Add view-only view (can_edit=False, can_view_details=True)
            class ViewOnlyUserView(XGovModelView):
                can_edit = False
                can_view_details = True

            admin.add_view(ViewOnlyUserView(User, db.session))

        yield app, db

        with app.app_context():
            db.engine.dispose()

    def test_first_column_links_to_details_when_can_edit_false_but_can_view_details_true(
        self, app_with_details_view
    ):
        """Test first column links to details view when can_edit is False but can_view_details is True."""
        app, db = app_with_details_view

        with app.app_context():
            # Create a test user
            import datetime

            user = User(
                email="viewonly@example.com",
                name="View Only User",
                age=25,
                job="Test Job",
                favourite_colour=list(
                    User.__table__.c.favourite_colour.type.enum_class
                )[0],
                created_at=datetime.date.today(),
            )
            db.session.add(user)
            db.session.commit()

            client = app.test_client()
            response = client.get("/admin/user/")
            assert response.status_code == 200
            html = response.data.decode("utf-8")

            # Check that edit links are NOT present
            assert 'href="/admin/user/edit/' not in html
            # Check that details links ARE present
            assert 'href="/admin/user/details/' in html
            assert "govuk-link govuk-link--no-visited-state" in html
            # The visually hidden "(view details)" text should be present
            assert "(view details)" in html
            # The visually hidden "(view and edit)" text should NOT be present
            assert "(view and edit)" not in html
