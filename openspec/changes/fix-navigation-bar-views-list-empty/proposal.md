## Why

Após cadastro ou login, ao navegar para a rota `/feeds`, o sistema lança `RuntimeError: views list is empty` ao tentar definir a barra de navegação (`NavigationBar`). O erro ocorre porque `set_navbar(page)` é chamado dentro da construção da view (antes do `page.views.append()`), mas o setter de `page.navigation_bar` no Flet exige que a lista de views não esteja vazia — e ela foi esvaziada por `page.views.clear()` no início do handler `on_route_change`. Este erro impede qualquer navegação para telas com navbar após o fluxo de autenticação.

## What Changes

- Remover as chamadas a `set_navbar(page)` de dentro de cada função de view (`feed_list_view`, `entry_list_view`, `entry_view`, `category_list_view`, `home_view`, `about_view`)
- Centralizar a chamada a `set_navbar(page)` no handler `on_route_change` (`app/app.py`), executando-a APÓS `page.views.append(v)` e antes de `page.update()`, apenas para rotas que exigem navbar (excluindo `/login`, `/register`, `/oauth/callback`)

## Capabilities

### New Capabilities

- `navbar-timing`: A barra de navegação deve ser configurada após a view estar presente em `page.views`, garantindo que o setter do Flet não encontre a lista de views vazia

### Modified Capabilities

- *Nenhuma* — o comportamento em runtime não muda; apenas corrige-se o momento de execução da chamada ao Flet API

## Impact

- **6 arquivos de view**: remoção da chamada `set_navbar()` e do import `from app.controls.nav_bar import set_navbar` onde não for mais necessário
- **1 arquivo core**: `app/app.py` — adição da chamada `set_navbar(page)` no local correto do `on_route_change`
- **1 arquivo de controle**: `app/controls/nav_bar.py` — sem alterações (a função continua existindo, apenas será invocada de outro local)
- Sem mudanças de dependências, modelo de dados ou APIs
