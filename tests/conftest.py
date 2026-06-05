import os

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

host = os.getenv("COUSCOUS_DATABASE_HOST", "localhost")
port = os.getenv("COUSCOUS_DATABASE_PORT", "5432")
user = os.getenv("COUSCOUS_DATABASE_USER", "couscous")
password = os.getenv("COUSCOUS_DATABASE_PASS", "couscous")

DB_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/couscous_test"


@pytest.fixture
def mock_oauth_config(monkeypatch):
    import app.services.oauth_service as oauth_svc

    monkeypatch.setattr(oauth_svc, "GOOGLE_CLIENT_ID", "test-google-id")
    monkeypatch.setattr(oauth_svc, "GOOGLE_CLIENT_SECRET", "test-google-secret")
    monkeypatch.setattr(oauth_svc, "GITHUB_CLIENT_ID", "test-github-id")
    monkeypatch.setattr(oauth_svc, "GITHUB_CLIENT_SECRET", "test-github-secret")


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()
