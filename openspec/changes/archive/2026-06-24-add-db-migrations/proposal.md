## Why

Toda inicialização do app destrói e recria o banco (`drop_all` + `create_all`), apagando dados do usuário. Além disso, não há sistema de versionamento de schema — qualquer mudança nos modelos exige recriação manual do banco. O `openspec/config.yaml` menciona Alembic mas nunca foi configurado.

## What Changes

- **Remover** `drop_all` do `init_async_db()` — dados não serão mais apagados no startup
- **Adicionar** Alembic como dependência e configurar ambiente de migrations assíncrono
- **Criar** migration inicial (`001_initial`) com o snapshot dos 6 modelos atuais
- **Adicionar** comandos no Makefile: `db-migrate-create`, `db-migrate-up`, `db-migrate-down`, `db-migrate-status`
- Migrations são aplicadas **manualmente** (não no startup automático)
- Testes continuam usando `create_all`/`drop_all` no banco `couscous_test`, sem Alembic

## Capabilities

### New Capabilities

- `db-migrations`: Sistema de versionamento de schema do banco de dados via Alembic, com migrations assíncronas, comandos Makefile para criar/aplicar/reverter, e migration inicial cobrindo os 6 modelos existentes (User, Feed, Entry, FeedMetadata, Category, EntryTag).

### Modified Capabilities

<!-- Nenhum spec existente tem mudança de requisito. A spec `auto-db-init` já requer preservação de dados no cenário "Existing tables"; o código atual é que a viola. A correção alinha implementação com o spec sem alterar os requisitos. -->

## Impact

- `database/service/database.py`: remover `drop_all` do `init_async_db()`
- `pyproject.toml`: adicionar `alembic` às dependências
- `Makefile`: novos targets `db-migrate-create`, `db-migrate-up`, `db-migrate-down`, `db-migrate-status`
- Novos arquivos: `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, `alembic/versions/001_initial.py`
- `openspec/specs/db-migrations/`: novo spec
- Nenhum breaking change — `init_async_db()` mantém `create_all` (idempotente) para garantir tabelas em fresh installs
