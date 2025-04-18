import os
from dotenv import load_dotenv
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine


load_dotenv()


engine = create_engine(os.getenv("POSTGRES_URL"))


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
