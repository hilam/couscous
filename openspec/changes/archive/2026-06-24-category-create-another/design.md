## Context

O diálogo de criação de categoria (`_build_create_dialog` em `category_list_view.py`) possui um único botão "Criar" que salva e fecha o diálogo. A lógica de submissão está inline no handler `_submit`. Não há navegação por teclado entre campos.

O usuário final deseja criar várias categorias em sequência sem reabrir o diálogo a cada vez.

Escopo: apenas `app/views/category_list_view.py`. Nenhum serviço, modelo ou rota é alterado.

## Goals / Non-Goals

**Goals:**
- Botão "Criar outro" salva categoria, limpa nome, recarrega dropdown, atualiza árvore, mantém diálogo aberto com foco no campo nome
- Botão "Criar" mantém comportamento inalterado
- ENTER no campo nome → foco no dropdown categoria-pai
- Lógica de submissão extraída em função compartilhada `_do_create()` para reuso entre os dois botões

**Non-Goals:**
- Não altera o diálogo de renomear categoria
- Não altera o serviço `category_service.py`
- Não altera o modelo `Category`
- Não adiciona atalhos de teclado no dropdown

## Decisions

| Decisão | Opção | Alternativa | Razão |
|---------|-------|-------------|-------|
| Estrutura dos handlers | Extrair `_do_create()` compartilhada, `_submit_and_close` e `_submit_and_continue` chamam `_do_create` | Duplicar lógica em cada handler | DRY, consistência no tratamento de erros |
| ENTER no campo nome | `name_field.on_submit = lambda e: asyncio.create_task(parent_dropdown.focus())` | Também submeter "Criar outro" ou "Criar" | Segue o padrão já usado em `login_view` e `register_view` (ENTER no primeiro campo → foco no próximo) |
| Sem trigger automático no dropdown | `on_change` do dropdown não dispara criação | Criar automaticamente ao selecionar pai | Evita criação acidental ao selecionar pai antes de digitar nome |
| Recarregar dropdown após "Criar outro" | Chamar `_load_parent_dropdown()` a cada criação bem-sucedida | Não recarregar | Necessário para que a nova categoria apareça como opção de pai em criações subsequentes |
| Foco pós-criação | `await name_field.focus()` | Manter foco no dropdown | O fluxo mais natural é começar digitando o próximo nome |

## Risks / Trade-offs

- **Nenhum risco significativo** — mudança puramente aditiva e localizada no frontend, sem alterações no banco de dados ou nos serviços.
