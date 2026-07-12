import pytest

from app.services.settings_service import UserSettings, get_settings, save_settings
from app.services.user_service import register


@pytest.mark.asyncio
async def test_get_settings_returns_defaults(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    settings = await get_settings(db_session, user.id)
    assert settings == UserSettings("light", 1.0)


@pytest.mark.asyncio
async def test_get_settings_returns_saved_values(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    await save_settings(db_session, user.id, theme_mode="dark", font_scale=1.3)
    settings = await get_settings(db_session, user.id)
    assert settings == UserSettings("dark", 1.3)


@pytest.mark.asyncio
async def test_save_settings_updates_theme_only(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    await save_settings(db_session, user.id, theme_mode="dark")
    settings = await get_settings(db_session, user.id)
    assert settings.theme_mode == "dark"
    assert settings.font_scale == 1.0


@pytest.mark.asyncio
async def test_save_settings_updates_font_only(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    await save_settings(db_session, user.id, font_scale=1.3)
    settings = await get_settings(db_session, user.id)
    assert settings.font_scale == 1.3
    assert settings.theme_mode == "light"


@pytest.mark.asyncio
async def test_save_settings_updates_both(db_session):
    user = await register(db_session, "testuser", "pass")
    assert user.id is not None
    await save_settings(db_session, user.id, theme_mode="dark", font_scale=1.3)
    settings = await get_settings(db_session, user.id)
    assert settings == UserSettings("dark", 1.3)
