from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from database.service.config import db_type, DB_URL

engine = create_async_engine(DB_URL) if db_type == 'asyncpg' else create_engine(DB_URL)


def init_db():
    with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        SQLModel.metadata.create_all()


async def init_async_db():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    if db_type == 'asyncpg':
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session
    else:
        session = sessionmaker(engine)
        yield session
