import pytest
from datetime import datetime, timedelta, timezone

from app.services.cleanup_service import count_entries_older_than, purge_older_than
from database.models.couscous import Entry, EntryTag
from tests.test_factory import make_user, make_feed, create_feed_and_entry, make_entry


async def _entry(user_id, session, **overrides):
    """Create a feed + entry, always with a unique feed URL to avoid PK conflict."""
    import uuid
    url = f"https://example.com/feed-{uuid.uuid4().hex[:8]}"
    await make_feed(session, url=url, user_id=user_id)
    return await make_entry(session, feed_url=url, user_id=user_id, **overrides)


@pytest.mark.asyncio
async def test_count_entries_older_than_returns_count(db_session):
    user = await make_user(db_session)
    await _entry(user.id, db_session, link="https://example.com/a1")
    await _entry(user.id, db_session, link="https://example.com/a2")

    count = await count_entries_older_than(db_session, user.id, days=1)
    assert count == 0


@pytest.mark.asyncio
async def test_count_entries_older_than_counts_old_entries(db_session):
    user = await make_user(db_session)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old_time = now - timedelta(days=100)

    await _entry(user.id, db_session,
                 first_updated=old_time, first_updated_epoch=old_time,
                 link="https://example.com/old1")
    await _entry(user.id, db_session,
                 first_updated=now - timedelta(days=1),
                 first_updated_epoch=now - timedelta(days=1),
                 link="https://example.com/recent1")

    count = await count_entries_older_than(db_session, user.id, days=30)
    assert count == 1


@pytest.mark.asyncio
async def test_count_excludes_important(db_session):
    user = await make_user(db_session)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old_time = now - timedelta(days=100)

    await _entry(user.id, db_session,
                 first_updated=old_time, first_updated_epoch=old_time,
                 link="https://example.com/imp", important=1)
    await _entry(user.id, db_session,
                 first_updated=old_time, first_updated_epoch=old_time,
                 link="https://example.com/notimp", important=0)

    assert await count_entries_older_than(db_session, user.id, days=30) == 1


@pytest.mark.asyncio
async def test_count_is_scoped_to_user(db_session):
    u1 = await make_user(db_session, name="u1")
    u2 = await make_user(db_session, name="u2")
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=100)

    await _entry(u1.id, db_session,
                 first_updated=old, first_updated_epoch=old,
                 link="https://example.com/u1")
    await _entry(u2.id, db_session,
                 first_updated=old, first_updated_epoch=old,
                 link="https://example.com/u2")

    assert await count_entries_older_than(db_session, u1.id, days=30) == 1
    assert await count_entries_older_than(db_session, u2.id, days=30) == 1


@pytest.mark.asyncio
async def test_purge_removes_only_old_entries(db_session):
    user = await make_user(db_session)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=100)

    await _entry(user.id, db_session,
                 first_updated=old, first_updated_epoch=old,
                 link="https://example.com/old1")
    await _entry(user.id, db_session,
                 first_updated=now, first_updated_epoch=now,
                 link="https://example.com/recent1")

    assert await purge_older_than(db_session, user.id, days=30) == 1

    from sqlmodel import select
    remaining = (await db_session.execute(select(Entry))).scalars().all()
    assert len(remaining) == 1
    assert remaining[0].link == "https://example.com/recent1"


@pytest.mark.asyncio
async def test_purge_preserves_important(db_session):
    user = await make_user(db_session)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=100)

    await _entry(user.id, db_session,
                 first_updated=old, first_updated_epoch=old,
                 link="https://example.com/imp", important=1)
    await _entry(user.id, db_session,
                 first_updated=old, first_updated_epoch=old,
                 link="https://example.com/notimp", important=0)

    assert await purge_older_than(db_session, user.id, days=30) == 1

    from sqlmodel import select
    remaining = (await db_session.execute(select(Entry))).scalars().all()
    assert len(remaining) == 1
    assert remaining[0].link == "https://example.com/imp"


@pytest.mark.asyncio
async def test_purge_cascades_tags(db_session):
    user = await make_user(db_session)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=100)

    _, entry = await create_feed_and_entry(db_session, user_id=user.id,
        first_updated=old, first_updated_epoch=old)

    await db_session.execute(
        EntryTag.__table__.insert().values(
            entry_id=entry.id, tag="python", user_id=user.id
        )
    )
    await db_session.commit()

    assert await purge_older_than(db_session, user.id, days=30) == 1

    from sqlmodel import select
    assert len((await db_session.execute(select(EntryTag))).scalars().all()) == 0


@pytest.mark.asyncio
async def test_purge_scoped_to_user(db_session):
    u1 = await make_user(db_session, name="u1")
    u2 = await make_user(db_session, name="u2")
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=100)

    await _entry(u1.id, db_session,
                 first_updated=old, first_updated_epoch=old,
                 link="https://example.com/u1old")
    await _entry(u2.id, db_session,
                 first_updated=old, first_updated_epoch=old,
                 link="https://example.com/u2old")

    assert await purge_older_than(db_session, u1.id, days=30) == 1
    from sqlmodel import select
    remaining = (await db_session.execute(select(Entry))).scalars().all()
    assert len(remaining) == 1
    assert remaining[0].link == "https://example.com/u2old"


@pytest.mark.asyncio
async def test_purge_returns_zero_when_nothing(db_session):
    user = await make_user(db_session)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    await _entry(user.id, db_session,
                 first_updated=now, first_updated_epoch=now,
                 link="https://example.com/recent")
    assert await purge_older_than(db_session, user.id, days=1) == 0
