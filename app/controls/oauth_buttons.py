import asyncio

import flet as ft

from app.services import oauth_service


async def _oauth_click(page: ft.Page, error_text: ft.Text, provider: str):
    try:
        uri, _state = oauth_service.get_authorization_url(provider)
        await page.launch_url(uri)
    except ValueError as ex:
        error_text.value = str(ex)
        error_text.visible = True
        page.update()


def get_oauth_buttons(page: ft.Page, error_text: ft.Text) -> list[ft.Control]:
    buttons: list[ft.Control] = []
    providers = [
        ("google", "Entrar com Google", ft.Icons.ACCOUNT_CIRCLE),
        ("github", "Entrar com GitHub", ft.Icons.ACCOUNT_TREE),
    ]
    for provider, label, icon in providers:
        btn = ft.OutlinedButton(
            label,
            icon=icon,
            on_click=lambda _, p=provider: asyncio.create_task(
                _oauth_click(page, error_text, p)
            ),
        )
        buttons.append(btn)
    if buttons:
        buttons.insert(0, ft.Divider(height=20, color=ft.Colors.OUTLINE_VARIANT))
    return buttons
