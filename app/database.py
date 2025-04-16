from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine


POSTGRES_URL = "postgresql://bloguser:blogpassword@localhost:5432/blogdb"

engine = create_engine(POSTGRES_URL)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
