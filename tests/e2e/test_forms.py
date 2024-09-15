"""E2E tests for form validation and submission."""

import pytest


@pytest.mark.e2e
class TestFormValidation:
    """Test client-side and server-side form validation."""

    def test_required_field_validation(self, page):
        """Test required field validation shows errors."""
        page.goto(f"{page.base_url}/admin/user/new/")
        page.click('input[type="submit"]')

        error_messages = page.locator(".govuk-error-message")
        assert error_messages.count() > 0, "Expected error messages to be displayed"

        assert error_messages.first.get_attribute("class") == "govuk-error-message"

        error_form_groups = page.locator(".govuk-form-group--error")
        assert error_form_groups.count() > 0, "Expected form groups to have error class"

    def test_email_validation(self, page):
        """Test email field validates format."""
        page.goto(f"{page.base_url}/admin/user/new/")

        page.fill('input[name="email"]', "invalid-email")
        page.fill('input[name="name"]', "Test User")
        page.fill('input[name="age"]', "25")
        page.fill('input[name="job"]', "Tester")
        page.select_option("#favourite_colour", "RED")
        page.fill("#created_at-day", "15")
        page.fill("#created_at-month", "6")
        page.fill("#created_at-year", "2024")

        page.click('input[type="submit"]')

        email_error = page.locator("#email-error")
        assert email_error.is_visible(), "Expected email format validation error"
        error_text = email_error.text_content()
        assert "Invalid email address." in error_text, (
            f"Expected 'Invalid email address.' error, got: {error_text}"
        )

    def test_date_input_validation(self, page):
        """Test date input validates day/month/year."""
        page.goto(f"{page.base_url}/admin/user/new/")

        page.fill("#created_at-day", "32")
        page.fill("#created_at-month", "13")
        page.fill("#created_at-year", "2024")

        page.fill('input[name="email"]', "test@example.com")
        page.fill('input[name="name"]', "Test User")
        page.fill('input[name="age"]', "25")
        page.fill('input[name="job"]', "Tester")
        page.select_option("#favourite_colour", "RED")

        page.click('input[type="submit"]')

        error_messages = page.locator(".govuk-error-message")
        assert error_messages.count() > 0, "Expected date validation error"

    def test_error_summary(self, page):
        """Test error summary appears at top of form."""
        page.goto(f"{page.base_url}/admin/user/new/")
        page.click('input[type="submit"]')

        error_summary = page.locator(".govuk-error-summary")
        assert error_summary.is_visible(), "Expected GOV.UK error summary to be visible"

        error_title = page.locator(".govuk-error-summary__title")
        assert error_title.is_visible(), "Expected error summary title"

        error_list = page.locator(".govuk-error-summary__list")
        assert error_list.is_visible(), "Expected error summary list"

        error_links = page.locator(".govuk-error-summary__list a")
        assert error_links.count() > 0, "Expected links to fields with errors"


@pytest.mark.e2e
class TestFormSubmission:
    """Test successful form submission."""

    def test_create_form_submission(self, page):
        """Test successful record creation via form."""
        page.goto(f"{page.base_url}/admin/user/new/")

        page.fill('input[name="email"]', "e2e-test@example.com")
        page.fill('input[name="name"]', "E2E Test User")
        page.fill('input[name="age"]', "30")
        page.fill('input[name="job"]', "Tester")
        page.select_option("#favourite_colour", "RED")
        page.fill("#created_at-day", "15")
        page.fill("#created_at-month", "6")
        page.fill("#created_at-year", "2024")

        page.click('input[type="submit"]')

        assert "/admin/user/" in page.url, "Expected redirect to list view"
        assert "/admin/user/new/" not in page.url, "Should not remain on create page"

        success_banner = page.locator(".govuk-notification-banner--success")
        assert success_banner.is_visible(), "Expected success notification banner"
        success_text = success_banner.text_content()
        assert "Record was successfully created." in success_text, (
            f"Expected 'Record was successfully created.' message, got: {success_text}"
        )

        table_rows = page.locator(".govuk-table__body .govuk-table__row")
        found_new_user = False
        for i in range(table_rows.count()):
            row_text = table_rows.nth(i).text_content()
            if "e2e-test@example.com" in row_text:
                found_new_user = True
                break
        assert found_new_user, "Expected to find newly created user in list view"

    def test_edit_form_submission(self, page):
        """Test successful record update via form."""
        page.goto(f"{page.base_url}/admin/user/")

        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()

        assert "/admin/user/edit/" in page.url, "Expected to be on edit page"

        page.fill('input[name="name"]', "Updated E2E User")
        page.fill('input[name="age"]', "35")
        page.fill('input[name="job"]', "Senior Tester")

        page.click('input[type="submit"]')

        assert "/admin/user/" in page.url, "Expected redirect to list view"
        assert "/admin/user/edit/" not in page.url, "Should not remain on edit page"

        success_banner = page.locator(".govuk-notification-banner--success")
        assert success_banner.is_visible(), "Expected success notification banner"
        success_text = success_banner.text_content()
        assert "Record was successfully saved." in success_text, (
            f"Expected 'Record was successfully saved.' message, got: {success_text}"
        )

        table_rows = page.locator(".govuk-table__body .govuk-table__row")
        found_updated_user = False
        for i in range(table_rows.count()):
            row_text = table_rows.nth(i).text_content()
            if "Updated E2E User" in row_text and "Senior Tester" in row_text:
                found_updated_user = True
                break
        assert found_updated_user, "Expected to find updated user data in list view"


@pytest.mark.e2e
class TestFormComponents:
    """Test GOV.UK form components render correctly."""

    def test_govuk_input_classes(self, page):
        """Test text inputs have GOV.UK classes."""
        page.goto(f"{page.base_url}/admin/user/new/")

        text_inputs = page.locator(
            'input.govuk-input[type="text"], input.govuk-input[type="email"]'
        )
        assert text_inputs.count() > 0, "Expected text/email inputs with GOV.UK classes"

        email_input = page.locator('input[name="email"]')
        assert "govuk-input" in email_input.get_attribute("class"), (
            "Email input should have govuk-input class"
        )

        name_input = page.locator('input[name="name"]')
        assert "govuk-input" in name_input.get_attribute("class"), (
            "Name input should have govuk-input class"
        )

        age_input = page.locator('input[name="age"]')
        assert "govuk-input" in age_input.get_attribute("class"), (
            "Age input should have govuk-input class"
        )

        form_groups = page.locator(".govuk-form-group")
        assert form_groups.count() > 0, "Expected form groups with GOV.UK classes"

    def test_govuk_select_classes(self, page):
        """Test select dropdowns have GOV.UK classes."""
        page.goto(f"{page.base_url}/admin/user/new/")

        selects = page.locator("select.govuk-select")
        assert selects.count() > 0, "Expected select elements with GOV.UK classes"

        colour_select = page.locator('select[id="favourite_colour"]')
        assert colour_select.count() > 0, "Expected favourite_colour select field"
        assert "govuk-select" in colour_select.get_attribute("class"), (
            "Select should have govuk-select class"
        )

        options = colour_select.locator("option")
        assert options.count() >= 3, (
            "Expected at least 3 colour options (plus possibly blank)"
        )

    def test_govuk_button_classes(self, page):
        """Test buttons have GOV.UK classes."""
        page.goto(f"{page.base_url}/admin/user/new/")

        buttons = page.locator(".govuk-button")
        assert buttons.count() > 0, "Expected buttons with GOV.UK classes"

        submit_button = page.locator('input[type="submit"].govuk-button')
        assert submit_button.count() > 0, (
            "Expected submit button with govuk-button class"
        )

        assert submit_button.is_visible(), "Submit button should be visible"
        assert submit_button.is_enabled(), "Submit button should be enabled"
