from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.couscous import User


class State:
    def __init__(self):
        self.user: User | None = None
        self.active_feed_url: str | None = None
        self.loading: bool = False
        self.theme_mode: str = "light"
        self.font_scale: float = 1.0
