## 1. Database engine type narrowing

- [x] 1.1 Fix `database/service/database.py` — narrow `AsyncEngine | Engine` union with `isinstance` checks so `engine.begin()` works in both `init_db()` and `init_async_db()`
- [x] 1.2 Fix `database/service/database.py` — fix `get_session()` return type annotation to `AsyncGenerator[AsyncSession, None]`
- [x] 1.3 Fix `database/service/database.py` — narrow engine before `sessionmaker()` calls
- [x] 1.4 Fix `app/db.py` — narrow `AsyncEngine | Engine` union with `isinstance` before `sessionmaker()` and `engine` usage
- [x] 1.5 Fix `app/db.py` — add `await` to `session.close()` call
- [x] 1.6 Fix `app/db.py` — fix async generator return type annotation

## 2. Flet icon constants

- [x] 2.1 Fix `app/controls/feed_card.py` — replace `ft.icons.RSS_FEED` with `ft.Icons.RSS_FEED`
- [x] 2.2 Fix `app/controls/feed_card.py` — replace `ft.icons.DELETE_OUTLINE` with `ft.Icons.DELETE_OUTLINE`
- [x] 2.3 Fix `app/controls/article_card.py` — replace `ft.icons.ARTICLE` with `ft.Icons.ARTICLE`
- [x] 2.4 Fix `app/views/feed_list_view.py` — replace all `ft.icons.*` with `ft.Icons.*` (RSS_FEED, HOME, INFO, REFRESH, ADD)
- [x] 2.5 Fix `app/views/entry_list_view.py` — replace all `ft.icons.*` with `ft.Icons.*` (ARTICLE, HOME, RSS_FEED, INFO, REFRESH)
- [x] 2.6 Fix `app/views/entry_view.py` — replace all `ft.icons.*` with `ft.Icons.*` (HOME, RSS_FEED, INFO, STAR_BORDER, OPEN_IN_NEW)
- [x] 2.7 Fix `app/views/home_view.py` — replace all `ft.icons.*` with `ft.Icons.*` (HOME, RSS_FEED, INFO)
- [x] 2.8 Fix `app/views/login_view.py` — replace `ft.icons.RSS_FEED` with `ft.Icons.RSS_FEED`
- [x] 2.9 Fix `app/views/about_view.py` — replace all `ft.icons.*` with `ft.Icons.*` (HOME, RSS_FEED, INFO)

## 3. Flet padding/alignment utilities

- [x] 3.1 Fix all files — replace `ft.padding.all(N)` with `ft.Padding(N, N, N, N)` in `feed_card.py`, `article_card.py`, `feed_list_view.py`, `entry_list_view.py`, `entry_view.py`
- [x] 3.2 Fix all files — replace `ft.alignment.center` with `ft.Alignment.CENTER` in `feed_list_view.py`, `entry_list_view.py`, `entry_view.py`

## 4. TextStyle type mismatch

- [x] 4.1 Fix `app/views/login_view.py` — replace `style=ft.TextThemeStyle.HEADLINE_LARGE` with `theme_style=ft.TextThemeStyle.HEADLINE_LARGE`
- [x] 4.2 Fix `app/views/login_view.py` — replace `style=ft.TextThemeStyle.TITLE_MEDIUM` with `theme_style=ft.TextThemeStyle.TITLE_MEDIUM`
- [x] 4.3 Fix `app/views/home_view.py` — replace all `ft.TextThemeStyle.*` style references
- [x] 4.4 Fix `app/views/entry_view.py` — replace all `ft.TextThemeStyle.*` style references
- [x] 4.5 Fix `app/views/entry_list_view.py` — replace `ft.TextThemeStyle.TITLE_MEDIUM`
- [x] 4.6 Fix `app/views/feed_list_view.py` — replace `ft.TextThemeStyle.TITLE_MEDIUM`
- [x] 4.7 Fix `app/views/about_view.py` — replace `ft.TextThemeStyle.HEADLINE_MEDIUM`

## 5. Page API fixes

- [x] 5.1 Fix `app/views/feed_list_view.py` — replace `page.show_snack_bar(` with `page.overlay.append(ft.SnackBar(...))`
- [x] 5.2 Fix `app/views/feed_list_view.py` — replace `page.dialog = dlg` with `page.show_dialog(dlg)`
- [x] 5.3 Fix `app/views/feed_list_view.py` — replace `page.dialog.open = False` with `dlg.open = False`
- [x] 5.4 Fix `app/app.py` — replace `page.session.set("state", state)` with `page.session.store.set("state", state)`

## 6. Dialog update_async

- [x] 6.1 Fix `app/controls/confirm_dialog.py` — replace `await self.update_async()` with `self.update()`
- [x] 6.2 Fix `app/controls/add_feed_dialog.py` — replace `await self.update_async()` with `self.update()` in `_cancel` and `_submit`

## 7. Optional datetime handling

- [x] 7.1 Fix `app/services/entry_service.py` — guard `Entry.published.desc()` against None using `desc()` function

## 8. Column padding kwarg

- [x] 8.1 Fix `app/views/entry_view.py` — move `padding` out of `ft.Column()` by wrapping in `ft.Container`
