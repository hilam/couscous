import asyncio

import flet as ft

from app.context import PageContext
from app.services.cleanup_service import (
    count_entries_older_than,
    purge_older_than,
)

_PERIODS = [7, 30, 90, 365]


async def show_cleanup_dialog(ctx: PageContext) -> None:
    """Open cleanup dialog with period select, count, and async exec."""
    page = ctx.page
    user_id: int = (ctx.state.user.id or 0) if ctx.state.user else 0

    limpar_btn: ft.FilledButton  # forward declaration
    dialog: ft.AlertDialog  # forward declaration

    count_text = ft.Text(
        "Selecione um período para ver quantos artigos serão removidos."
    )
    dropdown = ft.Dropdown(
        label="Remover artigos com mais de",
        options=[ft.dropdown.Option(f"{d} dias") for d in _PERIODS],
        on_change=lambda e: asyncio.create_task(  # type: ignore[call-arg, has-type]
            _on_period_change(e, ctx, user_id, count_text, limpar_btn)
        ),
    )
    limpar_btn = ft.FilledButton(
        "Limpar",
        disabled=True,
        on_click=lambda e: asyncio.create_task(  # type: ignore[has-type]
            _on_cleanup(e, page, ctx, user_id, dropdown, dialog)
        ),
    )
    dialog = ft.AlertDialog(
        title=ft.Text("Limpar artigos antigos"),
        content=ft.Column(
            controls=[dropdown, count_text],
            tight=True,
            spacing=12,
            width=350,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: _close(e, dialog)),  # type: ignore[has-type]
            limpar_btn,
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def _close(e, dialog: ft.AlertDialog) -> None:
    dialog.open = False
    dialog.update()


async def _on_period_change(
    e, ctx: PageContext, user_id: int, count_text: ft.Text, limpar_btn: ft.FilledButton
) -> None:
    value = e.control.value
    if not value:
        return
    days = int(value.split()[0])

    async with ctx.open_session() as s:
        count = await count_entries_older_than(s, user_id, days)

    if count > 0:
        count_text.value = f"{count} artigos serão removidos."
        limpar_btn.disabled = False
    else:
        count_text.value = "Nenhum artigo para remover."
        limpar_btn.disabled = True

    count_text.update()
    limpar_btn.update()


async def _on_cleanup(  # noqa: PLR0913
    e,
    page: ft.Page,
    ctx: PageContext,
    user_id: int,
    dropdown: ft.Dropdown,
    dialog: ft.AlertDialog,
) -> None:
    value = dropdown.value
    if not value:
        return
    days = int(value.split()[0])

    dialog.open = False
    dialog.update()

    async with ctx.open_session() as s:
        removed = await purge_older_than(s, user_id, days)

    if removed > 0:
        label = "artigo" if removed == 1 else "artigos"
        msg = f"\U0001f9f9 {removed} {label} antigo removido."
        page.show_snack_bar(  # type: ignore[attr-defined]
            ft.SnackBar(content=ft.Text(msg), bgcolor=ft.Colors.GREEN_400)
        )
    else:
        page.show_snack_bar(  # type: ignore[attr-defined]
            ft.SnackBar(content=ft.Text("Nenhum artigo para remover."))
        )

    page.update()
