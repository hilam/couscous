from datetime import datetime, timezone

import pytest

from app.services.entry_service import list_recent
from app.services.search_service import search_entries
from app.services.tag_service import assign_tag
from tests.test_factory import make_entry, make_feed, make_user


def _now():
    return datetime(2024, 1, 1, 12, 0, 0)


@pytest.mark.asyncio
async def test_search_returns_relevant_results(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)

    e1 = await make_entry(
        db_session, feed.url, user.id,
        title="Machine learning basics",
        summary="An introduction to machine learning",
        published=_now(),
    )
    e2 = await make_entry(
        db_session, feed.url, user.id,
        title="Python web development",
        summary="Building web apps with Python",
        published=_now(),
    )

    results = await search_entries(db_session, "machine learning", user.id)
    assert len(results) >= 1
    assert results[0].id == e1.id


@pytest.mark.asyncio
async def test_search_no_results(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    await make_entry(db_session, feed.url, user.id, title="Hello world", published=_now())

    results = await search_entries(db_session, "xyzabc123", user.id)
    assert results == []


@pytest.mark.asyncio
async def test_search_empty_query(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)
    await make_entry(db_session, feed.url, user.id, title="Hello", published=_now())

    results = await search_entries(db_session, "   ", user.id)
    assert results == []


@pytest.mark.asyncio
async def test_search_with_category_filter(db_session):
    user = await make_user(db_session)
    feed1 = await make_feed(db_session, url="https://example.com/feed1", user_id=user.id)
    feed2 = await make_feed(db_session, url="https://example.com/feed2", user_id=user.id)

    from app.services.feed_service import update_feed_category
    from app.services.category_service import create_category

    cat = await create_category(db_session, user.id, "Tech")
    await update_feed_category(db_session, user.id, feed1.url, cat.id)

    e1 = await make_entry(
        db_session, feed1.url, user.id,
        title="Python tutorial", summary="Learn Python", published=_now(),
    )
    await make_entry(
        db_session, feed2.url, user.id,
        title="Python release", summary="Python 4.0 released", published=_now(),
    )

    results = await search_entries(db_session, "python", user.id, category_id=cat.id)
    assert len(results) == 1
    assert results[0].id == e1.id


@pytest.mark.asyncio
async def test_search_with_tag_filter(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)

    e1 = await make_entry(
        db_session, feed.url, user.id,
        title="GPT model architecture",
        summary="Deep dive into GPT",
        published=_now(),
    )
    e2 = await make_entry(
        db_session, feed.url, user.id,
        title="GPT tutorial for beginners",
        summary="Learn GPT step by step",
        published=_now(),
    )

    await assign_tag(db_session, e1.id, "ai", user.id)

    results = await search_entries(db_session, "gpt", user.id, tag="ai")
    assert len(results) == 1
    assert results[0].id == e1.id


@pytest.mark.asyncio
async def test_search_highlights_snippet(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)

    await make_entry(
        db_session, feed.url, user.id,
        title="Article about Python",
        summary="Python is a high-level programming language used for many purposes",
        published=_now(),
    )

    results = await search_entries(db_session, "python", user.id)
    assert len(results) >= 1
    assert results[0].summary is not None
    assert "<b>Python</b>" in results[0].summary or "<b>python</b>" in results[0].summary.lower()


@pytest.mark.asyncio
async def test_search_ignores_html_tags(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)

    await make_entry(
        db_session, feed.url, user.id,
        title="Web dev guide",
        content="<div class='code'>Hello world example</div>",
        published=_now(),
    )

    results = await search_entries(db_session, "hello", user.id)
    assert len(results) >= 1


@pytest.mark.asyncio
async def test_search_limits_results(db_session):
    user = await make_user(db_session)
    feed = await make_feed(db_session, user_id=user.id)

    for i in range(5):
        await make_entry(
            db_session, feed.url, user.id,
            title=f"Python tip {i}",
            summary=f"Python programming tip number {i}",
            published=_now(),
        )

    results = await search_entries(db_session, "python", user.id, limit=3)
    assert len(results) == 3
