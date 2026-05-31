from collections.abc import AsyncGenerator
from typing import cast

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from database.service.config import DB_URL, db_type

engine = create_async_engine(DB_URL) if db_type == "asyncpg" else create_engine(DB_URL)


def init_db():
    from database.models import couscous  # noqa: F401

    if isinstance(engine, AsyncEngine):
        msg = "init_db() requires sync engine, use init_async_db() for async"
        raise TypeError(msg)
    with engine.begin() as conn:
        SQLModel.metadata.create_all(bind=conn)


async def init_async_db():
    if not isinstance(engine, AsyncEngine):
        msg = "init_async_db() requires async engine"
        raise TypeError(msg)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession]:
    if isinstance(engine, AsyncEngine):
        async_session = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session
    else:
        sync_session = sessionmaker(engine)
        with sync_session() as session:
            yield cast("AsyncSession", session)
