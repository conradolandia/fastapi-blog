import os
import passlib.exc
from typing import Annotated
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import select

from app.models.user_model import User, TokenData, UserCreate
from app.database import SessionDep


# Initialize the password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v2/auth/token")


# hash password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# create access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM")
    )
    return encoded_jwt


# check if user exists
def check_user_exists(
    user: UserCreate, session: SessionDep
) -> tuple[bool, str | None]:
    # Check both email and username in a single query
    query = select(User).where(
        (User.email == user.email)
        | (User.username == user.username)
    )
    existing_user = session.exec(query).first()

    if existing_user:
        error = (
            "User with this email already exists"
            if existing_user.email == user.email
            else "User with this username already exists"
        )
        return True, error
    return False, None


# get current user
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = get_user(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# get current active user
def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# get user
def get_user(session: SessionDep, username: str):
    query = select(User).where(
        (User.username == username) | (User.email == username)
    )
    return session.exec(query).first()


# authenticate user
def authenticate_user(session: SessionDep, username: str, password: str):
    user = get_user(session, username)
    if not user:
        return False
    
    if verify_password(password, user.password):
        return user
    
    return False
