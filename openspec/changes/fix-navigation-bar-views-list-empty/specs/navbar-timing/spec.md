## ADDED Requirements

### Requirement: Navbar configurada após view ser adicionada ao page.views

O sistema DEVE configurar a `NavigationBar` (via `set_navbar`) somente após a view corrente ter sido adicionada a `page.views`, garantindo que o setter `page.navigation_bar` do Flet não encontre a lista de views vazia.

#### Scenario: Navegação para tela com navbar após login

- **WHEN** o usuário faz login com sucesso e é redirecionado para `/feeds`
- **THEN** a `NavigationBar` é exibida com o ícone "Feeds" selecionado, sem erros

#### Scenario: Navegação para tela com navbar após cadastro

- **WHEN** o usuário se cadastra com sucesso e é redirecionado para `/feeds`
- **THEN** a `NavigationBar` é exibida com o ícone "Feeds" selecionado, sem erros

#### Scenario: Navegação direta para rotas com navbar

- **WHEN** o usuário acessa diretamente as rotas `/feeds`, `/`, `/categories`, `/about`, `/feed/<url>`, ou `/entry/<id>`
- **THEN** a `NavigationBar` é exibida com o ícone correspondente à rota selecionado

### Requirement: Telas de autenticação não possuem navbar

O sistema NÃO DEVE configurar `NavigationBar` nas rotas `/login`, `/register` e `/oauth/callback`.

#### Scenario: Tela de login sem navbar

- **WHEN** o usuário acessa `/login`
- **THEN** a tela de login é exibida sem barra de navegação inferior

#### Scenario: Tela de cadastro sem navbar

- **WHEN** o usuário acessa `/register`
- **THEN** a tela de cadastro é exibida sem barra de navegação inferior
