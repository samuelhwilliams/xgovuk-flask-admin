import datetime
import uuid
from enum import StrEnum
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from example.enums import FavouriteColour


class Base(DeclarativeBase):
    def __str__(self):
        return f"<{self.__class__.__name__}({self.id})>"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    age: Mapped[int]
    job: Mapped[str]
    favourite_colour: Mapped[FavouriteColour | None]
    account: Mapped[Optional["Account"]] = relationship(back_populates="user")
    posts: Mapped[list["Post"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    created_at: Mapped[datetime.date]
    last_logged_in_at: Mapped[Optional[datetime.datetime]]
    active: Mapped[bool]


class Tag(StrEnum):
    RED = "red"
    YELLOW = "yellow"
    BLUE = "blue"


class Account(Base):
    __tablename__ = "account"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    user: Mapped[User] = relationship(back_populates="account")
    tags: Mapped[list[Tag]] = mapped_column(
        postgresql.ARRAY(SqlEnum(Tag, name="tag_enum", validate_strings=True)),
        nullable=False,
        default=list,
    )
    notes: Mapped[list[str]] = mapped_column(
        postgresql.ARRAY(postgresql.TEXT), nullable=False, default=list
    )


class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    content: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    author: Mapped[User] = relationship(back_populates="posts")
    published_at: Mapped[Optional[datetime.datetime]]
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=lambda: datetime.datetime.now()
    )
