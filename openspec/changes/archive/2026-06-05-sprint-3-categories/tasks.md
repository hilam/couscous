## 1. Data Model

- [x] 1.1 Add `Category` model to `database/models/couscous.py` with fields: id (PK), user_id (FK → users.id), name, parent_id (FK self-reference, nullable)
- [x] 1.2 Add `category_id` column (FK → categories.id, nullable) to `Feed` model in `database/models/couscous.py`
- [x] 1.3 Run `init_async_db()` to create the new `categories` table on startup

## 2. Category Service

- [x] 2.1 Create `app/services/category_service.py` with `create_category(session, user_id, name, parent_id=None)`, rejecting duplicates at same level
- [x] 2.2 Add `list_categories(session, user_id)` returning flat list of all user categories
- [x] 2.3 Add `get_category_tree(session, user_id)` building hierarchical tree in Python (dict with `children` lists)
- [x] 2.4 Add `rename_category(session, user_id, category_id, new_name)`, rejecting duplicates at same level
- [x] 2.5 Add `delete_category(session, user_id, category_id)` — promote children to root, unlink feeds, cycle detection

## 3. Category Management View

- [x] 3.1 Create `app/views/category_list_view.py` with route `/categories` — render category tree using `ft.ExpansionTile` or indented `ft.ListTile` items
- [x] 3.2 Implement "Nova Categoria" dialog (modal with name + parent selector) for create
- [x] 3.3 Implement rename via inline edit or context menu action
- [x] 3.4 Implement delete with confirmation dialog, handling children and feeds per spec
- [x] 3.5 Add navigation entry for categories (NavigationBar or AppBar action on `/feeds`)

## 4. Feed Service & Dialog Updates

- [x] 4.1 Add optional `category_id` parameter to `add_feed()` in `app/services/feed_service.py`
- [x] 4.2 Add `update_feed_category(session, user_id, feed_url, category_id)` to `feed_service.py`
- [x] 4.3 Update `AddFeedDialog` in `app/controls/add_feed_dialog.py` — add category dropdown with tree indentation, populated from `get_category_tree()`

## 5. Feed List View — Group by Category

- [x] 5.1 Update `feed_list_view.py` to fetch categories and build a grouped feed list
- [x] 5.2 Render category section headers with feed cards nested beneath them
- [x] 5.3 Display uncategorized feeds under "Sem categoria" header, shown last
- [x] 5.4 Handle empty state correctly — "Nenhum feed adicionado" when no feeds exist at all

## 6. Tests

- [x] 6.1 Create `tests/test_category_service.py` — test create, list, tree, rename, delete with children, delete with feeds, duplicate rejection
- [x] 6.2 Update `tests/test_feed_service.py` — test `add_feed` with and without `category_id`, test `update_feed_category`
- [x] 6.3 Run full test suite (`uv run pytest`) and verify all tests pass
