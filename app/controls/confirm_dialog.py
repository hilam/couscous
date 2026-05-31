import flet as ft


class ConfirmDialog(ft.AlertDialog):
    def __init__(self, title: str, message: str, on_confirm):
        super().__init__()
        self.title = title
        self.content = ft.Text(message)
        self.actions = [
            ft.TextButton("Cancelar", on_click=self._cancel),
            ft.FilledButton("Confirmar", on_click=on_confirm),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _cancel(self, e):
        self.open = False
        self.update()
