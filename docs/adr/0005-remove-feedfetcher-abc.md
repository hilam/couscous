# FeedFetcher ABC removido — costura no cliente HTTP

Data: 2026-07-12

## Status

Aceito.

## Contexto

`app/services/feed_fetcher.py` continha uma ABC (`FeedFetcher`) com 1 método
(`fetch`) e 1 implementação (`HttpFeedFetcher`). A interface era quase tão
larga quanto a implementação — um módulo raso.

A interseção real para testes não é o resultado parseado (`FeedFetchResult`),
mas o nível HTTP: substituir o cliente real por um mock que retorna XML
bruto. Isso permite testar parsing e refresh juntos, em vez de mockar o
resultado já parseado.

Testes usavam `FakeFeedFetcher` que estendia a ABC e retornava
`FeedFetchResult` pré-construído — parsing nunca era exercitado em testes.

## Decisão

- `feed_fetcher.py` é deletado.
- `ParsedEntry`, `FeedFetchResult`, `_parse_entry` e a lógica HTTP vão para
  `refresh_service.py` como funções privadas.
- `refresh_single_feed(session, feed, client=None)` aceita
  `httpx.AsyncClient | None` como parâmetro de interseção. Se `None`, cria um
  cliente interno.
- Testes usam `httpx.MockTransport` para injetar XML real — parsing é
  testado junto com refresh.

## Consequências

**Positivas:**

- Um módulo a menos (`feed_fetcher.py` deletado, −88 linhas).
- Parsing é testado: XML malformado, atom vs rss, encoding — tudo passa pelo
  `feedparser` real.
- Costura no `httpx.AsyncClient`: mais fino que a ABC, mais próximo do
  efeito colateral real.
- `refresh_single_feed` fica mais profundo: parsing + HTTP + persistência
  numa interface de 3 parâmetros (session, feed, client opcional).

**Negativas:**

- Testes precisam gerar XML bruto em vez de objetos Python — mais verboso,
  mas mais fiel.
- `refresh_service.py` cresce (absorveu ~70 linhas de parsing). Ainda
  gerenciável (130 linhas).

## Alternativas consideradas

- **Manter a ABC** — a interseção tem dois adapters (HTTP + fake). Pela
  regra "um adapter = hipotético, dois = real", justificava manter. Mas o
  segundo adapter testava a interface errada (resultado parseado, não
  parsing). Rejeitado.
- **Callable `str -> Awaitable[str]`** — mais genérico, menos acoplado a
  httpx. Rejeitado porque httpx já é dependência e `MockTransport` é padrão
  da lib.
