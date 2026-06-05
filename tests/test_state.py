from app.state import State


def test_state_initializes_with_defaults():
    state = State()
    assert state.user is None
    assert state.active_feed_url is None
    assert state.loading is False


def test_state_user_mutable():
    state = State()
    state.user = "dummy"
    assert state.user == "dummy"


def test_state_active_feed_url_mutable():
    state = State()
    state.active_feed_url = "https://example.com/rss"
    assert state.active_feed_url == "https://example.com/rss"


def test_state_loading_mutable():
    state = State()
    state.loading = True
    assert state.loading is True
