import pytest

from app.services.user_service import register
from app.services.user_service import login


@pytest.mark.asyncio
async def test_registration_then_login_flow(db_session):
    user = await register(db_session, "newuser", "secret123")
    assert user.name == "newuser"

    logged_in = await login(db_session, "newuser", "secret123")
    assert logged_in is not None
    assert logged_in.name == "newuser"


@pytest.mark.asyncio
async def test_register_duplicate_username(db_session):
    await register(db_session, "dupuser", "pass1")
    with pytest.raises(ValueError, match="Nome de usuário já existe"):
        await register(db_session, "dupuser", "pass2")
