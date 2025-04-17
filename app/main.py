from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from sqlmodel import SQLModel, select

from .models.post import Post, PostPublic, PostUpdate, PostCreate
from .models.user import User, UserPublic, UserUpdate, UserCreate

from .database import SessionDep, engine


# Create the database and tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


# Initialize the FastAPI app
app = FastAPI(lifespan=lifespan)


########################## Routes ##########################


# Root route
@app.get("/")
def read_root():
    return {"message": "Blog API is running"}


# Get all posts
@app.get("/v2/posts")
def get_posts(session: SessionDep) -> list[PostPublic]:
    query = select(Post)
    posts = session.exec(query).all()
    return posts


# Get a single post
@app.get("/v2/posts/{id}")
def get_post_by_id(id: int, session: SessionDep) -> PostPublic:
    query = select(Post).where(Post.id == id)
    post = session.exec(query).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    return post


# Get latest post
@app.get("/v2/posts/latest")
def get_latest_post(session: SessionDep) -> PostPublic:
    query = select(Post).order_by(Post.created_at.desc()).limit(1)
    post = session.exec(query).first()
    return post


# Create a post
@app.post("/v2/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, session: SessionDep) -> PostPublic:
    db_post = Post.model_validate(post)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


# Delete a post
@app.delete("/v2/posts/{id}")
def delete_post(id: int, session: SessionDep) -> PostPublic:
    post = session.get(Post, id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    session.delete(post)
    session.commit()
    return post


# Update a post
@app.put("/v2/posts/{id}")
def update_post(id: int, post_update: PostUpdate, session: SessionDep) -> PostPublic:
    post = session.get(Post, id)
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
