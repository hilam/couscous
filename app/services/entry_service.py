from sqlmodel import desc, select

from database.models.couscous import Entry


async def list_entries(
    session,
    feed_url: str,
    *,
    user_id: int | None = None,
    unread_only: bool = False,
    important_only: bool = False,
):
    query = select(Entry).where(Entry.feed == feed_url)
    if user_id is not None:
        query = query.where(Entry.user_id == user_id)
    if unread_only:
        query = query.where(Entry.read == 0)
    if important_only:
        query = query.where(Entry.important == 1)
    query = query.order_by(desc(Entry.published))
    result = await session.execute(query)
    return result.scalars().all()


async def get_entry(session, entry_id: int):
    result = await session.execute(select(Entry).where(Entry.id == entry_id))
    return result.scalar_one_or_none()


async def mark_read(session, entry_id: int, user_id: int, *, read: bool = True):
    entry = (
        await session.execute(
            select(Entry).where(Entry.id == entry_id, Entry.user_id == user_id)
        )
    ).scalar_one_or_none()
    if entry:
        entry.read = 1 if read else 0
        await session.commit()


async def mark_important(
    session, entry_id: int, user_id: int, *, important: bool = True
):
    entry = (
        await session.execute(
            select(Entry).where(Entry.id == entry_id, Entry.user_id == user_id)
        )
    ).scalar_one_or_none()
    if entry:
        entry.important = 1 if important else 0
        await session.commit()


async def get_unread_count(session, user_id: int) -> int:
    result = await session.execute(
        select(Entry).where(Entry.user_id == user_id, Entry.read == 0)
    )
    return len(result.scalars().all())
