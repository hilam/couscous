## ADDED Requirements

### Requirement: Filtrar entries por categoria recursivamente

O serviço `list_recent` DEVE aceitar um parâmetro opcional `include_subcategories: bool` que, quando `True` e combinado com `category_id`, faz com que a consulta inclua entries de feeds pertencentes à categoria especificada E a todas as suas subcategorias descendentes (recursivamente).

#### Scenario: Categoria com feeds diretos e em subcategorias

- **WHEN** `list_recent` é chamado com `category_id=1`, `include_subcategories=True`, e a categoria 1 tem subcategorias 2 e 3, cada uma com feeds
- **THEN** o resultado inclui entries de feeds com `category_id` em {1, 2, 3}

#### Scenario: Categoria sem subcategorias

- **WHEN** `list_recent` é chamado com `category_id=5`, `include_subcategories=True`, e a categoria 5 não possui subcategorias
- **THEN** o resultado inclui apenas entries de feeds com `category_id=5` (comportamento idêntico a `include_subcategories=False`)

#### Scenario: include_subcategories=False mantém comportamento atual

- **WHEN** `list_recent` é chamado com `category_id=1`, `include_subcategories=False` (padrão)
- **THEN** o resultado inclui apenas entries de feeds com `category_id=1`, sem incluir subcategorias

#### Scenario: Sem category_id ignora o parâmetro

- **WHEN** `list_recent` é chamado com `category_id=None` e `include_subcategories=True`
- **THEN** o parâmetro `include_subcategories` é ignorado e retorna todas as entries recentes do usuário

### Requirement: Coleta de IDs de categorias descendentes

O sistema DEVE fornecer uma função auxiliar que, dado um `category_id`, retorna uma lista contendo o ID da categoria raiz e todos os IDs de suas categorias descendentes recursivamente.

#### Scenario: Árvore com dois níveis

- **WHEN** a função é chamada com o ID da categoria raiz que possui dois filhos, cada um com um neto
- **THEN** retorna uma lista com os 5 IDs (raiz + 2 filhos + 2 netos)

#### Scenario: Categoria folha

- **WHEN** a função é chamada com o ID de uma categoria sem filhos
- **THEN** retorna uma lista contendo apenas o ID da própria categoria

#### Scenario: Categoria inexistente

- **WHEN** a função é chamada com um ID de categoria que não existe
- **THEN** retorna uma lista vazia
