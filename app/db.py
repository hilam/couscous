from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from database.service.config import db_type
from database.service.database import engine


@asynccontextmanager
async def get_db_session():
    if db_type == "asyncpg":
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session
    else:
        Session = sessionmaker(engine)
        session = Session()
        try:
            yield session
        finally:
            session.close()
