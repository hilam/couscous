## ADDED Requirements

### Requirement: Botão de copiar link na visualização de entry

O `entry_view` DEVE exibir um botão de copiar link no `AppBar` que copia o link da entry para a área de transferência usando `navigator.clipboard.writeText` via `page.run_javascript()`.

#### Scenario: Copiar link com sucesso

- **WHEN** o usuário clica no botão de copiar link no `AppBar` da entry
- **THEN** o sistema executa `navigator.clipboard.writeText(url)` via JavaScript
- **AND** exibe um snackbar com a mensagem "Link copiado!"

#### Scenario: Falha ao copiar link

- **WHEN** a operação `navigator.clipboard.writeText` falha (ex: permissão negada, contexto não seguro)
- **THEN** o sistema exibe o snackbar "Link copiado!" (comportamento padrão do Python)
- **AND** o JavaScript injeta um banner de erro visível no DOM: "⚠️ Erro ao copiar link — verifique as permissões do navegador"
- **AND** o banner desaparece automaticamente após 5 segundos

### Requirement: Botão de copiar link no ArticleCard

O `ArticleCard` DEVE exibir um botão de copiar link que copia o link da entry representada pelo card.

#### Scenario: Copiar link do card

- **WHEN** o usuário clica no botão de copiar link em um `ArticleCard`
- **THEN** o sistema copia o link da entry associada ao card
- **AND** exibe o snackbar "Link copiado!"

### Requirement: Posicionamento consistente do botão

O botão de copiar link DEVE ser posicionado de forma consistente:
- No `entry_view`: como `IconButton` com ícone `Icons.CONTENT_COPY` no `actions` do `AppBar`
- No `ArticleCard`: como `IconButton` com ícone `Icons.CONTENT_COPY` posicionado no `subtitle` do `ListTile`, dentro de um `Row` de ações

#### Scenario: Botão visível no AppBar da entry

- **WHEN** o usuário visualiza uma entry individual
- **THEN** o `AppBar` contém um `IconButton` com ícone de cópia (`Icons.CONTENT_COPY`) entre as ações

#### Scenario: Botão visível no ArticleCard

- **WHEN** uma lista de entries é exibida
- **THEN** cada `ArticleCard` contém um `IconButton` de cópia no `subtitle` do `ListTile`, dentro de um `Row` de ações

### Requirement: Entry sem link ou plataforma não-web não exibe botão

Se uma entry não possui link (`entry.link` é `None` ou vazio), ou se a plataforma não é web (`page.web` é `False`), o botão de copiar link NÃO DEVE ser exibido.

#### Scenario: Entry sem link

- **WHEN** uma entry tem `link = None`
- **THEN** o botão de copiar link não é renderizado no `entry_view` nem no `ArticleCard`

#### Scenario: Plataforma não-web

- **WHEN** o app está rodando em plataforma nativa/desktop (`page.web = False`)
- **THEN** o botão de copiar link não é renderizado em nenhum local
