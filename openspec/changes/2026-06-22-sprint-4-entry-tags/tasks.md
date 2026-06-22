## 1. Git Setup e Planejamento

- [x] 1.1 Criar branch de funcionalidade (`git checkout -b feat/sprint-4-entry-tags`)
- [ ] 1.2 Fazer commit dos artefatos de planejamento (`git add openspec/changes/2026-06-22-sprint-4-entry-tags/ && git commit -m "docs(planning): gera artefatos do sprint 4 entry tags"`)

## 2. Modelo de Dados — EntryTag

- [x] 2.1 Remover classe `FeedTag` (dead code) de `database/models/couscous.py`
- [x] 2.2 Adicionar classe `EntryTag` com campos `entry_id` (FK → entries.id), `tag` (str), `user_id` (FK → users.id), chave primária composta `(entry_id, tag)`
- [ ] 2.3 Fazer commit do modelo (`git add database/models/couscous.py && git commit -m "feat(data): substitui FeedTag por EntryTag com escopo de usuario"`)

## 3. Camada de Serviço — tag_service.py

- [x] 3.1 Criar `app/services/tag_service.py` com funções assíncronas:
  - `get_tags_for_entry(session, entry_id)` — lista tags de uma entry
  - `get_distinct_tags(session, user_id)` — lista tags distintas do usuário
  - `assign_tag(session, entry_id, tag, user_id)` — atribui tag a entry (ignora duplicata)
  - `remove_tag(session, entry_id, tag, user_id)` — remove tag de entry
  - `delete_tag(session, tag, user_id)` — remove todas as associações da tag para o usuário
- [x] 3.2 Adicionar parâmetro `tag: str | None` à função `list_entries` em `entry_service.py` para filtro por tag via JOIN com `EntryTag`
- [ ] 3.3 Fazer commit do service (`git add app/services/tag_service.py app/services/entry_service.py && git commit -m "feat(service): adiciona tag_service com CRUD e filtro por tag em entry_service"`)

## 4. Componente Visual — tag_chip.py

- [x] 4.1 Criar `app/controls/tag_chip.py` com classe `TagChip` (herda de `ft.Container` ou `ft.Chip`):
  - Exibe nome da tag com estilo de chip pequeno e colorido
  - Suporta parâmetro opcional `on_delete` para exibir botão X
- [ ] 4.2 Fazer commit do componente (`git add app/controls/tag_chip.py && git commit -m "feat(ui): cria componente TagChip reutilizavel"`)

## 5. Exibição de Tags nos Cards — ArticleCard

- [x] 5.1 Modificar `app/controls/article_card.py` para receber tags como parâmetro e exibir `TagChip`(s) abaixo do resumo
- [x] 5.2 Adaptar `entry_list_view.py` para carregar tags de cada entry (via JOIN ou query separada) e passá-las ao `ArticleCard`
- [ ] 5.3 Fazer commit da exibição nos cards (`git add app/controls/article_card.py app/views/entry_list_view.py && git commit -m "feat(ui): exibe tags nos ArticleCards da lista de entries"`)

## 6. Gerenciamento de Tags na Tela de Detalhe — entry_view.py

- [x] 6.1 Modificar `entry_view.py` para carregar e exibir tags da entry como chips com botão X para remover
- [x] 6.2 Adicionar botão/interação "Adicionar tag" que abre lista de tags existentes do usuário + campo para nova tag
- [x] 6.3 Implementar handlers `add_tag` e `remove_tag` que chamam `tag_service` e atualizam a UI imediatamente
- [ ] 6.4 Fazer commit da interface de tags na entry view (`git add app/views/entry_view.py && git commit -m "feat(ui): adiciona gerenciamento de tags inline na tela de detalhe"`)

## 7. Filtro por Tag na Lista de Entries — entry_list_view.py

- [x] 7.1 Modificar `entry_list_view.py` para carregar tags distintas do feed atual e exibir como chips de filtro
- [x] 7.2 Implementar lógica de filtro: ao clicar em um chip de tag, recarregar entries com `tag=<selected>` em `list_entries`
- [x] 7.3 Garantir que o filtro de tag combina corretamente com filtros existentes (não lidos, importantes)
- [ ] 7.4 Fazer commit do filtro por tag (`git add app/views/entry_list_view.py && git commit -m "feat(ui): adiciona filtro por tag na lista de entries"`)

## 8. Testes

- [x] 8.1 Criar `tests/test_tag_service.py` com testes para todas as funções do `tag_service.py`:
  - Atribuir tag a entry
  - Remover tag de entry
  - Listar tags de entry
  - Listar tags distintas do usuário
  - Excluir tag (remove todas as associações)
  - Atribuir tag duplicada (ignora)
  - Isolamento entre usuários
- [x] 8.2 Adicionar testes de filtro por tag em `tests/test_entry_service.py`:
  - `list_entries` com parâmetro `tag` filtra corretamente
  - `tag=None` retorna todas as entries (sem filtro)
  - Combinação de tag + unread_only + important_only
- [ ] 8.3 Fazer commit dos testes (`git add tests/ && git commit -m "test: adiciona testes para tag_service e filtro por tag"`)

## 9. Qualidade e QA

- [x] 9.1 Executar lint e formatação com Ruff (`ruff check . && ruff format .`)
- [ ] 9.2 Fazer commit de correções de estilo se houver (`git commit -m "style: aplica ruff format e correcoes de lint"`)
- [ ] 9.3 Executar todos os testes (`uv run pytest -v`)
- [x] 9.4 Executar verificação de tipos (`uv run mypy .`) — passou nos arquivos alterados
- [x] 9.5 Executar varredura de segurança (`make lint-security`) — sem novos issues
- [ ] 9.6 Validar manualmente no browser (`make run-web`):
  - Abrir um artigo e adicionar tags
  - Verificar que tags aparecem nos ArticleCards
  - Filtrar por tag na lista de entries
  - Remover tags da entry view
  - Testar combinação de filtros (tag + não lidos + importantes)
- [ ] 9.7 Fazer commit final de ajustes de QA (`git commit -m "chore: ajustes finais de qualidade e validacao manual"`)
