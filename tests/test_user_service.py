import bcrypt
import pytest

from app.services.user_service import (
    get_by_name,
    get_by_oauth,
    get_or_create_oauth_user,
    login,
    register,
)
from database.models.couscous import User


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


@pytest.mark.asyncio
async def test_bcrypt_hash_format(db_session):
    user = await register(db_session, "bob", "s3cret")
    assert user.password.startswith("$2b$")
    assert len(user.password) == 60


@pytest.mark.asyncio
async def test_bcrypt_different_hashes(db_session):
    u1 = await register(db_session, "alice", "samepass")
    u2 = await register(db_session, "charlie", "samepass")
    assert u1.password != u2.password
    assert bcrypt.checkpw(b"samepass", u1.password.encode("utf-8"))
    assert bcrypt.checkpw(b"samepass", u2.password.encode("utf-8"))


@pytest.mark.asyncio
async def test_bcrypt_hash_verify_raw(db_session):
    user = await register(db_session, "dave", "mypassword")
    assert bcrypt.checkpw(b"mypassword", user.password.encode("utf-8"))
    assert not bcrypt.checkpw(b"wrongpass", user.password.encode("utf-8"))


@pytest.mark.asyncio
async def test_get_by_oauth_returns_user(db_session):
    await get_or_create_oauth_user(db_session, "google", "abc123", "oauthuser")
    user = await get_by_oauth(db_session, "google", "abc123")
    assert user is not None
    assert user.name == "oauthuser"
    assert user.oauth_provider == "google"
    assert user.oauth_id == "abc123"


@pytest.mark.asyncio
async def test_get_by_oauth_returns_none(db_session):
    user = await get_by_oauth(db_session, "github", "nonexistent")
    assert user is None


@pytest.mark.asyncio
async def test_get_or_create_oauth_user_creates(db_session):
    user = await get_or_create_oauth_user(db_session, "github", "42", "ghuser")
    assert user.name == "ghuser"
    assert user.password is None
    assert user.oauth_provider == "github"
    assert user.oauth_id == "42"


@pytest.mark.asyncio
async def test_get_or_create_oauth_user_reuses(db_session):
    u1 = await get_or_create_oauth_user(db_session, "github", "42", "ghuser")
    u2 = await get_or_create_oauth_user(db_session, "github", "42", "ghuser")
    assert u1.id == u2.id


@pytest.mark.asyncio
async def test_get_or_create_oauth_user_name_collision(db_session):
    await register(db_session, "regular", "password123")
    user = await get_or_create_oauth_user(db_session, "google", "99", "regular")
    assert user.name == "google_regular"
