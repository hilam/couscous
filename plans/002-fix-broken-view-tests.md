# Plano 002: Corrigir 12 testes de view quebrados — PageContext requer `session`

> **Instruções ao executor**: Siga este plano passo a passo. Execute todo
> comando de verificação e confirme o resultado esperado antes de passar para
> o próximo passo. Se algo na seção "Condições STOP" ocorrer, pare e reporte
> — não improvise. Quando terminar, atualize a linha de status deste plano
> em `plans/README.md`.
>
> **Verificação de deriva (execute primeiro)**: `git diff --stat c24a31f..HEAD -- tests/test_about_view.py tests/test_home.py tests/test_login_view.py tests/test_register_view.py tests/conftest.py`
> Se qualquer arquivo no escopo mudou desde que este plano foi escrito,
> compare os excertos de "Estado atual" contra o código vivo antes de
> prosseguir; em caso de incompatibilidade, trate como condição STOP.

## Status

- **Prioridade**: P1
- **Esforço**: P
- **Risco**: BAIXO
- **Depende de**: nenhum
- **Categoria**: bug, tests
- **Planejado em**: commit `c24a31f`, 2026-07-12

## Por que isso é importante

12 testes de view falham com `TypeError: PageContext.__init__() missing 1 required positional argument: '_session_factory'`. Isso quebra a confiança no comando `make test` — ninguém pode verificar se mudanças nas views introduzem regressões. A falha ocorre porque os testes foram escritos antes do ADR-0003 (que tornou `session` obrigatório no `PageContext`) e nunca foram atualizados.

A correção é adicionar mocks de `session` nas construções de `PageContext`. É uma mudança puramente de teste, risco zero para o runtime.

## Estado atual

Arquivos relevantes:

- `tests/test_about_view.py` — 2 testes: `test_about_view_route`, `test_about_view_contains_navigation_bar`. Ambos constroem `PageContext(page=page, state=state)` sem `session`.
- `tests/test_home.py` — 3 testes: `test_home_view_route`, `test_home_view_contains_navigation_bar`, `test_home_view_contains_rss_feed_button`. Mesmo problema.
- `tests/test_login_view.py` — 4 testes falhando (de 5 totais): `test_login_view_route`, `test_login_view_contains_username_password_fields`, `test_login_view_contains_login_button`, `test_login_view_register_link`. Mesmo problema.
- `tests/test_register_view.py` — 3 testes falhando (de 5 totais: `test_register_view_route`, `test_register_view_contains_fields`, `test_register_view_contains_register_button`. Mesmo problema.

```python
# tests/test_about_view.py:28-29 (padrão que se repete em todos os 4 arquivos)
page = MagicMock()
state = State()
ctx = PageContext(page=page, state=state)  # ← ERRO: falta session e _session_factory
```

Convenções do repositório:

- `from unittest.mock import AsyncMock, MagicMock` — usado em outros testes de app (test_app.py, test_entry_list_view.py).
- Os testes de view mockam `page` como `MagicMock()` e `state` como `State()`.
- Para callbacks que usam `ctx.open_session()`, o session factory é necessário. Views como `login_view` e `register_view` criam sua própria sessão via `ctx.open_session()` nos callbacks.

## Comandos que você vai precisar

| Propósito | Comando | Esperado em caso de sucesso |
|-----------|---------|------------------------------|
| Testes | `uv run pytest tests/test_about_view.py tests/test_home.py tests/test_login_view.py tests/test_register_view.py -v` | todos passam (0 failed) |
| Testes gerais | `make test` | 0 failed (12 falhas a menos que antes) |
| Lint | `make lint` | "All checks passed!" |

## Escopo

**No escopo** (os únicos arquivos que você deve modificar):
- `tests/conftest.py` — adicionar fixture `page_context` reutilizável
- `tests/test_about_view.py`
- `tests/test_home.py`
- `tests/test_login_view.py`
- `tests/test_register_view.py`

**Fora de escopo** (NÃO toque):
- Qualquer arquivo em `app/` — o bug está apenas nos testes
- Outros arquivos de teste que já passam
- A classe `PageContext` em `app/context.py` — a API atual está correta

## Fluxo git

- Branch: `advisor/002-fix-broken-view-tests`
- Commits: `fix: corrige 12 testes de view quebrados após ADR-0003`
- NÃO faça push ou abra PR a menos que o operador o instrua.

## Passos

### Passo 1: Adicionar fixture `page_context` em `tests/conftest.py`

Adicione ao final de `tests/conftest.py`, antes da fixture `mock_oauth_config` existente:

```python
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def page_context():
    """Fixture que cria um PageContext com session e _session_factory mockados."""
    from app.context import PageContext
    from app.state import State

    page = MagicMock()
    state = State()
    session = AsyncMock()
    session_factory = MagicMock()

    ctx = PageContext(
        page=page,
        state=state,
        session=session,
        _session_factory=session_factory,
    )
    return ctx
```

Nota: este é o padrão de imports do `tests/test_app.py` (veja `from unittest.mock import AsyncMock, MagicMock`). Siga-o.

**Verificar**: `uv run python -c "import tests.conftest"` → exit 0 (conftest carrega sem erro).

### Passo 2: Atualizar `tests/test_about_view.py`

Substitua as construções manuais de `PageContext` pela fixture `page_context`. As funções de teste devem receber `page_context` como parâmetro:

```python
@pytest.mark.asyncio
async def test_about_view_route(page_context):
    view = await about_view(page_context)
    assert view.route == "/about"


@pytest.mark.asyncio
async def test_about_view_contains_navigation_bar(page_context):
    await about_view(page_context)
    assert page_context.page.navigation_bar is not None
```

Remova os imports não mais necessários (`from app.context import PageContext`, `from app.state import State`). Mantenha `from unittest.mock import MagicMock` se ainda for usado (não será — pode remover).

Adicione `import pytest` se ainda não estiver presente.

**Verificar**: `uv run pytest tests/test_about_view.py -v` → 2 passed.

### Passo 3: Atualizar `tests/test_home.py`

Mesmo padrão do passo 2: substitua `PageContext(page=page, state=state)` por usar o parâmetro `page_context`.

```python
@pytest.mark.asyncio
async def test_home_view_route(page_context):
    view = await home_view(page_context)
    assert view.route == "/"


@pytest.mark.asyncio
async def test_home_view_contains_navigation_bar(page_context):
    await home_view(page_context)
    assert page_context.page.navigation_bar is not None


@pytest.mark.asyncio
async def test_home_view_contains_rss_feed_button(page_context):
    view = await home_view(page_context)
    buttons = _find_controls(view, ft.FilledButton)
    assert any("Ver meus feeds" in str(getattr(b, "content", "")) for b in buttons)
```

A função auxiliar `_find_controls` permanece no arquivo.

**Verificar**: `uv run pytest tests/test_home.py -v` → 3 passed.

### Passo 4: Atualizar `tests/test_login_view.py`

Leia o arquivo antes de editar para conferir todos os testes afetados. Erros de login_view são 4 (de 5 totais — o teste `test_login_view_enter_submit` já passava ou falha por outro motivo? Verifique).

Cada teste que cria `PageContext(page=..., state=...)` deve receber `page_context` como parâmetro e usá-lo.

Exemplo para `test_login_view_route`:
```python
@pytest.mark.asyncio
async def test_login_view_route(page_context):
    view = await login_view(page_context)
    assert view.route == "/login"
```

**Cuidado**: Alguns testes em `test_login_view.py` podem precisar de configuração extra no mock de `page` (ex: `page.overlay`). A fixture `page_context` expõe o mock via `page_context.page` — use `page_context.page.overlay = MagicMock()` se necessário.

**Verificar**: `uv run pytest tests/test_login_view.py -v` → todos passed (mínimo 4, idealmente 5).

### Passo 5: Atualizar `tests/test_register_view.py`

Mesmo padrão: parametrizar com `page_context`.

**Verificar**: `uv run pytest tests/test_register_view.py -v` → todos passed (mínimo 3, idealmente 5).

### Passo 6: Verificação final

```bash
uv run pytest tests/test_about_view.py tests/test_home.py tests/test_login_view.py tests/test_register_view.py -v
# Esperado: todos passed, 0 failed, mínimo 12 testes passando

make lint
# Esperado: "All checks passed!"
```

## Plano de testes

Nenhum novo teste necessário. Estamos apenas corrigindo testes existentes que quebraram devido a uma mudança de API (`PageContext` agora requer `session`). A cobertura de comportamento não muda — apenas restauramos a verificabilidade.

## Critérios de conclusão

- [ ] `uv run pytest tests/test_about_view.py tests/test_home.py tests/test_login_view.py tests/test_register_view.py -v` → 0 failed
- [ ] `make lint` sai com "All checks passed!"
- [ ] Nenhum arquivo em `app/` foi modificado (`git status`)
- [ ] A fixture `page_context` existe em `tests/conftest.py`
- [ ] Os 4 arquivos de teste não importam mais `PageContext` ou `State` diretamente (ou importam apenas o necessário para outras fixtures locais)

## Condições STOP

Pare e reporte (não improvise) se:

- O código nos arquivos de teste não corresponde aos excertos em "Estado atual".
- Algum teste de `login_view.py` ou `register_view.py` falha por falta de mock para `ctx.open_session()` — isso indica que o callback submit está sendo chamado durante o teste e precisa de um session mock com `__aenter__` e `__aexit__`.
- `make test` mostra mais de 12 falhas antes da correção (não toque em testes fora do escopo).
- A fixture `page_context` causa conflito com fixtures existentes em conftest.py.

## Notas de manutenção

- Se novas views forem adicionadas, seus testes devem usar a fixture `page_context` de `conftest.py` — não recriem `PageContext` manualmente.
- Se a assinatura de `PageContext` mudar novamente, só a fixture em conftest.py precisa ser atualizada.
- Testes que precisam inspecionar interações específicas no mock de `session` podem acessar `page_context.session` diretamente (é um `AsyncMock`).
