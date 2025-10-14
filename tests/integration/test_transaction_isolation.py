"""Test to verify transactional isolation is working correctly."""

import pytest
from tests.factories import UserFactory, PostFactory


@pytest.mark.integration
class TestTransactionIsolation:
    """Verify that database is properly rolled back between tests."""

    def test_isolation_1_create_user(self, db_session):
        """First test: Create a user and verify it exists."""
        user = UserFactory.create(name="Test User 1")
        print(f"\n[Test 1] Created user with id={user.id}, name={user.name}")

        # Verify user exists in this session
        all_users = db_session.query(UserFactory._meta.model).all()
        print(f"[Test 1] Total users in DB: {len(all_users)}")
        for u in all_users:
            print(f"[Test 1]   - User {u.id}: {u.name}")

        assert len(all_users) == 1
        assert all_users[0].name == "Test User 1"

    def test_isolation_2_db_should_be_empty(self, db_session):
        """Second test: Verify DB is empty (previous test data rolled back)."""
        all_users = db_session.query(UserFactory._meta.model).all()
        print(f"\n[Test 2] Total users in DB: {len(all_users)}")
        for u in all_users:
            print(f"[Test 2]   - User {u.id}: {u.name}")

        # This should be empty if rollback worked
        assert len(all_users) == 0, "Database should be empty after rollback!"

    def test_isolation_3_create_different_user(self, db_session):
        """Third test: Create a different user with same ID pattern."""
        user = UserFactory.create(name="Test User 3")
        print(f"\n[Test 3] Created user with id={user.id}, name={user.name}")

        all_users = db_session.query(UserFactory._meta.model).all()
        print(f"[Test 3] Total users in DB: {len(all_users)}")
        for u in all_users:
            print(f"[Test 3]   - User {u.id}: {u.name}")

        # Should only see the user from this test
        assert len(all_users) == 1
        assert all_users[0].name == "Test User 3"

        # If isolation is working, ID should be 1 again (or at least not 3)
        print(f"[Test 3] User ID is {user.id} (should be 1 if auto-increment reset)")

    def test_isolation_4_create_multiple_users(self, db_session):
        """Fourth test: Create multiple users."""
        user1 = UserFactory.create(name="User A")
        user2 = UserFactory.create(name="User B")
        post = PostFactory.create(title="Test Post", author=user1)

        print(
            f"\n[Test 4] Created user1 id={user1.id}, user2 id={user2.id}, post id={post.id}"
        )

        all_users = db_session.query(UserFactory._meta.model).all()
        all_posts = db_session.query(PostFactory._meta.model).all()

        print(f"[Test 4] Total users in DB: {len(all_users)}")
        print(f"[Test 4] Total posts in DB: {len(all_posts)}")

        # Should only see data from this test
        assert len(all_users) == 2
        assert len(all_posts) == 1

    def test_isolation_5_verify_empty_again(self, db_session):
        """Fifth test: Verify DB is empty again."""
        all_users = db_session.query(UserFactory._meta.model).all()
        all_posts = db_session.query(PostFactory._meta.model).all()

        print(f"\n[Test 5] Total users in DB: {len(all_users)}")
        print(f"[Test 5] Total posts in DB: {len(all_posts)}")

        # Everything should be rolled back
        assert len(all_users) == 0, "Users should be rolled back!"
        assert len(all_posts) == 0, "Posts should be rolled back!"
