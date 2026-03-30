"""E2E tests for form validation and submission."""

import pytest


@pytest.mark.e2e
class TestFormValidation:
    """Test client-side and server-side form validation."""

    def test_required_field_validation(self, page, screenshot):
        """Test required field validation shows errors."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Capture clean form state
        screenshot(page, "form-create-empty")

        page.click('input[type="submit"]')

        error_messages = page.locator(".govuk-error-message")
        assert error_messages.count() > 0, "Expected error messages to be displayed"

        assert error_messages.first.get_attribute("class") == "govuk-error-message"

        error_form_groups = page.locator(".govuk-form-group--error")
        assert error_form_groups.count() > 0, "Expected form groups to have error class"

        # Capture form with validation errors
        screenshot(page, "form-create-validation-errors")

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

    def test_create_form_submission(self, page, screenshot):
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
        page.check('input[name="active"]')

        page.click('input[type="submit"]')

        assert "/admin/user/" in page.url, "Expected redirect to list view"
        assert "/admin/user/new/" not in page.url, "Should not remain on create page"

        success_banner = page.locator(".govuk-notification-banner--success")
        assert success_banner.is_visible(), "Expected success notification banner"
        success_text = success_banner.text_content()
        assert "Record was successfully created." in success_text, (
            f"Expected 'Record was successfully created.' message, got: {success_text}"
        )

        # Capture success notification
        screenshot(page, "list-view-success-notification")

        table_rows = page.locator(".govuk-table__body .govuk-table__row")
        found_new_user = False
        for i in range(table_rows.count()):
            row_text = table_rows.nth(i).text_content()
            if "e2e-test@example.com" in row_text:
                found_new_user = True
                break
        assert found_new_user, "Expected to find newly created user in list view"

    def test_checkbox_form_submission(self, page):
        """Test checkbox field submits correctly and persists to database."""
        # Test creating with checkbox checked (active=True)
        page.goto(f"{page.base_url}/admin/user/new/")

        page.fill('input[name="email"]', "checkbox-test-active@example.com")
        page.fill('input[name="name"]', "Active User")
        page.fill('input[name="age"]', "28")
        page.fill('input[name="job"]', "Developer")
        page.select_option("#favourite_colour", "BLUE")
        page.fill("#created_at-day", "10")
        page.fill("#created_at-month", "3")
        page.fill("#created_at-year", "2024")

        # Check the active checkbox
        active_checkbox = page.locator('input[name="active"]')
        active_checkbox.check()
        assert active_checkbox.is_checked(), "Active checkbox should be checked"

        page.click('input[type="submit"]')

        success_banner = page.locator(".govuk-notification-banner--success")
        assert success_banner.is_visible(), "Expected success notification"

        # Navigate to the list view and find the created user
        page.goto(f"{page.base_url}/admin/user/")

        # Open filter panel to access search
        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()

        # Search for the active user to verify it was created
        search_input = page.locator('input[name="search"]')
        search_input.fill("checkbox-test-active@example.com")
        search_button = page.locator('button[type="submit"]:has-text("Apply filters")')
        search_button.click()

        # Find the user row and click edit
        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()

        # Verify the checkbox is checked when editing (confirms database state)
        active_checkbox_edit = page.locator('input[name="active"]')
        assert active_checkbox_edit.is_checked(), (
            "Active checkbox should be checked when editing (database value should be True)"
        )

        # Test creating with checkbox unchecked (active=False)
        page.goto(f"{page.base_url}/admin/user/new/")

        page.fill('input[name="email"]', "checkbox-test-inactive@example.com")
        page.fill('input[name="name"]', "Inactive User")
        page.fill('input[name="age"]', "32")
        page.fill('input[name="job"]', "Manager")
        page.select_option("#favourite_colour", "YELLOW")
        page.fill("#created_at-day", "20")
        page.fill("#created_at-month", "7")
        page.fill("#created_at-year", "2024")

        # Ensure the active checkbox is unchecked
        active_checkbox = page.locator('input[name="active"]')
        if active_checkbox.is_checked():
            active_checkbox.uncheck()
        assert not active_checkbox.is_checked(), "Active checkbox should be unchecked"

        page.click('input[type="submit"]')

        success_banner = page.locator(".govuk-notification-banner--success")
        assert success_banner.is_visible(), "Expected success notification"

        # Navigate to the list view and find the inactive user
        page.goto(f"{page.base_url}/admin/user/")

        # Open filter panel to access search
        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()

        # Search for the inactive user
        search_input = page.locator('input[name="search"]')
        search_input.fill("checkbox-test-inactive@example.com")
        search_button = page.locator('button[type="submit"]:has-text("Apply filters")')
        search_button.click()

        # Find the user row and click edit
        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()

        # Verify the checkbox is unchecked when editing (confirms database value is False)
        active_checkbox_edit = page.locator('input[name="active"]')
        assert not active_checkbox_edit.is_checked(), (
            "Active checkbox should be unchecked when editing (database value should be False)"
        )

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

    def test_govuk_checkbox_classes(self, page):
        """Test boolean fields render as GOV.UK checkboxes."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Check for GOV.UK checkbox container
        checkbox_containers = page.locator(".govuk-checkboxes")
        assert checkbox_containers.count() > 0, (
            "Expected checkbox container with GOV.UK classes"
        )

        # Check for the active field checkbox
        active_checkbox = page.locator('input[name="active"]')
        assert active_checkbox.count() > 0, "Expected active checkbox field"

        # Verify it has GOV.UK checkbox input class
        checkbox_input_class = active_checkbox.get_attribute("class")
        assert "govuk-checkboxes__input" in checkbox_input_class, (
            f"Expected govuk-checkboxes__input class, got: {checkbox_input_class}"
        )

        # Verify it's a checkbox type
        assert active_checkbox.get_attribute("type") == "checkbox", (
            "Active field should be a checkbox input"
        )

        # Check for associated label with GOV.UK class
        active_label = page.locator('label[for="active"]')
        assert active_label.count() > 0, "Expected label for active checkbox"
        label_class = active_label.get_attribute("class")
        assert "govuk-checkboxes__label" in label_class, (
            f"Expected govuk-checkboxes__label class, got: {label_class}"
        )

        # Verify form group has GOV.UK class
        form_groups = page.locator(".govuk-form-group")
        assert form_groups.count() > 0, "Expected form groups with GOV.UK classes"
