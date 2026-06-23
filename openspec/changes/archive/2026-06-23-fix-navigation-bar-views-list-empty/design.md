## Context

O setter `page.navigation_bar` do Flet invoca `__root_view()` internamente, que lança `RuntimeError: views list is empty` quando `page.views` está vazio. No handler `on_route_change` (`app/app.py:34`), a lista é esvaziada com `page.views.clear()` antes da view ser construída. As funções de view chamam `set_navbar(page)` durante sua construção (`feed_list_view:178`, `entry_list_view:156`, `entry_view:164`, `category_list_view:153`, `home_view:9`, `about_view:7`), resultando no erro.

As views de autenticação (`login_view`, `register_view`) e `oauth_callback_view` não chamam `set_navbar` — corretamente, pois não devem exibir navbar.

O arquivo `app/controls/nav_bar.py` contém a lógica de mapeamento de rotas para índices da `NavigationBar` e não precisa ser alterado.

## Goals / Non-Goals

**Goals:**
- Eliminar o `RuntimeError: views list is empty` ao navegar para qualquer rota com navbar
- Preservar o comportamento visual e funcional exato da `NavigationBar`
- Manter a ausência de navbar nas telas de autenticação

**Non-Goals:**
- Alterar a lógica de roteamento ou os destinos da `NavigationBar`
- Modificar o componente `set_navbar` em `nav_bar.py`
- Refatorar outras partes do `on_route_change`

## Decisions

**Decisão 1: Chamar `set_navbar` no handler, não nas views**

Mover a chamada de `set_navbar(page)` de dentro de cada função de view para o handler `on_route_change`, executando-a após `page.views.append(v)` e antes de `page.update()`.

Alternativa considerada: adiar `page.views.clear()` ou evitar limpá-lo. Rejeitada porque `page.views.clear()` é necessário para o modelo de navegação do Flet com `push_route`.

Alternativa considerada: cada view chamar `set_navbar` após construir e retornar o `ft.View`, mas antes do retorno — impossível, pois a view precisa ser adicionada a `page.views` primeiro.

**Decisão 2: Condicionar a navbar por rota**

Apenas rotas que precisam de navbar devem chamar `set_navbar`. Rotas de autenticação (`/login`, `/register`) e OAuth (`/oauth/callback`) não devem. A lógica: após `page.views.append(v)`, chamar `set_navbar(page)` para todas as rotas exceto as três de autenticação.

Alternativa considerada: chamar `set_navbar` incondicionalmente. Rejeitada porque configurar navbar em telas sem navbar é semanticamente incorreto e pode causar efeitos colaterais.

**Decisão 3: Remover imports de `set_navbar` das views**

Cada view que atualmente importa e chama `set_navbar` terá ambas as linhas removidas. O único local que importará `set_navbar` será `app/app.py`.

## Risks / Trade-offs

- **Acoplamento do handler com navbar** → O `on_route_change` passa a conhecer quais rotas têm navbar. Mitigação: a lista de rotas sem navbar (3 rotas) é estável e pequena. Se novas rotas sem navbar forem adicionadas, basta atualizar a condição.
- **Regressão visual** → Se `set_navbar` não for chamada para alguma rota, o usuário verá a tela sem navbar. Mitigação: o QA plan cobre todas as rotas com e sem navbar.
