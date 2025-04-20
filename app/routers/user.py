from typing import Annotated

from fastapi import HTTPException, status, APIRouter, Depends
from sqlmodel import select

from app.models import user_model
from app.models.post_model import Post
from app.database import SessionDep
from app.utils.security import (
    check_user_exists,
    hash_password,
    get_current_active_user,
)

router = APIRouter(
    prefix="/v2/users",
    tags=["Users"],
)


# Create a user
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(
    user: user_model.UserCreate, session: SessionDep
) -> user_model.UserPublic:
    # Check if user already exists
    user_exists, error = check_user_exists(user, session)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    db_user = user_model.User.model_validate(user)
    db_user.password = hash_password(user.password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


# Get current user
@router.get("/me")
def get_my_profile(
    current_user: Annotated[user_model.User, Depends(get_current_active_user)],
) -> user_model.UserPublic:
    return current_user


# Get a single user
@router.get("/{id}")
def get_user_by_id(id: int, session: SessionDep) -> user_model.UserPublic:
    query = select(user_model.User).where(user_model.User.id == id)
    user = session.exec(query).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found",
        )
    return user


# Update my profile
@router.put("/me")
def update_my_profile(
    user_update: user_model.UserUpdate,
    session: SessionDep,
    current_user: Annotated[user_model.User, Depends(get_current_active_user)],
) -> user_model.UserPublic:
    user = session.get(user_model.User, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {current_user.id} not found",
        )

    # Check if the authenticated user is updating their own profile
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )

    # Convert to dict excluding unset values
    update_data = user_update.model_dump(exclude_unset=True)

    # Hash password if it's being updated
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    # Check if the user is updating their own email
    if "email" in update_data:
        # Check if the email is already taken
        email_exists, error = check_user_exists(update_data["email"], session)
        if email_exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
            
    # Check if the user is updating their username
    if "username" in update_data:
        # Check if the username is already taken by another user
        query = select(user_model.User).where(
            (user_model.User.username == update_data["username"]) & 
            (user_model.User.id != user.id)
        )
        existing_user = session.exec(query).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="User with this username already exists"
            )

    # Only update fields that were provided
    for key, value in update_data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


# Delete my profile
@router.delete("/me")
def delete_my_profile(
    session: SessionDep,
    current_user: Annotated[user_model.User, Depends(get_current_active_user)],
) -> user_model.UserPublic:
    user = session.get(user_model.User, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {current_user.id} not found",
        )

    # First delete all posts by this user to maintain referential integrity
    query = select(Post).where(Post.author_id == user.id)
    posts = session.exec(query).all()
    for post in posts:
        session.delete(post)
    
    # Then delete the user
    session.delete(user)
    session.commit()

    return user
