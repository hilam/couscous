import asyncio

import flet as ft

from app.controls.oauth_buttons import get_oauth_buttons
from app.services.user_service import register


async def register_view(ctx) -> ft.View:
    page = ctx.page
    state = ctx.state

    name_field = ft.TextField(label="Nome de usu\u00e1rio", autofocus=True)
    password_field = ft.TextField(label="Senha", password=True)
    error_text = ft.Text("", color=ft.Colors.RED, visible=False)

    async def submit(e):
        name = name_field.value.strip()
        password = password_field.value.strip()

        if not name or not password:
            error_text.value = "Preencha todos os campos"
            error_text.visible = True
            page.update()
            return

        async with ctx.open_session() as session:
            try:
                user = await register(session, name, password)

                if user:
                    state.user = user
                    await page.push_route("/")
                else:
                    error_text.value = "Nome de usu\u00e1rio j\u00e1 existe"
                    error_text.visible = True
                    page.update()
            except ValueError as ex:
                error_text.value = str(ex)
                error_text.visible = True
                page.update()

    async def go_to_login(e):
        await page.push_route("/login")

    name_field.on_submit = lambda e: asyncio.create_task(password_field.focus())
    password_field.on_submit = submit
    submit_btn = ft.FilledButton("Registrar", on_click=submit)
    login_link = ft.TextButton("J\u00e1 tenho conta", on_click=go_to_login)

    form_controls: list[ft.Control] = [
        name_field,
        password_field,
        error_text,
        submit_btn,
        login_link,
    ]
    form_controls.extend(get_oauth_buttons(page, error_text))

    return ft.View(
        route="/register",
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.RSS_FEED, size=80, color=ft.Colors.CYAN_400),
                    ft.Text("CousCous", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                    ft.Text(
                        "Crie sua conta",
                        theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=form_controls,
                            spacing=10,
                        ),
                        padding=20,
                        width=350,
                    ),
                ],
            )
        ],
    )
