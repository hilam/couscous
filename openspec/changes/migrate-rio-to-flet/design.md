## Context

O CousCous é um leitor RSS com backend FastAPI + SQLModel/SQLAlchemy e frontend Rio, rodando em dois processos separados. A substituição do Rio pelo Flet unifica tudo num processo único e adiciona portabilidade real (web, desktop, mobile) com uma única base Python.

O banco (`database/models/` e `database/service/`) permanece intacto. A camada de API REST do FastAPI é substituída por funções de serviço Python chamadas diretamente pelas views.

## Goals / Non-Goals

**Goals:**
- Substituir Rio por Flet como framework de UI
- Unificar frontend e backend em um único processo
- Manter models SQLModel e sessões AsyncSession exatamente como estão
- Criar camada de serviço reutilizável (feed_service, entry_service, user_service)
- Suporte a build para web, desktop e mobile via `flet build`
- Navegação baseada em rotas com sessão de banco por tela

**Non-Goals:**
- Não alterar o schema do banco ou models
- Não adicionar autenticação complexa (login simples por enquanto)
- Não implementar sync offline ou cache local
- Não substituir SQLModel por outro ORM

## Decisions

| Decisão | Opção Escolhida | Alternativas | Razão |
|---------|----------------|--------------|-------|
| Arquitetura | Flet puro (acesso direto ao DB) | Flet + FastAPI (2 processos) | Simplicidade; API REST não é necessária para um app desktop/mobile |
| Sessão de banco | Uma AsyncSession por tela | Sessão global, sessão por operação | Ciclo de vida claro: abre ao entrar na view, fecha ao sair |
| Async | AsyncSession + handlers async no Flet | Tudo sync | Compatibilidade com Postgres; Flet suporta async nativamente |
| Navegação | `page.on_route_change` + pilha de `ft.View` | NavigationBar apenas | Permite sub-rotas (ex: `/feed/:url`, `/entry/:id`) |
| Models | SQLModel (inalterado) | SQLAlchemy Core, raw SQL | Zero mudança no código existente |
| Refresh de RSS | `asyncio.to_thread()` para operação blocking | Thread dedicada, subprocesso | Simples e seguro; não bloqueia o event loop do Flet |
| Estado global | `app/state.py` com classe State | session-state do Flet, DB | Claro, testável, desacoplado do Flet |

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Flet é mais novo que Rio — ecossistema menor | Funcionalidades necessárias (NavigationBar, ListView, Markdown, Card) são maduras no Flet |
| AsyncSession + Flet async tem overlap de event loops? | Flet roda no `asyncio` nativo; `get_session` já usa `AsyncSession` — compatível |
| Refresh de RSS bloqueia a UI | Usar `asyncio.to_thread` ou `run_in_executor` + indicador de loading no Flet |
| Perda da API REST pública | Se necessário no futuro, dá pra expor FastAPI separadamente; o service layer já encapsula a lógica |
| Test fixtures precisam ser refeitas | `web.create_app` some; tests passam a usar Flet test utils ou chamar services direto |
