## Capability: entry-tags

### Test: Criar tag com sucesso
**Traces**: `specs/entry-tags/spec.md` → Requirement: Criar tag
- **GIVEN** um usuário autenticado com `user_id=1`
- **WHEN** o serviço `create_tag` é chamado com nome "python" e `user_id=1`
- **THEN** a tag "python" é associada ao usuário 1 (primeira atribuição a uma entry materializa a tag)

### Test: Criar tag duplicada — retorna existente
**Traces**: `specs/entry-tags/spec.md` → Requirement: Criar tag
- **GIVEN** o usuário 1 já possui a tag "python"
- **WHEN** o serviço tenta criar novamente a tag "python" para o mesmo usuário
- **THEN** não cria duplicata; a tag existente é retornada

### Test: Listar tags do usuário
**Traces**: `specs/entry-tags/spec.md` → Requirement: Listar tags do usuário
- **GIVEN** o usuário 1 possui tags "python" e "django" em suas entries
- **WHEN** o serviço `list_tags` é chamado com `user_id=1`
- **THEN** retorna ["django", "python"] (ordenado alfabeticamente)

### Test: Listar tags — sem tags
**Traces**: `specs/entry-tags/spec.md` → Requirement: Listar tags do usuário
- **GIVEN** o usuário 1 não possui nenhuma tag em suas entries
- **WHEN** o serviço `list_tags` é chamado com `user_id=1`
- **THEN** retorna lista vazia

### Test: Excluir tag do usuário
**Traces**: `specs/entry-tags/spec.md` → Requirement: Excluir tag
- **GIVEN** o usuário 1 tem a tag "python" em 3 entries
- **WHEN** o serviço `delete_tag` é chamado com nome "python" e `user_id=1`
- **THEN** todas as associações `EntryTag` com tag "python" do usuário 1 são removidas

### Test: Tentar excluir tag de outro usuário — não afeta
**Traces**: `specs/entry-tags/spec.md` → Requirement: Excluir tag
- **GIVEN** usuário 2 tem a tag "python" em suas entries
- **WHEN** usuário 1 tenta excluir a tag "python"
- **THEN** as associações do usuário 2 permanecem intactas

### Test: Atribuir tag a entry
**Traces**: `specs/entry-tags/spec.md` → Requirement: Atribuir tag a uma entry
- **GIVEN** usuário 1 tem uma entry de id=10
- **WHEN** o serviço `assign_tag` é chamado com entry_id=10, tag="python", user_id=1
- **THEN** a associação `EntryTag(entry_id=10, tag="python", user_id=1)` é criada

### Test: Atribuir tag já associada — ignora
**Traces**: `specs/entry-tags/spec.md` → Requirement: Atribuir tag a uma entry
- **GIVEN** entry 10 já tem a tag "python" do usuário 1
- **WHEN** o serviço `assign_tag` é chamado novamente com os mesmos parâmetros
- **THEN** a operação é ignorada (não lança erro, não cria duplicata)

### Test: Atribuir tag de outro usuário — rejeita
**Traces**: `specs/entry-tags/spec.md` → Requirement: Atribuir tag a uma entry
- **GIVEN** usuário 2 tem a tag "python"
- **WHEN** usuário 1 tenta atribuir "python" a uma entry que pertence a usuário 1, mas usando uma tag que pertence ao contexto do usuário 2
- **THEN** comportamento: a tag é atribuída com `user_id=1` (cada usuário tem seu próprio namespace de tags). O teste verifica que `EntryTag.user_id` é sempre o do usuário da operação.

### Test: Remover tag de entry
**Traces**: `specs/entry-tags/spec.md` → Requirement: Remover tag de uma entry
- **GIVEN** entry 10 do usuário 1 tem a tag "python"
- **WHEN** o serviço `remove_tag` é chamado com entry_id=10, tag="python", user_id=1
- **THEN** a associação `EntryTag` é removida

### Test: CRÍTICO — ArticleCard exibe tags
**Traces**: `specs/entry-tags/spec.md` → Requirement: Exibir tags no ArticleCard
- **GIVEN** uma entry possui tags ["python", "tutorial"]
- **WHEN** o `ArticleCard` é renderizado para essa entry
- **THEN** o card exibe dois chips com os textos "python" e "tutorial"

### Test: ArticleCard sem tags
**Traces**: `specs/entry-tags/spec.md` → Requirement: Exibir tags no ArticleCard
- **GIVEN** uma entry não possui tags
- **WHEN** o `ArticleCard` é renderizado para essa entry
- **THEN** o card não exibe nenhum chip de tag

### Test: Adicionar tag na entry view
**Traces**: `specs/entry-tags/spec.md` → Requirement: Gerenciar tags na tela de detalhe da entry
- **GIVEN** usuário está visualizando uma entry sem tags
- **WHEN** o usuário seleciona a tag "python" para adicionar
- **THEN** a tag aparece como chip na tela de detalhe imediatamente

### Test: Remover tag na entry view
**Traces**: `specs/entry-tags/spec.md` → Requirement: Gerenciar tags na tela de detalhe da entry
- **GIVEN** usuário está visualizando uma entry com a tag "python"
- **WHEN** o usuário clica no X do chip "python"
- **THEN** o chip desaparece imediatamente da tela de detalhe

### Test: EDGE — Tag com nome muito longo
**Traces**: `specs/entry-tags/spec.md` → (edge case)
- **GIVEN** um usuário tenta criar uma tag
- **WHEN** o nome da tag excede 100 caracteres
- **THEN** o sistema rejeita a operação com erro de validação

### Test: EDGE — Tag vazia
**Traces**: `specs/entry-tags/spec.md` → (edge case)
- **GIVEN** um usuário tenta criar uma tag
- **WHEN** o nome da tag é string vazia ou apenas espaços
- **THEN** o sistema rejeita a operação

### Test: EDGE — Remover tag que não está na entry
**Traces**: `specs/entry-tags/spec.md` → (edge case)
- **GIVEN** entry 10 não tem a tag "python"
- **WHEN** o serviço `remove_tag` é chamado com entry_id=10, tag="python"
- **THEN** a operação é ignorada sem erro

### Test: EDGE — Entries de usuários diferentes com mesma tag
**Traces**: `specs/entry-tags/spec.md` → (edge case)
- **GIVEN** usuário 1 e usuário 2 ambos usam a tag "python"
- **WHEN** cada um lista suas tags
- **THEN** cada um vê apenas "python" em seu próprio contexto (namespaces isolados por user_id)

## Capability: entry-filters

### Test: CRÍTICO — Filtrar entries por tag
**Traces**: `specs/entry-filters/spec.md` → Requirement: Filter entries by tag
- **GIVEN** um feed tem 5 entries, 2 com tag "python", 3 sem
- **WHEN** o filtro de tag "python" é ativado
- **THEN** apenas as 2 entries com tag "python" são exibidas

### Test: Remover filtro de tag
**Traces**: `specs/entry-filters/spec.md` → Requirement: Filter entries by tag
- **GIVEN** o filtro de tag "python" está ativo mostrando 2 entries
- **WHEN** o usuário desseleciona o filtro
- **THEN** todas as 5 entries do feed são exibidas novamente

### Test: Combinação de filtros — tag + não lidos + importantes
**Traces**: `specs/entry-filters/spec.md` → Requirement: Filter entries by tag
- **GIVEN** um feed com entries variadas: algumas com tag "python", algumas não lidas, algumas importantes
- **WHEN** o usuário ativa simultaneamente filtro "python", "não lidos" e "importantes"
- **THEN** apenas entries que possuem a tag "python" E não foram lidas E são importantes aparecem

### Test: EDGE — Filtrar por tag inexistente
**Traces**: `specs/entry-filters/spec.md` → (edge case)
- **GIVEN** nenhuma entry do feed tem a tag "rust"
- **WHEN** o usuário filtra por "rust"
- **THEN** lista vazia é exibida

### Test: EDGE — Filtro de tag com feed vazio
**Traces**: `specs/entry-filters/spec.md` → (edge case)
- **GIVEN** um feed sem entries
- **WHEN** o usuário tenta filtrar por qualquer tag
- **THEN** lista vazia é exibida (não quebra)

## Edge Cases

- **Concorrência**: Dois requests simultâneos tentando atribuir a mesma tag à mesma entry — a chave composta `(entry_id, tag)` previne duplicatas no banco
- **Case sensitivity**: Tags "Python" e "python" são tratadas como strings distintas (PostgreSQL é case-sensitive por padrão). O service DEVE normalizar para lowercase.
- **Unicode em tags**: Tags com caracteres acentuados ou emojis devem ser aceitas (ex: "café", "inteligência artificial")
- **Cascade delete**: Ao remover um feed, as entries são removidas e as EntryTag correspondentes devem ser removidas em cascade

## Integration Points

- **`entry_service.py`**: `list_entries` ganha parâmetro `tag`; `get_entry` deve retornar tags junto com a entry (ou query separada)
- **`feed_service.py`**: `remove_feed` deve garantir que EntryTag das entries do feed sejam removidas (via cascade)
- **`entry_view.py`**: Carrega tags da entry ao abrir; gerencia adição/remoção inline
- **`entry_list_view.py`**: Carrega tags distintas do feed para exibir chips de filtro; passa tag selecionada ao `list_entries`
- **`ArticleCard`**: Recebe lista de tags e renderiza chips

## Review Notes

Nenhuma ambiguidade ou cenário não-testável identificado nos specs. Os cenários de spec cobrem os fluxos principais e a seção de Edge Cases cobre condições de contorno.
