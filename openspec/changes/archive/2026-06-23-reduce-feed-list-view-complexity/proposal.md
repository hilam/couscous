## Why

A função `feed_list_view` em `app/views/feed_list_view.py` tem 52 statements, ultrapassando o limite de 50 imposto pela regra PLR0915 do Ruff. Isso quebra o `make lint` e impede a passagem no CI gate (`make check-all`). O callback `on_feed_added` concentra ~20 statements com lógica de negócio (criação de feed + refresh + navegação) que pode ser extraída sem alterar comportamento.

## What Changes

- Extrair a lógica do callback `on_feed_added` para uma função assíncrona de módulo `_handle_feed_added` em `app/views/feed_list_view.py`
- Substituir o closure por um wrapper lambda que invoca a nova função com os parâmetros necessários
- `confirm_delete` e `delete_feed` permanecem como closures dentro da view (extraí-los seria overkill para esta mudança)

## Capabilities

### New Capabilities

Nenhuma — refatoração interna, sem nova funcionalidade.

### Modified Capabilities

Nenhuma — sem alteração de comportamento visível ao usuário.

## Impact

- **Arquivo modificado**: `app/views/feed_list_view.py`
- **Risco**: Baixo — extração mecânica de closure, sem mudança de lógica
- **Testes**: Os testes existentes em `tests/test_views.py` ou `tests/test_feed_list_view.py` devem continuar passando sem alteração
