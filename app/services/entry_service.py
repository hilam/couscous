from sqlmodel import desc, select

from database.models.couscous import Entry


async def list_entries(session, feed_url: str):
    result = await session.execute(
        select(Entry).where(Entry.feed == feed_url).order_by(desc(Entry.published))
    )
    return result.scalars().all()


async def get_entry(session, entry_id: int):
    result = await session.execute(select(Entry).where(Entry.id == entry_id))
    return result.scalar_one_or_none()


async def mark_read(session, entry_id: int, *, read: bool = True):
    entry = (
        await session.execute(select(Entry).where(Entry.id == entry_id))
    ).scalar_one_or_none()
    if entry:
        entry.read = 1 if read else 0
        await session.commit()


async def mark_important(session, entry_id: int, *, important: bool = True):
    entry = (
        await session.execute(select(Entry).where(Entry.id == entry_id))
    ).scalar_one_or_none()
    if entry:
        entry.important = 1 if important else 0
        await session.commit()
