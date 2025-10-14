"""Unit tests for GOV.UK pagination helper."""

import pytest
from xgovuk_flask_admin import govuk_pagination_params_builder


@pytest.mark.unit
class TestPaginationBuilder:
    """Test govuk_pagination_params_builder function."""

    def test_first_page(self):
        """Test pagination params for page 0."""

        def url_gen(page):
            return f"/?page={page}"

        result = govuk_pagination_params_builder(0, 5, url_gen)

        # Assert no 'previous' link
        assert "previous" not in result

        # Assert 'next' link exists
        assert "next" in result
        assert result["next"]["href"] == "/?page=1"

        # Assert page 1 is current (0-indexed input becomes 1-indexed in items)
        current_items = [item for item in result["items"] if item.get("current")]
        assert len(current_items) == 1
        assert current_items[0]["number"] == 1

    def test_last_page(self):
        """Test pagination params for last page."""

        def url_gen(page):
            return f"/?page={page}"

        result = govuk_pagination_params_builder(4, 5, url_gen)

        # Assert 'previous' link exists
        assert "previous" in result
        assert result["previous"]["href"] == "/?page=3"

        # Assert no 'next' link
        assert "next" not in result

        # Assert page 5 is current (0-indexed input becomes 1-indexed)
        current_items = [item for item in result["items"] if item.get("current")]
        assert len(current_items) == 1
        assert current_items[0]["number"] == 5

    def test_middle_page_with_ellipsis(self):
        """Test pagination params with ellipsis for many pages."""

        def url_gen(page):
            return f"/?page={page}"

        result = govuk_pagination_params_builder(5, 10, url_gen)

        # Assert ellipsis items present
        ellipsis_items = [item for item in result["items"] if item.get("ellipsis")]
        assert len(ellipsis_items) > 0

        # Assert page 6 is current (0-indexed input 5 becomes 1-indexed 6)
        current_items = [item for item in result["items"] if item.get("current")]
        assert len(current_items) == 1
        assert current_items[0]["number"] == 6

    def test_three_pages_or_less_no_ellipsis(self):
        """Test pagination without ellipsis for small page counts."""

        def url_gen(page):
            return f"/?page={page}"

        result = govuk_pagination_params_builder(1, 3, url_gen)

        # Assert no ellipsis
        ellipsis_items = [item for item in result["items"] if item.get("ellipsis")]
        assert len(ellipsis_items) == 0

        # Assert all 3 pages shown
        page_items = [item for item in result["items"] if "number" in item]
        assert len(page_items) == 3
        assert [item["number"] for item in page_items] == [1, 2, 3]

    def test_includes_govuk_classes(self):
        """Test that GOV.UK classes are added to pagination."""

        def url_gen(page):
            return f"/?page={page}"

        result = govuk_pagination_params_builder(0, 2, url_gen)

        # Assert 'govuk-!-text-align-center' class present
        assert "classes" in result
        assert result["classes"] == "govuk-!-text-align-center"

    def test_single_page(self):
        """Test pagination with only one page."""

        def url_gen(page):
            return f"/?page={page}"

        result = govuk_pagination_params_builder(0, 1, url_gen)

        # Assert no previous/next links
        assert "previous" not in result
        assert "next" not in result

        # Assert single page shown
        page_items = [item for item in result["items"] if "number" in item]
        assert len(page_items) == 1
        assert page_items[0]["number"] == 1
        assert page_items[0]["current"] is True
