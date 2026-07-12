from dataclasses import dataclass

import flet as ft
from sqlmodel import select
from sqlmodel import update as sqlmodel_update

from database.models.couscous import User


@dataclass
class UserSettings:
    theme_mode: str = "light"
    font_scale: float = 1.0
    auto_cleanup_days: int | None = None


async def get_settings(session, user_id: int) -> UserSettings:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        return UserSettings()
    return UserSettings(
        theme_mode=user.theme_mode or "light",
        font_scale=user.font_scale or 1.0,
        auto_cleanup_days=user.auto_cleanup_days,
    )


_UNSET = object()  # sentinel to distinguish "not provided" from None


async def save_settings(
    session,
    user_id: int,
    theme_mode: str | None = None,
    font_scale: float | None = None,
    auto_cleanup_days: int | None | object = _UNSET,
) -> None:
    values: dict = {}
    if theme_mode is not None:
        values["theme_mode"] = theme_mode
    if font_scale is not None:
        values["font_scale"] = font_scale
    if auto_cleanup_days is not _UNSET:
        values["auto_cleanup_days"] = auto_cleanup_days
    if values:
        stmt = sqlmodel_update(User).where(User.id == user_id).values(**values)  # type: ignore[arg-type]
        await session.execute(stmt)
        await session.commit()


def apply_settings_to_page(page: ft.Page, theme_mode: str, font_scale: float) -> None:
    """Apply theme_mode and font_scale to a Flet page."""
    page.theme_mode = getattr(ft.ThemeMode, theme_mode.upper())

    t = page.theme or ft.Theme()
    tt = t.text_theme or ft.TextTheme()
    style_attrs = [
        "display_large",
        "display_medium",
        "display_small",
        "headline_large",
        "headline_medium",
        "headline_small",
        "title_large",
        "title_medium",
        "title_small",
        "body_large",
        "body_medium",
        "body_small",
        "label_large",
        "label_medium",
        "label_small",
    ]
    for attr in style_attrs:
        style = getattr(tt, attr, None)
        if style is not None and style.size is not None:
            kwargs = {}
            for f in ft.TextStyle.__dataclass_fields__:
                v = getattr(style, f, None)
                if v is not None:
                    kwargs[f] = v
            kwargs["size"] = round(style.size * font_scale, 1)
            setattr(tt, attr, ft.TextStyle(**kwargs))
    t.text_theme = tt
    page.theme = t
    page.update()
