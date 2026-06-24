import flet as ft


class TagChip(ft.Container):
    def __init__(self, tag: str, on_delete=None):
        self.tag = tag
        controls: list[ft.Control] = [
            ft.Text(
                tag,
                size=11,
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.W_500,
            ),
        ]
        if on_delete:
            controls.append(
                ft.IconButton(
                    ft.Icons.CLOSE,
                    icon_size=12,
                    width=16,
                    height=16,
                    padding=ft.Padding.all(0),
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE_70,
                        padding=ft.Padding.all(0),
                    ),
                    on_click=lambda e: on_delete(tag),
                )
            )

        super().__init__(
            content=ft.Row(
                controls=controls,
                spacing=2,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.CYAN_600,
            border_radius=ft.BorderRadius.all(12),
            padding=ft.Padding(
                left=8, top=2, right=8 if not on_delete else 2, bottom=2
            ),
        )
