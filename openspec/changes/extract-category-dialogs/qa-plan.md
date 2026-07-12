## Capability: (refatoração interna — sem specs comportamentais)

Esta mudança não modifica capacidades existentes nem introduz novas. A validação foca em garantir que o comportamento dos dialogs permanece idêntico após a extração.

### Test: CRITICAL — RenameCategoryDialog abre e permite renomear
**Traces**: (refatoração interna — sem spec associado)
- **GIVEN** um nó de categoria com `{"id": 1, "name": "Tecnologia"}`
- **WHEN** `RenameCategoryDialog` é instanciado com `page`, `refresh_cb` e `ctx`
- **THEN** o dialog exibe o campo de nome preenchido com "Tecnologia" e botões Cancelar/Renomear

### Test: CRITICAL — RenameCategoryDialog submete renomeação
**Traces**: (refatoração interna — sem spec associado)
- **GIVEN** `RenameCategoryDialog` aberto com nome "Tecnologia"
- **WHEN** usuário altera para "Tech" e clica Renomear
- **THEN** `rename_category()` é chamado com o novo nome e `refresh_cb()` é invocado

### Test: CRITICAL — CreateCategoryDialog abre com campos vazios
**Traces**: (refatoração interna — sem spec associado)
- **GIVEN** `CreateCategoryDialog` é instanciado
- **WHEN** `load_parents()` é chamado
- **THEN** o dropdown de categoria pai carrega opções e o campo nome está vazio

### Test: CreateCategoryDialog submete criação
**Traces**: (refatoração interna — sem spec associado)
- **GIVEN** `CreateCategoryDialog` com nome "Novidades" e categoria pai "Raiz"
- **WHEN** usuário clica Criar
- **THEN** `create_category()` é chamado e `refresh_cb()` é invocado

### Test: CreateCategoryDialog "Criar outro" limpa e refoca
**Traces**: (refatoração interna — sem spec associado)
- **GIVEN** `CreateCategoryDialog` após criar uma categoria com sucesso
- **WHEN** usuário clica "Criar outro"
- **THEN** o campo nome é limpo, o dropdown recarrega e o campo nome recebe foco

### Test: CreateCategoryDialog valida duplicata
**Traces**: (refatoração interna — sem spec associado)
- **GIVEN** `CreateCategoryDialog` com nome de categoria já existente
- **WHEN** usuário tenta criar
- **THEN** um SnackBar "Categoria já existe neste nível" é exibido e o dialog permanece aberto

## Edge Cases

- **Nome vazio**: `_submit` / `_do_create` retorna sem fazer nada se o nome estiver vazio
- **Parent dropdown com valor "0"**: Deve ser interpretado como `None` (categoria raiz)
- **Load parents com lista vazia**: Deve mostrar apenas "Nenhuma (raiz)" como opção
- **Cancelar**: Fecha o dialog sem executar nenhuma ação
- **ctx.state.user.id None**: Deve ser tratado com guarda para evitar crash (mypy)

## Integration Points

- `CreateCategoryDialog.load_parents()` importa `_flatten_tree_for_dropdown` de `category_list_view.py` — verificar se import circular não ocorre
- Ambos dialogs usam `ctx.open_session()` para operações de banco — verificar se sessão é aberta/fechada corretamente
- `category_list_view.py` deve chamar `CreateCategoryDialog.load_parents()` após `open = True` e antes de `page.update()`

## Review Notes

_Nenhuma._ Sem specs comportamentais para revisar. A validação é puramente técnica (typecheck, lint, testes existentes).
