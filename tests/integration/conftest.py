"""Shared pytest fixtures for integration tests."""
from typing import Generator

import pytest
from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy.orm import Session

from example.app import _create_app
from tests.factories import UserFactory, AccountFactory, PostFactory

# Store app components at module level for session scope
_app_components = None


def get_app_components():
    """Get or create app components (app, db, admin) for testing."""
    global _app_components
    if _app_components is None:
        _app_components = _create_app(
            config_overrides={
                "TESTING": True,
                "SQLALCHEMY_ENGINES": {"default": {"url": "sqlite:///:memory:", "echo": True, "connect_args":{"autocommit": False} }},
            },
            seed=False
        )
    return _app_components


@pytest.fixture(scope="session")
def app():
    """Create test Flask app using factory."""
    app, db, admin = get_app_components()
    return app


@pytest.fixture(scope="session")
def db(app):
    """Get database instance from factory.

    This returns the db object but should not be used directly for database operations.
    Use db_session fixture instead for proper transactional isolation.
    """
    app, db, admin = get_app_components()
    return db


@pytest.fixture(scope="function", autouse=False)
def db_session(request, app, db: SQLAlchemy) -> Generator[Session, None, None]:
    # Set up a DB session that is fully isolated for each specific test run. We override Flask-SQLAlchemy-Lite's (FSL)
    # sessionmaker configuration to use a connection with a transaction started, and configure FSL to use savepoints
    # for any flushes/commits that happen within the test. When the test finishes, this fixture will do a full rollback,
    # preventing any data leaking beyond the scope of the test.
    #
    # NOTE: this fixture is automatically used by all integration tests, and provides both an app context and a test
    # request context. So you will not need to manually create these within your integration tests.

    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()

        original_configuration = db.sessionmaker.kw.copy()
        db.sessionmaker.configure(bind=connection, join_transaction_mode="create_savepoint")

        UserFactory._meta.sqlalchemy_session = db.session
        AccountFactory._meta.sqlalchemy_session = db.session
        PostFactory._meta.sqlalchemy_session = db.session

        try:
            yield db.session

        finally:
            # Restore the original sessionmaker configuration.
            db.sessionmaker.configure(**original_configuration)

            db.session.close()
            transaction.rollback()

            connection.close()

            UserFactory._meta.sqlalchemy_session = None
            AccountFactory._meta.sqlalchemy_session = None
            PostFactory._meta.sqlalchemy_session = None


@pytest.fixture(scope="session")
def admin_instance(app):
    """Get Flask-Admin instance from factory."""
    app, db, admin = get_app_components()
    return admin


@pytest.fixture(scope="session")
def user_model_view(admin_instance):
    """Get UserModelView from admin instance."""
    # Find the user view from registered views
    for view in admin_instance._views:
        if view.name == "User":
            return view
    raise RuntimeError("UserModelView not found")


@pytest.fixture(scope="session")
def account_model_view(admin_instance):
    """Get AccountModelView from admin instance."""
    # Find the account view from registered views
    for view in admin_instance._views:
        if view.name == "Account":
            return view
    raise RuntimeError("AccountModelView not found")


@pytest.fixture
def client(app, admin_instance):
    """Create test client with views registered."""
    return app.test_client()
