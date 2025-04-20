from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import TIMESTAMP

if TYPE_CHECKING:
    from app.models.user_model import User


class PostBase(SQLModel):
    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    published: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), index=True, nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), index=True, nullable=False),
    )


class Post(PostBase, table=True):
    __tablename__ = "posts"
    id: int = Field(default=None, primary_key=True, nullable=False)
    author_id: int = Field(default=None, nullable=False, foreign_key="users.id", ondelete="CASCADE")
    author: "User" = Relationship(back_populates="posts")


# Simplified User reference for PostPublic
class UserShared(SQLModel):
    id: int
    username: str
    email: str
    created_at: datetime


class PostPublic(SQLModel):
    id: int
    title: str
    content: str
    published: bool
    author_id: int
    author: UserShared
    created_at: datetime
    updated_at: datetime


class PostCreate(PostBase):
    pass


class PostUpdate(SQLModel):
    title: str | None = None
    content: str | None = None
    published: bool | None = None
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
