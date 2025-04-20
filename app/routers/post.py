from typing import Annotated, List
from datetime import datetime, timezone
from fastapi import HTTPException, status, APIRouter, Depends
from sqlmodel import select

from app.models import post_model, user_model
from app.database import SessionDep
from app.utils.security import get_current_active_user


router = APIRouter(
    prefix="/v2/posts",
    tags=["Posts"],
)


# Get all posts
@router.get("/", response_model=List[post_model.PostPublic])
def get_posts(session: SessionDep, limit: int = 10, skip: int = 0, search: str | None = None):
    query = select(post_model.Post).offset(skip).limit(limit)
    if search:
        query = query.where(post_model.Post.title.ilike(f"%{search}%"))
    posts = session.exec(query).all()
    return posts


# Get latest post - must come before /{id} route
@router.get("/latest", response_model=post_model.PostPublic)
def get_latest_post(session: SessionDep):
    query = select(post_model.Post).order_by(post_model.Post.created_at.desc()).limit(1)
    post = session.exec(query).first()
    return post


# Get a single post
@router.get("/{id}", response_model=post_model.PostPublic)
def get_post_by_id(id: int, session: SessionDep):
    query = select(post_model.Post).where(post_model.Post.id == id)
    post = session.exec(query).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    return post


# Create a post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=post_model.PostPublic)
def create_post(
    post_data: post_model.PostCreate,
    session: SessionDep,
    current_user: Annotated[user_model.User, Depends(get_current_active_user)],
):
    user = session.get(user_model.User, current_user.id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Set the author_id to the current user's ID
    db_post = post_model.Post.model_validate(post_data)
    db_post.author_id = user.id
    
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


# Delete a post
@router.delete("/{id}", response_model=post_model.PostPublic)
def delete_post(
    id: int,
    session: SessionDep,
    current_user: Annotated[user_model.User, Depends(get_current_active_user)],
):
    user = session.get(user_model.User, current_user.id)
    post = session.get(post_model.Post, id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    if post.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User {user.id} is not the author of this post",
        )
    
    session.delete(post)
    session.commit()
    return post


# Update a post
@router.put("/{id}", response_model=post_model.PostPublic)
def update_post(
    id: int, post_update: post_model.PostUpdate, session: SessionDep,
    current_user: Annotated[user_model.User, Depends(get_current_active_user)],
):
    user = session.get(user_model.User, current_user.id)
    post = session.get(post_model.Post, id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    if post.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User {user.id} is not the author of this post",
        )

    # Convert to dict excluding unset values
    update_data = post_update.model_dump(exclude_unset=True)

    # Only update fields that were provided
    for key, value in update_data.items():
        setattr(post, key, value)
    post.updated_at = datetime.now(timezone.utc)
    session.add(post)
    session.commit()
    session.refresh(post)
    return post
