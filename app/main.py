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


# check if user exists
def check_user_exists(user: UserCreate, session: SessionDep) -> bool:
    query = select(User).where(User.email == user.email)
    existing_user = session.exec(query).first()
    if existing_user:
        error = "User with this email already exists"
        return True, error
    query = select(User).where(User.username == user.username)
    existing_user = session.exec(query).first()
    if existing_user:
        error = "User with this username already exists"
        return True, error
    return False, None


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


# Create a user
@app.post("/v2/users", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: SessionDep) -> UserPublic:
    # Check if user already exists
    user_exists, error = check_user_exists(user, session)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


# Get all users
@app.get("/v2/users")
def get_users(session: SessionDep) -> list[UserPublic]:
    query = select(User)
    users = session.exec(query).all()
    return users


# Get a single user
@app.get("/v2/users/{id}")
def get_user_by_id(id: int, session: SessionDep) -> UserPublic:
    query = select(User).where(User.id == id)
    user = session.exec(query).first()
    return user


# Update an user
@app.put("/v2/users/{id}")
def update_user(id: int, user_update: UserUpdate, session: SessionDep) -> UserPublic:
    user = session.get(User, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found",
        )

    # Convert to dict excluding unset values
    update_data = user_update.model_dump(exclude_unset=True)

    # Only update fields that were provided
    for key, value in update_data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


# Delete an user
@app.delete("/v2/users/{id}")
def delete_user(id: int, session: SessionDep) -> UserPublic:
    user = session.get(User, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found",
        )
    session.delete(user)
    session.commit()
    return user
