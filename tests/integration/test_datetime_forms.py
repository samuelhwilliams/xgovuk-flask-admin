"""Integration tests for datetime form rendering and submission."""

import pytest
from datetime import datetime
from bs4 import BeautifulSoup
from example.models import User


@pytest.mark.integration
class TestDateTimeFormRendering:
    """Test datetime form field rendering."""

    def test_create_form_renders_datetime_input(self, client):
        """Test create form renders GovDateTimeInput widget."""
        response = client.get("/admin/user/new/")

        assert response.status_code == 200
        html = response.data.decode("utf-8")

        # Check for datetime field components (last_logged_in_at)
        assert "last_logged_in_at-day" in html
        assert "last_logged_in_at-month" in html
        assert "last_logged_in_at-year" in html
        assert "last_logged_in_at-hour" in html
        assert "last_logged_in_at-minute" in html
        assert "last_logged_in_at-second" in html

    def test_edit_form_renders_datetime_with_values(self, app, db_session, client):
        """Test edit form renders datetime fields with existing values."""
        # Create test user with datetime
        with app.app_context():
            user = User(
                email="datetime-test@example.com",
                name="DateTime Test",
                age=30,
                job="Tester",
                favourite_colour="RED",
                created_at=datetime(2024, 6, 15).date(),
                last_logged_in_at=datetime(2024, 6, 15, 14, 30, 45),
            )
            db_session.add(user)
            db_session.commit()
            user_id = user.id

        response = client.get(f"/admin/user/edit/?id={user_id}")

        assert response.status_code == 200
        html = response.data.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        # Check that datetime values are populated by finding specific input fields
        day_input = soup.find("input", id="last_logged_in_at-day")
        assert day_input is not None, "Day input not found"
        assert day_input.get("value") == "15", f"Expected day=15, got {day_input.get('value')}"

        month_input = soup.find("input", id="last_logged_in_at-month")
        assert month_input is not None, "Month input not found"
        assert month_input.get("value") == "06", f"Expected month=06, got {month_input.get('value')}"

        year_input = soup.find("input", id="last_logged_in_at-year")
        assert year_input is not None, "Year input not found"
        assert year_input.get("value") == "2024", f"Expected year=2024, got {year_input.get('value')}"

        hour_input = soup.find("input", id="last_logged_in_at-hour")
        assert hour_input is not None, "Hour input not found"
        assert hour_input.get("value") == "14", f"Expected hour=14, got {hour_input.get('value')}"

        minute_input = soup.find("input", id="last_logged_in_at-minute")
        assert minute_input is not None, "Minute input not found"
        assert minute_input.get("value") == "30", f"Expected minute=30, got {minute_input.get('value')}"

        second_input = soup.find("input", id="last_logged_in_at-second")
        assert second_input is not None, "Second input not found"
        assert second_input.get("value") == "45", f"Expected second=45, got {second_input.get('value')}"

        # Cleanup
        with app.app_context():
            db_session.delete(user)
            db_session.commit()

    def test_nullable_datetime_field_renders(self, client):
        """Test nullable datetime field renders correctly."""
        response = client.get("/admin/user/new/")

        assert response.status_code == 200
        html = response.data.decode("utf-8")

        # Check for nullable datetime field (last_logged_in_at is nullable)
        assert "last_logged_in_at-day" in html
        assert "last_logged_in_at-month" in html
        assert "last_logged_in_at-year" in html
        assert "last_logged_in_at-hour" in html
        assert "last_logged_in_at-minute" in html
        assert "last_logged_in_at-second" in html


@pytest.mark.integration
class TestDateTimeFormSubmission:
    """Test datetime form submission and validation."""

    def test_form_shows_govuk_styling(self, client):
        """Test datetime form fields have GOV.UK classes."""
        response = client.get("/admin/user/new/")

        assert response.status_code == 200
        html = response.data.decode("utf-8")

        # Check for GOV.UK classes
        assert "govuk-input" in html
        assert "govuk-form-group" in html
