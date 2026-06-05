import pytest

from app.services.oauth_service import get_authorization_url, is_provider_available
from app.services.user_service import get_by_oauth, get_or_create_oauth_user


def _clear_oauth_config(monkeypatch):
    import app.services.oauth_service as oauth_svc

    monkeypatch.setattr(oauth_svc, "GOOGLE_CLIENT_ID", None)
    monkeypatch.setattr(oauth_svc, "GOOGLE_CLIENT_SECRET", None)
    monkeypatch.setattr(oauth_svc, "GITHUB_CLIENT_ID", None)
    monkeypatch.setattr(oauth_svc, "GITHUB_CLIENT_SECRET", None)


@pytest.mark.asyncio
async def test_is_provider_available_true(mock_oauth_config):
    assert is_provider_available("google") is True
    assert is_provider_available("github") is True


@pytest.mark.asyncio
async def test_is_provider_available_false(monkeypatch):
    _clear_oauth_config(monkeypatch)
    assert is_provider_available("google") is False
    assert is_provider_available("github") is False


@pytest.mark.asyncio
async def test_is_provider_available_unknown(monkeypatch):
    _clear_oauth_config(monkeypatch)
    assert is_provider_available("gitlab") is False


@pytest.mark.asyncio
async def test_get_authorization_url_google(mock_oauth_config):
    uri, state = get_authorization_url("google")
    assert uri.startswith("https://accounts.google.com/")
    assert "state=" in uri
    assert "code_challenge=" in uri
    assert isinstance(state, str)
    assert len(state) > 0


@pytest.mark.asyncio
async def test_get_authorization_url_github(mock_oauth_config):
    uri, state = get_authorization_url("github")
    assert uri.startswith("https://github.com/")
    assert "state=" in uri
    assert "code_challenge=" in uri
    assert isinstance(state, str)
    assert len(state) > 0


@pytest.mark.asyncio
async def test_get_authorization_url_not_configured(monkeypatch):
    _clear_oauth_config(monkeypatch)
    with pytest.raises(ValueError, match="not configured"):
        get_authorization_url("google")


@pytest.mark.asyncio
async def test_get_authorization_url_unknown_provider(mock_oauth_config):
    with pytest.raises(ValueError, match="not configured"):
        get_authorization_url("gitlab")


@pytest.mark.asyncio
async def test_get_or_create_oauth_user_creates(db_session):
    user = await get_or_create_oauth_user(db_session, "google", "12345", "googleuser")
    assert user.name == "googleuser"
    assert user.oauth_provider == "google"
    assert user.oauth_id == "12345"
    assert user.password is None


@pytest.mark.asyncio
async def test_get_or_create_oauth_user_returns_existing(db_session):
    u1 = await get_or_create_oauth_user(db_session, "google", "12345", "googleuser")
    u2 = await get_or_create_oauth_user(db_session, "google", "12345", "googleuser")
    assert u1.id == u2.id
    assert u2.name == "googleuser"


@pytest.mark.asyncio
async def test_get_or_create_oauth_user_name_collision_google(db_session):
    await get_or_create_oauth_user(db_session, "google", "111", "collision")
    user = await get_or_create_oauth_user(db_session, "google", "222", "collision")
    assert user.name == "google_collision"


@pytest.mark.asyncio
async def test_get_or_create_oauth_user_name_collision_github(db_session):
    await get_or_create_oauth_user(db_session, "github", "111", "collision")
    user = await get_or_create_oauth_user(db_session, "github", "222", "collision")
    assert user.name == "gh_collision"


@pytest.mark.asyncio
async def test_get_by_oauth_found(db_session):
    await get_or_create_oauth_user(db_session, "google", "12345", "testuser")
    user = await get_by_oauth(db_session, "google", "12345")
    assert user is not None
    assert user.name == "testuser"


@pytest.mark.asyncio
async def test_get_by_oauth_not_found(db_session):
    user = await get_by_oauth(db_session, "google", "nonexistent")
    assert user is None


@pytest.mark.asyncio
async def test_get_by_oauth_wrong_provider(db_session):
    await get_or_create_oauth_user(db_session, "google", "12345", "testuser")
    user = await get_by_oauth(db_session, "github", "12345")
    assert user is None
