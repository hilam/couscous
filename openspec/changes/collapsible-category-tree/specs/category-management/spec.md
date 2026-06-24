## MODIFIED Requirements

### Requirement: List categories as tree

O sistema DEVE retornar todas as categorias do usuário autenticado organizadas como uma estrutura de árvore hierárquica. Cada nó da árvore DEVE incluir, além dos campos existentes (`id`, `name`, `parent_id`, `children`), os campos `feed_count` (quantidade de feeds diretamente associados à categoria), `total_feed_count` (quantidade de feeds na categoria e em todas as suas descendentes), e `unread_count` (quantidade de artigos não lidos na categoria e em todas as suas descendentes).

#### Scenario: Flat categories

- **WHEN** usuário possui duas categorias raiz "Tech" e "News" sem filhos, cada uma com 2 feeds, com 3 e 1 artigos não lidos respectivamente
- **THEN** o sistema retorna ambas no nível raiz, cada uma com `feed_count=2`, `total_feed_count=2`, `unread_count` igual a 3 e 1 respectivamente, e `children=[]`

#### Scenario: Nested categories

- **WHEN** usuário possui "Tech" como raiz (1 feed, 2 não lidos) e "Python" como filha de "Tech" (2 feeds, 1 não lido)
- **THEN** "Tech" tem `feed_count=1`, `total_feed_count=3`, `unread_count=3`; "Python" tem `feed_count=2`, `total_feed_count=2`, `unread_count=1`

#### Scenario: No categories

- **WHEN** usuário não possui categorias
- **THEN** o sistema retorna uma árvore vazia
