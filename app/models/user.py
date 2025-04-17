from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import TIMESTAMP
from pydantic import EmailStr


class UserBase(SQLModel):
    email: EmailStr = Field(nullable=False, unique=True)
    username: str = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), index=True, nullable=False),
    )


class User(UserBase, table=True):
    __tablename__ = "users"
    id: int = Field(default=None, primary_key=True)


class UserPublic(SQLModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass
