from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, delete, func  # type: ignore[attr-defined]

from database.models.couscous import Entry


async def count_entries_older_than(
    session: AsyncSession, user_id: int, days: int
) -> int:
    """Count entries older than `days` for a user, excluding important ones."""
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=days)
    stmt = select(func.count(Entry.id)).where(
        Entry.user_id == user_id,
        Entry.important == 0,
        Entry.first_updated_epoch < cutoff,
    )
    result = await session.execute(stmt)
    return result.scalar_one()


async def purge_older_than(
    session: AsyncSession, user_id: int, days: int
) -> int:
    """Remove entries older than `days` for a user, excluding important ones.

    Returns the number of entries removed.
    EntryTag rows are deleted in cascade via FK ondelete=CASCADE.
    """
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=days)

    # Count first so we can return the number
    count = await count_entries_older_than(session, user_id, days)
    if count == 0:
        return 0

    stmt = delete(Entry).where(
        Entry.user_id == user_id,
        Entry.important == 0,
        Entry.first_updated_epoch < cutoff,
    )
    await session.execute(stmt)
    await session.commit()
    return count
