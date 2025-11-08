"""E2E tests for array filter UI interactions."""

import pytest


@pytest.mark.e2e
class TestArrayEnumFilters:
    def test_array_enum_filter_shows_multiselect(self, page):
        page.goto(f"{page.base_url}/admin/account/")

        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()

        page.locator(".moj-filter")

        tags_fieldset = page.locator('legend:has-text("Filter by Tags")')
        assert tags_fieldset.count() > 0, "Expected Tags filter fieldset"

        select_elements = page.locator("select.govuk-select")
        assert select_elements.count() > 0, "Expected select elements for tags filter"

        found_tags_select = False
        for i in range(select_elements.count()):
            select = select_elements.nth(i)
            options = select.locator("option")
            option_texts = [
                options.nth(j).text_content().strip() for j in range(options.count())
            ]

            combined_text = " ".join(option_texts).lower()
            if (
                "red" in combined_text
                or "blue" in combined_text
                or "yellow" in combined_text
            ):
                found_tags_select = True
                assert "govuk-select" in select.get_attribute("class"), (
                    "Expected GOV.UK select class on array enum filter"
                )
                break

        assert found_tags_select, (
            "Expected to find tags enum select with colour options"
        )

    def test_array_enum_filter_submission(self, page):
        page.goto(f"{page.base_url}/admin/account/")

        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()

        page.locator(".moj-filter")

        choices_wrapper = page.locator(".gem-c-select-with-search .choices").first
        choices_wrapper.click()

        red_option = page.locator(".choices__item--choice:has-text('red')").first
        red_option.click()

        apply_button = page.locator(
            '#filter_form button[type="submit"]:has-text("Apply filters")'
        )
        apply_button.click()

        assert "flt" in page.url, "Expected filter parameter in URL"

        filter_toggle_after = page.locator(".moj-action-bar__filter button")
        filter_toggle_after.click()
        page.locator(".moj-filter")

        filter_tags = page.locator(".moj-filter-tags .moj-filter__tag")
        assert filter_tags.count() > 0, (
            "Expected filter tag to be displayed after submission"
        )

    def test_array_enum_filter_multiple_operations(self, page):
        page.goto(f"{page.base_url}/admin/account/")

        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()

        page.locator(".moj-filter")

        tags_fieldset = page.locator('legend:has-text("Filter by Tags")')
        assert tags_fieldset.count() > 0, "Expected Tags filter fieldset"

        operation_labels = page.locator(
            'fieldset:has(legend:has-text("Filter by Tags")) label'
        ).all_text_contents()

        operation_text = " ".join([label.lower() for label in operation_labels])

        assert (
            "contains" in operation_text
            or "not contains" in operation_text
            or "has any of" in operation_text
            or "equals" in operation_text
        ), f"Expected array filter operations in labels, got: {operation_labels}"

    def test_array_filter_displays_active_tag(self, page):
        page.goto(f"{page.base_url}/admin/account/?flt0_0=RED")

        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()

        page.locator(".moj-filter")

        filter_tags = page.locator(".moj-filter__tag")
        assert filter_tags.count() > 0, "Expected filter tag for active array filter"

        tag_text = filter_tags.first.text_content()
        assert tag_text, "Expected filter tag to have text content"


@pytest.mark.e2e
class TestArrayTextFilters:
    def test_array_text_filter_shows_input(self, page):
        page.goto(f"{page.base_url}/admin/account/")

        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()

        page.locator(".moj-filter")

        notes_fieldset = page.locator('legend:has-text("Filter by Notes")')
        assert notes_fieldset.count() > 0, "Expected Notes filter fieldset"

        text_inputs = page.locator("#filter_form input.govuk-input")
        assert text_inputs.count() > 0, "Expected text input fields for notes filter"

    def test_array_text_filter_submission(self, page):
        page.goto(f"{page.base_url}/admin/account/")

        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()

        page.locator(".moj-filter")

        text_input = page.locator("#filter_form input.govuk-input").first
        text_input.fill("test note")

        apply_button = page.locator(
            '#filter_form button[type="submit"]:has-text("Apply filters")'
        )
        apply_button.click()

        assert "flt" in page.url, "Expected filter parameter in URL"

        filter_toggle_after = page.locator(".moj-action-bar__filter button")
        filter_toggle_after.click()
        page.locator(".moj-filter")

        filter_tags = page.locator(".moj-filter-tags .moj-filter__tag")
        assert filter_tags.count() > 0, (
            "Expected filter tag to be displayed after text array filter submission"
        )


@pytest.mark.e2e
class TestArrayFilterPersistence:
    def test_array_filter_persists_after_pagination(self, page):
        page.goto(f"{page.base_url}/admin/account/?flt0_0=RED")

        assert "flt0_0=RED" in page.url, "Expected array filter in URL"

        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()
        page.locator(".moj-filter")

        filter_tag = page.locator(".moj-filter__tag")
        assert filter_tag.count() > 0, "Expected filter tag for array filter"

        next_page_link = page.locator(".govuk-pagination__next a")

        if next_page_link.count() > 0:
            next_page_link.click()

            assert "flt0_0=RED" in page.url, (
                "Expected array filter to persist after pagination"
            )

            filter_toggle_after = page.locator(".moj-action-bar__filter button")
            filter_toggle_after.click()
            page.locator(".moj-filter")

            filter_tag_after = page.locator(".moj-filter__tag")
            assert filter_tag_after.count() > 0, (
                "Expected filter tag after pagination with array filter"
            )

    def test_array_filter_removal(self, page):
        page.goto(f"{page.base_url}/admin/account/?flt0_0=RED")

        assert "flt0_0=RED" in page.url, "Expected array filter in URL"

        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()
        page.locator(".moj-filter")

        filter_tag = page.locator(".moj-filter__tag")
        assert filter_tag.count() > 0, "Expected filter tag for array filter"

        filter_tag.first.click()

        assert "flt0_0" not in page.url, "Expected array filter to be removed from URL"

        filter_toggle_after = page.locator(".moj-action-bar__filter button")
        filter_toggle_after.click()
        page.locator(".moj-filter")

        filter_tag_after = page.locator(".moj-filter__tag")
        assert filter_tag_after.count() == 0, (
            "Expected no filter tags after removing array filter"
        )

    def test_multiple_array_filters_combined(self, page):
        page.goto(f"{page.base_url}/admin/account/")

        filter_toggle = page.locator(".moj-action-bar__filter button")
        filter_toggle.click()

        page.locator(".moj-filter")

        choices_wrapper = page.locator(".gem-c-select-with-search .choices").first
        choices_wrapper.click()

        red_option = page.locator(".choices__item--choice:has-text('red')").first
        red_option.click()

        apply_button = page.locator(
            '#filter_form button[type="submit"]:has-text("Apply filters")'
        )
        apply_button.click()

        assert "flt0_0" in page.url, "Expected first filter in URL"

        filter_toggle_2 = page.locator(".moj-action-bar__filter button")
        filter_toggle_2.click()

        notes_input = page.locator("#filter_form input.govuk-input").first
        notes_input.fill("test")

        apply_button_2 = page.locator(
            '#filter_form button[type="submit"]:has-text("Apply filters")'
        )
        apply_button_2.click()

        assert "flt0_0" in page.url, "Expected tags filter to persist"
        assert "flt1_0" in page.url or "flt" in page.url, (
            "Expected notes filter to be added"
        )

        filter_toggle_3 = page.locator(".moj-action-bar__filter button")
        filter_toggle_3.click()
        page.locator(".moj-filter")

        filter_tags = page.locator(".moj-filter-tags .moj-filter__tag")
        assert filter_tags.count() >= 2, (
            "Expected at least 2 filter tags for combined array filters"
        )
