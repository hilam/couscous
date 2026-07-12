## Context

`feed_browser.py` (237 linhas) contém 5 funções puras de operação do `ExploreState` dataclass. São funções de integração que recebem `session + ExploreState` e retornam novo `ExploreState`. Nenhuma depende de Flet, o que as torna testáveis diretamente com a fixture `db_session` (PostgreSQL real via asyncpg).

O repositório já tem padrões consolidados de teste de serviço em `tests/test_entry_service.py`, factories em `tests/test_factory.py`, e a fixture `db_session` em `tests/conftest.py`.

## Goals / Non-Goals

**Goals:**
- Cobertura >80% do módulo `app.services.feed_browser`
- Mínimo 11 testes distribuídos entre as 5 funções
- Seguir o padrão de `tests/test_entry_service.py` (imports, estrutura, fixtures)

**Non-Goals:**
- Nenhuma alteração em `app/services/feed_browser.py` ou qualquer outro arquivo de produção
- Nenhum mock de banco — usa `db_session` real (teste de integração)

## Decisions

| Decisão | Alternativa | Por quê |
|---------|-------------|---------|
| `db_session` real (PostgreSQL) | `AsyncMock` de sessão | Funções chamam `list_recent()`, `search_entries()`, etc., que executam SQL real com tsvector — mock seria frágil e impreciso |
| Factories de `test_factory.py` | Criar dados inline | Padrão já estabelecido; `make_user`, `make_feed`, `make_entry` reduzem boilerplate |
| Agrupar testes por função (load, select_category, etc.) | Agrupar por cenário | Mais fácil de mapear cobertura para cada função; nome dos testes já indica o cenário |

## Risks / Trade-offs

- **Risco**: `search()` depende de tsvector do PostgreSQL. A fixture `db_session` já cria a coluna via `_add_search_vector_column()`, mas se o banco de teste não tiver a extensão, o teste falha. → Mitigação: executar `make db-up` antes (PostgreSQL 16 inclui tsvector por padrão).
- **Risco**: Testes com `db_session` são ~0.5-1s cada (setup/teardown do banco). 11+ testes → ~10-15s. → Aceitável para a cobertura obtida; mitigação futura: fixture session-scoped.
