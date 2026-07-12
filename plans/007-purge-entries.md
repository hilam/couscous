# Plano 007: Implementar limpeza automática de entries antigas (Purge)

> **Instruções ao executor**: Siga este plano passo a passo. Execute todo
> comando de verificação e confirme o resultado esperado antes de passar para
> o próximo passo. Se algo na seção "Condições STOP" ocorrer, pare e reporte
> — não improvise. Quando terminar, atualize a linha de status deste plano
> em `plans/README.md`.
>
> **Verificação de deriva (execute primeiro)**: `git diff --stat c24a31f..HEAD -- app/services/entry_service.py database/models/couscous.py app/views/feed_list_view.py app/controls/ confirm_dialog.py`
> Se qualquer arquivo no escopo mudou desde que este plano foi escrito,
> compare os excertos de "Estado atual" contra o código vivo antes de
> prosseguir; em caso de incompatibilidade, trate como condição STOP.

## Status

- **Prioridade**: P2
- **Esforço**: M
- **Risco**: BAIXO
- **Depende de**: plano 002 (testes de view funcionais ajudam a verificar UI do purge)
- **Categoria**: direction
- **Planejado em**: commit `c24a31f`, 2026-07-12

## Por que isso é importante

Entries RSS acumulam indefinidamente. Um usuário com 20 feeds que publicam 5 artigos/dia gera 3.000 entries/mês. Sem limpeza, o banco cresce, buscas ficam mais lentas, e a interface fica poluída com artigos de meses atrás.

O README lista "Limpeza do banco de dados (apagar notícias mais antigas)" como feature. Ela não existe no código. A implementação é surpreendentemente simples porque o modelo `Entry` já tem os campos necessários: `published` (data de publicação), `read` (0/1), e `important` (0/1 — entries importantes são preservadas).

## Estado atual

Modelo `Entry` em `database/models/couscous.py` já tem tudo que precisamos:
- `published: datetime | None` — data de publicação original
- `read: int` — 0 (não lida) ou 1 (lida)
- `important: int` — 0 (normal) ou 1 (importante, não deletar)
- `user_id: int` — escopo por usuário
- `added_by: str` — "system" para entries de refresh

Serviços existentes relevantes:
- `entry_service.py` — já tem `list_entries()`, `get_entry()`, `mark_read()`, `mark_important()`. NÃO tem função de purge.
- `feed_service.py` — já tem `list_feeds()`, `remove_feed()`. Padrão a seguir: usa `session.delete()` + `session.commit()`.

UI existente relevante:
- `feed_list_view.py` — já tem botão de refresh e botão de adicionar feed na AppBar. Pode ganhar botão de purge.
- `confirm_dialog.py` — já existe `ConfirmDialog` que podemos reutilizar para confirmar antes de deletar.

Convenções do repositório (CONTEXT.md):
- **Purge**: "Limpeza automática de entries antigas e lidas, configurável por período (dias/semanas/meses). Entries importantes não são afetadas."
- **Entry**: unidade de consumo. Pode estar lida ou não lida, importante ou normal.

## Comandos que você vai precisar

| Propósito | Comando | Esperado em caso de sucesso |
|-----------|---------|------------------------------|
| Typecheck | `make typecheck` | "Success: no issues found" |
| Lint | `make lint` | "All checks passed!" |
| Testes | `uv run pytest tests/test_entry_service.py -v` | todos passam |
| Testes purge | `uv run pytest tests/test_entry_service.py -k "purge" -v` | novos testes passam |

## Escopo

**No escopo**:
- `app/services/entry_service.py` — adicionar `purge_entries()` e `get_entry_counts_by_age()`
- `tests/test_entry_service.py` — adicionar testes para as novas funções
- `app/views/feed_list_view.py` — adicionar botão de purge com dialog de confirmação e seletor de período
- `app/controls/purge_dialog.py` — criar dialog de configuração de purge

**Fora de escopo** (NÃO toque):
- Purge automático agendado (cron/timer) — este plano implementa purge manual
- Configuração por feed (apenas global por usuário)
- `database/models/couscous.py` — sem novas colunas, sem migration
- `app/views/explore_view.py` — purge afeta todas as views que listam entries indiretamente

## Fluxo git

- Branch: `advisor/007-purge-entries`
- Commits:
  - `feat: adiciona purge_entries e get_entry_counts_by_age no entry_service`
  - `test: adiciona testes para purge_entries`
  - `feat: adiciona PurgeDialog e botão de purge na feed_list_view`
- NÃO faça push ou abra PR a menos que o operador o instrua.

## Passos

### Passo 1: Adicionar `purge_entries()` em `entry_service.py`

Adicione ao final de `app/services/entry_service.py`:

```python
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete


async def get_entry_counts_by_age(
    session, user_id: int, *, days: int = 30
) -> dict[str, int]:
    """Count entries by purge eligibility.

    Returns counts for: total, eligible (read + older than N days + not important),
    important (preserved), unread (preserved).
    """
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=days)

    total_result = await session.execute(
        select(func.count(Entry.id)).where(Entry.user_id == user_id)
    )
    total = total_result.scalar() or 0

    eligible_result = await session.execute(
        select(func.count(Entry.id)).where(
            Entry.user_id == user_id,
            Entry.read == 1,
            Entry.important == 0,
            Entry.published < cutoff,
        )
    )
    eligible = eligible_result.scalar() or 0

    important_result = await session.execute(
        select(func.count(Entry.id)).where(
            Entry.user_id == user_id,
            Entry.important == 1,
        )
    )
    important = important_result.scalar() or 0

    unread_result = await session.execute(
        select(func.count(Entry.id)).where(
            Entry.user_id == user_id,
            Entry.read == 0,
        )
    )
    unread = unread_result.scalar() or 0

    return {
        "total": total,
        "eligible": eligible,
        "important_preserved": important,
        "unread_preserved": unread,
    }


async def purge_entries(
    session, user_id: int, *, days: int = 30
) -> int:
    """Delete old read entries that are not marked important.

    Returns the number of entries deleted.
    """
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=days)

    result = await session.execute(
        delete(Entry).where(
            Entry.user_id == user_id,
            Entry.read == 1,
            Entry.important == 0,
            Entry.published < cutoff,
        )
    )
    await session.commit()
    return result.rowcount
```

Adicione `from sqlalchemy import delete` no topo (já deve ter `select`, `desc`). Verifique se `func` está importado (pode precisar de `from sqlalchemy import func`).

**Verificar**: `make typecheck` → "Success: no issues found".

### Passo 2: Adicionar testes em `tests/test_entry_service.py`

Adicione ao final do arquivo existente:

```python
from datetime import datetime, timedelta, timezone

from app.services.entry_service import get_entry_counts_by_age, purge_entries


async def _make_old_entry(db_session, user_id, feed_url, published_days_ago=60):
    """Helper: create an entry with a published date N days ago."""
    from database.models.couscous import Feed

    feed = Feed(url=feed_url, user_id=user_id)
    db_session.add(feed)
    await db_session.commit()

    published = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
        days=published_days_ago
    )
    entry = Entry(
        feed=feed_url,
        user_id=user_id,
        title=f"Old article {published_days_ago}d ago",
        link=f"https://example.com/old{published_days_ago}",
        published=published,
        last_updated=published,
        first_updated=published,
        first_updated_epoch=published,
        added_by="test",
        feed_order=0,
        read=1,
        important=0,
    )
    db_session.add(entry)
    await db_session.commit()
    return entry


@pytest.mark.asyncio
async def test_purge_deletes_old_read_entries(db_session):
    user = await _make_user(db_session)
    await _make_old_entry(db_session, user.id, "https://example.com/feed1", 60)
    await _make_old_entry(db_session, user.id, "https://example.com/feed2", 90)

    deleted = await purge_entries(db_session, user.id, days=30)
    assert deleted == 2


@pytest.mark.asyncio
async def test_purge_preserves_important(db_session):
    user = await _make_user(db_session)
    entry = await _make_old_entry(db_session, user.id, "https://example.com/feed1", 60)
    await mark_important(db_session, entry.id, user.id)

    deleted = await purge_entries(db_session, user.id, days=30)
    assert deleted == 0


@pytest.mark.asyncio
async def test_purge_preserves_unread(db_session):
    user = await _make_user(db_session)
    entry = await _make_old_entry(db_session, user.id, "https://example.com/feed1", 60)
    entry.read = 0
    await db_session.commit()

    deleted = await purge_entries(db_session, user.id, days=30)
    assert deleted == 0


@pytest.mark.asyncio
async def test_purge_preserves_recent(db_session):
    user = await _make_user(db_session)
    await _make_old_entry(db_session, user.id, "https://example.com/feed1", 5)

    deleted = await purge_entries(db_session, user.id, days=30)
    assert deleted == 0


@pytest.mark.asyncio
async def test_purge_zero_when_nothing_eligible(db_session):
    user = await _make_user(db_session)
    deleted = await purge_entries(db_session, user.id, days=30)
    assert deleted == 0


@pytest.mark.asyncio
async def test_get_entry_counts_by_age(db_session):
    user = await _make_user(db_session)
    await _make_old_entry(db_session, user.id, "https://example.com/feed1", 60)
    await _make_old_entry(db_session, user.id, "https://example.com/feed2", 60)
    entry = await _make_old_entry(db_session, user.id, "https://example.com/feed3", 60)
    await mark_important(db_session, entry.id, user.id)

    counts = await get_entry_counts_by_age(db_session, user.id, days=30)
    assert counts["total"] == 3
    assert counts["eligible"] == 2
    assert counts["important_preserved"] == 1
```

**Verificar**: `uv run pytest tests/test_entry_service.py -k "purge" -v` → 6 passed.

### Passo 3: Criar `PurgeDialog` em `app/controls/purge_dialog.py`

```python
"""Purge dialog — configure and execute entry cleanup."""

import asyncio

import flet as ft


class PurgeDialog(ft.AlertDialog):
    """Dialog to configure and confirm entry purge by age."""

    PERIODS = [
        ("7 dias", 7),
        ("30 dias", 30),
        ("90 dias", 90),
        ("180 dias", 180),
        ("365 dias", 365),
    ]

    def __init__(self, page: ft.Page, on_purge, get_counts_cb):
        super().__init__()
        self._page = page
        self._on_purge = on_purge
        self._get_counts = get_counts_cb

        self._period_dropdown = ft.Dropdown(
            label="Apagar entradas mais antigas que",
            options=[
                ft.dropdown.Option(str(days), label)
                for label, days in self.PERIODS
            ],
            value="30",
            expand=True,
            on_change=self._on_period_change,
        )

        self._counts_text = ft.Text("", size=13, color=ft.Colors.GREY)

        self.title = ft.Text("Limpeza do banco de dados")
        self.content = ft.Column(
            controls=[
                ft.Text(
                    "Remove entradas lidas que não estão marcadas como "
                    "importantes. Entradas não lidas e importantes são preservadas.",
                    size=13,
                ),
                self._period_dropdown,
                self._counts_text,
            ],
            width=400,
            tight=True,
            spacing=12,
        )
        self.actions = [
            ft.TextButton("Cancelar", on_click=self._cancel),
            ft.FilledButton("Limpar", on_click=self._confirm),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    async def load_counts(self):
        """Load and display purge eligibility counts."""
        days = int(self._period_dropdown.value or "30")
        counts = await self._get_counts(days)
        total = counts.get("total", 0)
        eligible = counts.get("eligible", 0)
        important = counts.get("important_preserved", 0)
        unread = counts.get("unread_preserved", 0)

        if eligible == 0:
            self._counts_text.value = (
                f"Total: {total} entradas. "
                f"Nenhuma elegível para limpeza ({important} importantes, "
                f"{unread} não lidas preservadas)."
            )
        else:
            self._counts_text.value = (
                f"Total: {total} entradas. "
                f"{eligible} serão removidas. "
                f"{important} importantes e {unread} não lidas serão preservadas."
            )
        self._counts_text.update()

    async def _on_period_change(self, e):
        await self.load_counts()

    def _cancel(self, e):
        self.open = False
        self.update()

    async def _confirm(self, e):
        self.open = False
        self.update()
        days = int(self._period_dropdown.value or "30")
        await self._on_purge(days)
```

**Verificar**: `make typecheck` → "Success: no issues found".

### Passo 4: Integrar botão de purge em `feed_list_view.py`

Adicione o import:
```python
from app.controls.purge_dialog import PurgeDialog
from app.services.entry_service import get_entry_counts_by_age, purge_entries
```

Adicione um handler de purge na função `feed_list_view()`:

```python
    async def open_purge_dialog(e):
        async def get_counts(days):
            async with ctx.open_session() as s:
                return await get_entry_counts_by_age(s, user_id, days=days)

        async def do_purge(days):
            async with ctx.open_session() as s:
                deleted = await purge_entries(s, user_id, days=days)
            snack = ft.SnackBar(
                content=ft.Text(f"{deleted} entradas removidas.")
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()
            await refresh(e)

        dlg = PurgeDialog(page, do_purge, get_counts)
        page.overlay.append(dlg)
        dlg.open = True
        await dlg.load_counts()
        page.update()
```

Adicione o botão na AppBar de `feed_list_view.py`, junto aos outros botões de action:

Na lista `actions` do `ft.AppBar` (aproximadamente linha 208), adicione:
```python
                    ft.IconButton(
                        ft.Icons.DELETE_SWEEP,
                        tooltip="Limpar entradas antigas",
                        on_click=open_purge_dialog,
                    ),
```

**Verificar**: `make typecheck` → "Success: no issues found". `make lint` → "All checks passed!".

### Passo 5: Verificação final

```bash
uv run pytest tests/test_entry_service.py -k "purge" -v
# Esperado: todos os 6 novos testes passam

make typecheck
# Esperado: "Success: no issues found"

make lint
# Esperado: "All checks passed!"
```

## Plano de testes

Os 6 novos testes em `tests/test_entry_service.py` cobrem:

| Teste | Caso |
|-------|------|
| `test_purge_deletes_old_read_entries` | Happy path: 2 entries antigas e lidas são deletadas |
| `test_purge_preserves_important` | Entrada importante não é deletada |
| `test_purge_preserves_unread` | Entrada não lida não é deletada |
| `test_purge_preserves_recent` | Entrada recente (<30 dias) não é deletada |
| `test_purge_zero_when_nothing_eligible` | Nenhuma entrada para deletar → 0 |
| `test_get_entry_counts_by_age` | Contagem correta de elegíveis/importantes |

## Critérios de conclusão

- [ ] `purge_entries()` e `get_entry_counts_by_age()` existem em `entry_service.py`
- [ ] 6 novos testes passam em `test_entry_service.py -k "purge"`
- [ ] `PurgeDialog` existe em `app/controls/purge_dialog.py`
- [ ] Botão de purge aparece na AppBar de `feed_list_view.py`
- [ ] `make typecheck` → "Success: no issues found"
- [ ] `make lint` → "All checks passed!"
- [ ] Nenhum arquivo fora da lista de escopo foi modificado

## Condições STOP

Pare e reporte (não improvise) se:

- `delete(Entry)` não funciona com SQLModel/SQLAlchemy async — pode precisar de `await session.execute(delete(...))` em vez de chamada direta.
- Os testes de purge interferem com outros testes — se `test_entry_service.py` completo falhar após adicionar os novos testes, pode ser que o `db_session` compartilhado tenha efeitos colaterais do delete.
- O `PurgeDialog` causa importação circular com `feed_list_view.py` — verifique se está importando apenas de `.controls` e `.services`, não de `.views`.

## Notas de manutenção

- Purge é manual (acionado por botão). Para purge automático agendado, seria necessário um background task ou job. O modelo atual (single-user, desktop) não tem infra de scheduler — isso é um enhancement futuro.
- O cutoff é baseado em `published` (data de publicação original do artigo), não em `first_updated` (quando entrou no sistema). Se um feed republica artigos antigos, eles podem ser deletados imediatamente se `published` for antigo.
- O purge deleta em cascata? `EntryTag` tem `ondelete="CASCADE"` no modelo, então tags de entries deletadas são removidas automaticamente. Mas `search_vector` (tsvector) é uma coluna generated — não requer limpeza separada.
