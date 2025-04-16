from datetime import datetime
from sqlmodel import SQLModel, Field, Column, Boolean
from sqlalchemy import TIMESTAMP, func


class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: int = Field(default=None, primary_key=True, nullable=False)
    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    published: bool = Field(
        sa_column=Column(Boolean, server_default="TRUE", nullable=False)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(datetime.UTC),
        sa_column=Column(
            TIMESTAMP(timezone=True),
            index=True,
            nullable=False,
            server_default=func.now(),
        ),
    )
