## ADDED Requirements

### Requirement: Criar tag
O sistema DEVE permitir ao usuário criar uma nova etiqueta (tag) associada ao seu `user_id`.

#### Scenario: Criar tag com sucesso
- **WHEN** o usuário informa um nome de tag válido (não vazio, até 100 caracteres)
- **THEN** o sistema cria a tag associada ao `user_id` do usuário autenticado e a retorna

#### Scenario: Criar tag duplicada
- **WHEN** o usuário tenta criar uma tag com nome que já existe para o mesmo `user_id`
- **THEN** o sistema retorna a tag existente sem criar duplicata

### Requirement: Listar tags do usuário
O sistema DEVE permitir ao usuário listar todas as suas tags.

#### Scenario: Listar tags
- **WHEN** o usuário solicita a lista de tags
- **THEN** o sistema retorna todas as tags associadas ao `user_id` do usuário autenticado, ordenadas alfabeticamente

#### Scenario: Nenhuma tag cadastrada
- **WHEN** o usuário solicita a lista de tags e não possui nenhuma
- **THEN** o sistema retorna uma lista vazia

### Requirement: Excluir tag
O sistema DEVE permitir ao usuário excluir uma tag existente. Ao excluir, todas as associações da tag com entries devem ser removidas.

#### Scenario: Excluir tag com sucesso
- **WHEN** o usuário solicita a exclusão de uma tag que lhe pertence
- **THEN** o sistema remove a tag e todas as suas associações com entries

#### Scenario: Tentar excluir tag de outro usuário
- **WHEN** o usuário tenta excluir uma tag que pertence a outro `user_id`
- **THEN** o sistema não encontra a tag (não retorna erro, apenas não faz nada)

### Requirement: Atribuir tag a uma entry
O sistema DEVE permitir ao usuário atribuir uma tag existente a uma entry.

#### Scenario: Atribuir tag a entry
- **WHEN** o usuário associa uma tag existente a uma entry que pertence ao mesmo `user_id`
- **THEN** o sistema cria a associação `EntryTag` e a entry passa a exibir a tag

#### Scenario: Atribuir tag já associada
- **WHEN** o usuário tenta associar uma tag que já está atribuída à mesma entry
- **THEN** o sistema ignora a operação (não cria duplicata)

#### Scenario: Isolamento entre usuários — tags são namespacedas por user_id
- **WHEN** dois usuários diferentes usam a mesma string de tag (ex: "python") em suas respectivas entries
- **THEN** cada usuário vê apenas suas próprias tags; as operações de um usuário não afetam as tags do outro

### Requirement: Remover tag de uma entry
O sistema DEVE permitir ao usuário remover uma tag de uma entry.

#### Scenario: Remover tag de entry
- **WHEN** o usuário remove uma tag de uma entry que lhe pertence
- **THEN** o sistema remove a associação `EntryTag` e a tag deixa de ser exibida na entry

### Requirement: Exibir tags no ArticleCard
O sistema DEVE exibir as etiquetas associadas a cada entry nos cards da lista de artigos.

#### Scenario: Card com tags
- **WHEN** uma entry possui tags associadas
- **THEN** o `ArticleCard` exibe os nomes das tags como chips abaixo do resumo

#### Scenario: Card sem tags
- **WHEN** uma entry não possui tags associadas
- **THEN** o `ArticleCard` não exibe nenhum chip de tag

### Requirement: Gerenciar tags na tela de detalhe da entry
O sistema DEVE permitir adicionar e remover tags diretamente na `entry_view.py`.

#### Scenario: Adicionar tag na entry view
- **WHEN** o usuário está visualizando uma entry e seleciona uma tag para adicionar
- **THEN** o sistema associa a tag à entry e atualiza a lista de tags exibida imediatamente

#### Scenario: Remover tag na entry view
- **WHEN** o usuário clica no botão de remover de um chip de tag na tela de detalhe
- **THEN** o sistema remove a associação e o chip desaparece imediatamente
