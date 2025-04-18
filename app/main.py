import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.database import engine
from app.routers import post, user, auth


# Load the environment variables
load_dotenv()


# Create the database and tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


# Initialize the FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title=os.getenv("TITLE"),
    version=os.getenv("VERSION"),
    summary=os.getenv("SUMMARY"),
    description=os.getenv("DESCRIPTION"),
    contact=os.getenv("CONTACT"),
    license_info=os.getenv("LICENSE_INFO"),
)


# Add CORS middleware
origins = os.getenv("ALLOWED_ORIGINS").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


########################## Routers ##########################

app.include_router(user.router)
app.include_router(post.router)
app.include_router(auth.router)


# Root route for testing
# @app.get("/", tags=["Root"])
# def read_root():
#     return {
#         "message": "API is running",
#         "version": app.version,
#         "python_version": sys.version,
#         "platform": platform.platform(),
#         "fastapi_version": fastapi_version,
#     }
