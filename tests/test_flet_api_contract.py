"""Contrato de APIs do Flet 1.x.

Trava o app contra o retorno às chamadas inexistentes (page.open,
page.run_javascript, page.close_bottom_sheet) que quebravam em runtime na
era 0.x, e afirma a presença das APIs 1.x nas quais convergimos
(page.show_dialog, page.pop_dialog, ft.Clipboard + shared_service).

Nota: o app usa page.views (app/app.py) como campo de dataclass acessível
na INSTÂNCIA. A asserção "views" abaixo trava o contrato real: views deve
permanecer campo dataclass de ft.Page — se o Flet remover a API, o teste
falha antes da regressão chegar a app/app.py.
"""

import dataclasses

import flet as ft


def test_show_dialog_and_pop_dialog_exist():
    assert hasattr(ft.Page, "show_dialog")
    assert hasattr(ft.Page, "pop_dialog")


def test_removed_zero_x_apis_are_absent():
    assert not hasattr(ft.Page, "open")
    assert not hasattr(ft.Page, "run_javascript")
    assert not hasattr(ft.Page, "close_bottom_sheet")
    assert not hasattr(ft.Page, "close_dialog")


def test_page_views_is_dataclass_field():
    """Garante que page.views continua disponível como campo dataclass de ft.Page.

    O app depende de page.views.clear()/append() para a navegação multi-view
    (app/app.py). Um teste com hasattr(ft.Page, "views") seria vazio: False na
    classe por artefato do default_factory mesmo com a API existindo. Esta
    trava afirma o contrato real e falha se o Flet remover o campo.
    """
    assert "views" in {f.name for f in dataclasses.fields(ft.Page)}


def test_native_clipboard_available():
    assert hasattr(ft, "Clipboard")
    from flet.controls.client_action import shared_service

    assert callable(shared_service)
