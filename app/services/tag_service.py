from sqlalchemy import func
from sqlmodel import select

from database.models.couscous import Entry, EntryTag


async def get_tags_for_entry(session, entry_id: int) -> list[str]:
    result = await session.execute(
        select(EntryTag.tag).where(EntryTag.entry_id == entry_id).order_by(EntryTag.tag)
    )
    return list(result.scalars().all())


async def get_distinct_tags(session, user_id: int) -> list[str]:
    result = await session.execute(
        select(EntryTag.tag)
        .where(EntryTag.user_id == user_id)
        .distinct()
        .order_by(EntryTag.tag)
    )
    return list(result.scalars().all())


async def get_distinct_tags_for_feed(session, feed_url: str, user_id: int) -> list[str]:
    feed_entry_ids = select(Entry.id).where(
        Entry.feed == feed_url, Entry.user_id == user_id
    )
    result = await session.execute(
        select(EntryTag.tag)
        .where(
            EntryTag.user_id == user_id,
            EntryTag.entry_id.in_(feed_entry_ids),  # type: ignore[attr-defined]
        )
        .distinct()
        .order_by(EntryTag.tag)
    )
    return list(result.scalars().all())


async def assign_tag(session, entry_id: int, tag: str, user_id: int) -> None:
    tag = tag.strip().lower()
    if not tag:
        return
    existing = await session.execute(
        select(EntryTag).where(EntryTag.entry_id == entry_id, EntryTag.tag == tag)
    )
    if existing.scalar_one_or_none():
        return
    entry_tag = EntryTag(entry_id=entry_id, tag=tag, user_id=user_id)
    session.add(entry_tag)
    await session.commit()


async def remove_tag(session, entry_id: int, tag: str, user_id: int) -> None:
    tag = tag.strip().lower()
    existing = await session.execute(
        select(EntryTag).where(
            EntryTag.entry_id == entry_id,
            EntryTag.tag == tag,
            EntryTag.user_id == user_id,
        )
    )
    entry_tag = existing.scalar_one_or_none()
    if entry_tag:
        await session.delete(entry_tag)
        await session.commit()


async def get_distinct_tags_with_counts(session, user_id: int) -> list[tuple[str, int]]:
    result = await session.execute(
        select(EntryTag.tag, func.count(EntryTag.entry_id))  # type: ignore[arg-type]
        .where(EntryTag.user_id == user_id)
        .group_by(EntryTag.tag)
        .order_by(EntryTag.tag)
    )
    return [(row[0], row[1]) for row in result.all()]


async def delete_tag(session, tag: str, user_id: int) -> None:
    tag = tag.strip().lower()
    result = await session.execute(
        select(EntryTag).where(EntryTag.tag == tag, EntryTag.user_id == user_id)
    )
    for entry_tag in result.scalars().all():
        await session.delete(entry_tag)
    await session.commit()
