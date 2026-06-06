## Why

O fluxo OAuth está quebrado: ao autenticar com Google ou GitHub, o usuário é redirecionado de volta para a tela de login em vez de `/feeds`. A causa é que o `_oauth_states` (dict em memória de módulo) não sobrevive ao redirect do provider — a reconexão WebSocket cria uma nova sessão Flet que não contém o state armazenado.

Além disso, `page.launch_url()` foi depreciado no Flet 0.90.0, gerando `DeprecationWarning` em dois pontos do código.

## What Changes

- `_oauth_states` em `oauth_service.py` migra de dict de módulo para `page.session.store`, que o Flet persiste entre reconexões da mesma sessão de browser
- `get_authorization_url()` passa a receber `page` como parâmetro para acessar `page.session`
- `handle_callback()` passa a receber `page` como parâmetro para ler o state da sessão
- `page.launch_url()` substituído por `UrlLauncher().launch_url()` em `oauth_buttons.py` e `entry_view.py`

## Capabilities

### New Capabilities
<!-- nenhuma nova capability — é correção de bug existente -->

### Modified Capabilities
- `oauth-authentication`: O armazenamento do state OAuth muda de memória volátil de módulo para `page.session.store` (sessão Flet persistente). O comportamento externo permanece o mesmo — o que muda é a confiabilidade do fluxo entre sessões.

## Impact

- `app/services/oauth_service.py` — `get_authorization_url()` e `handle_callback()` ganham parâmetro `page`
- `app/controls/oauth_buttons.py` — `_oauth_click()` passa `page` para `get_authorization_url()`; troca `launch_url`
- `app/views/oauth_callback_view.py` — passa `page` para `handle_callback()`
- `app/views/entry_view.py` — troca `launch_url`
- Testes afetados: `test_oauth_service.py` precisa adaptar mocks para novo parâmetro `page`
