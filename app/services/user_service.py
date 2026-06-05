import bcrypt
from sqlmodel import select

from database.models.couscous import User


async def get_by_name(session, name: str) -> User | None:
    result = await session.execute(select(User).where(User.name == name))
    return result.scalar_one_or_none()


async def get_by_oauth(session, provider: str, oauth_id: str) -> User | None:
    result = await session.execute(
        select(User).where(User.oauth_provider == provider, User.oauth_id == oauth_id)
    )
    return result.scalar_one_or_none()


async def get_or_create_oauth_user(
    session, provider: str, oauth_id: str, name: str
) -> User:
    existing = await get_by_oauth(session, provider, oauth_id)
    if existing:
        return existing

    existing_name = await get_by_name(session, name)
    if existing_name:
        prefix = {"google": "google_", "github": "gh_"}.get(provider, f"{provider}_")
        name = f"{prefix}{name}"

    user = User(
        name=name,
        password=None,
        oauth_provider=provider,
        oauth_id=oauth_id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def register(session, name: str, password: str) -> User:
    existing = (
        await session.execute(select(User).where(User.name == name))
    ).scalar_one_or_none()
    if existing:
        msg = "Nome de usuário já existe"
        raise ValueError(msg)

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = User(name=name, password=hashed)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def login(session, name: str, password: str) -> User | None:
    result = await session.execute(select(User).where(User.name == name))
    user = result.scalar_one_or_none()

    if not user:
        msg = "Usuário não encontrado"
        raise ValueError(msg)

    if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        msg = "Senha incorreta"
        raise ValueError(msg)

    return user
