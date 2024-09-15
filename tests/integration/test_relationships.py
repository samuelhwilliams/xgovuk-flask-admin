"""Integration tests for foreign key relationships."""

import pytest


@pytest.mark.integration
class TestRelationships:
    """Test handling of foreign key relationships."""

    @pytest.fixture
    def users_with_accounts(self, db_session, app, sample_users):
        """Create users with associated accounts."""
        from tests.conftest import Account
        import uuid

        with app.app_context():
            accounts = []
            for user in sample_users[:3]:
                account = Account(id=str(uuid.uuid4()), user_id=user.id)
                db_session.add(account)
                accounts.append(account)

            db_session.commit()
            yield sample_users, accounts

            # Cleanup
            db_session.query(Account).delete()
            db_session.commit()

    @pytest.mark.xfail(
        reason="Not implemented: Assert select dropdown for user relationship"
    )
    def test_relationship_field_renders_as_select(self, client, users_with_accounts):
        """Test foreign key field renders as GOV.UK select dropdown."""
        client.get("/admin/account/new/")
        # TODO: Assert select dropdown for user relationship
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(
        reason="Not implemented: Assert user information shown in account list"
    )
    def test_relationship_displays_related_object(self, client, users_with_accounts):
        """Test relationship displays related object string representation."""
        _, accounts = users_with_accounts
        client.get("/admin/account/")
        # TODO: Assert user information shown in account list
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(
        reason="Not implemented: Assert account created with correct user_id"
    )
    def test_can_create_with_relationship(self, client, sample_users, db_session):
        """Test creating record with foreign key relationship."""
        user = sample_users[0]
        data = {"id": "test-account-id", "user": str(user.id)}
        client.post("/admin/account/new/", data=data, follow_redirects=True)
        # TODO: Assert account created with correct user_id
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(reason="Not implemented: Assert account now linked to new user")
    def test_can_edit_relationship(self, client, users_with_accounts, db_session):
        """Test changing foreign key relationship."""
        users, accounts = users_with_accounts
        account = accounts[0]
        new_user = users[1]

        data = {"id": account.id, "user": str(new_user.id)}
        client.post(
            f"/admin/account/edit/?id={account.id}", data=data, follow_redirects=True
        )
        # TODO: Assert account now linked to new user
        raise NotImplementedError("Test not implemented")
