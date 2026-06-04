## Context

Adicionar um feed RSS cria apenas o registro `Feed(url=...)` no banco sem baixar o conteúdo. O usuário precisa manualmente clicar "Atualizar" para ver o feed populado. O serviço `refresh_single_feed` em `refresh_service.py` já implementa todo o parsing — falta apenas conectá-lo ao fluxo de adição.

## Goals / Non-Goals

**Goals:**
- `add_feed` deve retornar o feed criado para que a view possa navegar até ele
- `on_feed_added` deve chamar `refresh_single_feed` após criar o feed
- Em caso de URL inválida, o feed é criado com `last_exception` e o usuário permanece na lista com feedback visual
- Em caso de sucesso, navegar automaticamente para `/feed/<url>` (entry list view)

**Non-Goals:**
- Não alterar `refresh_single_feed` — já funciona
- Não adicionar novas dependências
- Não modificar o modelo de dados

## Decisions

| Decisão | Opção | Alternativa | Razão |
|---------|-------|-------------|-------|
| Onde chamar o refresh | Na view (`on_feed_added`), após `add_feed` | Dentro de `add_feed` no service | Mantém service desacoplado; view controla o fluxo e navegação |
| Como navegar | `page.push_route(f"/feed/{feed.url}")` | `page.go()` | `push_route` mantém histórico de navegação |
| Feedback de erro | Feed criado com `last_exception` + SnackBar | Não criar o feed | Permite ao usuário ver o feed mesmo se falhar, e tentar novamente |

## Risks / Trade-offs

- [Refresh lento] → Feed com muitas entradas pode travar a UI brevemente; aceitável pois é operação única por adição
- [URL inválida] → Feed é criado mesmo sem sucesso; `last_exception` permite diagnóstico e re-tentativa via refresh manual
