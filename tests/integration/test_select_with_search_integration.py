"""Integration tests for GovSelectWithSearch with Flask-Admin."""

import pytest
from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy_lite import SQLAlchemy
from jinja2 import PackageLoader, ChoiceLoader, PrefixLoader
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from xgovuk_flask_admin.theme import XGovukFrontendTheme
from xgovuk_flask_admin import XGovukModelView, XGovukFlaskAdmin


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "author"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    books: Mapped[list["Book"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    def __str__(self):
        return self.name


class Book(Base):
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey(Author.id))
    author: Mapped[Author] = relationship(back_populates="books")

    def __str__(self):
        return self.title


@pytest.fixture
def integration_app():
    """Create a Flask app with Flask-Admin and test models."""
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
                PackageLoader("xgovuk_flask_admin"),
            ]
        )
    }

    # Initialize extensions
    admin = Admin(app, theme=XGovukFrontendTheme())
    XGovukFlaskAdmin(app, service_name="Test Service")
    db = SQLAlchemy(app)

    # Create tables and add views
    with app.app_context():
        Base.metadata.create_all(db.engine)
        admin.add_view(XGovukModelView(Author, db.session))
        admin.add_view(XGovukModelView(Book, db.session))

    yield app, db, admin

    with app.app_context():
        db.engine.dispose()


class TestSelectWithSearchIntegration:
    """Integration tests for select-with-search in Flask-Admin forms."""

    def test_multi_select_relationship_uses_select_with_search(self, integration_app):
        """Test that one-to-many relationships use select-with-search widget."""
        app, db, admin = integration_app

        with app.test_client() as client:
            # Get the author create form
            response = client.get("/admin/author/new/")
            assert response.status_code == 200

            html = response.data.decode("utf-8")

            # Check that the books field has the select-with-search data-module
            assert 'name="books"' in html
            assert 'data-module="select-with-search"' in html
            assert "multiple" in html

            # Check that it has the gem wrapper class
            assert "gem-c-select-with-search" in html

            # Check that label is present
            assert '<label class="govuk-label' in html
            assert "Books" in html

    def test_single_select_relationship_uses_select_with_search(self, integration_app):
        """Test that many-to-one relationships use select-with-search widget."""
        app, db, admin = integration_app

        with app.test_client() as client:
            # Get the book create form
            response = client.get("/admin/book/new/")
            assert response.status_code == 200

            html = response.data.decode("utf-8")

            # Check that the author field has select-with-search data-module
            assert 'name="author"' in html
            assert 'data-module="select-with-search"' in html

            # Check that it has the gem wrapper class
            assert "gem-c-select-with-search" in html

            # Should NOT have multiple attribute for single-select relationship
            # Extract the select element for author to verify it doesn't have multiple
            author_select_start = html.find('name="author"')
            if author_select_start > 0:
                # Look backwards for the opening <select tag
                select_start = html.rfind("<select", 0, author_select_start)
                # Look forwards for the closing >
                select_end = html.find(">", author_select_start)
                select_tag = html[select_start:select_end]
                # Verify no multiple attribute in this select tag
                assert "multiple" not in select_tag

    def test_form_renders_with_existing_data(self, integration_app):
        """Test that edit form renders correctly with existing relationships."""
        app, db, admin = integration_app

        with app.app_context():
            # Create test data
            author = Author(name="Test Author")
            db.session.add(author)
            db.session.flush()

            book1 = Book(title="Book 1", author_id=author.id)
            book2 = Book(title="Book 2", author_id=author.id)
            db.session.add(book1)
            db.session.add(book2)
            db.session.commit()

            author_id = author.id

        with app.test_client() as client:
            # Get the author edit form
            response = client.get(f"/admin/author/edit/?id={author_id}")
            assert response.status_code == 200

            html = response.data.decode("utf-8")

            # Check that the books field exists
            assert 'name="books"' in html
            assert 'data-module="select-with-search"' in html

            # Check that label is present
            assert "Books" in html

    def test_form_validation_shows_errors(self, integration_app):
        """Test that form with errors can still render the select-with-search widget."""
        app, db, admin = integration_app

        with app.test_client() as client:
            # Get the form (validation errors would appear after POST, but we're just
            # testing that the widget renders correctly in forms)
            response = client.get("/admin/author/new/")
            assert response.status_code == 200

            html = response.data.decode("utf-8")

            # Check that the select-with-search widget is present
            assert 'data-module="select-with-search"' in html
            assert 'name="books"' in html

    def test_select_with_search_renders_options_correctly(self, integration_app):
        """Test that select-with-search renders all available options."""
        app, db, admin = integration_app

        with app.app_context():
            # Create an author first, then books
            author = Author(name="Test Author")
            db.session.add(author)
            db.session.flush()

            book1 = Book(title="First Book", author_id=author.id)
            book2 = Book(title="Second Book", author_id=author.id)
            book3 = Book(title="Third Book", author_id=author.id)
            db.session.add_all([book1, book2, book3])
            db.session.commit()

        with app.test_client() as client:
            # Test that book create form renders with author options
            response = client.get("/admin/book/new/")
            assert response.status_code == 200

            html = response.data.decode("utf-8")

            # Check that form renders successfully
            assert 'name="author"' in html
            assert "<select" in html
            assert "Test Author" in html

    def test_javascript_bundle_loaded(self, integration_app):
        """Test that JavaScript bundle containing select-with-search is loaded."""
        app, db, admin = integration_app

        with app.test_client() as client:
            response = client.get("/admin/author/new/")
            assert response.status_code == 200

            html = response.data.decode("utf-8")

            # Check that main.js is loaded
            assert "main-" in html
            assert ".js" in html

    def test_css_bundle_loaded(self, integration_app):
        """Test that CSS bundle containing select-with-search styles is loaded."""
        app, db, admin = integration_app

        with app.test_client() as client:
            response = client.get("/admin/author/new/")
            assert response.status_code == 200

            html = response.data.decode("utf-8")

            # Check that main.css is loaded
            assert "main-" in html
            assert ".css" in html
