from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractAsyncContextManager

    import flet as ft
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.state import State


@dataclass
class PageContext:
    page: ft.Page
    state: State
    session: AsyncSession | None = None
    _session_factory: Callable[[], AbstractAsyncContextManager[AsyncSession]] | None = (
        None
    )

    @asynccontextmanager
    async def new_session(self) -> AbstractAsyncContextManager[AsyncSession]:
        _msg = "No session factory configured"
        if self._session_factory is None:
            raise RuntimeError(_msg)
        async with self._session_factory() as session:
            yield session
