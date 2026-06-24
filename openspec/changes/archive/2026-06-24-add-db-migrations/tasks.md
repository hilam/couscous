## 1. Git Setup e Planejamento

- [x] 1.1 Criar branch `chore/add-db-migrations`
- [x] 1.2 Fazer commit do proposal (`docs(planning): generate proposal`)
- [x] 1.3 Fazer commit dos specs (`docs(planning): generate specs`)
- [x] 1.4 Fazer commit do design (`docs(planning): generate design`)
- [x] 1.5 Fazer commit do qa-plan (`docs(planning): generate qa-plan`)

## 2. Dependência Alembic

- [x] 2.1 Adicionar `alembic` ao `pyproject.toml` em `[project] dependencies`
- [x] 2.2 Executar `uv sync` para instalar a nova dependência
- [x] 2.3 Fazer commit (`chore: adiciona alembic como dependência`)

## 3. Configuração do Ambiente Alembic

- [x] 3.1 Inicializar Alembic com `uv run alembic init alembic` (cria `alembic.ini` e `alembic/`)
- [x] 3.2 Substituir `alembic/env.py` pela versão assíncrona com `SQLModel.metadata` e import dos 6 modelos
- [x] 3.3 Ajustar `alembic.ini` — `sqlalchemy.url` como placeholder (sobrescrito pelo `env.py`)
- [x] 3.4 Fazer commit (`chore: configura ambiente alembic assíncrono com SQLModel`)

## 4. Migration Inicial

- [x] 4.1 Executar `uv run alembic revision --autogenerate -m "initial"` para gerar `001_initial.py`
- [x] 4.2 Revisar a migration gerada — verificar se todas as 6 tabelas, colunas, PKs e FKs estão corretas
- [x] 4.3 Fazer commit (`chore: adiciona migration inicial com schema dos 6 modelos`)

## 5. Corrigir init_async_db

- [x] 5.1 Remover `await conn.run_sync(SQLModel.metadata.drop_all)` de `database/service/database.py:init_async_db()`
- [x] 5.2 Verificar que `create_all` permanece (garante fresh install sem migrations)
- [x] 5.3 Fazer commit (`fix: remove drop_all do init_async_db para preservar dados`)

## 6. Comandos Makefile

- [x] 6.1 Adicionar target `db-migrate-create` — `uv run alembic revision --autogenerate -m "$(name)"` com validação do parâmetro `name`
- [x] 6.2 Adicionar target `db-migrate-up` — `uv run alembic upgrade head`
- [x] 6.3 Adicionar target `db-migrate-down` — `uv run alembic downgrade -1`
- [x] 6.4 Adicionar target `db-migrate-status` — `uv run alembic current`
- [x] 6.5 Fazer commit (`chore: adiciona comandos de migration ao Makefile`)

## 7. Documentação

- [x] 7.1 Atualizar `AGENTS.md` com fluxo de migrations: fresh install (`make db-migrate-up` antes de `make run-web`), mudança de schema (`make db-migrate-create` → `make db-migrate-up`)
- [x] 7.2 Atualizar `README.md` se necessário (menção ao sistema de migrations)
- [x] 7.3 Atualizar `openspec/specs/db-migrations/spec.md` se necessário (spec já criado como delta)
- [x] 7.4 Fazer commit (`docs: documenta fluxo de migrations no AGENTS.md`)

## 8. QA — Validação conforme qa-plan

- [x] 8.1 Executar `make db-clean` para zerar o banco e verificar fresh install com `make db-migrate-up` + `make run-web`
- [x] 8.2 Verificar que `make db-migrate-status` mostra estado correto após aplicar migrations
- [x] 8.3 Verificar que `make db-migrate-create name="teste"` gera migration corretamente
- [x] 8.4 Verificar que `make db-migrate-down` reverte a última migration
- [x] 8.5 Testar cenário crítico: criar usuário + feed, reiniciar app, verificar que dados sobrevivem
- [x] 8.6 Verificar que `make db-migrate-create` sem `name` exibe erro claro
- [x] 8.7 Executar `make check-all` (lint + typecheck + test + security) e verificar zero erros
- [ ] 8.8 Fazer commit de ajustes de QA se necessário (`test: valida migrations com cenários do qa-plan`)

## 9. Finalização

- [x] 9.1 Executar `make lint` e `make format` — corrigir se necessário
- [x] 9.2 Executar `make typecheck` — verificar zero erros
- [x] 9.3 Executar `make test` — verificar que todos os testes passam
- [x] 9.4 Executar `make security` — verificar zero issues
- [x] 9.5 Fazer commit final de ajustes (`chore: ajustes finais de lint e typecheck`)
