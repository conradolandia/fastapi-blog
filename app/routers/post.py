from typing import Annotated
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
@router.get("/")
def get_posts(session: SessionDep) -> list[post_model.PostPublic]:
    query = select(post_model.Post)
    posts = session.exec(query).all()
    return posts


# Get a single post
@router.get("/{id}")
def get_post_by_id(id: int, session: SessionDep) -> post_model.PostPublic:
    query = select(post_model.Post).where(post_model.Post.id == id)
    post = session.exec(query).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    return post


# Get latest post
@router.get("/latest")
def get_latest_post(session: SessionDep) -> post_model.PostPublic:
    query = select(post_model.Post).order_by(post_model.Post.created_at.desc()).limit(1)
    post = session.exec(query).first()
    return post


# Create a post
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: post_model.PostCreate,
    session: SessionDep,
    current_user: Annotated[user_model.User, Depends(get_current_active_user)],
) -> post_model.PostPublic:
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
@router.delete("/{id}")
def delete_post(
    id: int,
    session: SessionDep,
    current_user: Annotated[user_model.User, Depends(get_current_active_user)],
) -> post_model.PostPublic:
    user = session.get(user_model.User, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    post = session.get(post_model.Post, id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    session.delete(post)
    session.commit()
    return post


# Update a post
@router.put("/{id}")
def update_post(
    id: int, post_update: post_model.PostUpdate, session: SessionDep,
    current_user: Annotated[user_model.User, Depends(get_current_active_user)],
) -> post_model.PostPublic:
    user = session.get(user_model.User, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    post = session.get(post_model.Post, id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )

    # Convert to dict excluding unset values
    update_data = post_update.model_dump(exclude_unset=True)

    # Only update fields that were provided
    for key, value in update_data.items():
        setattr(post, key, value)

    session.add(post)
    session.commit()
    session.refresh(post)

    return post
