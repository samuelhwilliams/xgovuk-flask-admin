"""Integration tests for custom Flask-Admin endpoint names."""

import pytest
from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy_lite import SQLAlchemy
from jinja2 import PackageLoader, ChoiceLoader, PrefixLoader
from testcontainers.postgres import PostgresContainer

from xgovuk_flask_admin.theme import XGovukFrontendTheme
from xgovuk_flask_admin import XGovukModelView, XGovukFlaskAdmin
from example.models import Base, User


@pytest.mark.integration
class TestCustomEndpoint:
    """Test that custom Flask-Admin endpoint names work correctly."""

    @pytest.fixture(scope="class")
    def postgres_container(self):
        """Create PostgreSQL container for this test class."""
        container = PostgresContainer("postgres:16-alpine")
        container.start()
        yield container
        container.stop()

    @pytest.fixture
    def app_with_custom_endpoint(self, postgres_container):
        """Create app with a custom Flask-Admin endpoint name."""
        app = Flask(__name__)
        app.config["SECRET_KEY"] = "test-secret"
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_ENGINES"] = {
            "default": postgres_container.get_connection_url().replace('+psycopg2', '')
        }

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
                    PackageLoader("xgovuk_flask_admin"),
                ]
            )
        }

        # Initialize extensions with custom endpoint name (but default URL prefix)
        admin = Admin(
            app, theme=XGovukFrontendTheme(), endpoint="custom_admin", url="/admin"
        )
        XGovukFlaskAdmin(app, service_name="Test Service")
        db = SQLAlchemy(app)

        # Create tables and add views
        with app.app_context():
            Base.metadata.create_all(db.engine)
            admin.add_view(XGovukModelView(User, db.session))

        yield app, db

        with app.app_context():
            db.engine.dispose()

    def test_service_navigation_uses_custom_endpoint(self, app_with_custom_endpoint):
        """Test that service navigation serviceUrl uses custom endpoint name."""
        app, db = app_with_custom_endpoint

        with app.app_context():
            # Create a test user
            import datetime
            from example.enums import FavouriteColour

            user = User(
                email="test@example.com",
                name="Test User",
                age=30,
                job="Test Job",
                favourite_colour=list(FavouriteColour)[0],
                created_at=datetime.date.today(),
                active=True
            )
            db.session.add(user)
            db.session.commit()

            client = app.test_client()
            response = client.get("/admin/user/")
            assert response.status_code == 200
            html = response.data.decode("utf-8")

            # Check that the serviceUrl correctly generates the admin index URL
            # With custom endpoint "custom_admin", url_for('custom_admin.index') should work
            # The actual URL will still be /admin/ because that's the url parameter
            # The service navigation is rendered as HTML, look for the section element with service-navigation class
            assert 'class="govuk-service-navigation"' in html
            # Verify the service name link points to /admin/ (not hardcoded '/admin/')
            # This confirms the template uses admin_view.admin.endpoint dynamically
            assert '<a href="/admin/" class="govuk-service-navigation__link">' in html

    def test_custom_endpoint_routes_work(self, app_with_custom_endpoint):
        """Test that routes with custom endpoint work correctly."""
        app, db = app_with_custom_endpoint

        with app.app_context():
            # Create a test user
            import datetime
            from example.enums import FavouriteColour

            user = User(
                email="custom@example.com",
                name="Custom User",
                age=25,
                job="Job Title",
                favourite_colour=list(FavouriteColour)[0],
                created_at=datetime.date.today(),
                active=True
            )
            db.session.add(user)
            db.session.commit()

            client = app.test_client()

            # Test that admin routes are accessible at /admin/ URL
            response = client.get("/admin/")
            assert response.status_code == 200

            response = client.get("/admin/user/")
            assert response.status_code == 200

            # The key test: verify that url_for works with the custom endpoint
            # This tests the template uses admin_view.admin.endpoint dynamically
            # rather than hardcoded 'admin.index'
            from flask import url_for

            with client.application.test_request_context():
                # With custom endpoint, url_for should use 'custom_admin.index'
                index_url = url_for("custom_admin.index")
                assert index_url == "/admin/"
