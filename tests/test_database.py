"""Testes para o módulo database/service/database.py"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_init_async_db_does_not_drop_existing_data():
    """init_async_db deve preservar dados — drop_all NÃO deve ser chamado."""
    mock_conn = AsyncMock()

    mock_begin_ctx = AsyncMock()
    mock_begin_ctx.__aenter__.return_value = mock_conn

    mock_engine = MagicMock()
    mock_engine.begin.return_value = mock_begin_ctx

    with patch("database.service.database.engine", mock_engine):
        from database.service.database import init_async_db

        await init_async_db()

        called_callables = [
            c.args[0] if c.args else None for c in mock_conn.run_sync.call_args_list
        ]
        assert len(called_callables) == 1, (
            f"Esperado apenas create_all, mas foram {len(called_callables)} chamadas"
        )
