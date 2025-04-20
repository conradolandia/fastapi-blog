from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import TIMESTAMP
from pydantic import BaseModel, EmailStr
from app.models.post_model import Post


class UserBase(SQLModel):
    email: EmailStr = Field(nullable=False, unique=True)
    username: str = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)
    disabled: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), index=True, nullable=False),
    )


class User(UserBase, table=True):
    __tablename__ = "users"
    id: int = Field(default=None, primary_key=True)
    posts: list["Post"] = Relationship(back_populates="author")


# Simplified Post reference for UserPublic
class PostShared(SQLModel):
    id: int
    title: str
    content: str
    created_at: datetime


class UserPublic(SQLModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    posts: list[PostShared] = []


class UserCreate(SQLModel):
    email: EmailStr
    username: str
    password: str


class UserUpdate(SQLModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    disabled: bool | None = False


class UserLogin(SQLModel):
    email: EmailStr
    password: str


class UserInDB(SQLModel):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
