"""Contrato de APIs do Flet 1.x.

Trava o app contra o retorno às chamadas inexistentes (page.open,
page.run_javascript, page.close_bottom_sheet) que quebravam em runtime na
era 0.x, e afirma a presença das APIs 1.x nas quais convergimos
(page.show_dialog, page.pop_dialog, ft.Clipboard + shared_service).

Nota: page.views continua sendo API válida no 1.x, porém como campo de
dataclass acessível na INSTÂNCIA (dir()/hasattr na classe não o listam),
usado internamente por render_views/pop_views_until. Por isso a asserção
"views" abaixo é feita na classe e não conflita com o uso em app/app.py.
"""

import flet as ft


def test_show_dialog_and_pop_dialog_exist():
    assert hasattr(ft.Page, "show_dialog")
    assert hasattr(ft.Page, "pop_dialog")


def test_removed_zero_x_apis_are_absent():
    assert not hasattr(ft.Page, "open")
    assert not hasattr(ft.Page, "run_javascript")
    assert not hasattr(ft.Page, "close_bottom_sheet")
    assert not hasattr(ft.Page, "close_dialog")


def test_page_views_absent_at_class_level():
    assert not hasattr(ft.Page, "views")


def test_native_clipboard_available():
    assert hasattr(ft, "Clipboard")
    from flet.controls.client_action import shared_service

    assert callable(shared_service)
