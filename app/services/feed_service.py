from sqlmodel import select

from database.models.couscous import Feed


async def list_feeds(session, user_id: int):
    result = await session.execute(
        select(Feed).where(Feed.user_id == user_id)
    )
    return result.scalars().all()


async def add_feed(session, user_id: int, url: str):
    existing = (
        await session.execute(
            select(Feed).where(Feed.url == url, Feed.user_id == user_id)
        )
    ).scalar_one_or_none()
    if existing:
        msg = "Feed já cadastrado"
        raise ValueError(msg)

    new_feed = Feed(url=url, user_id=user_id)
    session.add(new_feed)
    await session.commit()
    await session.refresh(new_feed)
    return new_feed


async def remove_feed(session, user_id: int, url: str):
    feed = (
        await session.execute(
            select(Feed).where(Feed.url == url, Feed.user_id == user_id)
        )
    ).scalar_one_or_none()
    if feed:
        await session.delete(feed)
        await session.commit()
