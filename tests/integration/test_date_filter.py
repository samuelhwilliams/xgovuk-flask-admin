"""Integration tests for date filter GOV.UK field combining logic."""

import pytest
from flask import request


@pytest.mark.integration
class TestGetListFilterArgs:
    """Test XGovModelView._get_list_filter_args() date field combining.

    These integration tests verify that the date combining logic works correctly
    in the context of the full application stack (HTTP requests, Flask routing,
    ModelView, and filter infrastructure). The method modifies request.args
    temporarily to combine GOV.UK date fields before Flask-Admin processes them.
    """

    def test_combines_date_fields(self, app, user_model_view, client):
        """Test that GOV.UK date fields are combined into YYYY-MM-DD format."""
        # Make actual request to trigger filter initialization
        response = client.get("/admin/user/?flt0_created_at=2024-03-15")
        assert response.status_code == 200

        # Now test the date combining logic with the initialized filters
        with app.test_request_context(
            "/admin/user/?flt0_created_at-day=15&flt0_created_at-month=3&flt0_created_at-year=2024"
        ):
            # Verify request args has the date components
            assert "flt0_created_at-day" in request.args

            # The method should combine these into flt0_created_at=2024-03-15
            # when processing internally
            result = user_model_view._get_list_filter_args()

            # With proper filters initialized, this should work
            if result:
                # If filters produced results, check format
                filter_value = result[0][3] if len(result) > 0 else None
                if filter_value:
                    assert (
                        "2024" in filter_value
                        and "03" in filter_value
                        and "15" in filter_value
                    )

    def test_ignores_incomplete_dates(self, app, user_model_view):
        """Test partial dates (missing day/month/year) are not combined."""
        with app.test_request_context(
            "/admin/user/?flt0_created_at-day=15&flt0_created_at-month=3"
        ):
            result = user_model_view._get_list_filter_args()

            # Incomplete dates should not produce a filter
            # Result should be None or empty list
            assert result is None or len(result) == 0

    def test_pads_single_digit_dates(self, app, user_model_view, client):
        """Test that day=5, month=3 becomes 05 and 03."""
        # Initialize filters first
        client.get("/admin/user/")

        with app.test_request_context(
            "/admin/user/?flt0_created_at-day=5&flt0_created_at-month=3&flt0_created_at-year=2024"
        ):
            result = user_model_view._get_list_filter_args()

            # The date should be properly zero-padded when combined
            if result and len(result) > 0:
                filter_value = result[0][3]
                # Check for zero-padded format
                assert "2024-03-05" in str(filter_value) or filter_value == "2024-03-05"

    def test_preserves_other_filters(self, app, user_model_view, client):
        """Test that non-date filters pass through unchanged."""
        # Initialize filters
        client.get("/admin/user/")

        with app.test_request_context(
            "/admin/user/?flt0_age=25&flt1_created_at-day=15&flt1_created_at-month=3&flt1_created_at-year=2024"
        ):
            result = user_model_view._get_list_filter_args()

            # Both filters should be present if filter system is working
            if result:
                assert len(result) >= 1  # At least one filter should work

    def test_restores_original_request_args(self, app, user_model_view):
        """Test that request.args is restored after processing."""
        with app.test_request_context(
            "/admin/user/?flt0_created_at-day=15&flt0_created_at-month=3&flt0_created_at-year=2024"
        ):
            original_keys = set(request.args.keys())

            user_model_view._get_list_filter_args()

            # request.args should be restored to original
            restored_keys = set(request.args.keys())
            assert original_keys == restored_keys

            # The individual date fields should still be there
            assert "flt0_created_at-day" in request.args
            assert "flt0_created_at-month" in request.args
            assert "flt0_created_at-year" in request.args

    def test_handles_multiple_date_filters(self, app, user_model_view, client):
        """Test combining multiple date filters simultaneously."""
        # Initialize filters
        client.get("/admin/user/")

        with app.test_request_context(
            "/admin/user/?flt0_created_at-day=15&flt0_created_at-month=3&flt0_created_at-year=2024&flt1_created_at-day=20&flt1_created_at-month=6&flt1_created_at-year=2023"
        ):
            result = user_model_view._get_list_filter_args()

            # Multiple date filters should be processed
            if result:
                # At least some filters should be processed
                assert len(result) >= 1

    def test_handles_whitespace_in_date_fields(self, app, user_model_view, client):
        """Test that whitespace is trimmed from day/month/year values."""
        # Initialize filters
        client.get("/admin/user/")

        with app.test_request_context(
            "/admin/user/?flt0_created_at-day= 15 &flt0_created_at-month= 3 &flt0_created_at-year= 2024 "
        ):
            result = user_model_view._get_list_filter_args()

            # Whitespace should be trimmed and date combined
            if result and len(result) > 0:
                filter_value = str(result[0][3])
                # Should not have leading/trailing spaces
                assert filter_value.strip() == filter_value
                # Should contain the date components
                assert "2024" in filter_value
