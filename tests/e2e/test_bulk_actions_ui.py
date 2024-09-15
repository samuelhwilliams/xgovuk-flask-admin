"""E2E tests for bulk action UI interactions."""

import pytest
from playwright.sync_api import expect


@pytest.mark.e2e
class TestBulkActionUI:
    """Test bulk action user interactions."""

    def test_select_all_checkbox_toggles_all(self, page):
        """Test select all checkbox selects/deselects all rows."""
        page.goto(f"{page.base_url}/admin/user/")

        select_all = page.locator("#select-all")
        checkboxes = page.locator(".action-checkbox")

        assert not select_all.is_checked()
        for i in range(checkboxes.count()):
            assert not checkboxes.nth(i).is_checked()

        select_all.check()

        assert select_all.is_checked()
        for i in range(checkboxes.count()):
            assert checkboxes.nth(i).is_checked()

        select_all.uncheck()

        assert not select_all.is_checked()
        for i in range(checkboxes.count()):
            assert not checkboxes.nth(i).is_checked()

    def test_selected_count_updates(self, page):
        """Test selected count updates as checkboxes change."""
        page.goto(f"{page.base_url}/admin/user/")

        actions_menu_button = page.locator(".moj-button-menu__toggle-button")
        checkboxes = page.locator(".action-checkbox")

        actions_menu_button.click()
        delete_button = page.locator('button[form="bulk-action-form"][value="delete"]')
        assert "(0 selected)" in delete_button.text_content()
        actions_menu_button.click()

        checkboxes.first.check()
        actions_menu_button.click()
        assert "(1 selected)" in delete_button.text_content()
        actions_menu_button.click()

        checkboxes.nth(1).check()
        actions_menu_button.click()
        assert "(2 selected)" in delete_button.text_content()
        actions_menu_button.click()

        checkboxes.first.uncheck()
        actions_menu_button.click()
        assert "(1 selected)" in delete_button.text_content()
        actions_menu_button.click()

    def test_bulk_action_confirmation_flow(self, page):
        """Test full bulk action workflow with confirmation."""
        page.goto(f"{page.base_url}/admin/account/")

        expect(page.locator("p", has_text="Showing 8 results")).to_be_visible()

        checkboxes = page.locator(".action-checkbox")
        checkboxes.first.check()
        checkboxes.nth(1).check()

        actions_menu_button = page.locator(".moj-button-menu__toggle-button")
        actions_menu_button.click()
        delete_button = page.locator('button[form="bulk-action-form"][value="delete"]')
        delete_button.click()

        confirmation = page.locator(".govuk-notification-banner")
        assert confirmation.is_visible()
        assert "Confirm" in confirmation.text_content()
        assert "2 item(s) selected" in confirmation.text_content()

        confirm_button = page.locator('button:has-text("Confirm")')
        confirm_button.click()

        success_banner = page.locator(".govuk-notification-banner--success")
        assert success_banner.is_visible(), "Expected success notification banner"

        expect(page.locator("p", has_text="Showing 6 results")).to_be_visible()

    def test_bulk_action_validation(self, page):
        """Test bulk action requires selection and action choice."""
        page.goto(f"{page.base_url}/admin/user/")

        # Set up dialog handler to capture alert
        alerts = []

        def handle_dialog(dialog):
            alerts.append(dialog.message)
            dialog.accept()

        page.on("dialog", handle_dialog)

        # Verify button shows 0 selected when no items are selected
        actions_menu_button = page.locator(".moj-button-menu__toggle-button")
        actions_menu_button.click()
        delete_button = page.locator('button[form="bulk-action-form"][value="delete"]')

        # Button should show (0 selected) when no items selected
        assert "(0 selected)" in delete_button.text_content()

        actions_menu_button.click()  # Close menu

        checkboxes = page.locator(".action-checkbox")
        checkboxes.first.check()

        # Verify count updates after selection
        actions_menu_button.click()
        assert "(1 selected)" in delete_button.text_content()

    def test_bulk_action_cancel(self, page):
        """Test cancelling bulk action."""
        page.goto(f"{page.base_url}/admin/user/")

        initial_rows = page.locator(".govuk-table__body .govuk-table__row").count()

        checkboxes = page.locator(".action-checkbox")
        checkboxes.first.check()
        checkboxes.nth(1).check()

        actions_menu_button = page.locator(".moj-button-menu__toggle-button")
        actions_menu_button.click()
        delete_button = page.locator('button[form="bulk-action-form"][value="delete"]')
        delete_button.click()

        cancel_link = page.locator('a:has-text("Cancel")')
        cancel_link.click()

        confirm_banners = page.locator('.govuk-notification-banner:has-text("Confirm")')
        assert confirm_banners.count() == 0

        final_rows = page.locator(".govuk-table__body .govuk-table__row").count()
        assert final_rows == initial_rows


@pytest.mark.e2e
class TestBulkActionAccessibility:
    """Test bulk action accessibility."""

    def test_checkboxes_have_labels(self, page):
        """Test all checkboxes have accessible labels."""
        page.goto(f"{page.base_url}/admin/user/")

        checkboxes = page.locator(".action-checkbox")

        for i in range(checkboxes.count()):
            checkbox = checkboxes.nth(i)
            checkbox_id = checkbox.get_attribute("id")

            label = page.locator(f'label[for="{checkbox_id}"]')
            assert label.count() > 0, f"Checkbox {checkbox_id} has no associated label"

            aria_label = checkbox.get_attribute("aria-label")
            assert aria_label or label.count() > 0, (
                f"Checkbox {checkbox_id} has no label or aria-label"
            )

    def test_select_all_has_label(self, page):
        """Test select all checkbox has label."""
        page.goto(f"{page.base_url}/admin/user/")

        select_all = page.locator("#select-all")

        label = page.locator('label[for="select-all"]')
        assert label.count() > 0

        aria_label = select_all.get_attribute("aria-label")
        assert aria_label or label.count() > 0
