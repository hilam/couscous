import flet as ft

from app.services.user_service import login
from app.state import State
from database.service.database import get_db_session


async def login_view(page: ft.Page, state: State) -> ft.View:
    name_field = ft.TextField(label="Nome de usuário", autofocus=True)
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

        async with get_db_session() as session:
            try:
                user = await login(session, name, password)

                if user:
                    state.user = user
                    await page.push_route("/feeds")
                else:
                    error_text.value = "Usuário não encontrado"
                    error_text.visible = True
                    page.update()
            except ValueError as ex:
                error_text.value = str(ex)
                error_text.visible = True
                page.update()

    async def go_to_register(e):
        await page.push_route("/register")

    submit_btn = ft.FilledButton("Entrar", on_click=submit)
    register_link = ft.TextButton("Criar conta", on_click=go_to_register)

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
                            controls=[
                                name_field,
                                password_field,
                                error_text,
                                submit_btn,
                                register_link,
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
