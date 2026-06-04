## Why

`httpx.get` por padrão não segue redirecionamentos HTTP. Muitos feeds RSS usam redirecionamento (HTTP→HTTPS, feedburner, encurtadores) e falham ao serem adicionados.

## What Changes

- Adicionar `follow_redirects=True` à chamada `httpx.get` em `refresh_single_feed`

## Capabilities

### New Capabilities
- `follow-redirects`: requisições HTTP para feeds RSS seguem redirecionamentos

## Impact

- `app/services/refresh_service.py`: alterar `httpx.get(feed.url, timeout=30)` para `httpx.get(feed.url, timeout=30, follow_redirects=True)`
