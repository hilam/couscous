## Context

Atualmente `init_async_db()` em `database/service/database.py` executa `drop_all` seguido de `create_all` a cada inicialização do app. Isso:
- Apaga todos os dados do usuário (feeds, entries, categorias, tags)
- Viola o spec `auto-db-init` que no cenário "Existing tables" diz "no tables SHALL be modified"
- Impede qualquer persistência entre reinicializações do app

O `openspec/config.yaml` menciona Alembic como ferramenta de migrations, mas nunca foi instalado ou configurado.

## Goals / Non-Goals

**Goals:**
- Remover `drop_all` do `init_async_db()` — dados sobrevivem a reinicializações
- Configurar Alembic para versionamento de schema com engine assíncrona (asyncpg) e SQLModel
- Criar migration inicial com snapshot dos 6 modelos atuais
- Fornecer comandos Makefile para gerenciar migrations (criar, aplicar, reverter, verificar status)

**Non-Goals:**
- Auto-migrate no startup (migrations são aplicadas manualmente via Makefile)
- Migrations para o banco de testes (`couscous_test` — continua com `create_all`/`drop_all`)
- Alterar o schema dos modelos — apenas capturar o estado atual

## Decisions

### 1. `init_async_db()` mantém `create_all`, remove `drop_all`

**Decisão**: `init_async_db()` continua usando `create_all` (que é idempotente graças a `CREATE TABLE IF NOT EXISTS`), mas remove a chamada a `drop_all`.

**Alternativa considerada**: Substituir `create_all` por `alembic upgrade head` no startup.
**Por que não**: O usuário decidiu que migrations devem ser manuais. `create_all` garante que um fresh install funcione sem precisar rodar migrations manualmente — o `make db-migrate-up` é necessário apenas quando há mudanças incrementais de schema.

### 2. Alembic no root do projeto (`alembic.ini` + `alembic/`)

**Decisão**: Arquivos de configuração do Alembic ficam na raiz do projeto, seguindo o padrão da comunidade.

**Alternativa considerada**: Colocar dentro de `database/`.
**Por que não**: O Alembic espera `alembic.ini` no diretório de execução por padrão. Colocar dentro de `database/` exigiria `--config database/alembic.ini` em todos os comandos, adicionando atrito desnecessário.

### 3. `env.py` usa `database/service/config.py:DB_URL` como fonte da URL

**Decisão**: O `alembic.ini` contém um placeholder (`driver://user:pass@localhost/dbname`) e o `env.py` sobrescreve com `DB_URL` importado de `config.py`.

**Alternativa considerada**: Duplicar a URL no `alembic.ini`.
**Por que não**: Duas fontes de verdade para a mesma configuração inevitavelmente divergem. `config.py` já lê de `.env` e é o single source of truth para conexão com o banco.

### 4. Engine assíncrona com `asyncio.run()` no `env.py`

**Decisão**: O `env.py` cria uma engine assíncrona via `create_async_engine` e usa `asyncio.run()` para executar `run_migrations_online()`.

**Alternativa considerada**: Usar engine síncrona (`psycopg2`).
**Por que não**: O projeto usa exclusivamente `asyncpg`. Manter duas libs de driver PostgreSQL seria redundante. O Alembic não tem API assíncrona nativa, mas o padrão `asyncio.run()` é amplamente utilizado pela comunidade.

### 5. Migration inicial via `--autogenerate`

**Decisão**: A primeira migration (`001_initial.py`) é gerada com `alembic revision --autogenerate -m "initial"` após configurar o `env.py`, capturando o estado atual de todos os 6 modelos.

**Alternativa considerada**: Escrever a migration manualmente.
**Por que não**: Autogenerate reduz risco de erro humano e garante fidelidade exata ao schema dos modelos SQLModel. A migration gerada será revisada antes do commit.

### 6. `alembic` em dependências principais, não dev

**Decisão**: `alembic` vai em `[project] dependencies`, não em `[dependency-groups] dev`.

**Alternativa considerada**: Colocar apenas em dev.
**Por que não**: Embora migrations sejam executadas manualmente, o pacote é parte essencial do toolchain do projeto e deve estar disponível em qualquer ambiente onde o projeto seja instalado.

### 7. Testes sem Alembic

**Decisão**: `tests/conftest.py` continua usando `create_all`/`drop_all` direto, sem envolvimento do Alembic.

**Alternativa considerada**: Usar Alembic também nos testes.
**Por que não**: Adicionaria complexidade e lentidão desnecessárias. Testes precisam de isolamento e velocidade — `create_all`/`drop_all` em um banco dedicado (`couscous_test`) é a abordagem mais simples e rápida.

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| `create_all` vs `alembic upgrade` podem divergir — se alguém modificar modelos e rodar o app sem rodar migrations, as tabelas serão criadas com `create_all` mas o Alembic não saberá | Documentar no AGENTS.md que mudanças de modelo exigem `make db-migrate-create` + `make db-migrate-up`. O `make db-migrate-status` mostra discrepâncias |
| `asyncio.run()` no `env.py` pode conflitar com event loops existentes em alguns cenários | Só é chamado via CLI (`alembic upgrade head`), nunca dentro do app Flet. Sem conflito |
| Migration inicial pode não capturar índices customizados (apenas FK indexes são auto-gerados) | Revisar a migration gerada. Índices adicionais podem ser adicionados manualmente ou em migration futura |
| Usuário esquecer de rodar `make db-migrate-up` após `make db-clean` | `init_async_db()` com `create_all` serve como safety net — tabelas são criadas mesmo sem migrations |

## Open Questions

- Nenhuma pendente. Todas as decisões foram resolvidas durante a exploração.
