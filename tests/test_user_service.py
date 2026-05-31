import pytest

from app.services.user_service import register, login, get_by_name


@pytest.mark.asyncio
async def test_register_user(db_session):
    user = await register(db_session, "testuser", "password123")
    assert user.name == "testuser"
    assert user.password == "password123"


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
    with pytest.raises(ValueError, match="Senha incorreta"):
        await login(db_session, "testuser", "wrongpass")


@pytest.mark.asyncio
async def test_login_unknown_user_raises(db_session):
    with pytest.raises(ValueError, match="Usuário não encontrado"):
        await login(db_session, "nonexistent", "password123")


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
