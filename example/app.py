"""
An example app to be used with the xgov-flask-admin theme for testing.
"""

import datetime
import random
import uuid

import faker
from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy_lite import SQLAlchemy

from example.enums import FavouriteColour
from example.models import Base, User, Account, Post
from example.views import UserModelView, PostModelView, AccountModelView
from xgov_flask_admin import XGovFrontendTheme, XGovFlaskAdmin, XGovModelView
from govuk_frontend_wtf.main import WTFormsHelpers
from jinja2 import PackageLoader, ChoiceLoader, PrefixLoader


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
    app.config["SQLALCHEMY_ENGINES"] = {"default": "sqlite:///default.sqlite"}

    # Apply config overrides
    if config_overrides:
        app.config.update(config_overrides)

    # Configure Jinja2 loaders
    app.jinja_options = {
        "loader": ChoiceLoader(
            [
                PrefixLoader(
                    {"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}
                ),
                PrefixLoader(
                    {"govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf")}
                ),
                PackageLoader("xgov_flask_admin"),
            ]
        )
    }

    # Initialize extensions
    admin = Admin(app, theme=XGovFrontendTheme())
    XGovFlaskAdmin(app, service_name="Gov Design System - Flask Admin")
    WTFormsHelpers(app)
    db = SQLAlchemy(app)

    # Create tables and add views
    with app.app_context():
        Base.metadata.create_all(db.engine)
        admin.add_view(UserModelView(User, db.session, category="Models"))
        admin.add_view(PostModelView(Post, db.session, category="Models"))
        admin.add_view(AccountModelView(Account, db.session, category="Models"))

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
