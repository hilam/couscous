import flet as ft

from app.db import get_db_session
from app.services.user_service import login, register
from app.state import State


async def login_view(page: ft.Page, state: State) -> ft.View:
    name_field = ft.TextField(label="Nome de usuário", autofocus=True)
    password_field = ft.TextField(label="Senha", password=True)
    error_text = ft.Text("", color=ft.colors.RED, visible=False)
    is_login = True

    async def toggle_mode(e):
        nonlocal is_login
        is_login = not is_login
        submit_btn.text = "Entrar" if is_login else "Registrar"  # type: ignore[attr-defined]
        toggle_btn.text = "Criar conta" if is_login else "Já tenho conta"  # type: ignore[attr-defined]
        error_text.visible = False
        page.update()

    async def submit(e):
        name = name_field.value.strip()
        password = password_field.value.strip()

        if not name or not password:
            error_text.value = "Preencha todos os campos"
            error_text.visible = True
            page.update()
            return

        async with get_db_session() as session:
            try:
                if is_login:
                    user = await login(session, name, password)
                else:
                    user = await register(session, name, password)

                if user:
                    state.user = user
                    page.go("/feeds")
                else:
                    error_text.value = (
                        "Usuário não encontrado"
                        if is_login
                        else "Nome de usuário já existe"
                    )
                    error_text.visible = True
                    page.update()
            except ValueError as ex:
                error_text.value = str(ex)
                error_text.visible = True
                page.update()

    submit_btn = ft.FilledButton("Entrar", on_click=submit)
    toggle_btn = ft.TextButton("Criar conta", on_click=toggle_mode)

    return ft.View(
        route="/login",
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.RSS_FEED, size=80, color=ft.colors.CYAN_400),
                    ft.Text("CousCous", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                    ft.Text(
                        "Entre com sua conta",
                        theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                name_field,
                                password_field,
                                error_text,
                                submit_btn,
                                toggle_btn,
                            ],
                            spacing=10,
                        ),
                        padding=20,
                        width=350,
                    ),
                ],
            )
        ],
    )
