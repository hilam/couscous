## ADDED Requirements

### Requirement: Expandir e colapsar categorias

O sistema DEVE exibir a árvore de categorias com um indicador visual de toggle (`▶` colapsado, `⮋` expandido) para todo nó que possua subcategorias. O estado de expansão de cada nó DEVE ser independente e mantido enquanto o usuário permanece na tela. A expansão de um nó NÃO DEVE afetar o estado de expansão de outros nós (irmãos ou ancestrais).

#### Scenario: Expandir categoria pai

- **WHEN** usuário clica em uma categoria que possui subcategorias e está colapsada
- **THEN** o indicador muda para `⮋` e as subcategorias filhas tornam-se visíveis imediatamente

#### Scenario: Colapsar categoria pai

- **WHEN** usuário clica em uma categoria que possui subcategorias e está expandida
- **THEN** o indicador muda para `▶` e as subcategorias filhas (e toda sua descendência visível) são ocultadas imediatamente

#### Scenario: Folha sem toggle

- **WHEN** uma categoria não possui subcategorias
- **THEN** o nó é exibido sem indicador de toggle (`▶`/`⮋`)

#### Scenario: Colapsar ancestral não afeta estado interno dos descendentes

- **WHEN** usuário colapsa uma categoria pai que possui um filho expandido
- **THEN** ao expandir novamente o pai, o filho que estava expandido permanece expandido (seu estado interno foi preservado)

### Requirement: Badge de artigos não lidos por categoria

O sistema DEVE exibir um badge numérico ao lado do nome de cada categoria indicando a quantidade total de artigos não lidos naquela categoria e em todas as suas subcategorias descendentes (contagem recursiva). O badge DEVE ser ocultado quando a contagem for zero.

#### Scenario: Badge visível com contagem recursiva

- **WHEN** a categoria "Tecnologia" tem 3 artigos não lidos em feeds diretamente nela e a subcategoria "Frontend" tem 2 artigos não lidos
- **THEN** o badge de "Tecnologia" exibe "5"

#### Scenario: Badge oculto com contagem zero

- **WHEN** uma categoria e todas as suas descendentes não possuem artigos não lidos
- **THEN** nenhum badge é exibido para esta categoria

#### Scenario: Atualização do badge após leitura

- **WHEN** o usuário marca um artigo como lido e retorna à tela principal
- **THEN** os badges são recalculados e a contagem da categoria afetada e seus ancestrais é decrementada

### Requirement: Clique contextual na categoria

O sistema DEVE executar duas ações independentes ao clicar em uma categoria: (a) toggle de expandir/colapsar, se o nó possuir subcategorias; (b) seleção da categoria e carregamento de notícias, se a categoria possuir feeds (diretamente ou em qualquer subcategoria descendente). As ações (a) e (b) DEVEM ocorrer simultaneamente quando ambas as condições forem verdadeiras.

#### Scenario: Categoria com filhos e feeds — toggle + seleção

- **WHEN** usuário clica em "Tecnologia", que possui subcategorias E feeds (diretos ou em descendentes)
- **THEN** o nó expande/colapsa E o painel de notícias é atualizado com as entries de "Tecnologia" e todas as suas subcategorias

#### Scenario: Categoria com filhos mas sem feeds — somente toggle

- **WHEN** usuário clica em "Finanças", que possui subcategorias mas nenhum feed em toda a sua árvore
- **THEN** o nó expande/colapsa, mas o painel de notícias NÃO é alterado

#### Scenario: Categoria folha com feeds — somente seleção

- **WHEN** usuário clica em "React" (categoria sem filhos, mas com feeds)
- **THEN** o painel de notícias é atualizado com as entries da categoria "React"

#### Scenario: Categoria folha sem feeds — sem ação

- **WHEN** usuário clica em uma categoria folha que não possui feeds
- **THEN** nenhuma ação ocorre (painel de notícias inalterado, sem toggle pois não há filhos)

### Requirement: Seleção visual da categoria ativa

O sistema DEVE destacar visualmente a categoria atualmente selecionada (aquela cujas notícias estão sendo exibidas no painel central), diferenciando-a das demais categorias e da opção "Recentes".

#### Scenario: Categoria selecionada destacada

- **WHEN** "Tecnologia" é a categoria selecionada
- **THEN** o tile de "Tecnologia" é exibido com destaque visual (estilo `selected`) e "Recentes" perde o destaque

#### Scenario: Recentes selecionado

- **WHEN** usuário clica em "Recentes"
- **THEN** "Recentes" recebe destaque, a seleção de categoria é limpa, e o painel exibe todas as entries recentes sem filtro de categoria

### Requirement: Comportamento mobile simplificado

No modo mobile (largura < 600px), o sistema DEVE manter o `PopupMenuButton` com a lista plana de categorias (sem expand/colapsar interativo), mas DEVE incluir os badges de contagem de não lidos no texto de cada item do menu.

#### Scenario: Menu mobile exibe badges

- **WHEN** usuário abre o menu de categorias em dispositivo mobile e "Tecnologia" tem 5 não lidos
- **THEN** o item do menu exibe "Tecnologia (5)"

#### Scenario: Menu mobile sem badge para zero

- **WHEN** "Finanças" tem 0 não lidos e usuário abre o menu mobile
- **THEN** o item do menu exibe apenas "Finanças" sem contagem
