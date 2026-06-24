# Database Migrations

Versionamento de schema do banco de dados via Alembic com suporte assíncrono (asyncpg + SQLModel).

## Requirements

### Requirement: Migration inicial captura todos os modelos existentes
O sistema DEVE possuir uma migration inicial que capture o schema completo dos 6 modelos atuais (User, Feed, Entry, FeedMetadata, Category, EntryTag), produzida via `alembic revision --autogenerate`.

#### Scenario: Migration inicial gerada a partir dos modelos
- **WHEN** o desenvolvedor executa `alembic revision --autogenerate -m "initial"` com todos os modelos importados no `env.py`
- **THEN** um arquivo de migration é gerado em `alembic/versions/` contendo as operações `create_table` para todas as 6 tabelas, com colunas, tipos, chaves primárias e foreign keys correspondentes aos modelos SQLModel

#### Scenario: Migration inicial é aplicável em banco vazio
- **WHEN** `alembic upgrade head` é executado em um banco PostgreSQL sem nenhuma tabela
- **THEN** todas as 6 tabelas são criadas com sucesso, sem erros

### Requirement: Comandos Makefile para gerenciar migrations
O sistema DEVE prover comandos no Makefile para criar, aplicar, reverter e verificar migrations.

#### Scenario: Criar nova migration
- **WHEN** o desenvolvedor executa `make db-migrate-create name="descricao-da-mudanca"`
- **THEN** o Alembic compara os modelos atuais com o estado do banco e gera um novo arquivo de migration em `alembic/versions/` com um ID único e a descrição fornecida

#### Scenario: Aplicar migrations pendentes
- **WHEN** o desenvolvedor executa `make db-migrate-up`
- **THEN** o Alembic aplica todas as migrations ainda não executadas, na ordem correta, e exibe o novo estado do banco

#### Scenario: Reverter última migration
- **WHEN** o desenvolvedor executa `make db-migrate-down`
- **THEN** o Alembic reverte a migration mais recente e exibe o estado anterior do banco

#### Scenario: Verificar estado das migrations
- **WHEN** o desenvolvedor executa `make db-migrate-status`
- **THEN** o Alembic exibe a migration atual do banco e lista quais migrations estão pendentes, se houver

### Requirement: Ambiente Alembic configurado para SQLModel assíncrono
O sistema DEVE possuir um `alembic/env.py` configurado para usar engine assíncrona (`asyncpg`), com `target_metadata = SQLModel.metadata` e importação explícita de todos os modelos para que o autogenerate funcione.

#### Scenario: Autogenerate detecta todos os modelos
- **WHEN** `alembic revision --autogenerate` é executado
- **THEN** o Alembic detecta a estrutura de todos os modelos importados no `env.py` (User, Feed, Entry, FeedMetadata, Category, EntryTag) e gera operações DDL correspondentes

#### Scenario: URL do banco é lida da configuração do projeto
- **WHEN** o Alembic precisa conectar ao banco para gerar ou aplicar migrations
- **THEN** a URL de conexão é obtida de `database/service/config.py:DB_URL`, que por sua vez lê de variáveis de ambiente (`.env`)

### Requirement: init_async_db preserva dados existentes
O sistema DEVE garantir que `init_async_db()` não apague dados ao iniciar. A função DEVE usar apenas `create_all` (que é idempotente devido a `CREATE TABLE IF NOT EXISTS`), sem chamar `drop_all`.

#### Scenario: Startup com banco populado
- **WHEN** o app inicia e as tabelas já existem com dados de feeds, entries, usuários, categorias e tags
- **THEN** `init_async_db()` completa sem erro e nenhum dado é removido ou alterado

#### Scenario: Fresh install sem migrations aplicadas
- **WHEN** o app inicia e o banco está vazio (nenhuma tabela existe)
- **THEN** `init_async_db()` cria todas as tabelas via `create_all` e o app funciona normalmente
