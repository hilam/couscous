## Context

Atualmente `make typecheck` reporta 10 erros mypy em 5 arquivos. Os erros se agrupam em 3 causas raiz:

1. **Tipo errado em `get_db_session` (5 erros)**: A função retorna `-> AsyncGenerator[AsyncSession]`, mas `@asynccontextmanager` transforma o retorno em `AbstractAsyncContextManager[AsyncSession]`. `AsyncGenerator` não tem `__aenter__`/`__aexit__` — só funciona com `async for`, não `async with`. O efeito cascata atinge `context.py:28` (2 erros) e `app.py:78,81,110` (3 erros).

2. **Coroutine OAuth não awaitada (1 erro)**: `_oauth_click` é síncrono mas chama `page.launch_url(uri)` que é `async def`. O coroutine é criado e descartado — a URL nunca abre. Bug funcional real.

3. **Variância de `list[Control]` vs `list[LayoutControl]` (4 erros)**: Mypy infere `list[LayoutControl]` para `form_controls` porque os itens iniciais são `LayoutControl`. `list` é invariante, então `.extend(get_oauth_buttons(...))` (que retorna `list[Control]`) e `Column(controls=form_controls)` (que espera `list[Control]`) falham.

## Goals / Non-Goals

**Goals:**
- `make typecheck` deve retornar zero erros
- Corrigir bug real dos botões OAuth (launch_url nunca executado)
- Manter compatibilidade total com o comportamento em runtime existente (exceto OAuth)

**Non-Goals:**
- Adicionar novas regras de mypy ou aumentar severidade
- Refatorar a arquitetura de sessões ou o sistema de rotas
- Alterar a interface pública de `get_db_session()`

## Decisions

### Decisão 1: Corrigir tipo de retorno de get_db_session para AbstractAsyncContextManager

**Escolha**: Alterar a anotação de retorno em `database/service/database.py` de `-> AsyncGenerator[AsyncSession]` para `-> AbstractAsyncContextManager[AsyncSession]`. Em `app/context.py`, alterar `_session_factory: Callable[[], AsyncGenerator[AsyncSession]] | None` para `Callable[[], AbstractAsyncContextManager[AsyncSession]] | None`.

**Alternativa considerada**: Remover a anotação de retorno e deixar mypy inferir. Rejeitada — anotações explícitas documentam a API e ajudam outros desenvolvedores.

**Alternativa considerada**: Usar `AsyncContextManager[AsyncSession]` (sem Abstract). Rejeitada — `@asynccontextmanager` retorna o tipo abstrato, e `AbstractAsyncContextManager` é o tipo base correto.

### Decisão 2: Tornar _oauth_click assíncrono

**Escolha**: Declarar `async def _oauth_click(...)` e usar `await page.launch_url(uri)`. Flet suporta nativamente `on_click` handlers assíncronos — o framework detecta coroutines e as awaita automaticamente.

**Alternativa considerada**: Usar `page.run_task(page.launch_url(uri))` para agendar a coroutine sem tornar o handler async. Rejeitada — `run_task` é menos direto e `page.launch_url` é naturalmente uma operação awaitable.

**Alternativa considerada**: Suprimir o erro com `# type: ignore[unused-coroutine]`. Rejeitada — isso esconderia o bug real (URL nunca abre). O mypy está correto em apontar o problema.

### Decisão 3: Anotar form_controls como list[ft.Control]

**Escolha**: Adicionar anotação explícita `form_controls: list[ft.Control] = [...]` em `login_view.py` e `register_view.py`. Isso resolve ambos os erros de variância de uma vez, já que `list[Control]` aceita `.extend(Iterable[Control])` e é aceito por `Column(controls=list[Control])`.

**Alternativa considerada**: Usar `Sequence[ft.Control]` que é covariante. Rejeitada — `list` é necessário porque `.extend()` é usado, e `Column.controls` espera `list[Control]`.

## Risks / Trade-offs

- **Mudança de `_oauth_click` para async** → Se Flet tiver alguma limitação com handlers async em versões antigas, pode quebrar. Mitigação: Flet 0.85.2 (versão atual do projeto) suporta handlers async nativamente, verificado no código fonte do Flet.
- **Alteração de tipo em `get_db_session`** → `AbstractAsyncContextManager` é mais abstrato que `AsyncGenerator`. Se algum código externo depender da anotação anterior, pode quebrar. Mitigação: a função só é usada internamente, e `async with` funciona identicamente com ambos os tipos.
- **Regressão em runtime** → As mudanças são puramente de anotação (exceto OAuth). Mitigação: executar `make test` após as alterações para confirmar que todos os testes passam.
