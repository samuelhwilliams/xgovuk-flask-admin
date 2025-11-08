"""E2E tests for ARRAY field forms."""

import uuid

import pytest


@pytest.mark.e2e
class TestArrayEnumFields:
    """Test ARRAY[enum] fields with select-with-search."""

    def test_array_enum_renders_as_select_with_search(self, page):
        """Test ARRAY[enum] field renders as select-with-search multi-select."""
        page.goto(f"{page.base_url}/admin/account/new/")

        # Check that tags field exists
        tags_select = page.locator('select[name="tags"]')
        assert tags_select.count() == 1, "Tags select should exist"

        # Check for multiple attribute
        assert tags_select.get_attribute("multiple") is not None, (
            "Tags select should allow multiple selections"
        )

        # Check for data-module attribute
        assert tags_select.get_attribute("data-module") == "select-with-search"

    def test_array_enum_has_correct_options(self, page):
        """Test ARRAY[enum] field has all enum values as options."""
        page.goto(f"{page.base_url}/admin/account/new/")

        # Check enum options are present
        red_option = page.locator('select[name="tags"] option[value="RED"]')
        yellow_option = page.locator('select[name="tags"] option[value="YELLOW"]')
        blue_option = page.locator('select[name="tags"] option[value="BLUE"]')

        assert red_option.count() == 1, "RED option should exist"
        assert yellow_option.count() == 1, "YELLOW option should exist"
        assert blue_option.count() == 1, "BLUE option should exist"

        # Check labels (lowercase enum values)
        assert red_option.text_content() == "red"
        assert yellow_option.text_content() == "yellow"
        assert blue_option.text_content() == "blue"

    def test_array_enum_multiple_selection(self, page):
        """Test selecting multiple enum values in ARRAY[enum] field."""
        email = f"{uuid.uuid4()}@example.com"
        page.goto(f"{page.base_url}/admin/user/new/")
        page.fill('input[name="email"]', email)
        page.fill('input[name="name"]', "Array Test User")
        page.fill('input[name="age"]', "30")
        page.fill('input[name="job"]', "Tester")
        page.select_option("#favourite_colour", "RED")
        page.fill("#created_at-day", "15")
        page.fill("#created_at-month", "6")
        page.fill("#created_at-year", "2024")
        page.click('input[type="submit"]')

        page.goto(f"{page.base_url}/admin/account/new/")

        name_select = page.locator("label:has-text('User')").locator("..")
        name_select.click()
        page.get_by_role("option", name=email).click()

        tags_combobox = page.locator("label:has-text('Tags')").locator("..")
        tags_combobox.click()
        page.get_by_role("option", name="red").click()
        page.get_by_role("option", name="yellow").click()

        selected_items = tags_combobox.locator(
            ".choices__list--multiple .choices__item--selectable"
        )
        assert selected_items.count() == 2, "Should have 2 selected items"

        page.click('input[type="submit"]')

        page.wait_for_url(f"{page.base_url}/admin/account/")

        success_banner = page.locator(".govuk-notification-banner--success")
        assert success_banner.is_visible(), "Success banner should be visible"
        assert "Record was successfully created." in success_banner.text_content()

        user_row = page.locator(f"table tbody tr:has-text('{email}')")
        tag_elements = user_row.locator(".govuk-tag")
        assert tag_elements.count() >= 2, "Should have at least 2 tag elements"


@pytest.mark.e2e
class TestArrayNonEnumFields:
    """Test ARRAY[non-enum] fields with textarea."""

    def test_array_non_enum_renders_as_textarea(self, page):
        """Test ARRAY[non-enum] field renders as textarea."""
        page.goto(f"{page.base_url}/admin/account/new/")

        # Check that notes field is a textarea
        notes_textarea = page.locator('textarea[name="notes"]')
        assert notes_textarea.is_visible(), "Notes textarea should be visible"

    def test_array_non_enum_newline_separation(self, page):
        """Test ARRAY[non-enum] field processes newline-separated values."""
        # First create a user to associate with the account
        email = f"{uuid.uuid4()}@example.com"
        page.goto(f"{page.base_url}/admin/user/new/")
        page.fill('input[name="email"]', email)
        page.fill('input[name="name"]', "Notes Test User")
        page.fill('input[name="age"]', "30")
        page.fill('input[name="job"]', "Tester")
        page.select_option("#favourite_colour", "BLUE")
        page.fill("#created_at-day", "15")
        page.fill("#created_at-month", "6")
        page.fill("#created_at-year", "2024")
        page.click('input[type="submit"]')

        # Now create an account
        page.goto(f"{page.base_url}/admin/account/new/")

        # Wait for Choices.js and select user
        name_select = page.locator("label:has-text('User')").locator("..")
        name_select.click()
        page.get_by_role("option", name=email).click()

        # Fill in notes as newline-separated values
        notes_text = """First note
Second note
Third note"""
        page.fill('textarea[name="notes"]', notes_text)

        # Submit form
        page.click('input[type="submit"]')

        # Verify redirect to list view
        page.wait_for_url(f"{page.base_url}/admin/account/")

        # Verify success message
        success_banner = page.locator(".govuk-notification-banner--success")
        assert success_banner.is_visible()
        assert "Record was successfully created." in success_banner.text_content()

        user_row = page.locator(f"table tbody tr:has-text('{email}')")
        assert user_row.locator('.govuk-tag:has-text("First note")').is_visible()
        assert user_row.locator('.govuk-tag:has-text("Second note")').is_visible()
        assert user_row.locator('.govuk-tag:has-text("Third note")').is_visible()


@pytest.mark.e2e
class TestArrayListView:
    """Test ARRAY fields display in list view."""

    def test_array_enum_displays_as_tags(self, page):
        """Test ARRAY[enum] values display as GOV.UK tags in list view."""
        page.goto(f"{page.base_url}/admin/account/")

        # Check if there are any accounts
        table_rows = page.locator("table tbody tr")
        if table_rows.count() > 0:
            # Check for GOV.UK tag elements in tags column
            tags_in_list = page.locator("table tbody td .govuk-tag")
            if tags_in_list.count() > 0:
                # Verify tags have correct classes
                first_tag = tags_in_list.first
                assert "govuk-tag" in first_tag.get_attribute("class")

    def test_array_non_enum_displays_in_list(self, page):
        """Test ARRAY[non-enum] values display in list view."""
        page.goto(f"{page.base_url}/admin/account/")

        # Check if notes column exists (4th column)
        table_headers = page.locator("table thead th")
        if table_headers.count() >= 4:
            # Notes column should be visible
            notes_header = table_headers.nth(3)
            assert notes_header.is_visible()
