"""Testes para feed_browser.py — operações do ExploreState."""
from datetime import datetime, timedelta

import pytest

from app.services.category_service import create_category
from app.services.feed_browser import (
    ExploreState,
    clear_tags,
    load,
    load_more,
    search,
    select_category,
    toggle_tag,
)
from app.services.feed_service import update_feed_category
from app.services.tag_service import assign_tag
from database.models.couscous import EntryTag
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


# ── paginação keyset (load_more) ─────────────────────────────────────────────


async def _make_60_recent(db_session, user_id, base=None):
    base = base or datetime(2024, 1, 1)
    created = []
    for i in range(60):
        _, entry = await create_feed_and_entry(
            db_session,
            user_id,
            url=f"https://example.com/f{i}",
            link=f"https://example.com/a{i}",
            title=f"Article {i}",
            published=base + timedelta(minutes=i),
        )
        created.append(entry)
    return created


@pytest.mark.asyncio
async def test_load_accumulates_cursor_and_has_more(db_session):
    user = await make_user(db_session)
    await _make_60_recent(db_session, user.id)

    state = await load(db_session, user.id)
    assert len(state.entries) == 50
    assert state.has_more is True
    assert state.cursor == (state.entries[-1].published, state.entries[-1].id)


@pytest.mark.asyncio
async def test_load_more_accumulates_without_overlap(db_session):
    user = await make_user(db_session)
    entries = await _make_60_recent(db_session, user.id)
    await assign_tag(db_session, entries[59].id, "top", user.id)
    await assign_tag(db_session, entries[5].id, "old", user.id)

    state = await load(db_session, user.id)
    page1_ids = {e.id for e in state.entries}

    state2 = await load_more(db_session, state, user.id)
    new_ids = {e.id for e in state2.entries[50:]}

    assert len(state2.entries) == 60
    assert page1_ids.isdisjoint(new_ids)
    assert len(page1_ids | new_ids) == 60
    assert state2.has_more is False
    assert state2.cursor is not None
    # tag_map é merge: tags da página 1 e da página 2 presentes
    assert state2.tag_map.get(entries[59].id) == ["top"]
    assert state2.tag_map.get(entries[5].id) == ["old"]


@pytest.mark.asyncio
async def test_select_category_resets_cursor(db_session):
    user = await make_user(db_session)
    base = datetime(2024, 1, 1)
    cat = await create_category(db_session, user.id, "Cat")
    for i in range(3):
        feed, _ = await create_feed_and_entry(
            db_session,
            user.id,
            url=f"https://example.com/c{i}",
            link=f"https://example.com/c{i}",
            published=base + timedelta(minutes=i),
        )
        await update_feed_category(db_session, user.id, feed.url, cat.id)

    state = await load(db_session, user.id)
    state = await select_category(db_session, state, cat.id, user.id)
    assert len(state.entries) == 3
    assert state.has_more is False
    assert state.cursor == (state.entries[-1].published, state.entries[-1].id)

    # estado "gasto" com cursor antigo é resetado pela seleção de categoria
    stale = ExploreState(
        cursor=(datetime(2030, 1, 1), 99999),
        has_more=True,
        tree=state.tree,
    )
    state2 = await select_category(db_session, stale, cat.id, user.id)
    assert len(state2.entries) == 3
    assert state2.has_more is False
    assert state2.cursor == (state.entries[-1].published, state.entries[-1].id)


@pytest.mark.asyncio
async def test_search_has_more_false(db_session):
    user = await make_user(db_session)
    await create_feed_and_entry(
        db_session,
        user.id,
        url="https://example.com/ml",
        title="Machine learning basics",
        link="https://example.com/ml",
    )

    state = await load(db_session, user.id)
    state = await search(db_session, state, "machine", user.id)
    assert state.is_searching is True
    assert state.has_more is False
    assert state.cursor is None


@pytest.mark.asyncio
async def test_load_entry_tags_scoped_by_user(db_session):
    user_a = await make_user(db_session, "usera", "passa")
    user_b = await make_user(db_session, "userb", "passb")
    _, entry_a = await create_feed_and_entry(db_session, user_a.id)

    await assign_tag(db_session, entry_a.id, "python", user_a.id)
    # linha legada/cruzada: tag de entry_a atribuída por outro usuário
    db_session.add(EntryTag(entry_id=entry_a.id, tag="ghost", user_id=user_b.id))
    await db_session.commit()

    state = await load(db_session, user_a.id)
    assert state.tag_map.get(entry_a.id) == ["python"]
