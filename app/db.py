from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import cast

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from database.service.database import engine


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession]:
    if isinstance(engine, AsyncEngine):
        async_session = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session
    else:
        sync_session = sessionmaker(engine)
        session = cast("AsyncSession", sync_session())
        try:
            yield session
        finally:
            await session.close()
