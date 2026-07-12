import os

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

host = os.getenv("COUSCOUS_DATABASE_HOST", "localhost")
port = os.getenv("COUSCOUS_DATABASE_PORT", "5432")
user = os.getenv("COUSCOUS_DATABASE_USER", "couscous")
password = os.getenv("COUSCOUS_DATABASE_PASS", "couscous")

DB_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/couscous_test"


async def _add_search_vector_column(conn):
    """Add search_vector generated column (managed by PostgreSQL, not SQLModel)."""
    await conn.execute(text("""
        ALTER TABLE entries ADD COLUMN IF NOT EXISTS search_vector tsvector
          GENERATED ALWAYS AS (
            to_tsvector('simple',
              regexp_replace(
                coalesce(title, '') || ' ' ||
                coalesce(summary, '') || ' ' ||
                coalesce(content, ''),
                '<[^>]+>', '', 'g'
              )
            )
          ) STORED;
    """))
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_entries_search_vector_test
        ON entries USING GIN (search_vector);
    """))
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_entries_user_published_test
        ON entries (user_id, published DESC);
    """))


from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def page_context():
    """Fixture que cria um PageContext com session e _session_factory mockados."""
    from app.context import PageContext
    from app.state import State

    page = MagicMock()
    state = State()
    session = AsyncMock()
    session_factory = MagicMock()

    ctx = PageContext(
        page=page,
        state=state,
        session=session,
        _session_factory=session_factory,
    )
    return ctx


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
    async with engine.begin() as conn:
        await _add_search_vector_column(conn)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()
