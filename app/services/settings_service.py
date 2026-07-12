from dataclasses import dataclass

from sqlmodel import select, update as sqlmodel_update

from database.models.couscous import User


@dataclass
class UserSettings:
    theme_mode: str = "light"
    font_scale: float = 1.0


async def get_settings(session, user_id: int) -> UserSettings:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        return UserSettings()
    return UserSettings(
        theme_mode=user.theme_mode or "light",
        font_scale=user.font_scale or 1.0,
    )


async def save_settings(
    session,
    user_id: int,
    theme_mode: str | None = None,
    font_scale: float | None = None,
) -> None:
    values: dict = {}
    if theme_mode is not None:
        values["theme_mode"] = theme_mode
    if font_scale is not None:
        values["font_scale"] = font_scale
    if values:
        stmt = sqlmodel_update(User).where(User.id == user_id).values(**values)
        await session.execute(stmt)
        await session.commit()
