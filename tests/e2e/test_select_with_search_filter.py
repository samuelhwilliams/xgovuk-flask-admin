"""E2E tests for SelectWithSearchFilterInList on the post list view."""

import pytest


def _open_filter_panel(page):
    page.goto(f"{page.base_url}/admin/post/")
    page.wait_for_selector(".moj-action-bar__filter button")
    page.locator(".moj-action-bar__filter button").click()
    page.wait_for_selector(".moj-filter:visible")
    author_section = page.locator(
        '.govuk-accordion__section:has(.govuk-accordion__section-button:has-text("Author email"))'
    )
    if "govuk-accordion__section--expanded" not in (
        author_section.get_attribute("class") or ""
    ):
        author_section.locator(".govuk-accordion__section-button").click()


@pytest.mark.e2e
class TestSelectWithSearchFilterInListEnhancement:
    def test_filter_uses_choices_js(self, page):
        _open_filter_panel(page)

        author_select = page.locator('select[name="flt0_0"]')
        assert author_select.count() > 0
        assert author_select.get_attribute("data-module") == "select-with-search"

        author_field = page.locator('label[for="flt0_0"]').locator("..")
        author_field.locator(".choices").wait_for()
        assert "gem-c-select-with-search" in (author_field.get_attribute("class") or "")

    def test_filter_options_populate_from_db(self, page):
        _open_filter_panel(page)

        author_select = page.locator('select[name="flt0_0"]')
        option_count = author_select.locator("option").count()

        assert option_count > 1

    def test_applying_filter_updates_url(self, page):
        _open_filter_panel(page)

        author_field = page.locator('label[for="flt0_0"]').locator("..")
        choices_wrapper = author_field.locator(".choices")
        choices_wrapper.click()
        author_field.locator(".choices__list--dropdown").wait_for(state="visible")

        author_field.locator(
            '.choices__list--dropdown .choices__item--choice[data-value]:not([data-value=""])'
        ).first.click()

        with page.expect_navigation():
            page.locator(
                '#filter_form button[type="submit"]:has-text("Apply filters")'
            ).click()

        assert "flt0_0=" in page.url
