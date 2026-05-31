import pytest
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine
from sqlmodel import Session

load_dotenv()


@pytest.fixture
def db_session():
    engine = create_engine("sqlite://", echo=False)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
