"""Teste de deriva: `alembic upgrade head` (modo offline) vs metadata SQLModel.

O script DDL completo é aplicado num schema scratch `drift` dentro do banco
`couscous_test` — nunca no schema `public`, nunca no banco `couscous`.
"""

import shutil
import subprocess
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel

from conftest import DB_URL

import database.models.couscous  # noqa: F401 — registra as tabelas no metadata

REPO_ROOT = Path(__file__).resolve().parents[1]
DRIFT_SCHEMA = "drift"
MODEL_TABLES = {"users", "feeds", "entries", "categories", "entry_tags"}
EXPECTED_TABLES = MODEL_TABLES | {"alembic_version"}
DDL_MANAGED_EXTRA_COLUMNS = {("entries", "search_vector")}
DDL_MANAGED_EXTRA_INDEXES = {"entries": {"idx_entries_search_vector"}}


def _alembic_offline_script() -> str:
    uv = shutil.which("uv") or str(Path.home() / ".local/bin/uv")
    proc = subprocess.run(
        [uv, "run", "alembic", "upgrade", "head", "--sql"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert proc.returncode == 0, f"alembic upgrade head --sql falhou:\n{proc.stderr}"
    return proc.stdout


def _split_statements(script: str) -> list[str]:
    statements: list[str] = []
    buffer: list[str] = []
    for line in script.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        if stripped in ("BEGIN;", "BEGIN", "COMMIT;", "COMMIT"):
            continue
        buffer.append(line)
        if stripped.endswith(";"):
            statement = "\n".join(buffer).strip().rstrip(";").strip()
            if statement:
                statements.append(statement)
            buffer = []
    assert not buffer, f"statement pendente no script alembic: {buffer}"
    return statements


def _read_schema(connection) -> tuple[set, dict, dict]:
    inspector = inspect(connection)
    tables = set(inspector.get_table_names(schema=DRIFT_SCHEMA))
    columns = {
        table: {column["name"] for column in inspector.get_columns(table, schema=DRIFT_SCHEMA)}
        for table in tables
    }
    indexes = {
        table: {
            index["name"]
            for index in inspector.get_indexes(table, schema=DRIFT_SCHEMA)
            if index["name"]
            not in {
                c["name"]
                for c in inspector.get_unique_constraints(table, schema=DRIFT_SCHEMA)
            }
        }
        for table in tables
    }
    return tables, columns, indexes


@pytest_asyncio.fixture
async def drift_engine() -> AsyncEngine:
    engine = create_async_engine(DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.execute(text(f"DROP SCHEMA IF EXISTS {DRIFT_SCHEMA} CASCADE"))
    async with engine.begin() as conn:
        await conn.execute(text(f"CREATE SCHEMA {DRIFT_SCHEMA}"))
        await conn.execute(text(f"SET search_path = {DRIFT_SCHEMA}"))
        for statement in _split_statements(_alembic_offline_script()):
            await conn.execute(text(statement))
    yield engine
    async with engine.begin() as conn:
        await conn.execute(text(f"DROP SCHEMA IF EXISTS {DRIFT_SCHEMA} CASCADE"))
    await engine.dispose()


@pytest.mark.asyncio
async def test_migrated_schema_matches_metadata(drift_engine: AsyncEngine) -> None:
    async with drift_engine.connect() as conn:
        tables, columns, indexes = await conn.run_sync(
            lambda sync_conn: _read_schema(sync_conn)
        )

    assert tables == EXPECTED_TABLES

    assert "search_vector" in columns["entries"], (
        "regressão do bug de f8979a38e1d0: search_vector ausente no head migrado"
    )
    assert "idx_entries_search_vector" in indexes["entries"], (
        "regressão do bug de f8979a38e1d0: índice GIN ausente no head migrado"
    )

    for table_name, table in SQLModel.metadata.tables.items():
        declared_columns = {column.name for column in table.columns}
        migrated_columns = columns[table_name]
        tolerated = {name for table, name in DDL_MANAGED_EXTRA_COLUMNS if table == table_name}

        assert declared_columns - migrated_columns == set(), (
            f"{table_name}: colunas do metadata ausentes no schema migrado: "
            f"{declared_columns - migrated_columns}"
        )
        assert migrated_columns - declared_columns == tolerated, (
            f"{table_name}: colunas extras inesperadas no schema migrado: "
            f"{migrated_columns - declared_columns - tolerated}"
        )

        declared_indexes = {index.name for index in table.indexes}
        migrated_indexes = indexes[table_name]
        tolerated_indexes = DDL_MANAGED_EXTRA_INDEXES.get(table_name, set())

        assert declared_indexes - migrated_indexes == set(), (
            f"{table_name}: índices dos models ausentes no schema migrado: "
            f"{declared_indexes - migrated_indexes}"
        )
        assert migrated_indexes - declared_indexes == tolerated_indexes, (
            f"{table_name}: índices extras inesperados no schema migrado: "
            f"{migrated_indexes - declared_indexes - tolerated_indexes}"
        )
