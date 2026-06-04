## Why

Ao adicionar um novo feed RSS, `refresh_single_feed` envolve todo o processamento de entradas num único `try/except`. Uma única entrada mal formatada (ex: `content` em formato inesperado ou `published_parsed` ausente) faz o refresh inteiro falhar. O usuário vê "Feed adicionado, mas erro ao buscar notícias" sem saber o motivo, e o feed fica sem nenhuma entrada.

## What Changes

- `refresh_single_feed`: processar cada entrada individualmente com `try/except` próprio, ignorando entradas problematicas em vez de abortar o feed inteiro
- `on_feed_added`: exibir a mensagem de erro real na SnackBar para diagnóstico
- Feed metadata (título, link) deve ser salvo mesmo se o processamento de entradas falhar parcialmente

## Capabilities

### New Capabilities
- `robust-entry-parsing`: parsing resiliente de entradas RSS — cada entrada é tratada individualmente, falhas não abortam o feed inteiro

## Impact

- `app/services/refresh_service.py`: reestruturar o loop de entradas com try/except por entrada
- `app/views/feed_list_view.py`: exibir o erro real na SnackBar em vez de mensagem genérica
