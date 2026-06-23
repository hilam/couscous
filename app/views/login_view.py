import asyncio

import flet as ft

from app.controls.oauth_buttons import get_oauth_buttons
from app.services.user_service import login


async def login_view(ctx) -> ft.View:
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

        async with ctx.new_session() as session:
            try:
                user = await login(session, name, password)

                if user:
                    state.user = user
                    await page.push_route("/feeds")
                else:
                    error_text.value = "Usu\u00e1rio n\u00e3o encontrado"
                    error_text.visible = True
                    page.update()
            except ValueError as ex:
                error_text.value = str(ex)
                error_text.visible = True
                page.update()

    async def go_to_register(e):
        await page.push_route("/register")

    name_field.on_submit = lambda e: asyncio.create_task(password_field.focus())
    password_field.on_submit = submit
    submit_btn = ft.FilledButton("Entrar", on_click=submit)
    register_link = ft.TextButton("Criar conta", on_click=go_to_register)

    form_controls: list[ft.Control] = [
        name_field,
        password_field,
        error_text,
        submit_btn,
        register_link,
    ]
    form_controls.extend(get_oauth_buttons(page, error_text))

    return ft.View(
        route="/login",
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
                        "Entre com sua conta",
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
