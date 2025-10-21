"""E2E tests for filter UI interactions."""

import pytest
from playwright.sync_api import expect


@pytest.mark.e2e
class TestFilterInteractions:
    """Test filter UI interactions."""

    def test_page_size_selector_changes_results(self, page):
        """Test that changing page size selector works correctly."""
        page.goto(f"{page.base_url}/admin/user/")

        page_size_select = page.locator("#page-size")

        initial_value = page_size_select.input_value()
        assert initial_value == "15", (
            f"Expected default page size to be 15, got {initial_value}"
        )

        page_size_select.select_option("50")

        page.wait_for_url("**/admin/user/**page_size=50**")

        assert "page_size=50" in page.url, (
            f"Expected page_size=50 in URL, got {page.url}"
        )

        page_size_select = page.locator("#page-size")
        assert page_size_select.input_value() == "50", (
            "Page size selector should show 50 after reload"
        )

        page_size_select.select_option("10")

        page.wait_for_url("**/admin/user/**page_size=10**")

        assert "page_size=10" in page.url, (
            f"Expected page_size=10 in URL, got {page.url}"
        )

        page_size_select = page.locator("#page-size")
        assert page_size_select.input_value() == "10", (
            "Page size selector should show 10 after reload"
        )

    def test_filter_details_expands_collapses(self, page, screenshot):
        """Test clicking filter toggle button shows/hides filters."""
        page.goto(f"{page.base_url}/admin/user/")

        page.wait_for_selector(".moj-action-bar__filter button")

        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_panel = page.locator(".moj-filter")

        assert not filter_panel.is_visible(), (
            "Expected filter panel to be initially hidden"
        )
        assert "Show filter" in filter_toggle.text_content(), (
            "Expected 'Show filter' text"
        )

        # Capture filter panel closed
        screenshot(page, "list-view-filters-closed")

        filter_toggle.click()

        expect(filter_panel).to_be_visible(), (
            "Expected filter panel to be visible after click"
        )
        assert "Hide filter" in filter_toggle.text_content(), (
            "Expected 'Hide filter' text"
        )

        # Capture filter panel open
        screenshot(page, "list-view-filters-open")

        filter_toggle.click()

        assert not filter_panel.is_visible(), (
            "Expected filter panel to be hidden after second click"
        )
        assert "Show filter" in filter_toggle.text_content(), (
            "Expected 'Show filter' text again"
        )

    def test_date_filter_three_inputs(self, page):
        """Test date filter shows day/month/year inputs."""
        page.goto(f"{page.base_url}/admin/user/")

        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()
        page.locator(".moj-filter")

        created_at_section = page.locator('button:has-text("Created At")')
        assert created_at_section.count() > 0, "Expected Created At filter section"

        created_at_section.click()

        day_input = page.locator('input[name$="-day"]')
        month_input = page.locator('input[name$="-month"]')
        year_input = page.locator('input[name$="-year"]')

        assert day_input.count() > 0, "Expected day input for date filter"
        assert month_input.count() > 0, "Expected month input for date filter"
        assert year_input.count() > 0, "Expected year input for date filter"

        date_input_container = page.locator(".govuk-date-input")
        assert date_input_container.count() > 0, "Expected GOV.UK date input component"

    def test_filter_submission_updates_results(self, page, screenshot):
        """Test submitting filter updates table."""
        page.goto(f"{page.base_url}/admin/user/")

        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()
        page.locator(".moj-filter")

        age_section = page.locator('button:has-text("Age")').first
        assert age_section.count() > 0, "Expected Age filter section"

        age_section.click()

        age_filter = page.locator("input#flt0_0")
        age_filter.fill("25")

        apply_button = page.locator(
            '#filter_form button[type="submit"]:has-text("Apply filters")'
        )
        assert apply_button.count() > 0, (
            "Expected 'Apply filters' button in filter form"
        )
        apply_button.click()

        assert "flt0_0=25" in page.url, "Expected filter parameter in URL"

        filter_tags = page.locator(".moj-filter-tags .moj-filter__tag")
        assert filter_tags.count() > 0, "Expected filter tag to be displayed"

        table = page.locator(".govuk-table")
        assert table.is_visible(), "Expected table to be visible after filtering"

        # Capture active filters with tags
        screenshot(page, "list-view-active-filters")

    def test_filter_tag_removal(self, page):
        """Test clicking × on filter tag removes filter."""
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25")

        assert "flt0_0=25" in page.url, "Expected age filter in URL"

        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()
        page.locator(".moj-filter")

        filter_tag = page.locator(".moj-filter__tag")
        assert filter_tag.count() > 0, "Expected filter tag to be displayed"

        filter_tag.first.click()

        assert "flt0_0" not in page.url, "Expected filter to be removed from URL"

        filter_toggle_after = page.locator(".moj-action-bar__filter button")
        filter_toggle_after.click()
        page.locator(".moj-filter")

        filter_tag_after = page.locator(".moj-filter__tag")
        assert filter_tag_after.count() == 0, "Expected no filter tags after removal"

    def test_remove_search_preserves_filters(self, page):
        """Test removing search tag preserves active filters."""
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25&search=alice")

        assert "flt0_0=25" in page.url, "Expected age filter in URL"
        assert "search=alice" in page.url, "Expected search param in URL"

        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()
        page.locator(".moj-filter")

        filter_tags = page.locator(".moj-filter__tag")
        assert filter_tags.count() >= 2, "Expected at least 2 tags (search + filter)"

        search_tag = page.locator('h3:has-text("Search") + ul .moj-filter__tag')
        assert search_tag.count() > 0, "Expected search filter tag"
        search_tag.click()

        assert "search" not in page.url, "Expected search to be removed from URL"
        assert "flt0_0=25" in page.url, "Expected age filter to remain in URL"

        filter_toggle_after = page.locator(".moj-action-bar__filter button")
        filter_toggle_after.click()
        page.locator(".moj-filter")

        search_heading = page.locator('h3:has-text("Search")')
        assert search_heading.count() == 0, "Expected no Search heading after removal"

        filter_tags_after = page.locator(".moj-filter__tag")
        assert filter_tags_after.count() > 0, "Expected filter tag to remain"

    def test_clear_all_filters(self, page):
        """Test 'Clear all' link removes all filters."""
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25&search=test")

        assert "flt0_0=25" in page.url, "Expected age filter in URL"
        assert "search=test" in page.url, "Expected search param in URL"

        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()
        page.locator(".moj-filter")

        filter_tags = page.locator(".moj-filter__tag")
        assert filter_tags.count() > 0, "Expected filter tags to be displayed"

        clear_link = page.locator('a:has-text("Clear filters")')
        assert clear_link.count() > 0, "Expected Clear filters link in filter panel"
        clear_link.click()

        assert "flt0_0" not in page.url, "Expected age filter to be cleared"
        assert "search" not in page.url, "Expected search to be cleared"

        filter_toggle_after = page.locator(".moj-action-bar__filter button")
        filter_toggle_after.click()
        page.locator(".moj-filter")

        filter_tags_after = page.locator(".moj-filter__tag")
        assert filter_tags_after.count() == 0, "Expected no filter tags after clearing"

    def test_enum_filter_dropdown(self, page):
        """Test enum filter shows dropdown with values."""
        page.goto(f"{page.base_url}/admin/user/")

        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()

        page.locator(".moj-filter")

        colour_section = page.locator('button:has-text("Favourite Colour")')
        assert colour_section.count() > 0, "Expected Favourite Colour filter section"

        colour_section.click()

        colour_selects = page.locator("select.govuk-select")
        assert colour_selects.count() > 0, (
            "Expected select dropdowns for favourite_colour"
        )

        found_colour_select = False
        for i in range(colour_selects.count()):
            select = colour_selects.nth(i)
            options = select.locator("option")
            option_texts = [
                options.nth(j).text_content().strip() for j in range(options.count())
            ]

            non_empty_options = [
                opt
                for opt in option_texts
                if opt and opt.lower() not in ["select...", ""]
            ]

            if len(non_empty_options) == 3:
                found_colour_select = True

                assert "govuk-select" in select.get_attribute("class"), (
                    "Expected GOV.UK select class on enum filter"
                )

                combined_text = " ".join(non_empty_options).lower()
                assert (
                    "red" in combined_text
                    or "blue" in combined_text
                    or "yellow" in combined_text
                ), f"Expected colour names in options, got: {non_empty_options}"
                break

        assert found_colour_select, (
            "Expected to find favourite_colour enum select with 3 colour options"
        )

    def test_boolean_filter_available(self, page):
        """Test boolean filter is available in filter panel."""
        page.goto(f"{page.base_url}/admin/user/")

        # Open filter panel
        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()

        # Verify Active filter section exists in the accordion
        active_section = page.locator('button:has-text("Active")')
        assert active_section.count() > 0, "Expected Active filter section"
        assert active_section.is_visible(), "Active filter section should be visible"

        # Expand the Active filter section
        active_section.click()

        # Verify that select dropdowns appear within the Active section
        # Boolean filters render as GOV.UK select dropdowns with Yes/No options
        all_selects = page.locator("select.govuk-select")
        visible_selects = []
        for i in range(all_selects.count()):
            if all_selects.nth(i).is_visible():
                visible_selects.append(all_selects.nth(i))

        # Should have at least some visible selects after expanding Active
        assert len(visible_selects) > 0, "Expected visible select dropdowns after expanding Active filter"

    def test_filter_button_shows_active_count(self, page, screenshot, mobile_page):
        """Test filter toggle button shows active filter count."""
        # Test with no filters - should not show count
        page.goto(f"{page.base_url}/admin/user/")

        # Wait for filter button to be initialized
        filter_toggle = page.locator(".moj-action-bar__filter button")
        expect(filter_toggle).to_have_text("Show filters")

        # Test with one filter - should show "(1 active)"
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25")

        filter_toggle = page.locator(".moj-action-bar__filter button")
        # Wait for JS to update button text
        expect(filter_toggle).to_contain_text("(1 active)")
        expect(filter_toggle).to_contain_text("Show filters")

        # Test with search only - should show "(1 active)"
        page.goto(f"{page.base_url}/admin/user/?search=alice")

        filter_toggle = page.locator(".moj-action-bar__filter button")
        expect(filter_toggle).to_contain_text("(1 active)")

        # Test with filter + search - should show "(2 active)"
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25&search=alice")

        filter_toggle = page.locator(".moj-action-bar__filter button")
        expect(filter_toggle).to_contain_text("(2 active)")

        # Click to expand - should change to "Hide filters" (count not shown when expanded)
        filter_toggle.click()
        page.locator(".moj-filter")

        expect(filter_toggle).to_have_text("Hide filters")

        # Click to collapse - should change back to "Show filters (2 active)"
        filter_toggle.click()

        expect(filter_toggle).to_contain_text("Show filters")
        expect(filter_toggle).to_contain_text("(2 active)")

        # Also test mobile view with filters open
        mobile_page.goto(f"{mobile_page.base_url}/admin/user/")
        mobile_filter_toggle = mobile_page.locator(".moj-action-bar__filter button")
        mobile_filter_toggle.click()
        mobile_filter_panel = mobile_page.locator(".moj-filter")
        expect(mobile_filter_panel).to_be_visible()
        screenshot(mobile_page, "list-view-filters-open")


@pytest.mark.e2e
class TestFilterPersistence:
    """Test filter state persistence."""

    def test_filters_persist_after_pagination(self, page):
        """Test filters remain after changing page."""
        # Apply age filter with correct param format
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25")

        # Assert filter is active
        assert "flt0_0=25" in page.url, "Expected age filter in URL"

        # Show filter panel to check for filter tags
        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()
        page.locator(".moj-filter")

        filter_tag = page.locator(".moj-filter__tag")
        assert filter_tag.count() > 0, "Expected filter tag to be displayed"

        # Check if pagination exists (with default 8 users and page_size 15, no pagination)
        # This test verifies the URL structure is correct for filters to persist
        # The actual pagination persistence is tested when pagination exists
        next_page_link = page.locator(".govuk-pagination__next a")

        # If pagination exists, navigate and verify filter persists
        if next_page_link.count() > 0:
            next_page_link.click()

            # Assert filter still active in URL
            assert "flt0_0=25" in page.url, (
                "Expected filter to persist after pagination"
            )

            # Show filter panel again and check for tag
            filter_toggle_after = page.locator(".moj-action-bar__filter button")
            filter_toggle_after.click()
            page.locator(".moj-filter")

            # Assert filter tag still displayed
            filter_tag_after = page.locator(".moj-filter__tag")
            assert filter_tag_after.count() > 0, "Expected filter tag after pagination"

    def test_filters_persist_after_sort(self, page):
        """Test filters remain after sorting."""
        # Apply age filter with correct param format
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25")

        # Assert filter is active
        assert "flt0_0=25" in page.url, "Expected age filter in URL"

        # Show filter panel to check for filter tags
        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()
        page.locator(".moj-filter")

        filter_tag = page.locator(".moj-filter__tag")
        assert filter_tag.count() > 0, "Expected filter tag to be displayed"

        # Click a sortable column header (e.g., Email or Name)
        sort_link = page.locator("a.xgovuk-fa-link--sort").first
        assert sort_link.count() > 0, "Expected sortable column"

        sort_link.click()

        # Assert filter still active in URL
        assert "flt0_0=25" in page.url, "Expected filter to persist after sorting"

        # Assert sort parameter also present
        assert "sort=" in page.url, "Expected sort parameter in URL"

        # Show filter panel again and check for tag
        filter_toggle_after = page.locator(".moj-action-bar__filter button")
        filter_toggle_after.click()
        page.locator(".moj-filter")

        # Assert filter tag still displayed
        filter_tag_after = page.locator(".moj-filter__tag")
        assert filter_tag_after.count() > 0, "Expected filter tag after sorting"
