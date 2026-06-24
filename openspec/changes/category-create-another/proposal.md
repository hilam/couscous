## Why

Criar várias categorias em sequência é tedioso. Atualmente o usuário precisa abrir o diálogo, preencher nome, selecionar pai, clicar "Criar", e repetir tudo do zero para cada categoria. Não há suporte à criação em lote.

## What Changes

- Adicionar botão "Criar outro" no diálogo de criação de categoria, que salva o registro mas mantém o formulário aberto, limpa o campo de nome, recarrega o dropdown de categorias-pai e atualiza a árvore de categorias em segundo plano.
- Manter o botão "Criar" com comportamento inalterado (salva e fecha o diálogo).
- Adicionar navegação por teclado: ENTER no campo de nome move o foco para o dropdown de categoria-pai.
- Extrair a lógica de submissão (`_do_create`) para reuso entre "Criar" e "Criar outro".

## Capabilities

### Modified Capabilities
- `category-management`: altera o requisito "Create category" para incluir o botão "Criar outro" e a navegação por teclado entre campos.

## Impact

- `app/views/category_list_view.py`: refatorar `_build_create_dialog` para adicionar botão "Criar outro", extrair lógica compartilhada, e configurar `on_submit` no campo de nome.
