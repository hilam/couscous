## Why

Nos formulários de login e registro, pressionar Enter nos campos de texto não submete o formulário — o usuário precisa clicar no botão. Isso quebra a expectativa padrão de formulários web/desktop.

## What Changes

- Adicionar `on_submit` ao campo de senha nos formulários de login e registro para submeter ao pressionar Enter
- Adicionar `on_submit` ao campo de nome para focar no campo de senha (Tab-like behavior)

## Capabilities

### New Capabilities
- `form-enter-submit`: formulários de login e registro submetem ao pressionar Enter no campo de senha

## Impact

- `app/views/login_view.py`: adicionar `on_submit` nos TextFields
- `app/views/register_view.py`: adicionar `on_submit` nos TextFields
