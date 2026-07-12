import flet as ft

from app.controls.cleanup_dialog import show_cleanup_dialog
from app.services.settings_service import (
    apply_settings_to_page,
    get_settings,
    save_settings,
)

_THEME_OPTIONS = [
    ("Claro", "light"),
    ("Escuro", "dark"),
    ("Sistema", "system"),
]

_CLEANUP_OPTIONS = [
    ("Desligado", None),
    ("7 dias", 7),
    ("30 dias", 30),
    ("90 dias", 90),
    ("365 dias", 365),
]

_DROPDOWN_VALUES = {str(d) if d else "none": d for _, d in _CLEANUP_OPTIONS}


async def settings_view(ctx) -> ft.View:  # noqa: C901, PLR0915
    page = ctx.page
    state = ctx.state

    settings = await get_settings(ctx.session, state.user.id)
    pending_theme = settings.theme_mode
    pending_font = settings.font_scale
    pending_cleanup_days = settings.auto_cleanup_days

    def _is_dirty():
        return pending_theme != state.theme_mode or pending_font != state.font_scale

    async def _on_theme_change(e):
        nonlocal pending_theme
        selected = e.control.selected
        if selected:
            pending_theme = e.control.data
            page.theme_mode = getattr(ft.ThemeMode, pending_theme.upper())
            _update_save_btn()
            page.update()

    async def _on_slider_change(e):
        nonlocal pending_font
        pending_font = round(e.control.value, 1)
        _update_preview()
        _update_save_btn()
        page.update()

    async def _on_save(e):
        nonlocal pending_theme, pending_font
        await save_settings(ctx.session, state.user.id, pending_theme, pending_font)
        state.theme_mode = pending_theme
        state.font_scale = pending_font
        apply_settings_to_page(page, pending_theme, pending_font)
        _update_save_btn()
        page.update()

    async def _on_about(e):
        dlg = ft.AlertDialog(
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.RSS_FEED, color=ft.Colors.CYAN_400),
                    ft.Text("CousCous", weight=ft.FontWeight.BOLD),
                ],
                spacing=8,
            ),
            content=ft.Column(
                controls=[
                    ft.Text("Vers\u00e3o 0.1.0"),
                    ft.Divider(),
                    ft.Text(
                        "CousCous \u00e9 um leitor de feeds RSS "
                        "constru\u00eddo com Python e Flet."
                    ),
                    ft.Text(
                        "Permite adicionar feeds RSS, visualizar artigos, "
                        "e gerenciar sua leitura de forma simples."
                    ),
                ],
                spacing=8,
                tight=True,
            ),
            actions=[ft.TextButton("Fechar", on_click=lambda _: _close_dialog(page))],
        )
        page.dialog = dlg  # type: ignore[attr-defined]
        dlg.open = True
        page.update()

    async def _on_cleanup_dropdown_change(e):
        nonlocal pending_cleanup_days
        key = e.control.value
        pending_cleanup_days = _DROPDOWN_VALUES.get(key)
        await save_settings(
            ctx.session, state.user.id, auto_cleanup_days=pending_cleanup_days
        )
        page.show_snack_bar(  # type: ignore[attr-defined]
            ft.SnackBar(content=ft.Text("Configura\u00e7\u00e3o de limpeza salva."))
        )
        page.update()

    async def _on_cleanup_click(e):
        await show_cleanup_dialog(ctx)

    async def _close_dialog(page: ft.Page):
        page.dialog.open = False  # type: ignore[attr-defined]
        page.update()

    def _update_preview():
        preview_text.size = 16 * pending_font

    def _update_save_btn():
        save_btn.disabled = not _is_dirty()

    theme_group = ft.RadioGroup(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.LIGHT_MODE,
                                size=24,
                                color=ft.Colors.AMBER_600
                                if opt[1] == "light"
                                else None,
                            ),
                            ft.Text(opt[0], size=12),
                        ],
                        spacing=4,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    data=opt[1],
                    padding=10,
                    border_radius=8,
                    ink=True,
                    on_click=_on_theme_change,
                    bgcolor=ft.Colors.CYAN_50
                    if opt[1] == settings.theme_mode
                    else None,
                )
                for opt in _THEME_OPTIONS
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )

    preview_text = ft.Text(
        "Aa",
        size=16 * settings.font_scale,
        weight=ft.FontWeight.BOLD,
    )

    font_slider = ft.Slider(
        min=0.8,
        max=1.5,
        divisions=7,
        value=settings.font_scale,
        label="{value}x",
        on_change=_on_slider_change,
    )

    save_btn = ft.FilledButton(
        "Salvar",
        disabled=True,
        on_click=_on_save,
    )

    about_btn = ft.OutlinedButton(
        "Sobre",
        icon=ft.Icons.INFO,
        on_click=_on_about,
    )

    # Map current value to dropdown key
    current_cleanup_key = (
        str(settings.auto_cleanup_days)
        if settings.auto_cleanup_days is not None
        else "none"
    )
    # pending_cleanup_days already initialized above

    cleanup_dropdown = ft.Dropdown(
        label="Limpeza autom\u00e1tica",
        value=current_cleanup_key,
        options=[
            ft.dropdown.Option(key, label)
            for label, val in _CLEANUP_OPTIONS
            for key, v in [("none" if val is None else str(val), val)]
        ],
        on_text_change=_on_cleanup_dropdown_change,
    )

    cleanup_btn = ft.FilledButton(
        "Limpar artigos antigos",
        icon=ft.Icons.DELETE_SWEEP,
        on_click=_on_cleanup_click,
    )

    return ft.View(
        route="/about",
        controls=[
            ft.AppBar(title=ft.Text("Config"), bgcolor=ft.Colors.CYAN_50),
            ft.SafeArea(
                content=ft.ListView(
                    controls=[
                        ft.Text("Tema", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                        theme_group,
                        ft.Divider(),
                        ft.Text(
                            "Tamanho do texto",
                            theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                        ),
                        ft.Row(
                            controls=[
                                ft.Text("A", size=12),
                                ft.Column(
                                    controls=[
                                        font_slider,
                                        ft.Row(
                                            controls=[preview_text],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                        ),
                                    ],
                                    expand=True,
                                ),
                                ft.Text("A", size=24),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Divider(),
                        ft.Row(
                            controls=[save_btn, about_btn],
                            spacing=16,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Divider(),
                        ft.Text(
                            "Limpeza de artigos",
                            theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                        ),
                        cleanup_dropdown,
                        ft.Row(
                            controls=[cleanup_btn],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=16,
                    padding=16,
                ),
            ),
        ],
    )
