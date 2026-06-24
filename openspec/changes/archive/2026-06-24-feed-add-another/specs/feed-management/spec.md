## ADDED Requirements

### Requirement: Multi-feed creation
O sistema DEVE oferecer um botão "Adicionar outro" no diálogo de adição de feed que salva o registro atual, faz o refresh do feed em background, e mantém o formulário aberto para adicionar feeds adicionais em sequência.

#### Scenario: Adicionar outro após primeiro feed
- **WHEN** o usuário preenche uma URL válida, seleciona uma categoria opcional e clica em "Adicionar outro"
- **THEN** o sistema salva o feed, faz o refresh das entradas em background, limpa o campo de URL, mantém o dropdown de categoria inalterado, atualiza a lista de feeds visível e mantém o diálogo aberto com o foco no campo de URL

#### Scenario: Adicionar outro com URL vazia
- **WHEN** o usuário clica em "Adicionar outro" com o campo de URL vazio
- **THEN** o sistema não faz nada (não salva, não fecha, não limpa)

#### Scenario: Adicionar outro com feed duplicado
- **WHEN** o usuário clica em "Adicionar outro" com uma URL que já existe para o usuário atual
- **THEN** o sistema exibe o snackbar "Feed já cadastrado", mantém a URL preenchida e mantém o diálogo aberto

#### Scenario: Adicionar outro com erro de refresh
- **WHEN** o usuário clica em "Adicionar outro" com uma URL válida, o feed é salvo mas o refresh falha (ex: URL inacessível, timeout)
- **THEN** o sistema exibe snackbar com o erro, o feed aparece na lista com `last_exception` registrado, e o diálogo permanece aberto com campos limpos para continuar

### Requirement: Keyboard navigation in feed creation form
O sistema DEVE permitir navegação por teclado entre os campos do formulário de adição de feed.

#### Scenario: ENTER no campo de URL
- **WHEN** o usuário pressiona ENTER no campo de URL do feed
- **THEN** o foco é movido para o dropdown de categoria

## MODIFIED Requirements

### Requirement: Add feed by URL
The system SHALL allow the user to add a new RSS feed by providing its URL. The feed SHALL be associated with the authenticated user's `user_id`. The user MAY optionally select a category for the feed; if no category is selected, the feed remains uncategorized. The dialog SHALL include both an "Adicionar" button (save, refresh, close dialog, and navigate to feed) and an "Adicionar outro" button (save, refresh in background, clear URL field, and keep dialog open for continued entry).

#### Scenario: Add valid feed
- **WHEN** user taps the "Adicionar feed" button and enters a valid RSS feed URL
- **THEN** the system creates the feed associated with the current user and shows it in the feed list

#### Scenario: Add valid feed with category
- **WHEN** user taps the "Adicionar feed" button, enters a valid RSS feed URL, and selects a category
- **THEN** the system creates the feed associated with the current user and the selected category, and shows it grouped under that category in the feed list

#### Scenario: Add duplicate feed
- **WHEN** user enters a URL that already exists for the current user
- **THEN** the system shows an error message "Feed já cadastrado"

#### Scenario: Adicionar button saves, refreshes, and navigates
- **WHEN** user fills a valid URL and clicks "Adicionar"
- **THEN** the system saves the feed, refreshes its entries, closes the dialog, and navigates to `/feed/{url}`

#### Scenario: Adicionar outro button saves, refreshes, and stays
- **WHEN** user fills a valid URL and clicks "Adicionar outro"
- **THEN** the system saves the feed, refreshes its entries in background, clears the URL field, updates the feed list, and keeps the dialog open with focus returned to the URL field
