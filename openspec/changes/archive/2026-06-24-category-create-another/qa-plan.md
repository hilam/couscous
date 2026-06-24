## Capability: category-management

### Test: Criar outro salva e mantém diálogo aberto — categoria raiz
**Traces**: `specs/category-management/spec.md` → Requirement: Multi-category creation
- **GIVEN** o diálogo "Nova Categoria" está aberto
- **AND** o campo de nome contém "Tecnologia"
- **AND** o dropdown categoria-pai está em "Nenhuma (raiz)"
- **WHEN** o usuário clica em "Criar outro"
- **THEN** a categoria "Tecnologia" é salva com `parent_id = NULL`
- **AND** o campo de nome é limpo
- **AND** o dropdown categoria-pai é recarregado e "Tecnologia" aparece como opção
- **AND** a árvore de categorias visível é atualizada mostrando "Tecnologia"
- **AND** o diálogo permanece aberto
- **AND** o foco está no campo de nome

### Test: Criar outro salva e mantém diálogo aberto — categoria filha
**Traces**: `specs/category-management/spec.md` → Requirement: Multi-category creation
- **GIVEN** o diálogo "Nova Categoria" está aberto
- **AND** existe a categoria "Tecnologia" na raiz
- **AND** o campo de nome contém "Python"
- **AND** o dropdown categoria-pai está selecionado em "Tecnologia"
- **WHEN** o usuário clica em "Criar outro"
- **THEN** a categoria "Python" é salva com `parent_id` apontando para "Tecnologia"
- **AND** o campo de nome é limpo
- **AND** o dropdown categoria-pai é recarregado e "Python" aparece como filha de "Tecnologia"
- **AND** o foco está no campo de nome

### Test: CRITICAL - Criar fecha o diálogo (comportamento inalterado)
**Traces**: `specs/category-management/spec.md` → Requirement: Create category
- **GIVEN** o diálogo "Nova Categoria" está aberto
- **AND** o campo de nome contém "News"
- **WHEN** o usuário clica em "Criar"
- **THEN** a categoria é salva e o diálogo é fechado
- **AND** a árvore de categorias é atualizada

### Test: Criar outro com nome vazio não faz nada
**Traces**: `specs/category-management/spec.md` → Requirement: Multi-category creation
- **GIVEN** o diálogo "Nova Categoria" está aberto
- **AND** o campo de nome está vazio
- **WHEN** o usuário clica em "Criar outro"
- **THEN** o sistema não tenta salvar
- **AND** o diálogo permanece aberto
- **AND** nenhum erro é exibido

### Test: Criar outro com nome duplicado exibe erro e mantém nome
**Traces**: `specs/category-management/spec.md` → Requirement: Multi-category creation
- **GIVEN** o diálogo "Nova Categoria" está aberto
- **AND** já existe uma categoria "Tech" na raiz
- **AND** o campo de nome contém "Tech"
- **AND** o dropdown categoria-pai está em "Nenhuma (raiz)"
- **WHEN** o usuário clica em "Criar outro"
- **THEN** o sistema exibe snackbar "Categoria já existe neste nível"
- **AND** o campo de nome mantém o valor "Tech"
- **AND** o diálogo permanece aberto

### Test: ENTER no campo nome move foco para dropdown
**Traces**: `specs/category-management/spec.md` → Requirement: Keyboard navigation in category creation form
- **GIVEN** o diálogo "Nova Categoria" está aberto
- **AND** o foco está no campo de nome
- **WHEN** o usuário pressiona ENTER no campo de nome
- **THEN** o foco move-se para o dropdown de categoria-pai

### Test: ENTER no campo nome após preencher nome
**Traces**: `specs/category-management/spec.md` → Requirement: Keyboard navigation in category creation form
- **GIVEN** o diálogo "Nova Categoria" está aberto
- **AND** o campo de nome contém "Design"
- **WHEN** o usuário pressiona ENTER no campo de nome
- **THEN** o foco move-se para o dropdown de categoria-pai
- **AND** o nome "Design" permanece preenchido (não é limpo, não submete)

### Test: EDGE - Criar outro múltiplas vezes em sequência
**Traces**: `specs/category-management/spec.md` → (edge case)
- **GIVEN** o diálogo "Nova Categoria" está aberto
- **WHEN** o usuário cria "A" com "Criar outro", depois "B" com "Criar outro", depois "C" com "Criar outro"
- **THEN** as três categorias existem na árvore
- **AND** o dropdown pai exibe todas elas como opções após cada criação
- **AND** o diálogo permanece aberto após cada criação

### Test: EDGE - Criar outro seguido de Criar
**Traces**: `specs/category-management/spec.md` → (edge case)
- **GIVEN** o diálogo "Nova Categoria" está aberto
- **WHEN** o usuário cria "A" com "Criar outro"
- **AND** preenche "B" e clica em "Criar"
- **THEN** ambas as categorias existem ("A" e "B")
- **AND** o diálogo fecha após "Criar"

### Test: EDGE - Cancelar diálogo após Criar outro
**Traces**: `specs/category-management/spec.md` → (edge case)
- **GIVEN** o diálogo "Nova Categoria" está aberto
- **AND** o usuário já criou uma categoria com "Criar outro"
- **WHEN** o usuário clica em "Cancelar"
- **THEN** o diálogo fecha normalmente
- **AND** a categoria criada anteriormente permanece salva

## Edge Cases

- **Cancelar após múltiplos "Criar outro"**: categorias já salvas não são desfeitas ao cancelar. Comportamento esperado, mas vale validar.
- **Dropdown não dispara criação ao selecionar pai**: `on_change` do dropdown não tem handler de submissão — apenas os botões disparam a criação.

## Integration Points

- **Árvore de categorias**: `refresh_tree()` é chamada tanto por "Criar" quanto por "Criar outro". Ambas devem produzir o mesmo resultado na árvore visível.
- **Serviço `create_category`**: não alterado. Ambos os botões passam pelos mesmos parâmetros e recebem o mesmo tratamento de erro (`ValueError` → snackbar).

## Review Notes

Nenhuma ambiguidade ou cenário não testável identificado.
