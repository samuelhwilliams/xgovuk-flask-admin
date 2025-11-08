"""E2E tests for GovSelectWithSearch JavaScript enhancement."""

import pytest


@pytest.mark.e2e
class TestSelectWithSearchEnhancement:
    """Test JavaScript enhancement of select-with-search component."""

    def test_select_with_search_enhances_multi_select(self, page):
        """Test that Choices.js enhances multi-select fields with data."""
        # First, go to an edit page to ensure we have data
        # Navigate to user list and click first edit link
        page.goto(f"{page.base_url}/admin/user/")

        # Click first edit link
        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()

        # Wait for Choices.js to initialize on the posts field
        # The posts field is a multi-select with select-with-search
        page.wait_for_selector(".choices")

        # Check that the select element has the data-module attribute
        select = page.locator('select[name="posts"]')
        assert select.count() > 0, "Select element should exist"
        assert select.get_attribute("data-module") == "select-with-search"
        assert select.get_attribute("multiple") is not None

        # Check that Choices.js has enhanced the select
        choices_wrapper = page.locator(".choices")
        assert choices_wrapper.count() > 0, (
            "Choices.js should enhance the select with .choices wrapper"
        )

        # Check that the wrapper has the GOV.UK gem class
        gem_wrapper = page.locator(".gem-c-select-with-search")
        assert gem_wrapper.count() > 0, "Should have gem-c-select-with-search wrapper"

        # Check that the user's existing posts are shown as selected tags
        selected_items = page.locator(".choices__list--multiple .choices__item")
        selected_count = selected_items.count()

        # Users should have 2-5 posts according to seed_database
        assert selected_count >= 2, (
            f"User should have at least 2 posts selected, found {selected_count}"
        )
        assert selected_count <= 5, (
            f"User should have at most 5 posts selected, found {selected_count}"
        )

    def test_select_with_search_shows_options_on_click(self, page):
        """Test that clicking the select shows a dropdown with options."""
        # Navigate to user edit page which has posts to select
        page.goto(f"{page.base_url}/admin/user/")

        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()

        # Wait for Choices.js to initialize
        page.wait_for_selector(".choices")

        # Click on the posts field's Choices wrapper to open the dropdown
        # Be specific to target the posts field (multi-select)
        posts_field = page.locator('label:has-text("Posts")').locator("..")
        choices_wrapper = posts_field.locator(".choices")
        choices_wrapper.click()

        # Wait for posts dropdown to appear specifically
        posts_field.locator(".choices__list--dropdown").wait_for(state="visible")

        # Check that dropdown has options (posts)
        dropdown_items = page.locator(".choices__list--dropdown .choices__item")
        assert dropdown_items.count() > 0, "Dropdown should contain post options"

    def test_select_with_search_search_filters_options(self, page):
        """Test that typing in the search filters the available options."""
        # Navigate to user edit page
        page.goto(f"{page.base_url}/admin/user/")

        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()

        # Wait for Choices.js to initialize
        page.wait_for_selector(".choices")

        # Click to open posts dropdown specifically
        posts_field = page.locator('label:has-text("Posts")').locator("..")
        choices_wrapper = posts_field.locator(".choices")
        choices_wrapper.click()
        posts_field.locator(".choices__list--dropdown").wait_for(state="visible")

        # Count initial options
        initial_count = page.locator(".choices__list--dropdown .choices__item").count()

        # Type in search box to filter - target the posts field's search input
        search_input = (
            page.locator('label:has-text("Posts")')
            .locator("..")
            .locator('.choices input[type="search"]')
        )
        search_input.fill("xyz_nonexistent_search_term")

        # Check that "No results found" message appears or options are filtered
        no_results = page.locator('.choices__item--choice:has-text("No results found")')
        filtered_items = page.locator(".choices__list--dropdown .choices__item--choice")

        # Either we should see "no results" or fewer items than before
        assert no_results.count() > 0 or filtered_items.count() < initial_count, (
            "Search should filter options or show no results message"
        )

    def test_select_with_search_shows_selected_items(self, page):
        """Test that selected items appear as tags."""
        # Navigate to user edit page
        page.goto(f"{page.base_url}/admin/user/")

        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()

        # Wait for Choices.js
        page.wait_for_selector(".choices")

        # Get initial count of selected items (posts field specifically)
        posts_field = page.locator('label:has-text("Posts")').locator("..")
        initial_selected = posts_field.locator(
            ".choices__list--multiple .choices__item"
        ).count()

        # Click to open posts dropdown
        choices_wrapper = posts_field.locator(".choices")
        choices_wrapper.click()
        posts_field.locator(".choices__list--dropdown").wait_for(state="visible")

        # Select first available option from posts dropdown
        first_option = posts_field.locator(
            ".choices__list--dropdown .choices__item--selectable"
        ).first
        if first_option.count() > 0:
            option_text = first_option.inner_text()
            first_option.click()

            # Check that a new selected item appears in the posts field
            selected_items = posts_field.locator(
                ".choices__list--multiple .choices__item"
            )
            new_count = selected_items.count()
            assert new_count == initial_selected + 1, (
                f"Should have {initial_selected + 1} selected items, found {new_count}"
            )

            # Verify the newly selected text appears somewhere in the selected items
            all_selected_text = " ".join(
                [selected_items.nth(i).inner_text() for i in range(new_count)]
            )
            assert option_text in all_selected_text, (
                f"Selected item '{option_text}' should appear in selected tags"
            )

    def test_select_with_search_remove_selected_item(self, page):
        """Test that clicking the X removes a selected item."""
        # Navigate to user edit page
        page.goto(f"{page.base_url}/admin/user/")

        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()

        # Wait for Choices.js
        page.wait_for_selector(".choices")

        # Select an item first - target posts field specifically
        posts_field = page.locator('label:has-text("Posts")').locator("..")
        choices_wrapper = posts_field.locator(".choices")
        choices_wrapper.click()
        posts_field.locator(".choices__list--dropdown").wait_for(state="visible")

        first_option = posts_field.locator(
            ".choices__list--dropdown .choices__item--selectable"
        ).first
        if first_option.count() > 0:
            first_option.click()

            # Now try to remove it from the posts field
            selected_items = posts_field.locator(
                ".choices__list--multiple .choices__item"
            )
            initial_count = selected_items.count()

            # Click the remove button (X)
            remove_button = selected_items.first.locator(".choices__button")
            if remove_button.count() > 0:
                remove_button.click()

                # Check that item was removed
                final_count = posts_field.locator(
                    ".choices__list--multiple .choices__item"
                ).count()
                assert final_count < initial_count, (
                    "Clicking X should remove the selected item"
                )

    def test_select_with_search_has_label(self, page):
        """Test that the label is visible above the select field."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Check that the posts field has a visible label
        posts_label = page.locator('label[for="posts"]')
        assert posts_label.is_visible()
        assert "Posts" in posts_label.inner_text()

    def test_select_with_search_fallback_without_js(self, page):
        """Test that the select works as a native multi-select without JavaScript."""
        # Disable JavaScript by blocking JS files
        page.route("**/*.js", lambda route: route.abort())

        page.goto(f"{page.base_url}/admin/user/new/")

        # The select should still be present and functional
        select = page.locator('select[name="posts"]')
        assert select.is_visible()
        assert select.get_attribute("multiple") is not None

        # No Choices.js wrapper should exist
        choices_wrapper = page.locator(".choices")
        assert choices_wrapper.count() == 0, (
            "No Choices.js enhancement without JavaScript"
        )

    def test_select_with_search_accessible_attributes(self, page):
        """Test that accessible attributes are preserved after JavaScript enhancement."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Wait for Choices.js to enhance the select
        page.wait_for_selector(".choices")

        # Check that the original select element still has proper attributes
        # (Choices.js hides it but should preserve attributes)
        select = page.locator('select[name="posts"]')
        assert select.count() > 0, "Select element should exist"
        assert select.get_attribute("id") == "posts"
        assert select.get_attribute("name") == "posts"

        # Check that label is associated with the field
        posts_label = page.locator('label[for="posts"]')
        assert posts_label.count() > 0

    def test_user_edit_shows_all_posts_in_dropdown(self, page):
        """Test that editing a user shows ALL posts (from all users) in the dropdown."""
        # Navigate to user edit page
        page.goto(f"{page.base_url}/admin/user/")

        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()

        # Wait for Choices.js
        page.wait_for_selector(".choices")

        # Click to open posts dropdown
        posts_field = page.locator('label:has-text("Posts")').locator("..")
        choices_wrapper = posts_field.locator(".choices")
        choices_wrapper.click()
        posts_field.locator(".choices__list--dropdown").wait_for(state="visible")

        # Count all available options in posts dropdown
        dropdown_items = posts_field.locator(
            ".choices__list--dropdown .choices__item--choice"
        )
        dropdown_count = dropdown_items.count()

        # Should have approximately 20 posts total (each user has 2-5 posts, 8 users)
        # Minus the ones already selected for this user
        assert dropdown_count >= 10, (
            f"Should have at least 10 posts in dropdown, found {dropdown_count}"
        )

    def test_user_edit_can_add_post_and_persist(self, page):
        """Test that adding a post to a user persists after save and reload."""
        # Navigate to user edit page
        page.goto(f"{page.base_url}/admin/user/")

        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()

        # Wait for Choices.js
        page.wait_for_selector(".choices")

        # Count initial selected posts (posts field specifically)
        posts_field = page.locator('label:has-text("Posts")').locator("..")
        initial_selected = posts_field.locator(
            ".choices__list--multiple .choices__item"
        ).count()

        # Click to open posts dropdown
        choices_wrapper = posts_field.locator(".choices")
        choices_wrapper.click()
        posts_field.locator(".choices__list--dropdown").wait_for(state="visible")

        # Select first available (unselected) option from posts dropdown
        available_options = posts_field.locator(
            ".choices__list--dropdown .choices__item--selectable"
        )
        assert available_options.count() > 0, (
            "Should have at least one post available to add"
        )

        added_post_title = available_options.first.inner_text()
        available_options.first.click()

        # Verify the new selection appears as a tag in the posts field
        new_selected_count = posts_field.locator(
            ".choices__list--multiple .choices__item"
        ).count()
        assert new_selected_count == initial_selected + 1, (
            f"Should have {initial_selected + 1} posts selected, found {new_selected_count}"
        )

        # Save the form
        save_button = page.locator('input[type="submit"][value="Save"]')
        save_button.click()

        # Verify success
        assert "/admin/user/" in page.url
        success_message = page.locator(".govuk-notification-banner--success")
        assert success_message.count() > 0, "Should show success message after saving"

        # Go back to edit the same user to verify persistence
        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()
        page.wait_for_selector(".choices")

        # Verify the added post is still selected (posts field specifically)
        posts_field = page.locator('label:has-text("Posts")').locator("..")
        final_selected = posts_field.locator(".choices__list--multiple .choices__item")
        final_count = final_selected.count()
        assert final_count == initial_selected + 1, (
            f"After reload, should still have {initial_selected + 1} posts, found {final_count}"
        )

        # Verify the added post title appears in the selected items
        all_selected_text = " ".join(
            [final_selected.nth(i).inner_text() for i in range(final_count)]
        )
        assert added_post_title in all_selected_text, (
            f"Added post '{added_post_title}' should still be selected after reload"
        )

    def test_user_edit_can_remove_post_and_persist(self, page):
        """Test that removing a post from a user persists after save and reload."""
        # Navigate to user edit page
        page.goto(f"{page.base_url}/admin/user/")

        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()

        # Wait for Choices.js
        page.wait_for_selector(".choices")

        # Get initial selected posts
        selected_items = page.locator(".choices__list--multiple .choices__item")
        initial_count = selected_items.count()
        assert initial_count > 0, "User should have at least one post to remove"

        # Get the title of the first post (remove "Remove item" button text)
        first_item_text = selected_items.first.inner_text()
        removed_post_title = first_item_text.replace("Remove item", "").strip()

        # Click remove button on first post
        remove_button = selected_items.first.locator(".choices__button")
        remove_button.click()

        # Verify post was removed from selected items
        new_count = page.locator(".choices__list--multiple .choices__item").count()
        assert new_count == initial_count - 1, (
            f"Should have {initial_count - 1} posts after removal, found {new_count}"
        )

        # Save the form
        save_button = page.locator('input[type="submit"][value="Save"]')
        save_button.click()

        # Verify success
        assert "/admin/user/" in page.url
        success_message = page.locator(".govuk-notification-banner--success")
        assert success_message.count() > 0, "Should show success message after saving"

        # Go back to edit the same user to verify persistence
        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()
        page.wait_for_selector(".choices")

        # Verify the post count is still reduced
        final_selected = page.locator(".choices__list--multiple .choices__item")
        final_count = final_selected.count()
        assert final_count == initial_count - 1, (
            f"After reload, should still have {initial_count - 1} posts, found {final_count}"
        )

        # Verify the removed post is NO LONGER in the selected items
        all_selected_text = " ".join(
            [final_selected.nth(i).inner_text() for i in range(final_count)]
        )
        assert removed_post_title not in all_selected_text, (
            f"Removed post '{removed_post_title}' should not be selected after reload"
        )

    def test_select_with_search_escapes_html_in_options(self, page):
        """Test that HTML in post titles is properly escaped in select-with-search options.

        Note: This test verifies the client-side behavior. The Post model in app.py
        has a __str__ method that returns the title, so post titles appear as text.
        This test verifies that IF HTML-like content appears in titles, it would be escaped.
        """
        # Navigate to user edit page
        page.goto(f"{page.base_url}/admin/user/")

        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()

        # Wait for Choices.js
        page.wait_for_selector(".choices")

        # Check the underlying HTML source before Choices.js processes it
        # The select element should have escaped HTML in option values and text
        page.content()

        # The Post model's default __str__ returns something like "<Post object at 0x...>"
        # Verify that these angle brackets are escaped in the HTML source
        # Look for the select element with posts
        select_html = page.locator('select[name="posts"]').inner_html()

        # If there are any angle brackets in option text, they should be HTML-escaped
        # We're checking that the template properly uses |e filter
        # The select should contain escaped entities if there's HTML-like content
        if (
            "<" in select_html
            and "option"
            not in select_html[select_html.find("<") : select_html.find("<") + 10]
        ):
            # Found a raw < that's not part of an HTML tag - this is bad
            assert "&lt;" in select_html or "&#" in select_html, (
                "Any < or > characters in option text should be HTML-escaped"
            )

        # Click to open Choices.js dropdown (posts field specifically)
        posts_field = page.locator('label:has-text("Posts")').locator("..")
        choices_wrapper = posts_field.locator(".choices")
        choices_wrapper.click()
        posts_field.locator(".choices__list--dropdown").wait_for(state="visible")

        # Get the Choices.js dropdown HTML from posts field
        dropdown_html = posts_field.locator(".choices__list--dropdown").inner_html()

        # Verify no executable script tags in the dropdown
        # (Would only appear if someone had a malicious __str__ method)
        assert "<script>" not in dropdown_html, (
            "Raw script tags should never appear in dropdown HTML"
        )
        assert "javascript:" not in dropdown_html.lower(), (
            "JavaScript protocol URLs should not appear in dropdown"
        )

        # The Choices.js library should also escape HTML when rendering items
        # Check that there are no onclick or other event handlers in the dropdown items
        dropdown_items = posts_field.locator(".choices__list--dropdown .choices__item")
        for i in range(min(dropdown_items.count(), 5)):  # Check first 5 items
            item_html = dropdown_items.nth(i).evaluate("el => el.outerHTML")
            assert "onclick=" not in item_html.lower(), (
                "No inline event handlers should be in dropdown items"
            )
            assert "onerror=" not in item_html.lower(), (
                "No inline event handlers should be in dropdown items"
            )

        # Verify that the dropdown items are text-only (no nested HTML elements for content)
        # The only allowed HTML should be structural (the item wrapper itself)
        first_item = dropdown_items.first
        if first_item.count() > 0:
            # The item should have data-value attribute (safe, set by Choices.js)
            assert first_item.get_attribute("data-value") is not None, (
                "Dropdown items should have data-value attribute"
            )

            # Get inner HTML and verify it's just text (no additional tags beyond structure)
            item_inner = first_item.inner_html()
            # Should not contain user-controllable HTML tags
            dangerous_tags = ["<script", "<img", "<iframe", "<object", "<embed", "<svg"]
            for tag in dangerous_tags:
                assert tag not in item_inner.lower(), (
                    f"Dangerous tag {tag} should not be in dropdown item HTML"
                )
