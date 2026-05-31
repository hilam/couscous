from sqlmodel import select

from database.models.couscous import Feed


async def list_feeds(session):
    result = session.execute(select(Feed))
    return result.scalars().all()


async def add_feed(session, url: str):
    existing = session.execute(select(Feed).where(Feed.url == url)).scalar_one_or_none()
    if existing:
        msg = "Feed já cadastrado"
        raise ValueError(msg)

    new_feed = Feed(url=url)
    session.add(new_feed)
    session.commit()
    session.refresh(new_feed)
    return new_feed


async def remove_feed(session, url: str):
    feed = session.execute(select(Feed).where(Feed.url == url)).scalar_one_or_none()
    if feed:
        session.delete(feed)
        session.commit()
