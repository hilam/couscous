from sqlmodel import select

from database.models.couscous import Feed


async def list_feeds(session):
    result = await session.execute(select(Feed))
    return result.scalars().all()


async def add_feed(session, url: str):
    existing = (
        await session.execute(select(Feed).where(Feed.url == url))
    ).scalar_one_or_none()
    if existing:
        msg = "Feed já cadastrado"
        raise ValueError(msg)

    new_feed = Feed(url=url)
    session.add(new_feed)
    await session.commit()
    await session.refresh(new_feed)
    return new_feed


async def remove_feed(session, url: str):
    feed = (
        await session.execute(select(Feed).where(Feed.url == url))
    ).scalar_one_or_none()
    if feed:
        await session.delete(feed)
        await session.commit()
