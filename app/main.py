from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from sqlmodel import SQLModel, select
from pydantic import BaseModel

from .models.post import Post
from .database import SessionDep, engine


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


########################## Models ##########################


# Post model for updates
class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    published: bool | None = None


########################## Routes ##########################


# Root route
@app.get("/")
def read_root():
    return {"message": "Blog API is running"}


# Get all posts
@app.get("/v2/posts")
def get_posts(session: SessionDep) -> list[Post]:
    model = select(Post)
    posts = session.exec(model).all()
    return posts


# Get a single post
@app.get("/v2/posts/{id}")
def get_post_by_id(id: int, session: SessionDep) -> Post:
    model = select(Post).where(Post.id == id)
    post = session.exec(model).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    return post


# Get latest post
@app.get("/v2/posts/latest")
def get_latest_post(session: SessionDep) -> Post:
    model = select(Post).order_by(Post.created_at.desc()).limit(1)
    post = session.exec(model).first()
    return post


# Create a post
@app.post("/v2/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post, session: SessionDep) -> dict:
    session.add(post)
    session.commit()
    session.refresh(post)
    return {
        "status": "success",
        "message": f"Post {post.id} created successfully",
        "data": post,
    }


# Delete a post
@app.delete("/v2/posts/{id}", status_code=status.HTTP_201_CREATED)
def delete_post(id: int, session: SessionDep) -> dict:
    post = session.get(Post, id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    session.delete(post)
    session.commit()
    session.refresh(post)
    return {
        "status": "success",
        "message": f"Post {id} deleted successfully",
        "data": post,
    }


# Update a post
@app.put("/v2/posts/{id}")
def update_post(id: int, post_update: PostUpdate, session: SessionDep) -> dict:
    post_query = session.get(Post, id)
    if not post_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )

    # Convert to dict excluding unset values
    update_data = post_update.model_dump(exclude_unset=True)

    # Only update fields that were provided
    for key, value in update_data.items():
        setattr(post_query, key, value)

    session.add(post_query)
    session.commit()
    session.refresh(post_query)

    return {
        "status": "success",
        "message": f"Post {id} updated successfully",
        "data": post_query,
    }
