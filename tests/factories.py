"""Factory Boy factories for creating test data."""

import datetime
import random
import uuid

import factory
from factory.faker import Faker as FactoryFaker

from example.enums import FavouriteColour
from example.models import User, Account, Post


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating User instances."""

    class Meta:
        model = User
        sqlalchemy_session = None  # Will be set by fixture
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    email = FactoryFaker("email")
    name = FactoryFaker("name")
    age = factory.Faker("random_int", min=18, max=100)
    job = FactoryFaker("job")
    favourite_colour = factory.LazyFunction(
        lambda: random.choice(list(FavouriteColour))
    )
    created_at = FactoryFaker("date_this_year")
    last_logged_in_at = factory.LazyFunction(
        lambda: datetime.datetime.now()
        - datetime.timedelta(days=random.randint(0, 365))
        if random.random() > 0.3
        else None
    )


class AccountFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Account instances."""

    class Meta:
        model = Account
        sqlalchemy_session = None  # Will be set by fixture
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    user = factory.SubFactory(UserFactory)
    user_id = factory.LazyAttribute(lambda obj: obj.user.id)


class PostFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Post instances."""

    class Meta:
        model = Post
        sqlalchemy_session = None  # Will be set by fixture
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    title = FactoryFaker("sentence", nb_words=6)
    content = factory.LazyFunction(
        lambda: "\n\n".join(
            [
                FactoryFaker("paragraph", nb_sentences=random.randint(2, 4)).evaluate(
                    None, None, {"locale": None}
                )
                for _ in range(random.randint(3, 5))
            ]
        )
    )
    author = factory.SubFactory(UserFactory)
    author_id = factory.LazyAttribute(lambda obj: obj.author.id)
    published_at = factory.LazyFunction(
        lambda: datetime.datetime.now()
        - datetime.timedelta(days=random.randint(0, 180))
        if random.random() > 0.3
        else None
    )
    created_at = FactoryFaker("date_time_this_year")
