"""Unit tests for GovSelectWithSearch widget."""

import pytest
from flask import Flask
from markupsafe import Markup
from jinja2 import PackageLoader, ChoiceLoader, PrefixLoader
from xgov_flask_admin.widgets import GovSelectWithSearch


@pytest.fixture
def test_app():
    """Create a test Flask app with proper Jinja2 loaders."""
    app = Flask(__name__)
    app.config["TESTING"] = True

    # Configure Jinja2 loaders to find xgov-flask-admin templates
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

    return app


class DummyField:
    """Mock field for testing widget rendering."""

    def __init__(
        self,
        name="test_field",
        label="Test Field",
        description=None,
        choices=None,
        data=None,
        errors=None,
    ):
        self.name = name
        self.id = name
        self.label = type("obj", (object,), {"text": label})
        self.description = description
        self.data = data or []
        self.errors = errors or []
        self.flags = []
        self._choices = choices or []

    def iter_choices(self):
        """Mimic WTForms SelectField iter_choices."""
        for value, label in self._choices:
            selected = value in self.data
            yield value, label, selected, {}


class TestGovSelectWithSearchWidget:
    """Unit tests for the GovSelectWithSearch widget."""

    def test_widget_has_template(self):
        """Test that widget has correct template path."""
        widget = GovSelectWithSearch()
        assert widget.template == "select-with-search.html"

    def test_widget_single_select(self, test_app):
        """Test rendering a single-select field."""
        widget = GovSelectWithSearch(multiple=False)
        field = DummyField(
            name="country",
            label="Country",
            choices=[("uk", "United Kingdom"), ("us", "United States")],
            data=[],
        )

        with test_app.app_context():
            result = widget(field)

        assert isinstance(result, Markup)
        assert 'id="country"' in result
        assert 'name="country"' in result
        assert 'data-module="select-with-search"' in result
        assert '<label class="govuk-label"' in result
        assert "Country" in result
        assert "United Kingdom" in result
        assert "United States" in result

    def test_widget_multiple_select(self, test_app):
        """Test rendering a multi-select field."""
        widget = GovSelectWithSearch(multiple=True)
        field = DummyField(
            name="tags",
            label="Tags",
            choices=[("tag1", "Tag 1"), ("tag2", "Tag 2"), ("tag3", "Tag 3")],
            data=[],
        )

        with test_app.app_context():
            result = widget(field)

        assert isinstance(result, Markup)
        assert "multiple" in result
        assert 'data-module="select-with-search"' in result
        assert "Tag 1" in result
        assert "Tag 2" in result
        assert "Tag 3" in result

    def test_widget_with_selected_values(self, test_app):
        """Test rendering field with pre-selected values."""
        widget = GovSelectWithSearch(multiple=True)
        field = DummyField(
            name="colors",
            label="Favorite Colors",
            choices=[("red", "Red"), ("blue", "Blue"), ("green", "Green")],
            data=["red", "green"],
        )

        with test_app.app_context():
            result = widget(field)

        assert "selected" in result
        # Check that selected options have the selected attribute
        assert 'value="red" selected' in result or 'value="red"selected' in result
        assert 'value="green" selected' in result or 'value="green"selected' in result

    def test_widget_with_hint_text(self, test_app):
        """Test rendering field with hint text."""
        widget = GovSelectWithSearch(multiple=True)
        field = DummyField(
            name="topics",
            label="Topics",
            description="Select all topics that apply",
            choices=[("tech", "Technology"), ("science", "Science")],
            data=[],
        )

        with test_app.app_context():
            result = widget(field)

        assert "govuk-hint" in result
        assert "Select all topics that apply" in result
        assert 'aria-describedby="topics-hint"' in result

    def test_widget_with_error_message(self, test_app):
        """Test rendering field with error message."""
        widget = GovSelectWithSearch(multiple=True)
        field = DummyField(
            name="categories",
            label="Categories",
            choices=[("cat1", "Category 1"), ("cat2", "Category 2")],
            data=[],
            errors=["Please select at least one category"],
        )

        with test_app.app_context():
            result = widget(field)

        assert "govuk-form-group--error" in result
        assert "govuk-error-message" in result
        assert "Please select at least one category" in result
        assert "govuk-select--error" in result

    def test_widget_with_hint_and_error(self, test_app):
        """Test rendering field with both hint text and error message."""
        widget = GovSelectWithSearch(multiple=True)
        field = DummyField(
            name="skills",
            label="Skills",
            description="Choose your top skills",
            choices=[("python", "Python"), ("javascript", "JavaScript")],
            data=[],
            errors=["Select at least one skill"],
        )

        with test_app.app_context():
            result = widget(field)

        assert "govuk-hint" in result
        assert "Choose your top skills" in result
        assert "govuk-error-message" in result
        assert "Select at least one skill" in result
        assert 'aria-describedby="skills-hint skills-error"' in result

    def test_widget_empty_choices(self, test_app):
        """Test rendering field with no choices."""
        widget = GovSelectWithSearch(multiple=True)
        field = DummyField(name="empty", label="Empty Field", choices=[], data=[])

        with test_app.app_context():
            result = widget(field)

        assert "<select" in result
        assert 'id="empty"' in result
        # Should still render valid structure even with no options

    def test_widget_escapes_html_in_labels(self, test_app):
        """Test that HTML in labels is properly escaped."""
        widget = GovSelectWithSearch(multiple=False)
        field = DummyField(
            name="test",
            label="Test <script>alert('xss')</script>",
            choices=[
                ("1", "Option <b>1</b>"),
                ("<script>", "Dangerous <script>alert('xss')</script>"),
            ],
            data=[],
        )

        with test_app.app_context():
            result = widget(field)

        # HTML in label should be escaped
        assert "&lt;script&gt;" in result
        assert "<script>" not in result
        assert "&lt;b&gt;" in result

        # HTML in option text should be escaped
        assert "Option &lt;b&gt;1&lt;/b&gt;" in result
        assert "Dangerous &lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;" in result

        # HTML in option value should be escaped
        assert 'value="&lt;script&gt;"' in result

        # Raw HTML should NOT be present
        assert "<b>1</b>" not in result
        assert "alert('xss')" not in result

    def test_map_gov_params_preserves_items(self, test_app):
        """Test that map_gov_params correctly saves items before parent processing."""
        widget = GovSelectWithSearch(multiple=True)
        field = DummyField(
            name="test", label="Test", choices=[("a", "A"), ("b", "B")], data=[]
        )

        kwargs = {
            "id": "test",
            "items": [
                {"text": "A", "value": "a", "selected": False},
                {"text": "B", "value": "b", "selected": False},
            ],
            "multiple": True,
        }

        with test_app.app_context():
            params = widget.map_gov_params(field, **kwargs)

        assert "select_items" in params
        assert len(params["select_items"]) == 2
        assert params["select_items"][0]["text"] == "A"
        assert params["select_items"][1]["text"] == "B"
        assert params["multiple"] is True

    def test_widget_includes_gem_wrapper_class(self, test_app):
        """Test that widget includes the gem-c-select-with-search wrapper class."""
        widget = GovSelectWithSearch(multiple=True)
        field = DummyField(name="test", label="Test", choices=[("1", "One")], data=[])

        with test_app.app_context():
            result = widget(field)

        assert "gem-c-select-with-search" in result
        assert "govuk-form-group" in result
