"""Unit tests for XGovCheckboxInput widget."""

import pytest
from flask import Flask
from jinja2 import PackageLoader, ChoiceLoader, PrefixLoader
from xgovuk_flask_admin.widgets import XGovCheckboxInput


@pytest.fixture
def test_app():
    """Create a test Flask app with proper Jinja2 loaders."""
    app = Flask(__name__)
    app.config["TESTING"] = True

    # Configure Jinja2 loaders to find xgovuk-flask-admin templates
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

    return app


class DummyField:
    """Mock field for testing widget rendering."""

    def __init__(
        self,
        name="test_checkbox",
        label="Test Checkbox",
        description=None,
    ):
        self.name = name
        self.id = name
        self.label = type("obj", (object,), {"text": label})
        self.description = description
        self.errors = []
        self.flags = []


class TestXGovCheckboxInput:
    """Unit tests for the XGovCheckboxInput widget hint handling."""

    def test_map_gov_params_strips_none_hint(self, test_app):
        """Test that map_gov_params strips hint when text is None.

        This addresses: https://github.com/LandRegistry/govuk-frontend-wtf/issues/112
        """
        widget = XGovCheckboxInput()
        field = DummyField(
            name="test",
            label="Test",
            description=None,
        )

        with test_app.app_context():
            # GovCheckboxInput expects items in kwargs
            params = widget.map_gov_params(field, items=[])

        # Should not have a 'hint' key when description is None
        assert 'hint' not in params

    def test_map_gov_params_preserves_valid_hint(self, test_app):
        """Test that map_gov_params preserves hint when text is provided."""
        widget = XGovCheckboxInput()
        field = DummyField(
            name="test",
            label="Test",
            description="Valid hint text",
        )

        with test_app.app_context():
            # GovCheckboxInput expects items in kwargs
            params = widget.map_gov_params(field, items=[])

        # Should have hint with valid text
        assert 'hint' in params
        assert params['hint']['text'] == "Valid hint text"
