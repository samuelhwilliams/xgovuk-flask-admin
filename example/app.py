"""
An example app to be used with the xgovuk-flask-admin theme for testing.
"""

import datetime
import os
import random
import uuid

import faker
from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy_lite import SQLAlchemy
from testcontainers.postgres import PostgresContainer

from example.enums import FavouriteColour
from example.models import Base, User, Account, Post
from example.views import UserModelView, PostModelView, AccountModelView, CustomView
from xgovuk_flask_admin import XGovukFlaskAdmin
from xgovuk_flask_admin.theme import XGovukFrontendTheme
from govuk_frontend_wtf.main import WTFormsHelpers
from jinja2 import PackageLoader, ChoiceLoader, PrefixLoader, FileSystemLoader

# Global container instance
_postgres_container = None


class ProxySession:
    """
    We provide a live proxy to db.session here, so that any access is scoped to the `app_context` of the moment.
    When we weren't using this and were passing `db.session` directly through to the model views below, it was
    holding a single session (id:1) open and using that forever, rather than using request-scoped sessions. This
    definitely feels very wrong and I suspect is a bug/bad practice recommendation in either flask-sqlalchemy-lite
    or flask-admin.

    This was discovered when adding the following config to `form_args` of one of the model views:

        "query_factory": lambda: db.session.query(Organisation).filter_by(can_manage_grants=True),

    This was causing some queries to be executed by flask-admin using the global/permanent session (id:1), and
    anything using that query factory to use request-scoped sessions. This was causing errors in SQLAlchemy when
    trying to persist certain changes.

    Using this proxy, initial set up will use the app context from `create_app`, but then any queries that are fired
    off during requests will use the request-scoped session.
    """

    def __init__(self, db_: SQLAlchemy) -> None:
        self.db = db_

    def __getattr__(self, name):  # type: ignore[no-untyped-def]
        return getattr(self.db.session, name)


def get_postgres_container():
    """Get or create a PostgreSQL testcontainer."""
    global _postgres_container
    if _postgres_container is None:
        _postgres_container = PostgresContainer("postgres:16-alpine")
        _postgres_container.start()
    return _postgres_container


def stop_postgres_container():
    """Stop and clean up the PostgreSQL testcontainer."""
    global _postgres_container
    if _postgres_container is not None:
        _postgres_container.stop()
        _postgres_container = None


def _create_app(config_overrides=None, seed: bool = True):
    """Application factory for creating Flask app instances.

    Args:
        config_overrides: Dict of config values to override defaults

    Returns:
        Tuple of (app, db, admin) instances
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "oh-no-its-a-secret"
    app.config["EXPLAIN_TEMPLATE_LOADING"] = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    # Use PostgreSQL testcontainer if USE_POSTGRES env var is set
    # Otherwise default to SQLite for backward compatibility with tests
    use_postgres = os.environ.get("USE_POSTGRES", "true").lower() in (
        "true",
        "1",
        "yes",
    )

    if use_postgres:
        postgres = get_postgres_container()
        app.config["SQLALCHEMY_ENGINES"] = {
            "default": postgres.get_connection_url().replace("+psycopg2", "")
        }
    else:
        app.config["SQLALCHEMY_ENGINES"] = {"default": "sqlite:///default.sqlite"}

    # Apply config overrides
    if config_overrides:
        app.config.update(config_overrides)

    # Configure Jinja2 loaders
    app.jinja_options = {
        "loader": ChoiceLoader(
            [
                FileSystemLoader("example/templates"),
                PrefixLoader(
                    {"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}
                ),
                PrefixLoader(
                    {"govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf")}
                ),
                PackageLoader("xgovuk_flask_admin"),
            ]
        )
    }

    # Initialize extensions
    admin = Admin(app, theme=XGovukFrontendTheme())
    XGovukFlaskAdmin(app, service_name="X-GOV.UK Flask Admin")
    WTFormsHelpers(app)
    db = SQLAlchemy(app)

    # Create tables and add views
    with app.app_context():
        Base.metadata.create_all(db.engine)
        admin.add_view(UserModelView(User, ProxySession(db), category="Models"))
        admin.add_view(PostModelView(Post, ProxySession(db), category="Models"))
        admin.add_view(AccountModelView(Account, ProxySession(db), category="Models"))
        admin.add_view(CustomView(name="Custom View", endpoint="custom"))

    if seed:
        seed_database(app, db)

    return app, db, admin


def create_app(config_overrides=None, seed: bool = True):
    return _create_app(config_overrides, seed=seed)[0]


def seed_database(app, db, num_users=8):
    """Populate database with sample data.

    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
        num_users: Number of sample users to create
    """
    with app.app_context():
        fake = faker.Faker()
        for _ in range(num_users):
            # Randomly set last_logged_in_at for some users
            last_login = None
            if random.random() > 0.3:  # 70% of users have logged in
                days_ago = random.randint(0, 365)
                last_login = datetime.datetime.now() - datetime.timedelta(days=days_ago)

            u = User(
                email=fake.email(),
                created_at=datetime.date.today(),
                name=fake.name(),
                age=random.randint(18, 100),
                job="blah blah",
                favourite_colour=random.choice(list(FavouriteColour)),
                last_logged_in_at=last_login,
                active=random.choice([True, False]),
            )
            db.session.add(u)
            db.session.flush()

            # Create account for user
            a = Account(id=str(uuid.uuid4()), user_id=u.id)
            db.session.add(a)

            # Create 2-5 posts for each user
            num_posts = random.randint(2, 5)
            for _ in range(num_posts):
                # Some posts are published, some are drafts
                published = None
                if random.random() > 0.3:  # 70% of posts are published
                    days_ago = random.randint(0, 180)
                    published = datetime.datetime.now() - datetime.timedelta(
                        days=days_ago
                    )

                # Generate multiline content with 3-5 paragraphs separated by newlines
                num_paragraphs = random.randint(3, 5)
                content_paragraphs = [
                    fake.paragraph(nb_sentences=random.randint(2, 4))
                    for _ in range(num_paragraphs)
                ]
                multiline_content = "\n\n".join(content_paragraphs)

                post = Post(
                    title=fake.sentence(nb_words=6).rstrip("."),
                    content=multiline_content,
                    author_id=u.id,
                    published_at=published,
                    created_at=datetime.datetime.now()
                    - datetime.timedelta(days=random.randint(0, 365)),
                )
                db.session.add(post)

        db.session.commit()
