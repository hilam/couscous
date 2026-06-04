## Context

`httpx.get` em `refresh_single_feed` não segue redirects (default `follow_redirects=False`). Basta adicionar o parâmetro.

## Goals / Non-Goals

**Goals:**
- Seguir redirects HTTP ao buscar feeds RSS
- Nenhuma mudança em comportamento para URLs que não redirecionam

**Non-Goals:**
- Não limitar número de redirects (default do httpx é 20, suficiente)

## Decisions

| Decisão | Opção | Razão |
|---------|-------|--------|
| Parâmetro | `follow_redirects=True` | Mais explícito que `allow_redirects` (httpx usa `follow_redirects`) |

## Risks / Trade-offs

- [Redirect infinito] → httpx tem limite interno de 20 redirects, lança `TooManyRedirects`
