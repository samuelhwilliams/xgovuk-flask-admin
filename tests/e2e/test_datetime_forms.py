"""E2E tests for datetime form validation and submission."""

import pytest


@pytest.mark.e2e
class TestDateTimeFormRendering:
    """Test datetime form rendering in browser."""

    def test_datetime_fields_render_six_inputs(self, page):
        """Test datetime fields render with six separate input boxes."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Check for datetime field (last_logged_in_at)
        assert page.locator("#last_logged_in_at-day").is_visible()
        assert page.locator("#last_logged_in_at-month").is_visible()
        assert page.locator("#last_logged_in_at-year").is_visible()
        assert page.locator("#last_logged_in_at-hour").is_visible()
        assert page.locator("#last_logged_in_at-minute").is_visible()
        assert page.locator("#last_logged_in_at-second").is_visible()

    def test_datetime_fields_have_govuk_classes(self, page):
        """Test datetime input fields have GOV.UK Design System classes."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Check GOV.UK classes on datetime inputs
        day_input = page.locator("#last_logged_in_at-day")
        assert "govuk-input" in day_input.get_attribute("class")

        hour_input = page.locator("#last_logged_in_at-hour")
        assert "govuk-input" in hour_input.get_attribute("class")

    def test_datetime_fields_have_appropriate_widths(self, page):
        """Test datetime fields have appropriate width classes."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Day and month should be width-2
        day_input = page.locator("#last_logged_in_at-day")
        assert "govuk-input--width-2" in day_input.get_attribute("class")

        # Year should be width-4
        year_input = page.locator("#last_logged_in_at-year")
        assert "govuk-input--width-4" in year_input.get_attribute("class")

    def test_datetime_fields_have_labels(self, page):
        """Test datetime fields have appropriate labels."""
        page.goto(f"{page.base_url}/admin/user/new/")
        page_content = page.content()

        # Check for field labels
        assert "Day" in page_content
        assert "Month" in page_content
        assert "Year" in page_content
        assert "Hour" in page_content
        assert "Minute" in page_content
        assert "Second" in page_content


@pytest.mark.e2e
class TestDateTimeFormSubmission:
    """Test datetime form submission."""

    def test_submit_form_with_valid_datetime(self, page):
        """Test submitting form with valid datetime."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Fill in required fields
        page.fill('input[name="email"]', "datetime-test@example.com")
        page.fill('input[name="name"]', "DateTime Test User")
        page.fill('input[name="age"]', "30")
        page.fill('input[name="job"]', "Tester")
        page.select_option("#favourite_colour", "RED")

        # Fill in date field (created_at)
        page.fill("#created_at-day", "15")
        page.fill("#created_at-month", "6")
        page.fill("#created_at-year", "2024")

        # Fill in datetime field (last_logged_in_at)
        page.fill("#last_logged_in_at-day", "20")
        page.fill("#last_logged_in_at-month", "8")
        page.fill("#last_logged_in_at-year", "2024")
        page.fill("#last_logged_in_at-hour", "14")
        page.fill("#last_logged_in_at-minute", "30")
        page.fill("#last_logged_in_at-second", "45")

        # Submit form
        page.click('input[type="submit"]')

        # Should redirect to list view
        assert "/admin/user/" in page.url
        assert "/admin/user/new/" not in page.url

        # Should show success message
        success_banner = page.locator(".govuk-notification-banner--success")
        assert success_banner.is_visible()

    def test_submit_form_with_invalid_datetime_day(self, page):
        """Test submitting form with invalid day in datetime."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Fill in required fields
        page.fill('input[name="email"]', "invalid-dt@example.com")
        page.fill('input[name="name"]', "Invalid DT User")
        page.fill('input[name="age"]', "30")
        page.fill('input[name="job"]', "Tester")
        page.select_option("#favourite_colour", "RED")

        # Fill in date field
        page.fill("#created_at-day", "15")
        page.fill("#created_at-month", "6")
        page.fill("#created_at-year", "2024")

        # Fill in datetime with invalid day
        page.fill("#last_logged_in_at-day", "32")  # Invalid
        page.fill("#last_logged_in_at-month", "8")
        page.fill("#last_logged_in_at-year", "2024")
        page.fill("#last_logged_in_at-hour", "14")
        page.fill("#last_logged_in_at-minute", "30")
        page.fill("#last_logged_in_at-second", "45")

        # Submit form
        page.click('input[type="submit"]')

        # Should show error
        error_messages = page.locator(".govuk-error-message")
        assert error_messages.count() > 0

    def test_submit_form_with_invalid_datetime_hour(self, page):
        """Test submitting form with invalid hour in datetime."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Fill in required fields
        page.fill('input[name="email"]', "invalid-hour@example.com")
        page.fill('input[name="name"]', "Invalid Hour User")
        page.fill('input[name="age"]', "30")
        page.fill('input[name="job"]', "Tester")
        page.select_option("#favourite_colour", "RED")

        # Fill in date field
        page.fill("#created_at-day", "15")
        page.fill("#created_at-month", "6")
        page.fill("#created_at-year", "2024")

        # Fill in datetime with invalid hour
        page.fill("#last_logged_in_at-day", "20")
        page.fill("#last_logged_in_at-month", "8")
        page.fill("#last_logged_in_at-year", "2024")
        page.fill("#last_logged_in_at-hour", "25")  # Invalid
        page.fill("#last_logged_in_at-minute", "30")
        page.fill("#last_logged_in_at-second", "45")

        # Submit form
        page.click('input[type="submit"]')

        # Should show error
        error_messages = page.locator(".govuk-error-message")
        assert error_messages.count() > 0

    def test_submit_form_with_nullable_datetime_empty(self, page):
        """Test submitting form with nullable datetime left empty."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Fill in required fields
        page.fill('input[name="email"]', "no-datetime@example.com")
        page.fill('input[name="name"]', "No DateTime User")
        page.fill('input[name="age"]', "30")
        page.fill('input[name="job"]', "Tester")
        page.select_option("#favourite_colour", "RED")

        # Fill in date field (required)
        page.fill("#created_at-day", "15")
        page.fill("#created_at-month", "6")
        page.fill("#created_at-year", "2024")

        # Leave datetime field empty (nullable)
        # Don't fill last_logged_in_at fields

        # Submit form
        page.click('input[type="submit"]')

        # Should succeed and redirect to list view
        assert "/admin/user/" in page.url
        assert "/admin/user/new/" not in page.url

    def test_edit_form_shows_existing_datetime(self, page):
        """Test edit form shows existing datetime values."""
        # First create a user with datetime
        page.goto(f"{page.base_url}/admin/user/new/")

        page.fill('input[name="email"]', "edit-datetime@example.com")
        page.fill('input[name="name"]', "Edit DateTime User")
        page.fill('input[name="age"]', "30")
        page.fill('input[name="job"]', "Tester")
        page.select_option("#favourite_colour", "RED")

        page.fill("#created_at-day", "15")
        page.fill("#created_at-month", "6")
        page.fill("#created_at-year", "2024")

        page.fill("#last_logged_in_at-day", "20")
        page.fill("#last_logged_in_at-month", "8")
        page.fill("#last_logged_in_at-year", "2024")
        page.fill("#last_logged_in_at-hour", "14")
        page.fill("#last_logged_in_at-minute", "30")
        page.fill("#last_logged_in_at-second", "45")

        page.click('input[type="submit"]')

        # Now navigate to edit the user
        page.goto(f"{page.base_url}/admin/user/")

        # Find and click edit link for our user
        page.locator('a:has-text("Edit")')
        # Find the row containing our user's email
        rows = page.locator(".govuk-table__body .govuk-table__row")
        for i in range(rows.count()):
            row_text = rows.nth(i).text_content()
            if "edit-datetime@example.com" in row_text:
                rows.nth(i).locator('a:has-text("Edit")').click()
                break

        assert "/admin/user/edit/" in page.url

        # Check that datetime values are pre-filled
        assert page.locator("#last_logged_in_at-day").input_value() == "20"
        assert page.locator("#last_logged_in_at-month").input_value() == "08"
        assert page.locator("#last_logged_in_at-year").input_value() == "2024"
        assert page.locator("#last_logged_in_at-hour").input_value() == "14"
        assert page.locator("#last_logged_in_at-minute").input_value() == "30"
        assert page.locator("#last_logged_in_at-second").input_value() == "45"

    def test_datetime_fields_show_error_class_on_validation_error(self, page):
        """Test datetime fields show error class when validation fails."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Fill in required fields
        page.fill('input[name="email"]', "error-class@example.com")
        page.fill('input[name="name"]', "Error Class User")
        page.fill('input[name="age"]', "30")
        page.fill('input[name="job"]', "Tester")
        page.select_option("#favourite_colour", "RED")

        page.fill("#created_at-day", "15")
        page.fill("#created_at-month", "6")
        page.fill("#created_at-year", "2024")

        # Fill in invalid datetime
        page.fill("#last_logged_in_at-day", "20")
        page.fill("#last_logged_in_at-month", "8")
        page.fill("#last_logged_in_at-year", "2024")
        page.fill("#last_logged_in_at-hour", "99")  # Invalid
        page.fill("#last_logged_in_at-minute", "30")
        page.fill("#last_logged_in_at-second", "45")

        # Submit form
        page.click('input[type="submit"]')

        # Check for error styling on datetime inputs
        day_input = page.locator("#last_logged_in_at-day")
        input_classes = day_input.get_attribute("class")
        assert "govuk-input--error" in input_classes

    def test_submit_datetime_with_midnight(self, page):
        """Test submitting datetime with midnight time (00:00:00)."""
        page.goto(f"{page.base_url}/admin/user/new/")

        page.fill('input[name="email"]', "midnight@example.com")
        page.fill('input[name="name"]', "Midnight User")
        page.fill('input[name="age"]', "30")
        page.fill('input[name="job"]', "Tester")
        page.select_option("#favourite_colour", "RED")

        page.fill("#created_at-day", "15")
        page.fill("#created_at-month", "6")
        page.fill("#created_at-year", "2024")

        # Midnight datetime
        page.fill("#last_logged_in_at-day", "1")
        page.fill("#last_logged_in_at-month", "1")
        page.fill("#last_logged_in_at-year", "2024")
        page.fill("#last_logged_in_at-hour", "0")
        page.fill("#last_logged_in_at-minute", "0")
        page.fill("#last_logged_in_at-second", "0")

        page.click('input[type="submit"]')

        # Should succeed
        assert "/admin/user/" in page.url
        assert "/admin/user/new/" not in page.url
        success_banner = page.locator(".govuk-notification-banner--success")
        assert success_banner.is_visible()
