## Context

As telas usam `page.push_route()` que passa por `on_route_change` (que limpa a pilha de views). Não há pilha de navegação — cada navegação é uma substituição. O botão de voltar precisa ser explícito, navegando para a rota "pai".

## Goals / Non-Goals

**Goals:**
- entry_view: voltar para `/feed/<feed_url>` (entry_list_view)
- entry_list_view: voltar para `/feeds` (feed_list_view)

**Non-Goals:**
- Não modificar a lógica de navegação (`on_route_change`)
- Não adicionar empilhamento de views

## Decisions

| Decisão | Opção | Alternativa | Razão |
|---------|-------|-------------|-------|
| Componente | `AppBar.leading` com `ft.IconButton(ft.Icons.ARROW_BACK)` | NavigationBar | `leading` é o local padrão para back button no Material Design |
| Navegação | `page.push_route()` | `page.go()` | Consistente com o resto do app |
| Rota alvo entry_view | `/feed/<entry.feed>` | `/feeds` | Volta para a lista de entradas do mesmo feed |

## Risks / Trade-offs

Nenhum. Mudança puramente aditiva.
