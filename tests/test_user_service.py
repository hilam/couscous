import pytest

from app.services.user_service import (
    get_by_name,
    get_or_create_oauth_user,
    login,
    register,
)


@pytest.mark.asyncio
async def test_register_user(db_session):
    user = await register(db_session, "testuser", "password123")
    assert user.name == "testuser"
    assert user.password.startswith("$2b$")


@pytest.mark.asyncio
async def test_register_duplicate_raises(db_session):
    await register(db_session, "testuser", "password123")
    with pytest.raises(ValueError, match="Nome de usuário já existe"):
        await register(db_session, "testuser", "otherpass")


@pytest.mark.asyncio
async def test_login_success(db_session):
    await register(db_session, "testuser", "password123")
    user = await login(db_session, "testuser", "password123")
    assert user is not None
    assert user.name == "testuser"


@pytest.mark.asyncio
async def test_login_wrong_password_raises(db_session):
    await register(db_session, "testuser", "password123")
    with pytest.raises(ValueError, match="Usuário ou senha inválidos"):
        await login(db_session, "testuser", "wrongpass")


@pytest.mark.asyncio
async def test_login_unknown_user_raises(db_session):
    with pytest.raises(ValueError, match="Usuário ou senha inválidos"):
        await login(db_session, "nonexistent", "password123")


@pytest.mark.asyncio
async def test_login_oauth_user_without_password_raises(db_session):
    await get_or_create_oauth_user(db_session, "google", "g-123", "oauthuser")
    with pytest.raises(ValueError, match="Usuário ou senha inválidos"):
        await login(db_session, "oauthuser", "qualquer")


@pytest.mark.asyncio
async def test_login_message_is_uniform(db_session):
    await get_or_create_oauth_user(db_session, "google", "g-123", "oauthuser")
    with pytest.raises(ValueError) as exc_oauth:
        await login(db_session, "oauthuser", "qualquer")
    with pytest.raises(ValueError) as exc_unknown:
        await login(db_session, "nonexistent", "password123")
    assert str(exc_oauth.value) == str(exc_unknown.value)


@pytest.mark.asyncio
async def test_get_by_name(db_session):
    await register(db_session, "testuser", "password123")
    user = await get_by_name(db_session, "testuser")
    assert user is not None
    assert user.name == "testuser"


@pytest.mark.asyncio
async def test_get_by_name_nonexistent(db_session):
    user = await get_by_name(db_session, "nonexistent")
    assert user is None






