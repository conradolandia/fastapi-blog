import os
from dotenv import load_dotenv
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

from app.models.settings_model import settings


load_dotenv()


engine = create_engine(settings.postgres_url)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
