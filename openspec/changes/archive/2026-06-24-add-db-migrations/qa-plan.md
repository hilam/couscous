## Capability: db-migrations

### Test: Migration inicial captura schema dos 6 modelos
**Traces**: `specs/db-migrations/spec.md` → Requirement: Migration inicial captura todos os modelos existentes
- **GIVEN** o `env.py` está configurado com `target_metadata = SQLModel.metadata` e todos os modelos importados (User, Feed, Entry, FeedMetadata, Category, EntryTag)
- **WHEN** o desenvolvedor executa `alembic revision --autogenerate -m "initial"`
- **THEN** um arquivo de migration é criado em `alembic/versions/` contendo operações `create_table()` para users, feeds, entries, feed_metadata, categories e entry_tags, com todas as colunas, tipos, PKs e FKs correspondentes aos modelos

### Test: Migration inicial aplica em banco vazio sem erros
**Traces**: `specs/db-migrations/spec.md` → Requirement: Migration inicial captura todos os modelos existentes
- **GIVEN** um banco PostgreSQL recém-criado, sem nenhuma tabela, e a migration inicial gerada em `alembic/versions/`
- **WHEN** `alembic upgrade head` é executado
- **THEN** as 6 tabelas são criadas, a tabela `alembic_version` registra o revision ID da migration inicial, e o comando sai com código 0

### Test: CRITICAL - Criar nova migration via Makefile
**Traces**: `specs/db-migrations/spec.md` → Requirement: Comandos Makefile para gerenciar migrations
- **GIVEN** o banco está no estado da migration inicial e um novo campo foi adicionado a um modelo SQLModel
- **WHEN** o desenvolvedor executa `make db-migrate-create name="adiciona campo avatar ao usuario"`
- **THEN** um novo arquivo de migration é gerado em `alembic/versions/` com ID único, nome contendo a descrição fornecida, e contendo a operação `add_column()` correspondente ao novo campo

### Test: CRITICAL - Aplicar migrations pendentes via Makefile
**Traces**: `specs/db-migrations/spec.md` → Requirement: Comandos Makefile para gerenciar migrations
- **GIVEN** existem 2 migrations pendentes (não aplicadas) em `alembic/versions/`
- **WHEN** o desenvolvedor executa `make db-migrate-up`
- **THEN** ambas as migrations são aplicadas em ordem, `alembic_version` é atualizado para o revision ID mais recente, e o output mostra o progresso de cada migration

### Test: Reverter última migration via Makefile
**Traces**: `specs/db-migrations/spec.md` → Requirement: Comandos Makefile para gerenciar migrations
- **GIVEN** o banco está no revision `abc123` (duas migrations aplicadas)
- **WHEN** o desenvolvedor executa `make db-migrate-down`
- **THEN** a migration mais recente é revertida, `alembic_version` volta ao revision anterior, e o banco retorna ao estado da primeira migration

### Test: Verificar estado das migrations via Makefile
**Traces**: `specs/db-migrations/spec.md` → Requirement: Comandos Makefile para gerenciar migrations
- **GIVEN** o banco está no revision `abc123` e existe uma migration pendente (`def456`)
- **WHEN** o desenvolvedor executa `make db-migrate-status`
- **THEN** o output mostra o revision atual (`abc123 (head)`) e indica que `def456` está pendente

### Test: Autogenerate detecta todos os modelos importados
**Traces**: `specs/db-migrations/spec.md` → Requirement: Ambiente Alembic configurado para SQLModel assíncrono
- **GIVEN** o `env.py` importa explicitamente User, Feed, Entry, FeedMetadata, Category, EntryTag de `database.models.couscous`
- **WHEN** `alembic revision --autogenerate` é executado
- **THEN** o Alembic detecta a estrutura de todas as 6 tabelas e gera operações DDL completas (colunas, tipos, PKs, FKs, defaults, nullable)

### Test: URL do banco é lida de config.py
**Traces**: `specs/db-migrations/spec.md` → Requirement: Ambiente Alembic configurado para SQLModel assíncrono
- **GIVEN** o arquivo `.env` contém `COUSCOUS_DATABASE_NAME=couscous` e demais variáveis de conexão
- **WHEN** o Alembic é executado (`alembic upgrade head`, `alembic revision`, etc.)
- **THEN** a conexão é estabelecida com o banco `couscous` usando as credenciais e host definidos nas variáveis de ambiente, sem usar o placeholder do `alembic.ini`

### Test: CRITICAL - Startup com banco populado não apaga dados
**Traces**: `specs/db-migrations/spec.md` → Requirement: init_async_db preserva dados existentes
- **GIVEN** o banco contém registros: 1 usuário, 3 feeds, 50 entries, 2 categorias, 5 tags
- **WHEN** o app inicia e `init_async_db()` é chamado
- **THEN** `init_async_db()` completa sem erro, e uma consulta ao banco confirma que todos os registros permanecem intactos (mesma contagem e conteúdo)

### Test: Fresh install sem tabelas cria schema via create_all
**Traces**: `specs/db-migrations/spec.md` → Requirement: init_async_db preserva dados existentes
- **GIVEN** um banco PostgreSQL vazio (recém-criado, sem tabelas)
- **WHEN** o app inicia e `init_async_db()` é chamado
- **THEN** as 6 tabelas são criadas e o app consegue executar operações normalmente (ex: criar usuário, adicionar feed)

### Test: EDGE - Banco inacessível causa erro no startup
**Traces**: `specs/db-migrations/spec.md` → (edge case)
- **GIVEN** o PostgreSQL não está rodando (Docker parado)
- **WHEN** o app inicia e `init_async_db()` tenta conectar
- **THEN** uma exceção é lançada e o app não serve nenhuma rota ou view

### Test: EDGE - create_all com tabelas já existentes é no-op
**Traces**: `specs/db-migrations/spec.md` → (edge case)
- **GIVEN** as 6 tabelas já existem no banco (schema idêntico aos modelos)
- **WHEN** `init_async_db()` chama `create_all`
- **THEN** nenhum erro é gerado e nenhuma tabela é alterada (`CREATE TABLE IF NOT EXISTS` é no-op)

### Test: EDGE - Migration com downgrade definido reverte corretamente
**Traces**: `specs/db-migrations/spec.md` → (edge case)
- **GIVEN** a migration inicial define `downgrade()` com `drop_table` para cada tabela
- **WHEN** `make db-migrate-down` é executado estando na migration inicial
- **THEN** todas as tabelas são removidas e o banco volta ao estado vazio

### Test: EDGE - Comando make db-migrate-create sem nome falha com mensagem clara
**Traces**: `specs/db-migrations/spec.md` → (edge case)
- **GIVEN** o Makefile exige o parâmetro `name`
- **WHEN** o desenvolvedor executa `make db-migrate-create` sem `name="..."`
- **THEN** o Makefile exibe mensagem de erro indicando que o nome é obrigatório

## Edge Cases

- **Banco parcialmente migrado**: Se o app foi iniciado com `create_all` (criou tabelas) mas depois `make db-migrate-up` é executado, o Alembic tentará criar tabelas que já existem e falhará. O fluxo correto é sempre usar Alembic desde o início (`make db-migrate-up` antes do primeiro `make run-web`).
- **Schema drift**: Se um desenvolvedor modificar modelos e rodar `make run-web` sem rodar `make db-migrate-create` + `make db-migrate-up`, as tabelas criadas por `create_all` terão o novo schema mas o Alembic não saberá. O `make db-migrate-status` pode detectar discrepâncias comparando o estado atual do banco com o revision head.
- **Múltiplos bancos (dev/staging)**: O Alembic usa a URL de `config.py`, que lê de `.env`. Para apontar para outro banco, é necessário alterar `.env` ou definir variáveis de ambiente antes de rodar os comandos.
- **Conflito de event loop**: `env.py` usa `asyncio.run()`. Se chamado dentro de um event loop já rodando (ex: dentro de um teste async), pode lançar `RuntimeError`. Isso não deve ocorrer no uso normal (CLI), mas é relevante para possíveis automações futuras.

## Integration Points

- **`init_async_db()` com Alembic**: Embora `init_async_db()` não chame Alembic, ambos manipulam o mesmo banco. O `create_all` do `init_async_db()` serve como safety net para fresh installs. A documentação (AGENTS.md) deve orientar o fluxo: primeiro `make db-migrate-up`, depois `make run-web`.
- **Testes (`conftest.py`)**: Testes usam banco `couscous_test` com `create_all`/`drop_all`. Mudanças nos modelos que requerem migration devem ser refletidas nos testes também — o `create_all` do conftest sempre usa os modelos atuais.
- **`.env` e `config.py`**: Ambos `init_async_db()` e Alembic (`env.py`) usam `database/service/config.py:DB_URL`. A consistência depende de ambos importarem do mesmo módulo.

## Review Notes

- Nenhum cenário ambíguo, contraditório ou não-testável identificado. Todos os 4 requisitos têm cenários verificáveis com precondições, ações e resultados esperados claros.
