"""Integration tests for column sorting."""

import pytest


@pytest.mark.integration
class TestSorting:
    """Test column sorting functionality."""

    @pytest.mark.xfail(
        reason="Not implemented: Verify results sorted by name ascending"
    )
    def test_sort_by_name_ascending(self, client, sample_users):
        """Test sorting by name in ascending order."""
        client.get("/admin/user/?sort=2")  # Assuming name is column 2
        # TODO: Verify results sorted by name ascending
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(
        reason="Not implemented: Verify results sorted by name descending"
    )
    def test_sort_by_name_descending(self, client, sample_users):
        """Test sorting by name in descending order."""
        client.get("/admin/user/?sort=2&desc=1")
        # TODO: Verify results sorted by name descending
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(reason="Not implemented: Verify results sorted by age")
    def test_sort_by_age(self, client, sample_users):
        """Test sorting by numeric column."""
        client.get("/admin/user/?sort=3")  # Assuming age is column 3
        # TODO: Verify results sorted by age
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(
        reason="Not implemented: Assert sort links have govuk-link class"
    )
    def test_sort_links_have_govuk_classes(self, client, sample_users):
        """Test sort links use GOV.UK styling."""
        client.get("/admin/user/")
        # TODO: Assert sort links have govuk-link class
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(reason="Not implemented: Assert sort indicator present")
    def test_sort_indicator_shown(self, client, sample_users):
        """Test active sort shows visual indicator."""
        client.get("/admin/user/?sort=2")
        # TODO: Assert sort indicator present
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(reason="Not implemented: Verify filter still active after sort")
    def test_sort_preserves_filters(self, client, sample_users):
        """Test sorting preserves active filters."""
        client.get("/admin/user/?flt0_age=20&sort=2")
        # TODO: Verify filter still active after sort
        raise NotImplementedError("Test not implemented")
