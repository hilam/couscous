from sqlmodel import select

from database.models.couscous import User


async def get_by_name(session, name: str) -> User | None:
    result = session.execute(select(User).where(User.name == name))
    return result.scalar_one_or_none()


async def register(session, name: str, password: str) -> User:
    existing = session.execute(
        select(User).where(User.name == name)
    ).scalar_one_or_none()
    if existing:
        raise ValueError("Nome de usuário já existe")

    user = User(name=name, password=password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


async def login(session, name: str, password: str) -> User | None:
    result = session.execute(select(User).where(User.name == name))
    user = result.scalar_one_or_none()

    if not user:
        raise ValueError("Usuário não encontrado")

    if user.password != password:
        raise ValueError("Senha incorreta")

    return user
