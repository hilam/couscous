## 1. Planejamento e Setup

- [ ] 1.1 Branch `chore/reduce-feed-list-view-complexity` já criada — confirmar `git branch`
- [ ] 1.2 Fazer commit dos artefatos de planejamento (já realizados nos passos anteriores)

## 2. Refatoração — Extrair `_handle_feed_added`

- [ ] 2.1 Criar função assíncrona de módulo `_handle_feed_added` em `app/views/feed_list_view.py` com a assinatura definida no design (`url`, `category_id`, `ctx`, `page`, `user_id`, `feed_list`, `confirm_delete_cb`)
- [ ] 2.2 Mover o corpo atual do closure `on_feed_added` para dentro de `_handle_feed_added`, ajustando referências das variáveis capturadas para os parâmetros recebidos
- [ ] 2.3 Substituir o closure `on_feed_added` dentro de `feed_list_view` por um lambda wrapper que invoca `_handle_feed_added` com os parâmetros da view
- [ ] 2.4 Fazer commit: `git commit -m "refactor(views): extrai on_feed_added para função de módulo"`

## 3. Validação de Qualidade

- [ ] 3.1 Executar `make lint` e verificar que PLR0915 não aparece mais para `feed_list_view.py`
- [ ] 3.2 Executar `make format` e aplicar correções se necessário
- [ ] 3.3 Fazer commit de ajustes de formatação se houver: `git commit -m "style: aplica ruff format"`
- [ ] 3.4 Executar `make typecheck` e verificar que não há novos erros de tipo
- [ ] 3.5 Executar `make test` e verificar que todos os testes existentes passam sem alteração

## 4. QA — Validação de Regressão

- [ ] 4.1 Validar cenário QA: adicionar feed válido → feed é criado e redireciona para `/feed/{url}`
- [ ] 4.2 Validar cenário QA: adicionar feed duplicado → SnackBar "Feed já cadastrado" é exibido
- [ ] 4.3 Validar cenário QA: adicionar feed com URL inválida → SnackBar com erro é exibido
- [ ] 4.4 Validar cenário QA: adicionar feed com categoria → feed aparece agrupado corretamente

## 5. Gate Final

- [ ] 5.1 Executar `make check-all` e verificar que passa completo (lint + typecheck + test + security)
- [ ] 5.2 Fazer commit final se necessário: `git commit -m "chore: verificação final check-all"`
