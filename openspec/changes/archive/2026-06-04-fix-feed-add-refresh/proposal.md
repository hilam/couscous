## Why

Ao adicionar um novo feed RSS, `add_feed()` persiste apenas a URL no banco sem baixar o conteúdo do feed. O feed aparece na lista sem título, sem link, e sem notícias — o usuário precisa manualmente clicar em "atualizar" para ver o resultado.

## What Changes

- `feed_service.add_feed()` deve também atualizar o feed via `refresh_single_feed` após persistir a URL, ou a view deve chamar o refresh após adicionar
- `feed_list_view.on_feed_added()` deve navegar automaticamente para a tela de listagem de entradas do feed recém-adicionado
- `add_feed` deve propagar o feed recem-criado para que a view possa usá-lo imediatamente

## Capabilities

### New Capabilities
- `feed-add-refresh`: refresh automático do feed imediatamente após adicionar nova URL

### Modified Capabilities
<!-- Nenhuma spec existente muda — o comportamento de adição de feed é interno à view/service -->

## Impact

- `app/services/feed_service.py`: `add_feed` precisa retornar o feed criado e possivelmente chamar refresh
- `app/views/feed_list_view.py`: `on_feed_added` precisa navegar para `/feed/<url>` após adicionar
- `app/services/refresh_service.py`: `refresh_single_feed` já existe e funciona — será reusada
