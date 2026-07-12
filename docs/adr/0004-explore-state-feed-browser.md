# ExploreState e FeedBrowser — estado extraído da view

Data: 2026-07-12

## Status

Aceito.

## Contexto

`explore_view` era responsável por 474 linhas de estado mutável (7 variáveis
`nonlocal`), operações de domínio (filtro por categoria/tag, busca full-text)
e construção de UI Flet, tudo no mesmo arquivo. A view era um módulo raso: a
interface (a view function) era tão larga quanto a implementação inteira, e
não havia separação entre lógica de estado e renderização.

Testar unitariamente a lógica de filtro exigia mockar Flet — o que impedia
testes de toggle_tag, select_category e search sem um page mockado.

## Decisão

- Extrair `ExploreState` (dataclass imutável — cada operação retorna uma
  nova instância) para `app/services/feed_browser.py`.
- Extrair 5 funções de operação (`load`, `select_category`, `toggle_tag`,
  `clear_tags`, `search`) — puras no sentido de que recebem sessão + estado
  velho e retornam estado novo.
- `explore_view` mantém uma única `nonlocal browser_state: ExploreState` e
  vira um renderizador: lê o estado, povoa a UI Flet.

## Consequências

**Positivas:**

- `feed_browser` é testável sem Flet: passa `session`, asserts no
  `ExploreState` retornado.
- Lógica de domínio (como "selecionar uma categoria expande ou filtra?")
  concentra em um lugar.
- View fica responsável só por mapear estado para controles Flet e disparar
  operações.
- Navegação por IA melhora: mudanças de filtro/busca tocam um arquivo,
  mudanças de layout tocam outro.

**Negativas:**

- `ExploreState` carrega dados prontos (entries, tag_map, tree, tag_counts)
  mesmo quando a view só precisa de um subconjunto. Custo aceitável para um
  app desktop com ~50 entradas por carga.
- Cada operação recarrega entries do banco (mesmo toggle_tag). Evita estado
  inconsistente entre filtros e dados — cache agressivo seria prematuro.

## Alternativas consideradas

- **Classe mutável (`FeedBrowser` com métodos que alteram `self`):** mais
  simples de implementar. Rejeitado porque estado mutável dificulta testes
  (testes precisam resetar ou recriar o objeto) e esconde quais campos cada
  operação modifica.
- **Manter tudo na view com closures:** era o estado atual — rejeitado por
  falta de testabilidade e localidade.
