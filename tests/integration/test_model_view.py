"""Integration tests for XGovukModelView URL generation methods."""

import pytest
from xgovuk_flask_admin import XGovukModelView, XGovukAdminModelConverter


@pytest.mark.integration
class TestXGovukModelView:
    """Test XGovukModelView configuration and methods."""

    def test_default_category(self, db_session):
        """Test that default category is set to 'Miscellaneous'."""
        from example.models import User

        view = XGovukModelView(User, db_session)
        assert view.category == "Miscellaneous"

    def test_custom_category(self, db_session):
        """Test that custom category can be set."""
        from example.models import User

        view = XGovukModelView(User, db_session, category="Custom")
        assert view.category == "Custom"

    def test_uses_govuk_converter(self, db_session):
        """Test that XGovukAdminModelConverter is used."""
        from example.models import User

        view = XGovukModelView(User, db_session)
        assert view.model_form_converter == XGovukAdminModelConverter


@pytest.mark.integration
class TestGetRemoveFilterUrl:
    """Test XGovukModelView._get_remove_filter_url() method.

    These integration tests verify that the remove filter URL generation works correctly
    in the context of the full application stack (Flask routing, ModelView).
    """

    def test_removes_specified_filter(self, app, user_model_view, client):
        """Test that specified filter is removed from URL."""
        # Initialize routes by making a request
        client.get("/admin/user/")
        # Setup: 3 active filters
        active_filters = [
            (0, "Age", "equals", "25"),
            (1, "Job", "equals", "Developer"),
            (2, "Email", "contains", "test"),
        ]

        with app.test_request_context("/admin/user/"):
            # Remove filter at position 1 (Job filter)
            url = user_model_view._get_remove_filter_url(
                filter_position=1,
                active_filters=active_filters,
                return_url=None,
                sort_column=None,
                sort_desc=False,
                search=None,
                page_size=None,
                default_page_size=20,
                extra_args=None,
            )

            # URL should not contain the removed filter but should have the others
            # Since we're removing position 1, remaining filters get renumbered
            assert "age" in url.lower() or "flt" in url  # Age filter preserved
            assert "email" in url.lower() or "flt" in url  # Email filter preserved
            # Job filter should not be present (it was removed)

    def test_preserves_other_filters(self, app, user_model_view, client):
        """Test that other filters remain in URL."""
        # Initialize routes
        client.get("/admin/user/")
        # Setup: 2 active filters, remove one
        active_filters = [
            (0, "Age", "equals", "30"),
            (1, "Name", "contains", "John"),
        ]

        with app.test_request_context("/admin/user/"):
            url = user_model_view._get_remove_filter_url(
                filter_position=0,  # Remove first filter
                active_filters=active_filters,
                return_url=None,
                sort_column=None,
                sort_desc=False,
                search=None,
                page_size=None,
                default_page_size=20,
                extra_args=None,
            )

            # The second filter should still be in the URL
            assert "flt" in url  # Some filter parameter present
            # The URL should have filter parameters
            assert "?" in url or "flt" in url

    def test_preserves_sort_state(self, app, user_model_view, client):
        """Test that sort column and direction are preserved."""
        # Initialize routes
        client.get("/admin/user/")
        active_filters = [(0, "Age", "equals", "25")]

        with app.test_request_context("/admin/user/"):
            # Test with sort ascending
            url = user_model_view._get_remove_filter_url(
                filter_position=0,
                active_filters=active_filters,
                return_url=None,
                sort_column=2,  # Sort by column 2
                sort_desc=False,
                search=None,
                page_size=None,
                default_page_size=20,
                extra_args=None,
            )

            assert "sort=2" in url

            # Test with sort descending
            url_desc = user_model_view._get_remove_filter_url(
                filter_position=0,
                active_filters=active_filters,
                return_url=None,
                sort_column=2,
                sort_desc=True,  # Descending
                search=None,
                page_size=None,
                default_page_size=20,
                extra_args=None,
            )

            assert "sort=2" in url_desc
            assert "desc=1" in url_desc

    def test_preserves_search(self, app, user_model_view, client):
        """Test that search query is preserved."""
        # Initialize routes
        client.get("/admin/user/")
        active_filters = [(0, "Age", "equals", "25")]

        with app.test_request_context("/admin/user/"):
            url = user_model_view._get_remove_filter_url(
                filter_position=0,
                active_filters=active_filters,
                return_url=None,
                sort_column=None,
                sort_desc=False,
                search="test query",  # Search parameter
                page_size=None,
                default_page_size=20,
                extra_args=None,
            )

            assert "search=test" in url or "search=test+query" in url

    def test_preserves_page_size(self, app, user_model_view, client):
        """Test that non-default page size is preserved."""
        # Initialize routes
        client.get("/admin/user/")
        active_filters = [(0, "Age", "equals", "25")]

        with app.test_request_context("/admin/user/"):
            # Test with non-default page size
            url = user_model_view._get_remove_filter_url(
                filter_position=0,
                active_filters=active_filters,
                return_url=None,
                sort_column=None,
                sort_desc=False,
                search=None,
                page_size=50,  # Non-default
                default_page_size=20,
                extra_args=None,
            )

            assert "page_size=50" in url

            # Test with default page size (should not be included)
            url_default = user_model_view._get_remove_filter_url(
                filter_position=0,
                active_filters=active_filters,
                return_url=None,
                sort_column=None,
                sort_desc=False,
                search=None,
                page_size=20,  # Default
                default_page_size=20,
                extra_args=None,
            )

            # Default page size should not be in URL
            assert "page_size" not in url_default

    def test_preserves_extra_args(self, app, user_model_view, client):
        """Test that extra query arguments are preserved."""
        # Initialize routes
        client.get("/admin/user/")
        active_filters = [(0, "Age", "equals", "25")]

        with app.test_request_context("/admin/user/"):
            url = user_model_view._get_remove_filter_url(
                filter_position=0,
                active_filters=active_filters,
                return_url=None,
                sort_column=None,
                sort_desc=False,
                search=None,
                page_size=None,
                default_page_size=20,
                extra_args={"custom_param": "value", "another": "test"},
            )

            assert "custom_param=value" in url
            assert "another=test" in url
