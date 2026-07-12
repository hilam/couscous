import pytest

from app.app import _ROUTES, _match_route
from app.controls.nav_bar import _INDEX_ROUTES
from app.views.category_list_view import category_list_view
from app.views.entry_list_view import entry_list_view
from app.views.entry_view import entry_view
from app.views.explore_view import explore_view
from app.views.feed_list_view import feed_list_view
from app.views.login_view import login_view


class TestRouteTable:
    def test_root_route_is_explore_view(self):
        route = _match_route("/")
        assert route is not None
        assert route.handler is explore_view

    def test_feeds_route_is_feed_list_view(self):
        route = _match_route("/feeds")
        assert route is not None
        assert route.handler is feed_list_view

    def test_feed_detail_route_is_entry_list_view(self):
        route = _match_route("/feed/https://example.com/rss")
        assert route is not None
        assert route.handler is entry_list_view

    def test_entry_detail_route_is_entry_view(self):
        route = _match_route("/entry/42")
        assert route is not None
        assert route.handler is entry_view

    def test_categories_route_is_category_list_view(self):
        route = _match_route("/categories")
        assert route is not None
        assert route.handler is category_list_view

    def test_login_route_is_login_view(self):
        route = _match_route("/login")
        assert route is not None
        assert route.handler is login_view

class TestNavBar:
    def test_index_zero_is_root(self):
        assert _INDEX_ROUTES[0] == "/"

    def test_index_one_is_feeds(self):
        assert _INDEX_ROUTES[1] == "/feeds"

    def test_index_two_is_categories(self):
        assert _INDEX_ROUTES[2] == "/categories"

    def test_index_three_is_about(self):
        assert _INDEX_ROUTES[3] == "/about"


class TestRouteOrder:
    def test_specific_routes_before_generic(self):
        """Ensure /feed/ and /entry/ come before / in the route table."""
        route_prefixes = [r.prefix for r in _ROUTES]
        feed_index = route_prefixes.index("/feed/")
        entry_index = route_prefixes.index("/entry/")
        root_index = route_prefixes.index("/")
        assert feed_index < root_index, "/feed/ must come before /"
        assert entry_index < root_index, "/entry/ must come before /"
