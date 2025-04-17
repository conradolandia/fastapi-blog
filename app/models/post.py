from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import TIMESTAMP


class PostBase(SQLModel):
    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    published: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), index=True, nullable=False),
    )


class Post(PostBase, table=True):
    __tablename__ = "posts"
    id: int = Field(default=None, primary_key=True)


class PostPublic(SQLModel):
    id: int
    title: str
    content: str
    created_at: datetime


class PostCreate(PostBase):
    pass


class PostUpdate(SQLModel):
    title: str | None = None
    content: str | None = None
    published: bool | None = None
