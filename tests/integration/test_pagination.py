"""Integration tests for pagination."""

import pytest


@pytest.mark.integration
class TestPagination:
    """Test pagination functionality."""

    @pytest.fixture
    def many_users(self, db_session, app):
        """Create many users for pagination testing."""
        from tests.conftest import User, FavouriteColour
        import datetime

        with app.app_context():
            users = []
            for i in range(50):
                user = User(
                    email=f"pagination{i}@example.com",
                    name=f"Pagination User {i}",
                    age=20 + (i % 30),
                    job=f"Job {i % 5}",
                    favourite_colour=list(FavouriteColour)[i % 3],
                    created_at=datetime.date(2024, 1, 1) + datetime.timedelta(days=i),
                    active=True,
                )
                db_session.add(user)
                users.append(user)

            db_session.commit()
            yield users

            # Cleanup
            db_session.query(User).delete()
            db_session.commit()

    @pytest.mark.xfail(reason="Not implemented: Assert no previous link")
    def test_first_page_no_previous(self, client, many_users):
        """Test first page has no previous link."""
        client.get("/admin/user/")
        # TODO: Assert no previous link
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(reason="Not implemented: Assert next link present")
    def test_first_page_has_next(self, client, many_users):
        """Test first page has next link."""
        client.get("/admin/user/")
        # TODO: Assert next link present
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(reason="Not implemented: Assert both previous and next links")
    def test_middle_page_has_both_links(self, client, many_users):
        """Test middle page has previous and next links."""
        client.get("/admin/user/?page=2")
        # TODO: Assert both previous and next links
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(
        reason="Not implemented: Calculate last page and assert no next link"
    )
    def test_last_page_no_next(self, client, many_users):
        """Test last page has no next link."""
        # TODO: Calculate last page
        # TODO: Assert no next link
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(reason="Not implemented: Assert 25 items shown")
    def test_page_size_selector(self, client, many_users):
        """Test page size can be changed."""
        client.get("/admin/user/?page_size=25")
        # TODO: Assert 25 items shown
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(reason="Not implemented: Assert govuk-pagination class")
    def test_pagination_uses_govuk_component(self, client, many_users):
        """Test pagination uses GOV.UK component."""
        client.get("/admin/user/")
        # TODO: Assert govuk-pagination class
        raise NotImplementedError("Test not implemented")
