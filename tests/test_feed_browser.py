"""Testes para feed_browser.py — operações do ExploreState."""
import pytest

from app.services.category_service import create_category
from app.services.feed_browser import (
    ExploreState,
    clear_tags,
    load,
    search,
    select_category,
    toggle_tag,
)
from app.services.feed_service import update_feed_category
from app.services.tag_service import assign_tag
from tests.test_factory import make_user, create_feed_and_entry


# ── load() ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_load_empty(db_session):
    user = await make_user(db_session)
    state = await load(db_session, user.id)
    assert state.entries == []
    assert state.tree == []
    assert state.tag_counts == []
    assert state.selected_category_id is None
    assert state.selected_tags == set()
    assert state.is_searching is False


@pytest.mark.asyncio
async def test_load_with_entries(db_session):
    user = await make_user(db_session)
    await create_feed_and_entry(db_session, user.id, "https://example.com/rss1")
    await create_feed_and_entry(db_session, user.id, "https://example.com/rss2")

    state = await load(db_session, user.id)
    assert len(state.entries) == 2
    assert state.tag_map == {}


@pytest.mark.asyncio
async def test_load_with_categories(db_session):
    user = await make_user(db_session)
    parent = await create_category(db_session, user.id, "Pais")
    child = await create_category(db_session, user.id, "Filha", parent_id=parent.id)

    feed1, _ = await create_feed_and_entry(db_session, user.id, "https://example.com/rss1")
    feed2, _ = await create_feed_and_entry(db_session, user.id, "https://example.com/rss2")
    await update_feed_category(db_session, user.id, feed1.url, parent.id)
    await update_feed_category(db_session, user.id, feed2.url, child.id)

    state = await load(db_session, user.id)
    assert len(state.tree) == 1
    assert state.tree[0]["name"] == "Pais"
    assert state.tree[0]["total_feed_count"] == 2
    assert len(state.tree[0]["children"]) == 1
    assert state.tree[0]["children"][0]["name"] == "Filha"


# ── select_category() ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_select_category_filters_entries(db_session):
    user = await make_user(db_session)
    cat_a = await create_category(db_session, user.id, "CatA")
    cat_b = await create_category(db_session, user.id, "CatB")

    feed_a, _ = await create_feed_and_entry(db_session, user.id, "https://example.com/a")
    feed_b, _ = await create_feed_and_entry(db_session, user.id, "https://example.com/b")
    await update_feed_category(db_session, user.id, feed_a.url, cat_a.id)
    await update_feed_category(db_session, user.id, feed_b.url, cat_b.id)

    state = await load(db_session, user.id)
    assert len(state.entries) == 2

    state = await select_category(db_session, state, cat_a.id, user.id)
    assert state.selected_category_id == cat_a.id
    assert len(state.entries) == 1


@pytest.mark.asyncio
async def test_select_category_with_subcategories(db_session):
    user = await make_user(db_session)
    parent = await create_category(db_session, user.id, "Parent")
    child = await create_category(db_session, user.id, "Child", parent_id=parent.id)

    feed_p, _ = await create_feed_and_entry(db_session, user.id, "https://example.com/p")
    feed_c, _ = await create_feed_and_entry(db_session, user.id, "https://example.com/c")
    await update_feed_category(db_session, user.id, feed_p.url, parent.id)
    await update_feed_category(db_session, user.id, feed_c.url, child.id)

    state = await load(db_session, user.id)
    state = await select_category(db_session, state, parent.id, user.id)
    assert len(state.entries) == 2  # parent + child


@pytest.mark.asyncio
async def test_select_category_expands_and_collapses(db_session):
    user = await make_user(db_session)
    parent = await create_category(db_session, user.id, "Parent")
    child = await create_category(db_session, user.id, "Child", parent_id=parent.id)

    feed, _ = await create_feed_and_entry(db_session, user.id, "https://example.com/p")
    await update_feed_category(db_session, user.id, feed.url, child.id)

    state = await load(db_session, user.id)
    state = await select_category(db_session, state, parent.id, user.id)
    assert parent.id in state.expanded_ids  # expandiu

    state = await select_category(db_session, state, parent.id, user.id)
    assert parent.id not in state.expanded_ids  # recolheu


# ── toggle_tag() e clear_tags() ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_toggle_tag_adds_and_removes(db_session):
    user = await make_user(db_session)
    feed, entry = await create_feed_and_entry(db_session, user.id)
    await assign_tag(db_session, entry.id, "python", user.id)

    state = await load(db_session, user.id)
    assert "python" not in state.selected_tags

    state = await toggle_tag(db_session, state, "python", user.id)
    assert "python" in state.selected_tags

    state = await toggle_tag(db_session, state, "python", user.id)
    assert "python" not in state.selected_tags


@pytest.mark.asyncio
async def test_toggle_tag_filters_entries(db_session):
    user = await make_user(db_session)
    feed1, entry1 = await create_feed_and_entry(db_session, user.id, "https://example.com/1")
    feed2, entry2 = await create_feed_and_entry(db_session, user.id, "https://example.com/2")
    await assign_tag(db_session, entry1.id, "python", user.id)

    state = await load(db_session, user.id)
    assert len(state.entries) == 2

    state = await toggle_tag(db_session, state, "python", user.id)
    assert len(state.entries) == 1


@pytest.mark.asyncio
async def test_clear_tags_removes_all(db_session):
    user = await make_user(db_session)
    feed, entry = await create_feed_and_entry(db_session, user.id)
    await assign_tag(db_session, entry.id, "python", user.id)

    state = await load(db_session, user.id)
    state = await toggle_tag(db_session, state, "python", user.id)
    assert "python" in state.selected_tags

    state = await clear_tags(db_session, state, user.id)
    assert state.selected_tags == set()
    assert len(state.entries) >= 1


# ── search() ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_finds_entries(db_session):
    user = await make_user(db_session)
    await create_feed_and_entry(
        db_session,
        user.id,
        url="https://example.com/ml",
        title="Machine learning basics",
        link="https://example.com/ml",
    )
    await create_feed_and_entry(
        db_session,
        user.id,
        url="https://example.com/cooking",
        title="Cooking 101",
        link="https://example.com/cooking",
    )

    state = await load(db_session, user.id)
    state = await search(db_session, state, "machine", user.id)
    assert state.is_searching is True
    assert len(state.entries) == 1
    assert "machine" in state.entries[0].title.lower()


@pytest.mark.asyncio
async def test_search_empty_query_clears(db_session):
    user = await make_user(db_session)
    feed, entry = await create_feed_and_entry(db_session, user.id)

    state = await load(db_session, user.id)
    state = await search(db_session, state, "machine", user.id)
    assert state.is_searching is True

    state = await search(db_session, state, "", user.id)
    assert state.is_searching is False
