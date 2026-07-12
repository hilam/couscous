# Plano 004: Paralelizar `refresh_all_feeds` com limite de concorrência

> **Instruções ao executor**: Siga este plano passo a passo. Execute todo
> comando de verificação e confirme o resultado esperado antes de passar para
> o próximo passo. Se algo na seção "Condições STOP" ocorrer, pare e reporte
> — não improvise. Quando terminar, atualize a linha de status deste plano
> em `plans/README.md`.
>
> **Verificação de deriva (execute primeiro)**: `git diff --stat c24a31f..HEAD -- app/services/refresh_service.py tests/test_refresh_service.py`
> Se qualquer arquivo no escopo mudou desde que este plano foi escrito,
> compare os excertos de "Estado atual" contra o código vivo antes de
> prosseguir; em caso de incompatibilidade, trate como condição STOP.

## Status

- **Prioridade**: P2
- **Esforço**: P
- **Risco**: BAIXO
- **Depende de**: nenhum
- **Categoria**: perf
- **Planejado em**: commit `c24a31f`, 2026-07-12

## Por que isso é importante

`refresh_all_feeds` itera sequencialmente por todos os feeds do usuário e os atualiza um por um via HTTP. Para um usuário com 20 feeds, isso significa 20+ segundos de refresh bloqueante. O `state.loading` fica `True` durante todo o período, travando a UI.

O ADR-0005 menciona que o refresh deveria ser "em paralelo, com limite de concorrência". A implementação atual é sequencial. A correção é trivial: usar `asyncio.gather` com `Semaphore` para limitar concorrência.

A única sutileza: cada `refresh_single_feed` faz `await session.commit()` na mesma sessão. Com execução paralela, commits concorrentes na mesma AsyncSession causariam race conditions. A solução é abrir uma sessão separada para cada feed — mas `refresh_single_feed` já recebe uma session como parâmetro, e os callbacks nas views já abrem sessões via `ctx.open_session()`. A abordagem mais simples: dar a cada feed sua própria sessão dentro da task paralela.

## Estado atual

```python
# app/services/refresh_service.py:47-51
async def refresh_all_feeds(
    session: AsyncSession,
    user_id: int,
    client: httpx.AsyncClient | None = None,
) -> None:
    result = await session.execute(select(Feed).where(Feed.user_id == user_id))
    feeds = result.scalars().all()

    for feed in feeds:
        await refresh_single_feed(session, feed, client=client)
```

O problema: loop sequencial. A função `refresh_single_feed` (linhas 54-96) faz operações de banco (`session.execute`, `session.add`, `session.commit`) e HTTP (`client.get`) — ambas I/O intensivas.

Convenções do repositório:

- `get_db_session()` em `database/service/database.py` — async context manager que cria uma nova AsyncSession.
- Padrão usado em callbacks de view: `async with ctx.open_session() as s: ... await refresh_single_feed(s, feed)` (feed_list_view.py:125).
- O `httpx.AsyncClient` é compartilhável entre tasks — ele já gerencia um pool de conexões internamente.
- `asyncio.Semaphore` é a ferramenta canônica para limitar concorrência.

## Comandos que você vai precisar

| Propósito | Comando | Esperado em caso de sucesso |
|-----------|---------|------------------------------|
| Typecheck | `make typecheck` | "Success: no issues found" |
| Testes | `uv run pytest tests/test_refresh_service.py -v` | todos passam |
| Lint | `make lint` | "All checks passed!" |

## Escopo

**No escopo** (os únicos arquivos que você deve modificar):
- `app/services/refresh_service.py` — refatorar `refresh_all_feeds`

**Fora de escopo** (NÃO toque):
- `refresh_single_feed` — a função individual continua igual
- Views que chamam `refresh_all_feeds` — a assinatura não muda
- `app/views/feed_list_view.py` — já chama `refresh_all_feeds(s, user_id)` corretamente

## Fluxo git

- Branch: `advisor/004-parallel-refresh-all-feeds`
- Commits: `perf: paraleliza refresh_all_feeds com Semaphore(5)`
- NÃO faça push ou abra PR a menos que o operador o instrua.

## Passos

### Passo 1: Refatorar `refresh_all_feeds` para execução paralela com semáforo

Substitua o loop sequencial em `app/services/refresh_service.py`:

```python
async def refresh_all_feeds(
    session: AsyncSession,
    user_id: int,
    client: httpx.AsyncClient | None = None,
) -> None:
    """Refresh all feeds for a user in parallel with concurrency limit.

    Each feed gets its own database session to avoid concurrent commits
    on the same AsyncSession.
    """
    from database.service.database import get_db_session

    result = await session.execute(select(Feed).where(Feed.user_id == user_id))
    feeds = result.scalars().all()

    if not feeds:
        return

    close_client = False
    if client is None:
        client = httpx.AsyncClient(timeout=30)
        close_client = True

    # ponytail: Semaphore(5), make configurable if throughput matters
    semaphore = asyncio.Semaphore(5)

    async def _refresh_one(feed: Feed) -> None:
        async with semaphore:
            async with get_db_session() as feed_session:
                await refresh_single_feed(feed_session, feed, client=client)

    try:
        await asyncio.gather(*(_refresh_one(f) for f in feeds))
    finally:
        if close_client:
            await client.aclose()
```

O que mudou:
1. Loop `for` → `asyncio.gather` com tasks por feed.
2. Cada feed ganha sua própria sessão via `get_db_session()` — evita race condition em commits.
3. `Semaphore(5)` limita a 5 feeds simultâneos (evita sobrecarregar servidores e conexões HTTP).
4. `httpx.AsyncClient` é criado fora do loop e compartilhado (httpx é thread-safe e async-safe para compartilhamento).

O import de `asyncio` já existe no topo do arquivo. Adicione `from database.service.database import get_db_session` no topo.

**Verificar**: `make typecheck` → "Success: no issues found".

### Passo 2: Verificar que testes existentes ainda passam

```bash
uv run pytest tests/test_refresh_service.py -v
# Esperado: todos passam. Os testes injetam client via parâmetro client=,
# então o refresh paralelo usa o mesmo MockTransport — as respostas são
# determinísticas e a concorrência não causa flakiness.
```

**Verificar**: `uv run pytest tests/test_refresh_service.py -v` → todos passam.

### Passo 3: Verificar lint

```bash
make lint
# Esperado: "All checks passed!"
```

## Plano de testes

Nenhum novo teste necessário. Os testes existentes em `tests/test_refresh_service.py` já cobrem:
- `test_refresh_all_feeds`: cria 3 feeds, verifica que 3 entries foram criadas.
- Como os testes usam `httpx.MockTransport` (respostas instantâneas), a paralelização não altera o comportamento determinístico.

O risco de flakiness é zero porque o MockTransport responde imediatamente e `asyncio.gather` preserva a ordem de resultados.

## Critérios de conclusão

- [ ] `make typecheck` sai com "Success: no issues found"
- [ ] `uv run pytest tests/test_refresh_service.py -v` → todos passam
- [ ] `make lint` sai com "All checks passed!"
- [ ] `grep -n "for feed in feeds" app/services/refresh_service.py` não retorna o loop sequencial antigo
- [ ] `grep -n "Semaphore" app/services/refresh_service.py` retorna a nova implementação
- [ ] Nenhum arquivo fora da lista de escopo foi modificado

## Condições STOP

Pare e reporte (não improvise) se:

- `test_refresh_all_feeds` começa a falhar após a paralelização — isso indicaria que o MockTransport não é seguro para uso concorrente (improvável, mas possível).
- `make typecheck` reporta erro sobre `asyncio.Semaphore` ou `get_db_session` — verifique imports.
- O código em "Estado atual" não corresponde ao que está no arquivo.

## Notas de manutenção

- O valor 5 do `Semaphore` foi escolhido como padrão seguro para não sobrecarregar servidores de feed. Se um usuário tiver 100+ feeds, 5 requisições simultâneas é conservador. Pode ser tornado configurável via `FeedMetadata` ou variável de ambiente no futuro.
- Se `get_db_session()` criar um pool de conexões por chamada (atualmente cada chamada cria um `async_sessionmaker`), isso pode criar muitos pools sob concorrência. Monitore com `docker stats` durante refresh — se o número de conexões Postgres disparar, extraia o `async_sessionmaker` para o nível de módulo em `database.py`.
- `refresh_all_feeds` agora ignora exceções de feeds individuais (o `gather` padrão propaga a primeira exceção). Se quiser que um feed com erro não impeça os outros, envolva `_refresh_one` com try/except. Isso é um enhancement futuro.
