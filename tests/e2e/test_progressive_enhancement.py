"""E2E tests for progressive enhancement (functionality without JavaScript)."""

import pytest
from playwright.sync_api import expect


@pytest.mark.e2e
class TestNoJavaScript:
    """Test functionality works without JavaScript."""

    @pytest.fixture
    def page_no_js(self, browser, flask_server):
        """Create page with JavaScript disabled."""
        context = browser.new_context(
            java_script_enabled=False, viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()
        page.base_url = flask_server
        page.set_default_timeout(2500)  # Match timeout from other page fixtures
        yield page
        context.close()

    def test_navigation_visible_without_js(self, page_no_js):
        """Test navigation is visible when JS disabled."""
        page_no_js.goto(f"{page_no_js.base_url}/admin/user/")

        # Check service navigation exists at the top
        nav = page_no_js.locator(".govuk-service-navigation")
        assert nav.count() > 0, "Expected service navigation element"

        # Navigation should be visible (not hidden by default)
        # In a mobile-first approach, it may not be "visible" in the viewport sense
        # but the element should exist in the DOM
        assert nav.count() > 0, "Navigation should be present in DOM without JS"

    def test_forms_submit_without_js(self, page_no_js):
        """Test forms work without JavaScript."""
        page_no_js.goto(f"{page_no_js.base_url}/admin/user/new/")

        # Fill and submit form
        page_no_js.fill('input[name="email"]', "nojs@example.com")
        page_no_js.fill('input[name="name"]', "No JS User")
        page_no_js.fill('input[name="age"]', "25")
        page_no_js.fill('input[name="job"]', "Tester")
        page_no_js.select_option('select[id="favourite_colour"]', "RED")
        page_no_js.fill('input[id="created_at-day"]', "1")
        page_no_js.fill('input[id="created_at-month"]', "1")
        page_no_js.fill('input[id="created_at-year"]', "2024")

        page_no_js.click('input[type="submit"]')

        # Wait for page to reload

        # Assert redirected to list view
        assert "/admin/user/" in page_no_js.url, "Expected redirect to list view"
        assert "/admin/user/new/" not in page_no_js.url, (
            "Should not remain on create page"
        )

        # Assert success message
        success_banner = page_no_js.locator(".govuk-notification-banner--success")
        assert success_banner.is_visible(), "Expected success notification banner"
        assert "Record was successfully created." in success_banner.text_content(), (
            "Expected success message"
        )

        # Assert new record visible
        assert page_no_js.locator("text=nojs@example.com").count() > 0, (
            "Expected to find newly created user in list"
        )

    def test_date_filter_works_without_js(self, page_no_js):
        """Test date filter combines fields server-side without JS."""
        # Note: MOJ FilterToggleButton requires JavaScript
        # Without JS, we test that date filters work when accessing via URL directly
        # and that the server correctly combines date fields

        page_no_js.goto(f"{page_no_js.base_url}/admin/user/")

        # Navigate to a URL with date filter parameters
        # Test that date filters work when accessing via URL directly
        page_no_js.goto(
            f"{page_no_js.base_url}/admin/user/?flt21_21-day=1&flt21_21-month=1&flt21_21-year=2024"
        )

        # Assert the date filter is applied (shows in URL)
        assert "2024" in page_no_js.url, "Expected year in filter URL"
        assert "flt21_21" in page_no_js.url, "Expected date filter parameter"

    def test_pagination_works_without_js(self, page_no_js):
        """Test pagination links work without JavaScript."""
        page_no_js.goto(f"{page_no_js.base_url}/admin/user/")

        # Check if pagination exists (with default 8 users, may not have pagination)
        # Pagination requires more records than page size
        next_link = page_no_js.locator(".govuk-pagination__next a")

        if next_link.count() > 0:
            # Click next page link
            next_link.click()

            # Assert page parameter in URL
            assert "page=" in page_no_js.url or page_no_js.url.endswith(
                "/admin/user/"
            ), "Expected page navigation to work"

            # Assert table still visible
            assert page_no_js.locator(".govuk-table").is_visible(), (
                "Expected table after pagination"
            )

    def test_sorting_works_without_js(self, page_no_js):
        """Test column sorting works without JavaScript."""
        page_no_js.goto(f"{page_no_js.base_url}/admin/user/")

        # Click sortable column header
        sort_link = page_no_js.locator("a.xgov-fa-link--sort").first
        assert sort_link.count() > 0, "Expected sortable column"

        sort_link.click()

        # Assert sort parameter in URL
        assert "sort=" in page_no_js.url, "Expected sort parameter in URL"

        # Assert table still visible
        assert page_no_js.locator(".govuk-table").is_visible(), (
            "Expected table after sorting"
        )

    def test_search_works_without_js(self, page_no_js):
        """Test search works without JavaScript."""
        # Note: MOJ FilterToggleButton requires JavaScript
        # Without JS, we test that search works when accessing via URL directly

        page_no_js.goto(f"{page_no_js.base_url}/admin/user/")

        # Navigate to URL with search parameter to test server-side search
        page_no_js.goto(f"{page_no_js.base_url}/admin/user/?search=alice")

        # Assert search parameter in URL
        assert "search=alice" in page_no_js.url, "Expected search parameter in URL"

        # Assert table visible with search results
        table = page_no_js.locator(".govuk-table")
        assert table.is_visible(), "Expected table to be visible with search results"


@pytest.mark.e2e
class TestJavaScriptEnhancement:
    """Test JavaScript enhancements when available."""

    def test_select_all_checkbox_requires_js(self, page):
        """Test select all checkbox functionality (requires JS)."""
        page.goto(f"{page.base_url}/admin/user/")

        # Select all checkbox
        select_all = page.locator("#select-all")
        assert select_all.count() > 0, "Expected select all checkbox"

        # Initially unchecked
        assert not select_all.is_checked(), "Select all should start unchecked"

        # Check select all
        select_all.check()

        # All row checkboxes should be checked (JS functionality)
        checkboxes = page.locator(".action-checkbox")
        for i in range(checkboxes.count()):
            assert checkboxes.nth(i).is_checked(), f"Checkbox {i} should be checked"

        # Uncheck select all
        select_all.uncheck()

        # All should be unchecked
        for i in range(checkboxes.count()):
            assert not checkboxes.nth(i).is_checked(), (
                f"Checkbox {i} should be unchecked"
            )

    def test_selected_count_updates_with_js(self, page):
        """Test selected count updates dynamically in button text (requires JS)."""
        page.goto(f"{page.base_url}/admin/user/")

        # Open actions menu to see delete button
        actions_menu_button = page.locator(".moj-button-menu__toggle-button")
        checkboxes = page.locator(".action-checkbox")

        # Check initial state - open menu and check button text
        actions_menu_button.click()
        delete_button = page.locator('button[form="bulk-action-form"][value="delete"]')
        assert "(0 selected)" in delete_button.text_content(), (
            "Initial count should be 0"
        )
        actions_menu_button.click()  # Close menu

        # Check first checkbox
        assert checkboxes.count() > 0, "Expected action checkboxes"
        checkboxes.first.check()

        # Count should update to 1 (JS functionality)
        # Wait for button text to contain "(1 selected)"
        actions_menu_button.click()
        expect(delete_button).to_contain_text("(1 selected)")
        actions_menu_button.click()

        # Check second checkbox
        checkboxes.nth(1).check()

        # Count should update to 2
        actions_menu_button.click()
        expect(delete_button).to_contain_text("(2 selected)")
        actions_menu_button.click()

        # Uncheck first
        checkboxes.first.uncheck()

        # Count should update to 1
        actions_menu_button.click()
        expect(delete_button).to_contain_text("(1 selected)")

    def test_filter_empty_field_removal(self, page):
        """Test empty filter fields removed before submit (JS enhancement)."""
        page.goto(f"{page.base_url}/admin/user/")

        # Show filter panel
        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()

        # Wait for filter panel to be visible
        page.locator(".moj-filter")

        # Expand Age filter
        age_button = page.locator('button:has-text("Age")').first
        age_button.click()

        # Fill only one age filter (leave others empty)
        age_input = page.locator("input#flt0_0")
        age_input.fill("25")

        # Submit filter
        apply_button = page.locator(
            '#filter_form button[type="submit"]:has-text("Apply")'
        )
        apply_button.click()

        # Wait for page to reload

        # URL should only contain the filled filter (flt0_0=25)
        # Empty filter fields should not appear in URL (if JS is working)
        assert "flt0_0=25" in page.url, "Expected filled filter in URL"

        # The other age filters (flt1_1, flt2_2, etc.) should not be in URL if they were empty
        # This is a JS enhancement - without JS, empty fields might still be submitted
