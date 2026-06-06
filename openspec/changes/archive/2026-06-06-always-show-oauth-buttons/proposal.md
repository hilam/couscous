## Why

OAuth login buttons (Google e GitHub) desaparecem das telas de login e registro quando as credenciais não estão configuradas no `.env`. Isso esconde do usuário a existência dessa opção, sem qualquer feedback. É melhor mostrar os botões sempre e exibir erro ao clicar, se o provider não estiver configurado.

Além disso, a lógica de renderização dos botões OAuth está duplicada em `login_view.py` e `register_view.py` (37 linhas idênticas em cada), violando DRY.

## What Changes

- Botões Google e GitHub sempre visíveis nas telas de `/login` e `/register`, independentemente da configuração OAuth
- Ao clicar em um botão de provider não configurado, o sistema exibe mensagem de erro (comportamento já implementado via `ValueError` capturado em `_oauth_click`)
- Código duplicado de `_oauth_buttons` e `_oauth_click` extraído para um controle compartilhado em `app/controls/oauth_buttons.py`
- `login_view.py` e `register_view.py` passam a importar do controle compartilhado

## Capabilities

### New Capabilities
- `oauth-button-component`: Controle compartilhado em `app/controls/oauth_buttons.py` que renderiza botões OAuth e gerencia o clique, reutilizável por qualquer view

### Modified Capabilities
- `oauth-authentication`: O comportamento de "esconder botão quando provider não configurado" (cenário "Missing OAuth configuration") é substituído por "mostrar sempre e exibir erro ao clicar"

## Impact

- `app/controls/oauth_buttons.py` (novo arquivo)
- `app/views/login_view.py` (remoção de código duplicado, novo import)
- `app/views/register_view.py` (remoção de código duplicado, novo import)
- `openspec/specs/oauth-authentication/spec.md` (atualização do cenário "Missing OAuth configuration")
