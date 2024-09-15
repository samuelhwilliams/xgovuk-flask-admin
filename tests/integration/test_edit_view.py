"""Integration tests for edit view functionality."""

import pytest


@pytest.mark.integration
class TestEditViewRendering:
    """Test edit view renders correctly."""

    @pytest.mark.xfail(reason="Not implemented: Assert GOV.UK form components")
    def test_renders_govuk_form(self, client, sample_users):
        """Test edit form uses GOV.UK components."""
        user_id = sample_users[0].id
        response = client.get(f"/admin/user/edit/?id={user_id}")
        assert response.status_code == 200
        # TODO: Assert GOV.UK form components
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(reason="Not implemented: Assert fields contain user data")
    def test_form_populated_with_data(self, client, sample_users):
        """Test form fields are pre-populated with existing data."""
        user = sample_users[0]
        client.get(f"/admin/user/edit/?id={user.id}")
        # TODO: Assert fields contain user data
        raise NotImplementedError("Test not implemented")


@pytest.mark.integration
class TestEditViewSubmission:
    """Test edit form submission."""

    @pytest.mark.xfail(
        reason="Not implemented: Prepare update data, submit form, and assert record updated with success message"
    )
    def test_updates_record(self, client, sample_users, db_session):
        """Test successful record update."""
        # TODO: Prepare update data
        # TODO: Submit form
        # TODO: Assert record updated
        # TODO: Assert success message
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(
        reason="Not implemented: Submit invalid data and assert validation errors displayed"
    )
    def test_validation_errors_displayed(self, client, sample_users):
        """Test validation errors shown with GOV.UK styling."""
        # TODO: Submit invalid data
        # TODO: Assert validation errors displayed
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(reason="Not implemented: Assert error message or redirect")
    def test_invalid_id_shows_error(self, client):
        """Test editing non-existent record shows error."""
        client.get("/admin/user/edit/?id=99999")
        # TODO: Assert error message or redirect
        raise NotImplementedError("Test not implemented")
