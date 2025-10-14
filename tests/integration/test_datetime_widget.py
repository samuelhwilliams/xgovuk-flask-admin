"""Unit tests for GovDateTimeInput widget."""

import pytest
from datetime import datetime
from wtforms import Form, DateTimeField
from xgovuk_flask_admin.widgets import GovDateTimeInput


class DateTimeForm(Form):
    """Test form with datetime field using GovDateTimeInput widget."""

    test_datetime = DateTimeField(
        "Test DateTime", widget=GovDateTimeInput(), format="%d %m %Y %H %M %S"
    )


@pytest.mark.integration
class TestGovDateTimeInput:
    """Test GovDateTimeInput widget rendering and parsing."""

    def test_widget_renders_six_fields(self, app):
        """Test widget renders six separate input fields."""
        with app.app_context():
            form = DateTimeForm()
            html = str(form.test_datetime)

            # Check that all six field IDs are present
            assert "test_datetime-day" in html
            assert "test_datetime-month" in html
            assert "test_datetime-year" in html
            assert "test_datetime-hour" in html
            assert "test_datetime-minute" in html
            assert "test_datetime-second" in html

    def test_widget_renders_with_existing_datetime(self, app):
        """Test widget renders correctly with existing datetime value."""
        with app.app_context():
            dt = datetime(2024, 6, 15, 14, 30, 45)
            form = DateTimeForm(data={"test_datetime": dt})
            html = str(form.test_datetime)

            # Check that values are correctly populated
            assert 'value="15"' in html or "value='15'" in html  # day
            assert 'value="06"' in html or "value='06'" in html  # month (zero-padded)
            assert 'value="2024"' in html or "value='2024'" in html  # year
            assert 'value="14"' in html or "value='14'" in html  # hour
            assert 'value="30"' in html or "value='30'" in html  # minute
            assert 'value="45"' in html or "value='45'" in html  # second

    def test_widget_template_name(self):
        """Test widget has correct template name."""
        widget = GovDateTimeInput()
        assert widget.template == "datetime-input.html"

    def test_widget_creates_fieldset(self, app):
        """Test widget creates GOV.UK fieldset structure."""
        with app.app_context():
            form = DateTimeForm()
            html = str(form.test_datetime)

            # Should include fieldset with legend
            assert "Test DateTime" in html  # Label should be in legend

    def test_widget_field_labels(self, app):
        """Test widget sets correct labels for each field."""
        with app.app_context():
            form = DateTimeForm()
            html = str(form.test_datetime)

            # Check for field labels (these are set in the widget's map_gov_params)
            assert "Day" in html
            assert "Month" in html
            assert "Year" in html
            assert "Hour" in html
            assert "Minute" in html
            assert "Second" in html

    def test_widget_handles_midnight(self, app):
        """Test widget correctly handles midnight (00:00:00)."""
        with app.app_context():
            dt = datetime(2024, 1, 1, 0, 0, 0)
            form = DateTimeForm(data={"test_datetime": dt})
            html = str(form.test_datetime)

            # Check midnight is rendered
            assert 'value="01"' in html or "value='01'" in html  # day
            assert 'value="2024"' in html or "value='2024'" in html  # year
            assert 'value="00"' in html or "value='00'" in html  # hour/minute/second

    def test_widget_handles_end_of_day(self, app):
        """Test widget correctly handles 23:59:59."""
        with app.app_context():
            dt = datetime(2024, 12, 31, 23, 59, 59)
            form = DateTimeForm(data={"test_datetime": dt})
            html = str(form.test_datetime)

            # Check end of day is rendered
            assert 'value="31"' in html or "value='31'" in html  # day
            assert 'value="12"' in html or "value='12'" in html  # month
            assert 'value="23"' in html or "value='23'" in html  # hour
            assert 'value="59"' in html or "value='59'" in html  # minute/second
