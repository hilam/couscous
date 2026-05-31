## Why

Rio é uma biblioteca Python para web com ecossistema pequeno, sem suporte a desktop ou mobile. Para um leitor RSS que naturalmente se beneficiaria de ser usável no celular, a falta de portabilidade real é uma limitação estrutural. Flet oferece uma única base Python que compila para web, desktop (Windows/Mac/Linux) e Android/iOS nativos.

## What Changes

- **BREAKING**: Substituir `rio-ui` por `flet` como framework de frontend
- **BREAKING**: Remover `web/` (código Rio) e `api/main.py` (FastAPI)
- **BREAKING**: Unificar em um único processo Python (`main.py`) — Flet acessa o banco direto via SQLModel
- **NOVA**: Estrutura `app/` com views, services, controls e state
- **NOVA**: Camada de serviço (`feed_service`, `entry_service`, `user_service`) substituindo os endpoints FastAPI
- **NOVO**: `flet build` como mecanismo de deploy para web, desktop e mobile
- Manter `database/` (models SQLModel, service de sessão) intacto
- Manter `pyproject.toml` como ferramenta de dependências (trocar `rio-ui` por `flet`) usando `uv`

## Capabilities

### New Capabilities

- `feed-viewing`: Listar feeds RSS, ver artigos de um feed, visualizar conteúdo de um artigo individual
- `feed-management`: Adicionar novo feed RSS, remover feed
- `user-auth`: Registrar usuário, fazer login, gerenciar sessão
- `feed-refresh`: Atualizar feeds RSS em background (operação blocking em thread separada)
- `cross-platform`: Build para web, desktop (macOS/Windows/Linux) e Android a partir do mesmo código

### Modified Capabilities

<!-- nenhuma — specs existentes está vazia -->

## Impact

- `web/` — removido (~350 linhas de componentes Rio)
- `api/main.py` — removido (FastAPI e rotas REST)
- `rio.toml` — removido (config do Rio)
- `pyproject.toml` — trocar `rio-ui` por `flet` nas dependências
- `main.py` — novo entrypoint (`ft.app(target=...)`)
- `app/` — novo pacote com views, services, controls, state
- `tests/conftest.py` — precisa adaptar fixtures (não usam mais `web.create_app`)
- Nenhuma alteração em `database/models/` ou `database/service/`
