## Context

`refresh_all_feeds` em `app/services/refresh_service.py` faz um loop `for feed in feeds: await refresh_single_feed(...)`. Cada chamada faz I/O de rede (HTTP GET) e I/O de banco (SELECT, INSERT, COMMIT). O loop sequencial subutiliza o I/O — enquanto um feed espera resposta HTTP, outros feeds poderiam estar sendo baixados.

## Goals / Non-Goals

**Goals:**
- Refresh de N feeds em ~tempo do feed mais lento (vs N × tempo médio)
- `asyncio.Semaphore(5)` protege servidores de feed e conexões HTTP
- Nenhuma mudança na API pública
- Nenhuma race condition em commits de banco

**Non-Goals:**
- Não alterar `refresh_single_feed` (função individual)
- Não alterar views ou callers
- Não propagar exceções de feeds individuais como falha total (futuro enhancement)

## Decisions

| Decisão | Alternativa | Por quê |
|---------|-------------|---------|
| `get_db_session()` por feed | Compartilhar mesma sessão com lock | Commits concorrentes na mesma AsyncSession causam race conditions; sessão própria por feed é segura |
| `asyncio.Semaphore(5)` | Sem limitação / número maior | 5 é conservador para não sobrecarregar servidores de feed; evita 20+ conexões HTTP simultâneas |
| `asyncio.gather` com tasks | `asyncio.wait` / `asyncio.as_completed` | `gather` é a API mais direta; coleta resultados em ordem; exceção em qualquer feed propaga |

## Risks / Trade-offs

- **Risco**: `get_db_session()` cria novo pool de conexão por chamada. Sob concorrência alta (100+ feeds), pode criar muitos pools. → Mitigação: monitorar com `docker stats`; se necessário, extrair `async_sessionmaker` para nível de módulo.
- **Risco**: Exceção em um feed cancela todos os outros (comportamento padrão do `gather`). → Aceito por enquanto; enhancement futuro: try/except por feed.
- **Risco**: MockTransport nos testes é thread-safe? httpx mock responde instantaneamente, race window é zero.
