"""Integration tests for XGovukAdminModelConverter."""

import pytest
from govuk_frontend_wtf.wtforms_widgets import GovTextInput, GovSelect
from xgovuk_flask_admin.widgets import GovDateInput


@pytest.mark.integration
class TestXGovukAdminModelConverter:
    """Test form field conversion for GOV.UK widgets."""

    def test_maps_string_to_gov_text_input(self,  user_model_view):
        """Test String columns get GovTextInput widget."""
        form = user_model_view.create_form()

        # Test string fields (email, name, job)
        assert isinstance(form.email.widget, GovTextInput)
        assert isinstance(form.name.widget, GovTextInput)
        assert isinstance(form.job.widget, GovTextInput)

    def test_maps_integer_with_inputmode(self, db_session, user_model_view):
        """Test Integer columns get numeric inputmode."""
        # Check that form_widget_args has inputmode set for integer fields
        assert "age" in user_model_view.form_widget_args
        assert "params" in user_model_view.form_widget_args["age"]
        assert (
            user_model_view.form_widget_args["age"]["params"]["inputmode"] == "numeric"
        )

        # Also verify the form field has GovTextInput widget
        form = user_model_view.create_form()
        assert isinstance(form.age.widget, GovTextInput)

    def test_maps_date_to_gov_date_input(self, db_session, user_model_view):
        """Test Date columns get GovDateInput widget with correct format."""
        form = user_model_view.create_form()

        # created_at is a Date field
        assert isinstance(form.created_at.widget, GovDateInput)
        # format is a list in WTForms DateField
        assert "%d %m %Y" in form.created_at.format

    def test_handles_enum_fields(self, db_session, user_model_view):
        """Test Enum columns are properly converted."""
        form = user_model_view.create_form()

        # favourite_colour is an Enum field
        assert isinstance(form.favourite_colour.widget, GovSelect)

        # Check that choices are available (enum values)
        choices = form.favourite_colour.choices
        assert len(choices) > 0

        # Choices should be tuples of (name, value) - e.g., ('RED', 'red')
        choice_names = [choice[0] for choice in choices if choice[0]]
        choice_labels = [choice[1] for choice in choices if choice[1]]

        # Verify enum names and values are in choices
        assert "RED" in choice_names
        assert "BLUE" in choice_names
        assert "YELLOW" in choice_names
        assert "red" in choice_labels
        assert "blue" in choice_labels
        assert "yellow" in choice_labels

    def test_widget_args_inheritance(self, db_session, user_model_view):
        """Test that widget args from view are merged with defaults."""
        # user_model_view should have implicit widget args populated
        assert hasattr(user_model_view, "form_widget_args")
        assert user_model_view.form_widget_args is not None

        # String fields should have label styling
        assert "name" in user_model_view.form_widget_args
        assert "label" in user_model_view.form_widget_args["name"]
        assert "classes" in user_model_view.form_widget_args["name"]["label"]
        assert (
            "govuk-label--s"
            in user_model_view.form_widget_args["name"]["label"]["classes"]
        )

        # Integer field should have inputmode in params
        assert "age" in user_model_view.form_widget_args
        assert "params" in user_model_view.form_widget_args["age"]
        assert (
            user_model_view.form_widget_args["age"]["params"]["inputmode"] == "numeric"
        )

    def test_field_args_inheritance(self, db_session, user_model_view):
        """Test that field args from view are merged with defaults."""
        # user_model_view should have implicit form args populated
        assert hasattr(user_model_view, "form_args")
        assert user_model_view.form_args is not None

        # String fields should have widget set
        assert "name" in user_model_view.form_args
        assert "widget" in user_model_view.form_args["name"]
        assert isinstance(user_model_view.form_args["name"]["widget"], GovTextInput)

        # Date field should have widget and format
        assert "created_at" in user_model_view.form_args
        assert "widget" in user_model_view.form_args["created_at"]
        assert isinstance(
            user_model_view.form_args["created_at"]["widget"], GovDateInput
        )
        assert user_model_view.form_args["created_at"]["format"] == "%d %m %Y"

        # Email field should preserve custom validators from view definition
        assert "email" in user_model_view.form_args
        assert "validators" in user_model_view.form_args["email"]
        # The Email validator should be present (added in UserModelView)
        validator_types = [
            type(v).__name__ for v in user_model_view.form_args["email"]["validators"]
        ]
        assert "Email" in validator_types
